import {test,before,after} from 'node:test';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import pg from 'pg';
import express from 'express';
import {databaseConfig} from './config.js';
import {Kanban,kanbanSchema} from './kanban.js';
import {SetupCredentials,setupCredentialSchema,setupExchangeHandler} from './setup-credentials.js';
import {agentHandler} from './agent-api.js';
const namespace='setup_test_'+crypto.randomBytes(8).toString('hex');const admin=new pg.Pool(databaseConfig(process.env,null,{test:true}));
const pool=new pg.Pool({...databaseConfig(process.env,null,{test:true}),options:`-c search_path=${namespace}`}),setup=new SetupCredentials(pool),board=new Kanban(pool),owner='setup-test-'+crypto.randomUUID(),relayId=crypto.randomUUID(),otherId=crypto.randomUUID();let http,origin;
before(async()=>{await admin.query(`CREATE SCHEMA ${namespace}`);await pool.query('CREATE TABLE IF NOT EXISTS swarms(id uuid PRIMARY KEY,owner text NOT NULL,config jsonb NOT NULL)');await kanbanSchema(pool);await setupCredentialSchema(pool);await pool.query('INSERT INTO swarms(id,owner,config) VALUES($1,$3,$4),($2,$3,$4)',[relayId,otherId,owner,{guildId:'123456789012345678',verifiedAt:new Date().toISOString()}]);
 const app=express();app.use(express.json());app.post('/agent/connect',setupExchangeHandler(setup,undefined));app.all(['/agent/v1','/agent/v1/:operation'],agentHandler({pool,board,relay:{profile:async()=>({id:'fixture',username:'Test'}),messages:async()=>({messages:[]})},authenticate:async()=>{throw Error('JWT not available');},version:'test'}));http=app.listen(0,'127.0.0.1');await new Promise(r=>http.once('listening',r));origin=`http://127.0.0.1:${http.address().port}`;
});
after(async()=>{await new Promise(r=>http.close(r));await pool.query('DELETE FROM kanban_agents WHERE owner=$1',[owner]);await pool.query('DELETE FROM swarms WHERE owner=$1',[owner]);await pool.end();await admin.query(`DROP SCHEMA ${namespace} CASCADE`);await admin.end();});
const exchange=token=>fetch(origin+'/agent/connect',{method:'POST',headers:{'Content-Type':'application/json',Authorization:'Bearer '+token},body:'{"name":"Database test"}',signal:AbortSignal.timeout(5000)});
const agent=async(token,operation,body={})=>{const r=await fetch(origin+'/agent/v1'+(operation?'/'+operation:''),{method:operation?'POST':'GET',headers:{'Content-Type':'application/json',Authorization:'Bearer '+token},body:operation?JSON.stringify(body):undefined,signal:AbortSignal.timeout(5000)});return {status:r.status,body:await r.json()};};
test('real SQL race grants exactly one credential and plain JSON HTTPS enforces scope and revocation',async()=>{
 const once=await setup.issue(owner,relayId);await assert.rejects(setup.issue('foreign',relayId),/not found/);assert.equal((await agent(once.token)).status,401);
 const rs=await Promise.all([exchange(once.token),exchange(once.token)]);assert.deepEqual(rs.map(r=>r.status).sort(),[200,401]);const credential=await rs.find(r=>r.status===200).json();assert.equal((await exchange(once.token)).status,401);
 const rows=(await pool.query('SELECT token_hash,relay_id FROM kanban_agents WHERE id=$1',[credential.credentialId])).rows;assert.equal(rows[0].relay_id,relayId);assert.ok(!JSON.stringify(rows).includes(credential.credential));
 const catalog=await agent(credential.credential);assert.equal(catalog.status,200);
 const names=catalog.body.operations.map(t=>t.name);assert.ok(names.includes('board_list_tasks'));assert.ok(names.includes('discord_update_bot_profile'));
 const call=(name,args={})=>agent(credential.credential,name,args);assert.equal((await call('board_list_tasks')).status,200);assert.equal((await call('discord_get_bot_profile',{relayId})).status,200);assert.equal((await call('discord_read_messages',{relayId})).status,200);assert.equal((await call('discord_get_bot_profile',{relayId:otherId})).status,403);

 await board.revoke(owner,credential.credentialId);assert.equal((await call('board_list_tasks')).status,401);
 const expired=await setup.issue(owner,relayId);await pool.query("UPDATE mcp_setup_tokens SET expires_at=now()-interval '1 second' WHERE token_hash=$1",[crypto.createHash('sha256').update(expired.token).digest('hex')]);assert.equal((await exchange(expired.token)).status,401);
 const fresh=await setup.issue(owner,relayId);await assert.rejects(setup.exchange(fresh.token,{name:''}));const a=await setup.exchange(fresh.token);await pool.query("UPDATE kanban_agents SET expires_at=now()-interval '1 second' WHERE id=$1",[a.credentialId]);assert.equal((await agent(a.credential)).status,401);
});
