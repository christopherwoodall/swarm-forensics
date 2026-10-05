import test from 'node:test';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import pg from 'pg';
import {databaseConfig} from './config.js';
import {Vault} from './vault.js';
import {ChatListener,listenerSchema,snowflakeAt} from './chat-listener.js';
const config=databaseConfig(process.env,null,{test:true}),schema='chat_test_'+crypto.randomBytes(6).toString('hex');
const setup=new pg.Pool(config);await setup.query(`CREATE SCHEMA ${schema}`);await setup.end();
const pool=new pg.Pool({...config,options:`-c search_path=${schema}`});
await pool.query('CREATE TABLE swarms(id uuid PRIMARY KEY,owner text NOT NULL,config jsonb NOT NULL)');await listenerSchema(pool);
const vault=new Vault(pool,crypto.randomBytes(32));await vault.init();
let clock=Date.now(),posts=[],calls=[];const relay={post:async(run,content,nonce,signal)=>{posts.push({run,content,nonce,signal});return {id:'1556792435932270704'};}};
const l=new ChatListener(pool,relay,vault,{origin:'https://chat.example.com',now:()=>clock,fairyRequest:async(url,opts)=>{calls.push({url,opts});return url.endsWith('/api/app-sessions')?{session_id:'fixture-session'}:{status:'stopped',background_jobs_running:0};}});
const bot='1556011112946729031',channel='1556035718042746892',guild='1430962816315031654';
async function row(){const id=crypto.randomUUID();await pool.query('INSERT INTO swarms VALUES($1,$2,$3)',[id,'owner',{verifiedAt:'fixture',guildId:guild,channelId:channel,chat:{mode:'normal',cooldownSeconds:0,maxRepliesPerHour:2},personality:'curious griffin'}]);await l.configure('owner',id,{enabled:true,controlOrigin:'https://runtime.example.com',integrationKey:'synthetic-private-key'});return {...(await pool.query('SELECT * FROM swarms WHERE id=$1',[id])).rows[0],...(await pool.query('SELECT integration_secret,control_origin FROM discord_chat_listener WHERE relay=$1',[id])).rows[0],bot_id:bot,bot_name:'Semi'};}
async function job(r,id=crypto.randomUUID()){const message={id,author:{id:'123456789012345678',bot:false},content:`<@${bot}> hello`,directed:true,timestamp:new Date(clock).toISOString()};const j=await l.enqueue(r,channel,id,[message]);await l.jobs(r);const saved=(await pool.query('SELECT * FROM discord_chat_job WHERE id=$1',[j])).rows[0];const request=JSON.parse(await vault.decrypt('owner',`chat-job:${j}`,saved.request_secret));const token=request.objective.match(/Authorization: Bearer ([\w-]+)/)[1];return {id:j,token,saved};}
test('persistence scopes configuration, encrypts keys, and never returns runtime/callback secrets',async()=>{
 const r=await row();await assert.rejects(l.configure('foreign',r.id,{enabled:false}),/not found/);
 const status=await l.status('owner',r.id);assert.equal(status.enabled,true);assert.equal(status.configured,true);assert.ok(!JSON.stringify(status).includes('synthetic-private-key'));
 const saved=(await pool.query('SELECT integration_secret FROM discord_chat_listener WHERE relay=$1',[r.id])).rows[0].integration_secret;assert.ok(saved.startsWith('v2:'));assert.equal(await vault.decrypt('owner',`chat-runtime:${r.id}`,saved),'synthetic-private-key');
 assert.equal((await l.status('foreign',r.id)).enabled,false);
});
test('one runtime per relay, idempotent message batches, single verified callback delivery and stable nonce',async()=>{
 posts=[];const r=await row(),j=await job(r);assert.equal(j.saved.state,'running');assert.equal(j.saved.session_id,'fixture-session');
 assert.equal(await l.enqueue(r,channel,j.saved.message_id,j.saved.messages),undefined);
 await assert.rejects(l.reply(j.id,'wrong','hello'),/not authorized/);assert.equal(posts.length,0);
 const result=await l.reply(j.id,j.token,'Griffin Go. Hello!');assert.equal(result.state,'completed');assert.equal(posts.length,1);assert.equal(posts[0].run.channelId,channel);assert.ok(posts[0].signal);
 assert.deepEqual(await l.reply(j.id,j.token,'Griffin Go. Hello!'),result);assert.equal(posts.length,1);
 await assert.rejects(l.reply(j.id,j.token,'different'),/differs/);
 const snapshot=await l.status('owner',r.id);assert.equal(snapshot.jobs[0].message_receipt,result.messageId);assert.ok(!JSON.stringify(snapshot).includes(j.token));
});
test('pause, disconnect, current Off/Mentions policy, and deadline prevent late posting',async()=>{
 for(const mode of ['pause','disconnect','off','mentions','deadline']){
 const r=await row(),j=await job(r);const before=posts.length;
 if(mode==='pause')await l.configure('owner',r.id,{enabled:false});
 if(mode==='disconnect')await pool.query("UPDATE swarms SET config=config-'verifiedAt' WHERE id=$1",[r.id]);
 if(mode==='off'||mode==='mentions'){await pool.query("UPDATE swarms SET config=jsonb_set(config,'{chat,mode}',$2) WHERE id=$1",[r.id,JSON.stringify(mode)]);if(mode==='mentions')await pool.query("UPDATE discord_chat_job SET messages=$2 WHERE id=$1",[j.id,JSON.stringify(j.saved.messages.map(m=>({...m,directed:false})))]);}
 if(mode==='deadline')await pool.query("UPDATE discord_chat_job SET deadline_at=now()-interval '1 second' WHERE id=$1",[j.id]);
 await assert.rejects(l.reply(j.id,j.token,'must not send'));assert.equal(posts.length,before);
 }
});
test('all-channel shared cap and silence work; failed deliveries are terminal, never blindly repeated',async()=>{
 const r=await row(),j=await job(r);assert.equal((await l.reply(j.id,j.token,'')).state,'skipped');
 await l.reserve('owner',r.id,'1');await l.reserve('owner',r.id,'2');await assert.rejects(l.reserve('owner',r.id,'3'),/limit/);assert.equal(await l.reserve('owner',r.id,'1'),'reserved');
 assert.equal(await l.enqueue(r,channel,'quota-trigger',[]),'suppressed');
 const r2=await row(),j2=await job(r2);const prior=relay.post;relay.post=async()=>{throw Error('Discord delivery uncertain');};try{await assert.rejects(l.reply(j2.id,j2.token,'hello'),/uncertain/);assert.equal((await l.status('owner',r2.id)).jobs[0].state,'failed');await assert.rejects(l.reply(j2.id,j2.token,'hello'),/expired, stopped or cancelled/);}finally{relay.post=prior;}
});
test('timeout cleanup cancels only owned dispatch; an undispatched queue is never started for cleanup',async()=>{
 const r=await row();const id=await l.enqueue(r,channel,'undispatched',[]);await pool.query("UPDATE discord_chat_job SET state='cancelled',finished_at=now() WHERE id=$1",[id]);const before=calls.length;await l.cleanup();assert.equal(calls.slice(before).some(c=>c.url.endsWith('/api/app-sessions')&&c.opts.body?.client_mutation_id===`chat-${id}`),false);assert.equal((await pool.query('SELECT stop_confirmed FROM discord_chat_job WHERE id=$1',[id])).rows[0].stop_confirmed,true);
});
test.after(async()=>{await pool.query(`DROP SCHEMA ${schema} CASCADE`);await pool.end();});

