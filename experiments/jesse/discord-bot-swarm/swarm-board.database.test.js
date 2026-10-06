import {test,before,after} from 'node:test';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import pg from 'pg';
import {databaseConfig} from './config.js';
import {Kanban,kanbanSchema} from './kanban.js';
const namespace='swarm_board_'+crypto.randomBytes(8).toString('hex');
const admin=new pg.Pool(databaseConfig(process.env,null,{test:true}));
const pool=new pg.Pool({...databaseConfig(process.env,null,{test:true}),options:`-c search_path=${namespace}`}),board=new Kanban(pool);
const guild='123456789012345678',otherGuild='123456789012345679',relayA=crypto.randomUUID(),relayB=crypto.randomUUID(),relayC=crypto.randomUUID();
const a={owner:'alice',kind:'owner',actor:'owner',guildId:guild},b={owner:'bob',kind:'owner',actor:'owner',guildId:guild},other={...a,guildId:otherGuild},mid=()=>crypto.randomUUID();let pa,pb;
before(async()=>{
 await admin.query(`CREATE SCHEMA ${namespace}`);await pool.query('CREATE TABLE swarms(id uuid PRIMARY KEY,owner text NOT NULL,config jsonb NOT NULL)');
 for(const [id,owner,guildId] of [[relayA,a.owner,guild],[relayB,b.owner,guild],[relayC,a.owner,otherGuild]])await pool.query('INSERT INTO swarms VALUES($1,$2,$3)',[id,owner,{guildId,verifiedAt:new Date().toISOString(),guildName:guildId===guild?'Shared server':'Other server'}]);
 await kanbanSchema(pool);
 for(const [principal,relay] of [[a,relayA],[b,relayB]]){const issued=await board.issue(principal.owner,{name:principal.owner+' agent',guildId:guild});await pool.query('UPDATE kanban_agents SET relay_id=$1 WHERE id=$2',[relay,issued.id]);const p=await board.principal(issued.token,()=>{throw Error('no fallback');});if(principal===a)pa=p;else pb=p;}
});
after(async()=>{await pool.end();await admin.query(`DROP SCHEMA ${namespace} CASCADE`);await admin.end();});
test('one owner can connect two bots concurrently and rotate, expire or revoke keys independently',async()=>{
 const owner='shared-laptop-'+crypto.randomUUID(),relays=[crypto.randomUUID(),crypto.randomUUID()];
 for(const id of relays)await pool.query('INSERT INTO swarms VALUES($1,$2,$3)',[id,owner,{guildId:'223456789012345678',verifiedAt:new Date().toISOString()}]);
 const authenticate=key=>board.principal(key.token,()=>{throw Error('no fallback');});
 const [first,second]=await Promise.all(relays.map((relayId,i)=>board.issue(owner,{name:'Laptop bot '+i,relayId})));
 assert.notEqual(first.id,second.id);assert.notEqual(first.token,second.token);
 const [pfirst,psecond]=await Promise.all([authenticate(first),authenticate(second)]);
 assert.equal(pfirst.relayId,relays[0]);assert.equal(psecond.relayId,relays[1]);
 const task=(await board.mutate(psecond,{title:'Second bot survives first bot rotation',mutationId:mid()},true)).task;
 await board.mutate(psecond,{taskId:task.id,revision:1,action:'claim',mutationId:mid()});
 const replacement=await board.issue(owner,{name:'Laptop bot 0 replacement',relayId:relays[0]});
 assert.equal((await authenticate(first)).relayId,relays[0]); // Registration never revokes another saved key.
 assert.equal((await authenticate(replacement)).relayId,relays[0]);
 await board.revoke(owner,first.id);await assert.rejects(authenticate(first),/revoked/);
 await assert.rejects(board.list(pfirst),/revoked/);
 await pool.query("UPDATE kanban_agents SET expires_at=now()-interval '1 second' WHERE id=$1",[replacement.id]);
 await assert.rejects(authenticate(replacement),/expired/);
 assert.equal((await authenticate(second)).actor,second.id);
 const done=(await board.mutate(psecond,{taskId:task.id,revision:2,action:'done',note:'Unaffected credential and claim',mutationId:mid()})).task;
 assert.equal(done.assignee,second.id);assert.equal(done.state,'done');
});
test('different accounts and channel agents share the server board, claims and events',async()=>{
 const t=(await board.mutate(pa,{title:'Shared task',mutationId:mid()},true)).task;
 assert.ok((await board.list(pb)).tasks.some(x=>x.id===t.id));assert.ok((await board.list(b)).tasks.some(x=>x.id===t.id));
 const results=await Promise.allSettled([board.mutate(pa,{taskId:t.id,revision:1,action:'claim',mutationId:mid()}),board.mutate(pb,{taskId:t.id,revision:1,action:'claim',mutationId:mid()})]);assert.equal(results.filter(r=>r.status==='fulfilled').length,1);
 const winner=results.find(r=>r.status==='fulfilled').value.task.assignee===pa.actor?pa:pb;
 await board.mutate(winner,{taskId:t.id,revision:2,action:'done',mutationId:mid()});
 assert.equal((await board.list(pb)).tasks.find(x=>x.id===t.id).state,'done');assert.ok((await board.events(pb)).events.some(e=>e.task_id===t.id&&e.payload.task.state==='done'));
 const agents=await board.agents(a.owner,guild);assert.equal(agents.length,2);assert.equal(agents.find(x=>x.id===pb.actor).can_revoke,false);await assert.rejects(board.revoke(a.owner,pb.actor),/not found/);
});
test('server isolation, dependency validation and explicit server selection fail closed',async()=>{
 const t=(await board.mutate(other,{title:'Separate server',mutationId:mid()},true)).task;
 assert.equal((await board.list(pa)).tasks.some(x=>x.id===t.id),false);assert.equal((await board.events(pa)).events.some(x=>x.task_id===t.id),false);
 await assert.rejects(board.mutate(pb,{taskId:t.id,revision:1,action:'claim',mutationId:mid()}),/not found/);
 await assert.rejects(board.mutate(pa,{title:'Bad dependency',dependencies:[t.id],mutationId:mid()},true),/Dependency not found/);
 await assert.rejects(board.list({...b,guildId:otherGuild}),/not authorized/);
 await assert.rejects(board.issue(b.owner,{name:'Foreign board',guildId:otherGuild}),/not authorized/);
 await assert.rejects(board.list({owner:a.owner,kind:'owner'}),/Select a Discord server/);
 assert.deepEqual((await board.boards(a.owner)).map(g=>g.id).sort(),[guild,otherGuild]);
});
test('human claims remain personal and retry IDs are scoped to their server',async()=>{
 const mutationId=mid(),first=(await board.mutate(a,{title:'Human claim',mutationId},true)).task;
 const second=(await board.mutate(other,{title:'Other board',mutationId},true)).task;assert.notEqual(first.id,second.id);
 await board.mutate(a,{taskId:first.id,revision:1,action:'claim',mutationId:mid()});
 await assert.rejects(board.mutate(b,{taskId:first.id,revision:2,action:'done',mutationId:mid()}),/belonging to you/);
 await board.mutate(a,{taskId:first.id,revision:2,action:'done',mutationId:mid()});
 const issued=await board.issue(b.owner,{name:'Board-only member',guildId:guild}),principal=await board.principal(issued.token,()=>{throw Error('no fallback');});
 assert.ok((await board.list(principal)).tasks.some(t=>t.id===first.id));await board.revoke(b.owner,issued.id);await assert.rejects(board.list(principal),/revoked/);
});
test('moving or disconnecting a channel cancels board access for existing agent principals',async()=>{
 const t=(await board.mutate(pa,{title:'Reclaim after disconnect',mutationId:mid()},true)).task;await board.mutate(pa,{taskId:t.id,revision:1,action:'claim',mutationId:mid()});
 await pool.query("UPDATE swarms SET config=config-'verifiedAt' WHERE id=$1",[relayA]);
 await assert.rejects(board.list(pa),/Reconnect/);await assert.rejects(board.mutate(pa,{taskId:t.id,revision:2,action:'done',mutationId:mid()}),/Reconnect/);
 assert.equal((await board.list(pb)).tasks.find(x=>x.id===t.id).effective_state,'stalled');assert.equal((await board.mutate(pb,{taskId:t.id,revision:2,action:'claim',mutationId:mid()})).task.assignee,pb.actor);
 await pool.query('UPDATE swarms SET config=$1 WHERE id=$2',[{guildId:otherGuild,verifiedAt:new Date().toISOString()},relayA]);assert.equal((await board.list(pa)).tasks.some(x=>x.id===t.id),false);assert.equal((await board.list(pa)).guildId,otherGuild);
});
test('migration preserves IDs, dependencies and events; ambiguous legacy boards stay unassigned',async()=>{
 const ns='migration_'+crypto.randomBytes(6).toString('hex');await admin.query(`CREATE SCHEMA ${ns}`);const db=new pg.Pool({...databaseConfig(process.env,null,{test:true}),options:`-c search_path=${ns}`});
 try{
 await db.query('CREATE TABLE swarms(id uuid PRIMARY KEY,owner text NOT NULL,config jsonb NOT NULL)');await kanbanSchema(db);
 for(const [owner,guildId] of [['single',guild],['multi',guild],['multi',otherGuild]])await db.query('INSERT INTO swarms VALUES($1,$2,$3)',[crypto.randomUUID(),owner,{guildId,verifiedAt:'now'}]);
 const first=crypto.randomUUID(),second=crypto.randomUUID(),ambiguous=crypto.randomUUID();for(const [id,owner,deps] of [[first,'single',[]],[second,'single',[first]],[ambiguous,'multi',[]]])await db.query('INSERT INTO kanban_tasks(id,owner,title,description,dependencies) VALUES($1,$2,$3,$4,$5)',[id,owner,'Existing','Keep me',deps]);
 await db.query('INSERT INTO kanban_events(owner,actor,mutation_id,request_hash,task_id,payload) VALUES($1,$2,$3,$4,$5,$6)',['single','owner',mid(),'hash',first,{task:{id:first}}]);await kanbanSchema(db);await kanbanSchema(db);
 const migrated=new Kanban(db),rows=(await migrated.list({owner:'single'})).tasks;assert.deepEqual(rows.map(t=>t.id).sort(),[first,second].sort());assert.deepEqual(rows.find(t=>t.id===second).dependencies,[first]);assert.equal((await migrated.events({owner:'single'})).events[0].task_id,first);
 assert.equal((await migrated.list({owner:'multi',guildId:guild})).tasks.length,2); // Shared server sees the single-server owner's migrated tasks.
 assert.equal((await migrated.list({owner:'multi',guildId:'unassigned'})).tasks[0].id,ambiguous);assert.ok((await migrated.boards('multi')).some(g=>g.id==='unassigned'));
 }finally{await db.end();await admin.query(`DROP SCHEMA ${ns} CASCADE`);}
});
