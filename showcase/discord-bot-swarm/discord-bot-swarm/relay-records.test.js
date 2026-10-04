import {test,before,after} from 'node:test';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import pg from 'pg';
import {databaseConfig} from './config.js';
import {Vault} from './vault.js';
import {saveVerifiedBot,agentPersonality} from './relay-records.js';
const namespace='relay_test_'+crypto.randomBytes(8).toString('hex');
const admin=new pg.Pool(databaseConfig(process.env,null,{test:true}));
const pool=new pg.Pool({...databaseConfig(process.env,null,{test:true}),options:`-c search_path=${namespace}`});
const vault=new Vault(pool,crypto.randomBytes(32));
before(async()=>{await admin.query(`CREATE SCHEMA ${namespace}`);await pool.query(`CREATE TABLE swarms(id uuid PRIMARY KEY,owner text NOT NULL,config jsonb NOT NULL);CREATE TABLE bots(id uuid PRIMARY KEY,swarm uuid REFERENCES swarms(id),bot_id text UNIQUE NOT NULL,name text NOT NULL,role text NOT NULL,secret text NOT NULL,position integer NOT NULL)`);await vault.init();});
after(async()=>{await pool.end();await admin.query(`DROP SCHEMA ${namespace} CASCADE`);await admin.end();});
test('verified token persists before channel setup, with owner-bound encryption',async()=>{
 const identity={id:'100000000000000001',name:'Synthetic bot'},token='synthetic-bot-secret';
 const saved=await saveVerifiedBot(pool,vault,'owner-A',identity,token);
 assert.equal(saved.config.setupStage,'invite');assert.equal(saved.config.channelId,undefined);assert.ok(!JSON.stringify(saved).includes(token));
 const row=(await pool.query('SELECT s.owner,b.secret FROM swarms s JOIN bots b ON b.swarm=s.id WHERE s.id=$1',[saved.id])).rows[0];
 assert.equal(row.owner,'owner-A');assert.equal(await vault.decrypt('owner-A',`discord:${saved.id}`,row.secret),token);
 await assert.rejects(vault.decrypt('owner-B',`discord:${saved.id}`,row.secret));
 const resumed=await saveVerifiedBot(pool,vault,'owner-A',identity,'synthetic-rotated-token');assert.equal(resumed.id,saved.id);const rotated=(await pool.query('SELECT secret FROM bots WHERE swarm=$1',[saved.id])).rows[0];assert.equal(await vault.decrypt('owner-A',`discord:${saved.id}`,rotated.secret),'synthetic-rotated-token');
 await assert.rejects(saveVerifiedBot(pool,vault,'owner-B',identity,token),{status:409});
 assert.equal((await pool.query('SELECT count(*)::int AS n FROM swarms')).rows[0].n,1);
});
test('concurrent verification creates only one durable bot record',async()=>{
 const identity={id:'100000000000000002',name:'Concurrent synthetic bot'};
 const results=await Promise.all([saveVerifiedBot(pool,vault,'owner-C',identity,'synthetic-secret'),saveVerifiedBot(pool,vault,'owner-C',identity,'synthetic-secret')]);assert.equal(results[0].id,results[1].id);
});

test('pending bot connections cannot read or post to Discord',async()=>{
 const {DiscordRelay}=await import('./discord.js');
 const relay=new DiscordRelay({query:async sql=>({rows:sql.includes('SELECT owner')?[{owner:'owner'}]:sql.includes('FROM bots')?[{secret:'cipher'}]:[{config:{name:'Pending bot'}}]})},{decrypt:async()=> 'synthetic'});
 await assert.rejects(relay.check('pending'),/Complete channel setup/);
 await assert.rejects(relay.messages({swarm:'pending',owner:'owner'},null,10),/Complete channel setup/);
 await assert.rejects(relay.post({swarm:'pending',owner:'owner'},'message','nonce'),/Complete channel setup/);
});

test('personality persists through separate connections and preserves owner/setup isolation',async()=>{
 const record=await saveVerifiedBot(pool,vault,'personality-owner',{id:'100000000000000091',name:'Personality fixture'},'synthetic-secret');
 await agentPersonality(pool,'personality-owner',record.id,'Friendly and direct');
 const second=new pg.Pool({...databaseConfig(process.env,null,{test:true}),options:`-c search_path=${namespace}`});
 try{assert.equal((await agentPersonality(second,'personality-owner',record.id)).personality,'Friendly and direct');await assert.rejects(agentPersonality(second,'other-owner',record.id,'overwrite'),/not found/);assert.equal((await pool.query('SELECT config FROM swarms WHERE id=$1',[record.id])).rows[0].config.setupStage,'invite');await agentPersonality(second,'personality-owner',record.id,'');assert.equal((await agentPersonality(pool,'personality-owner',record.id)).personality,'');}finally{await second.end();}
});