test('all accessible channels get independent durable cursors; bot triggers and one denied channel do not block another',async()=>{
 const r=await row(),second='1556035718042746893';Object.assign(r,{channels:[{id:channel,name:'general',guildId:guild},{id:second,name:'swarm',guildId:guild}],discovered_at:new Date(clock).toISOString(),announce:false});
 let phase=0;relay.messages=async(run,after)=>{if(!phase)return {messages:[]};if(run.channelId===channel)throw Error('Discord HTTP 403');const id=snowflakeAt(clock+100);return {messages:[{id,author:{id:'123456789012345678',bot:phase===1},content:'hello Semi',timestamp:new Date(clock).toISOString()}]};};
 await l.cycle(r);assert.equal((await pool.query('SELECT count(*)::int AS n FROM discord_chat_cursor WHERE relay=$1',[r.id])).rows[0].n,2);
 phase=1;await l.cycle(r);assert.equal((await l.status('owner',r.id)).state,'degraded');assert.equal((await l.status('owner',r.id)).jobs.length,0);
 phase=2;await l.cycle(r);const status=await l.status('owner',r.id);const jobs=status.jobs;assert.equal(jobs.length,1,JSON.stringify(status));assert.equal(jobs[0].channel_id,second);assert.equal(jobs[0].state,'running');
});
test('runtime guardrail 429 terminates the job without resubmitting or starting it during cleanup',async()=>{
 const r=await row(),id=await l.enqueue(r,channel,'quota-runtime',[]),old=l.fairyRequest;l.fairyRequest=async()=>{throw Object.assign(Error('Runtime daily allowance reached: HTTP 429'),{httpStatus:429});};
 try{await assert.rejects(l.jobs(r),/allowance/);const j=(await pool.query('SELECT * FROM discord_chat_job WHERE id=$1',[id])).rows[0];assert.equal(j.state,'failed');assert.equal(j.stop_confirmed,true);assert.equal(j.request_secret,null);}finally{l.fairyRequest=old;}
});
