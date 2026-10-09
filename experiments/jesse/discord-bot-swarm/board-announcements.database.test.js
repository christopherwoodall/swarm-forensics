import {test,before,after} from 'node:test';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import pg from 'pg';
import {databaseConfig} from './config.js';
import {Kanban,kanbanSchema} from './kanban.js';
import {deliverAnnouncements,announcementNonce} from './board-announcements.js';
const namespace='board_announce_'+crypto.randomBytes(8).toString('hex'),origin='https://swarm.example';
const admin=new pg.Pool(databaseConfig(process.env,null,{test:true}));
const pool=new pg.Pool({...databaseConfig(process.env,null,{test:true}),options:`-c search_path=${namespace}`}),board=new Kanban(pool);
const guild='123456789012345678',relayOn=crypto.randomUUID(),relayOff=crypto.randomUUID(),mid=()=>crypto.randomUUID();let on,off;
const agent=async(owner,relayId)=>{const issued=await board.issue(owner,{name:owner+' bot',relayId});return board.principal(issued.token,()=>{throw Error('no fallback');});};
const fakeRelay=(failures=0)=>({posts:[],async post(run,content,nonce){this.posts.push({run,content,nonce});if(failures-->0)throw Error('Discord unavailable');return {id:String(100000000000000000n+BigInt(this.posts.length))};}});
const rewind=()=>pool.query("UPDATE kanban_events SET announce_tried_at=announce_tried_at-interval '1 hour' WHERE announce_tried_at IS NOT NULL");
before(async()=>{
 await admin.query(`CREATE SCHEMA ${namespace}`);await pool.query('CREATE TABLE swarms(id uuid PRIMARY KEY,owner text NOT NULL,config jsonb NOT NULL)');
 for(const [id,owner,mode] of [[relayOn,'alice','normal'],[relayOff,'carol','off']])await pool.query('INSERT INTO swarms VALUES($1,$2,$3)',[id,owner,{guildId:guild,channelId:'223456789012345678',verifiedAt:new Date().toISOString(),chat:{mode}}]);
 await kanbanSchema(pool);on=await agent('alice',relayOn);off=await agent('carol',relayOff);
});
after(async()=>{await pool.end();await admin.query(`DROP SCHEMA ${namespace} CASCADE`);await admin.end();});

test('relay agent claims and completions post once as that bot, retrying with the same nonce',async()=>{
 const t=(await board.mutate(on,{title:'Wire the queue',mutationId:mid()},true)).task;
 await board.mutate(on,{taskId:t.id,revision:1,action:'claim',mutationId:mid()});
 await board.mutate(on,{taskId:t.id,revision:2,action:'renew',mutationId:mid()});
 await board.mutate(on,{taskId:t.id,revision:3,action:'done',note:'Released v2 and verified HTTPS.',mutationId:mid()});
 await board.mutate({owner:'alice',actor:'owner',kind:'owner'},{title:'Owner card',mutationId:mid()},true);
 const relay=fakeRelay(1),errors=[];
 await deliverAnnouncements(pool,relay,origin,{onError:e=>errors.push(e.message)});
 assert.equal(errors.length,1);assert.match(errors[0],/attempt 1: Discord unavailable/);
 await deliverAnnouncements(pool,relay,origin);await rewind();await deliverAnnouncements(pool,relay,origin);
 const delivered=relay.posts.slice(1);
 assert.deepEqual(delivered.map(p=>p.content),['Added task “Wire the queue” to the board <https://swarm.example/board.html>','Claimed “Wire the queue” <https://swarm.example/board.html>','Finished “Wire the queue”: Released v2 and verified HTTPS. <https://swarm.example/board.html>']);
 assert.equal(relay.posts[0].nonce,delivered[0].nonce);assert.ok(delivered.every(p=>p.run.swarm===relayOn&&p.run.owner==='alice'));
 const events=(await board.events(on)).events;
 assert.deepEqual(events.map(e=>e.announcement?.state??null),['posted','posted',null,'posted',null]);
 assert.equal(events[0].announcement.messageId,'100000000000000002');assert.equal(events[0].announcement.error,null);
 await deliverAnnouncements(pool,relay,origin);assert.equal(relay.posts.length,4);
});

test('Off chat mode skips announcements and repeated failures end visibly',async()=>{
 await board.mutate(off,{title:'Quiet card',mutationId:mid()},true);
 const quiet=fakeRelay();await deliverAnnouncements(pool,quiet,origin);assert.equal(quiet.posts.length,0);
 const skipped=(await board.events(off)).events.at(-1).announcement;assert.equal(skipped.state,'skipped');assert.match(skipped.error,/Off/);
 const t=(await board.mutate(on,{title:'Flaky',mutationId:mid()},true)).task,broken=fakeRelay(99);
 for(let i=0;i<6;i++){await deliverAnnouncements(pool,broken,origin);await rewind();}
 assert.equal(broken.posts.length,5);assert.ok(broken.posts.every(p=>p.nonce===broken.posts[0].nonce));
 const row=(await pool.query("SELECT seq,announce_state,announce_attempts,announce_error FROM kanban_events WHERE task_id=$1",[t.id])).rows[0];
 assert.deepEqual([row.announce_state,row.announce_attempts,row.announce_error],['failed',5,'Discord unavailable']);assert.equal(broken.posts[0].nonce,announcementNonce(row.seq));
});
