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
await pool.query('CREATE TABLE swarms(id uuid PRIMARY KEY,owner text NOT NULL,config jsonb NOT NULL)');await pool.query('CREATE TABLE bots(swarm uuid,bot_id text,name text,position integer DEFAULT 0)');await listenerSchema(pool);
const vault=new Vault(pool,crypto.randomBytes(32));await vault.init();
let clock=Date.now(),posts=[],calls=[];const relay={post:async(run,content,nonce,signal)=>{posts.push({run,content,nonce,signal});return {id:'1556792435932270704'};}};
const l=new ChatListener(pool,relay,vault,{origin:'https://chat.example.com',now:()=>clock,fairyRequest:async(url,opts)=>{calls.push({url,opts});return url.endsWith('/api/app-sessions')?{session_id:'fixture-session'}:{status:'stopped',background_jobs_running:0};}});
const bot='1556011112946729031',channel='1556035718042746892',guild='1430962816315031654';
async function row(){const id=crypto.randomUUID();await pool.query('INSERT INTO swarms VALUES($1,$2,$3)',[id,'owner',{verifiedAt:'fixture',guildId:guild,channelId:channel,chat:{mode:'normal',cooldownSeconds:0,maxRepliesPerHour:2,replyStyle:'brief'},personality:'curious griffin'}]);await pool.query('INSERT INTO bots VALUES($1,$2,$3,0)',[id,bot,'Semi']);await l.configure('owner',id,{enabled:true,controlOrigin:'https://runtime.example.com',integrationKey:'synthetic-private-key'});return {...(await pool.query('SELECT * FROM swarms WHERE id=$1',[id])).rows[0],...(await pool.query('SELECT integration_secret,control_origin FROM discord_chat_listener WHERE relay=$1',[id])).rows[0],bot_id:bot,bot_name:'Semi'};}
async function job(r,id=crypto.randomUUID()){await l.cleanup();const message={id,author:{id:'123456789012345678',bot:false},content:`<@${bot}> hello`,directed:true,timestamp:new Date(clock).toISOString()};const j=await l.enqueue(r,channel,id,[message]);await l.jobs(r);const saved=(await pool.query('SELECT * FROM discord_chat_job WHERE id=$1',[j])).rows[0];const request=JSON.parse(await vault.decrypt('owner',`chat-job:${j}`,saved.request_secret));const token=request.objective.match(/Authorization: Bearer ([\w-]+)/)[1];return {id:j,token,saved};}
test('persistence scopes configuration, encrypts keys, and never returns runtime/callback secrets',async()=>{
 const r=await row();await assert.rejects(l.configure('foreign',r.id,{enabled:false}),/not found/);
 const status=await l.status('owner',r.id);assert.equal(status.enabled,true);assert.equal(status.configured,true);assert.ok(!JSON.stringify(status).includes('synthetic-private-key'));
 const saved=(await pool.query('SELECT integration_secret FROM discord_chat_listener WHERE relay=$1',[r.id])).rows[0].integration_secret;assert.ok(saved.startsWith('v2:'));assert.equal(await vault.decrypt('owner',`chat-runtime:${r.id}`,saved),'synthetic-private-key');
 assert.equal((await l.status('foreign',r.id)).enabled,false);
});
test('one runtime per relay, idempotent message batches, single verified callback delivery and stable nonce',async()=>{
 posts=[];const r=await row(),j=await job(r);assert.equal(j.saved.state,'running');assert.equal(j.saved.session_id,'fixture-session');
 assert.equal(await l.enqueue(r,channel,j.saved.message_id,j.saved.messages),undefined);
 await assert.rejects(l.reply(j.id,'wrong-synthetic-token','hello'),/not authorized/);assert.equal(posts.length,0);
 const result=await l.reply(j.id,j.token,'Griffin Go, hello!');assert.equal(result.state,'completed');assert.equal(posts.length,1);assert.equal(posts[0].run.channelId,channel);assert.ok(posts[0].signal);
 assert.deepEqual(await l.reply(j.id,j.token,'Griffin Go, hello!'),result);assert.equal(posts.length,1);
 await assert.rejects(l.reply(j.id,j.token,'different'),/differs/);
 const snapshot=await l.status('owner',r.id);assert.equal(snapshot.jobs[0].message_receipt,result.messageId);assert.ok(!JSON.stringify(snapshot).includes(j.token));
});
test('callback rejects verbose replies before effects and permits corrected delivery while preserving old receipts',async()=>{
 posts=[];const r=await row(),j=await job(r);
 for(const content of ['Done. Hello!', 'done. hello.', 'x'.repeat(401), 'One\nTwo']){
  await assert.rejects(l.reply(j.id,j.token,content),e=>e.status===400&&/one brief sentence/.test(e.message));
  assert.equal(posts.length,0);
  const saved=(await pool.query('SELECT state,content FROM discord_chat_job WHERE id=$1',[j.id])).rows[0];assert.equal(saved.state,'running');assert.equal(saved.content,null);
  assert.equal((await pool.query('SELECT count(*)::int AS n FROM discord_chat_delivery WHERE relay=$1',[r.id])).rows[0].n,0);
 }
 assert.equal((await l.reply(j.id,j.token,'One brief sentence, verified.')).state,'completed');assert.equal(posts.length,1);
 const r2=await row(),j2=await job(r2),old='Earlier verbose reply. Preserved without reposting.';
 await pool.query("UPDATE discord_chat_job SET state='completed',content=$2,message_receipt=$3 WHERE id=$1",[j2.id,old,'1556792435932270704']);
 assert.equal((await l.reply(j2.id,j2.token,old)).state,'completed');assert.equal(posts.length,1);
 const r3=await row();await pool.query("UPDATE swarms SET config=jsonb_set(config,'{chat}',(config->'chat')-'replyStyle') WHERE id=$1",[r3.id]);const j3=await job(r3);
 assert.equal((await l.reply(j3.id,j3.token,'Other bot reply. Existing style stays.')).state,'completed');assert.equal(posts.length,2);
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
 const r=await row(),second='1556035718042746893';Object.assign(r,{activated_at:new Date(clock-10000).toISOString(),channels:[{id:channel,name:'general',guildId:guild},{id:second,name:'swarm',guildId:guild}],discovered_at:new Date(clock).toISOString(),announce:false});
 let phase=0;relay.messages=async(run,after)=>{if(!phase)return {messages:[]};if(run.channelId===channel)throw Error('Discord HTTP 403');const id=snowflakeAt(clock+100);return {messages:[{id,author:{id:'123456789012345678',bot:phase===1},content:'hello Semi',timestamp:new Date(clock).toISOString()}]};};
 await l.cycle(r);assert.equal((await pool.query('SELECT count(*)::int AS n FROM discord_chat_cursor WHERE relay=$1',[r.id])).rows[0].n,2);
 assert.equal((await pool.query('SELECT last_id FROM discord_chat_cursor WHERE relay=$1 AND channel_id=$2',[r.id,second])).rows[0].last_id,snowflakeAt(clock-10000));
 phase=1;await l.cycle(r);assert.equal((await l.status('owner',r.id)).state,'degraded');assert.equal((await l.status('owner',r.id)).jobs.length,0);
 phase=2;await l.cycle(r);const status=await l.status('owner',r.id);const jobs=status.jobs;assert.equal(jobs.length,1,JSON.stringify(status));assert.equal(jobs[0].channel_id,second);assert.equal(jobs[0].state,'running');
});
test('runtime guardrail 429 terminates the job without resubmitting or starting it during cleanup',async()=>{
 const r=await row(),id=await l.enqueue(r,channel,'quota-runtime',[]),old=l.fairyRequest;l.fairyRequest=async()=>{throw Object.assign(Error('Runtime daily allowance reached: HTTP 429'),{httpStatus:429,retryAt:clock/1000+60});};
 try{await assert.rejects(l.jobs(r),/allowance/);const j=(await pool.query('SELECT * FROM discord_chat_job WHERE id=$1',[id])).rows[0];assert.equal(j.state,'failed');assert.equal(j.stop_confirmed,true);assert.equal(j.request_secret,null);const status=await l.status('owner',r.id);assert.equal(status.state,'blocked');assert.ok(Date.parse(status.blocked_until)>clock);const saved=(await pool.query('SELECT blocked_until FROM discord_chat_listener WHERE relay=$1',[r.id])).rows[0];await l.cycle({...r,...saved});assert.equal((await l.status('owner',r.id)).state,'blocked');}finally{l.fairyRequest=old;}
});

test('any verified channel participant can request only supported self changes after explicit owner enablement',async()=>{
 const r=await row();await assert.rejects(l.selfChanges('foreign',r.id,'channel'),/not found/);await assert.rejects(l.selfChanges('owner',r.id,'owner'),/authorized Discord user/);await l.selfChanges('owner',r.id,'channel');
 const message={id:crypto.randomUUID(),author:{id:'816894571693735946',bot:false},content:'Semi change your personality to be quieter',timestamp:new Date(clock).toISOString(),directed:true};
 const id=await l.enqueue(r,channel,message.id,[message]);await l.jobs(r);const saved=(await pool.query('SELECT * FROM discord_chat_job WHERE id=$1',[id])).rows[0];assert.deepEqual(saved.allowed_fields,['personality']);assert.ok(Date.parse(saved.deadline_at)>clock+500000);
 const req=JSON.parse(await vault.decrypt('owner',`chat-job:${id}`,saved.request_secret)),token=req.objective.match(/Authorization: Bearer ([\w-]+)/)[1];assert.ok(req.objective.includes('TRUSTED SELF-CHANGE PERMISSION'));
 await assert.rejects(l.reply(id,token,'no',{username:'Other'}),/does not authorize/);
 await assert.rejects(l.reply(id,token,'Quieter now. All changed.',{personality:'curious griffin, quieter'}),e=>e.status===400&&/one brief sentence/.test(e.message));
 assert.equal((await pool.query('SELECT config FROM swarms WHERE id=$1',[r.id])).rows[0].config.personality,'curious griffin');
 assert.equal((await pool.query('SELECT state FROM discord_chat_job WHERE id=$1',[id])).rows[0].state,'running');
 const result=await l.reply(id,token,'Quieter now.',{personality:'curious griffin, quieter'});assert.deepEqual(result.selfChangeReceipt.appliedFields,['personality']);assert.equal((await pool.query('SELECT config FROM swarms WHERE id=$1',[r.id])).rows[0].config.personality,'curious griffin, quieter');
 assert.deepEqual(await l.reply(id,token,'Quieter now.',{personality:'curious griffin, quieter'}),result);
});
test('revoking participant policy blocks an already-running proposal; ordinary conversation cannot forge self permission',async()=>{
 const r=await row();await l.selfChanges('owner',r.id,'channel');const message={id:crypto.randomUUID(),author:{id:'816894571693735946',bot:false},content:'Semi change your name to Semington',timestamp:new Date(clock).toISOString(),directed:true};
 const id=await l.enqueue(r,channel,message.id,[message]);await l.jobs(r);const saved=(await pool.query('SELECT request_secret FROM discord_chat_job WHERE id=$1',[id])).rows[0],req=JSON.parse(await vault.decrypt('owner',`chat-job:${id}`,saved.request_secret)),token=req.objective.match(/Authorization: Bearer ([\w-]+)/)[1];await l.selfChanges('owner',r.id,'off');await assert.rejects(l.reply(id,token,'Changed',{username:'Semington'}),/withdrawn/);
 const ordinary=await job(await row());await assert.rejects(l.reply(ordinary.id,ordinary.token,'Changed',{personality:'new'}),/does not authorize/);
});
test('profile proposals use the existing owned API and verify before posting; an uncertain profile mutation is never retried',async()=>{
 const r=await row();await l.selfChanges('owner',r.id,'channel');let profileCalls=[];
 relay.profile=async(run,changes,signal)=>{assert.equal(run.owner,'owner');assert.ok(signal);profileCalls.push(changes);return {username:changes?.username||'Semington',avatarUrl:'https://cdn.example.com/avatar.png'};};
 async function nameJob(text){const message={id:crypto.randomUUID(),author:{id:'816894571693735946',bot:false},content:text,timestamp:new Date(clock).toISOString(),directed:true};const id=await l.enqueue(r,channel,message.id,[message]);await l.jobs(r);const saved=(await pool.query('SELECT request_secret FROM discord_chat_job WHERE id=$1',[id])).rows[0],req=JSON.parse(await vault.decrypt('owner',`chat-job:${id}`,saved.request_secret));return {id,token:req.objective.match(/Authorization: Bearer ([\w-]+)/)[1]};}
 const j=await nameJob('Semi rename yourself Semington');const out=await l.reply(j.id,j.token,'Semington it is.',{username:'Semington'});assert.deepEqual(profileCalls,[{username:'Semington'},undefined]);assert.equal(out.selfChangeReceipt.profile.username,'Semington');
 const j2=await nameJob('Semi rename yourself Semi');let attempts=0;relay.profile=async()=>{attempts++;throw Error('Profile update uncertain; reconcile profile.');};await assert.rejects(l.reply(j2.id,j2.token,'Changed',{username:'Semi'}),/uncertain/);await assert.rejects(l.reply(j2.id,j2.token,'Changed',{username:'Semi'}),/expired, stopped or cancelled/);assert.equal(attempts,1);
});

test('broad work preserves verified trigger, ordinary runtime tools, control checks and revocation',async()=>{
 const r=await row();await assert.rejects(l.workRequests('foreign',r.id,'channel'),/not found/);await l.workRequests('owner',r.id,'channel');const message={id:'1556804486108811315',author:{id:'269751214026129409',bot:false},content:'Semi add recent messages from general to your context',timestamp:new Date(clock).toISOString(),directed:true};const context={messages:[message],channels:[{id:channel,name:'swarm',guildId:guild}],omittedMessages:0};const id=await l.enqueue(r,channel,message.id,[message],context);await l.jobs(r);const saved=(await pool.query('SELECT * FROM discord_chat_job WHERE id=$1',[id])).rows[0],req=JSON.parse(await vault.decrypt('owner',`chat-job:${id}`,saved.request_secret)),token=req.objective.match(/Authorization: Bearer ([\w-]+)/)[1];assert.equal(saved.allowed_work,true);assert.deepEqual(saved.context,context);assert.ok(Date.parse(saved.deadline_at)>=clock+1799000);assert.match(req.objective,/ordinary FairyStack coding-agent capabilities/);assert.ok(!req.objective.includes('chat-only worker'));assert.ok(req.objective.length<=20000);assert.equal((await l.control(id,token)).authorityActive,true);await assert.rejects(l.control(id,'not-the-callback-token'),/not authorized/);
 // Saving the same authority does not cancel running work.
 await l.workRequests('owner',r.id,'channel');assert.equal((await l.control(id,token)).authorityActive,true);await l.workRequests('owner',r.id,'off');assert.equal((await l.control(id,token)).authorityActive,false);assert.equal((await l.status('owner',r.id)).jobs[0].state,'cancelled');await assert.rejects(l.reply(id,token,'should not post'),/expired, stopped or cancelled/);
});
test('general-channel evidence reaches a swarm turn with provenance; other-server channels are excluded',async()=>{
 const r=await row(),general='1430962817045106792';r.channels=[{id:channel,name:'swarm',guildId:guild},{id:general,name:'general',guildId:guild},{id:'999999999999999999',name:'other-server',guildId:'another-server'}];const old=relay.messages,reads=[];relay.messages=async(run,after,limit,signal)=>{reads.push(run);assert.equal(limit,30);assert.ok(signal);return {messages:[{id:'1556800956824420483',author:{id:'816894571693735946',bot:false},content:'I want every turn, tool call and artifact recorded for evaluation.',timestamp:new Date(clock-1000).toISOString()}]};};
 try{const trigger={id:'1556804486108811315',author:{id:'269751214026129409',bot:false},content:'Semi that referred to Colette in general',timestamp:new Date(clock).toISOString()};const context=await l.recentContext(r,channel,[trigger],AbortSignal.timeout(1000),trigger);assert.equal(reads.length,1);assert.equal(reads[0].channelId,general);assert.ok(context.messages.some(m=>m.channelName==='general'&&m.sourceUrl.includes(general)&&m.content.includes('evaluation')));assert.ok(context.messages.some(m=>m.id===trigger.id));assert.equal(context.channels.length,2);}finally{relay.messages=old;}
});
test('explicit replay verifies live Discord evidence and cannot invent an objective or author',async()=>{
 const r=await row();await l.workRequests('owner',r.id,'channel');const source={id:'1556804486108811315',author:{id:'269751214026129409',bot:false},content:'Semi add cross-channel context',timestamp:new Date(clock-1000000).toISOString()};const old=relay.messages;relay.messages=async()=>({messages:[source]});try{const receipt=await l.requestWork('owner',r.id,{channelId:channel,messageId:source.id});const saved=(await pool.query('SELECT * FROM discord_chat_job WHERE id=$1',[receipt.jobId])).rows[0];assert.equal(saved.allowed_work,true);assert.equal(saved.message_id,'work-replay-'+source.id);assert.equal(saved.messages.find(m=>m.id===saved.message_id).sourceMessageId,source.id);await assert.rejects(l.requestWork('owner',r.id,{channelId:channel,messageId:source.id}),/already queued/);await assert.rejects(l.requestWork('owner',r.id,{channelId:channel,messageId:'1556804486108811316'}),/not covered/);}finally{relay.messages=old;}
});

test('a work-authorized batch queues each human trigger and does not replace an earlier request with later chatter',async()=>{
 const r=await row();await l.workRequests('owner',r.id,'channel');Object.assign(r,{activated_at:new Date(clock-10000).toISOString(),channels:[{id:channel,name:'swarm',guildId:guild}],discovered_at:new Date(clock).toISOString(),announce:false});await pool.query('INSERT INTO discord_chat_cursor(relay,channel_id,last_id) VALUES($1,$2,$3)',[r.id,channel,snowflakeAt(clock-10000)]);const messages=[{id:snowflakeAt(clock-1000),author:{id:'269751214026129409',bot:false},content:'Semi add recent cross-channel messages',timestamp:new Date(clock-1000).toISOString()},{id:snowflakeAt(clock-500),author:{id:'816894571693735946',bot:false},content:'ehehehe',timestamp:new Date(clock-500).toISOString()}],old=relay.messages;relay.messages=async()=>({messages});try{await l.cycle(r);const jobs=(await pool.query('SELECT message_id,messages,allowed_work FROM discord_chat_job WHERE relay=$1 ORDER BY created_at',[r.id])).rows;assert.equal(jobs.length,2);assert.deepEqual(jobs.map(j=>j.message_id),messages.map(m=>m.id));assert.ok(jobs.every(j=>j.allowed_work&&j.messages.some(m=>m.id===j.message_id)));await l.cycle(r);assert.equal((await l.status('owner',r.id)).jobs.length,2);}finally{relay.messages=old;}
});

test('large cross-channel snapshots and long personalities shrink valid JSON without losing the verified trigger',async()=>{
 const r=await row();await l.workRequests('owner',r.id,'channel');await pool.query("UPDATE swarms SET config=jsonb_set(config,'{personality}',$2) WHERE id=$1",[r.id,JSON.stringify('p'.repeat(4000))]);const trigger={id:'1556804486108811315',author:{id:'269751214026129409',bot:false},content:'Semi please read your source and fix the listener',timestamp:new Date(clock).toISOString()};const messages=[trigger,...Array.from({length:40},(_,i)=>({...trigger,id:String(BigInt(trigger.id)+BigInt(i+1)),content:'recent context '.repeat(80),channelId:channel,channelName:'swarm'}))];trigger.channelId=channel;trigger.channelName='swarm';const context={channels:[{id:channel,name:'swarm',guildId:guild}],messages,omittedMessages:0};const id=await l.enqueue(r,channel,trigger.id,messages,context);const saved=(await pool.query('SELECT * FROM discord_chat_job WHERE id=$1',[id])).rows[0],req=JSON.parse(await vault.decrypt('owner',`chat-job:${id}`,saved.request_secret));assert.ok(req.objective.length<=20000);assert.ok(saved.context.omittedMessages>0);assert.ok(saved.messages.some(m=>m.id===trigger.id));assert.ok(req.objective.includes(trigger.content));assert.equal(saved.allowed_work,true);
});

test('successive turns retain one session, use persisted follow-up IDs and retire idle runtime on pause',async()=>{
 const r=await row(),original=l.fairyRequest;let creates=0,stops=0,inputs=[],state='open';
 await l.cleanup();l.fairyRequest=async(url,options)=>{if(url.endsWith('/api/app-sessions')){creates++;return {session_id:'retained-session'};}if(url.endsWith('/input')){inputs.push(options.body);return {session_id:'retained-session',turn:{turn_id:'opaque-turn',client_mutation_id:options.body.client_mutation_id,state:'queued'}};}if(url.endsWith('/stop')){stops++;state='stopped';return {};}return {status:state,upstream_status:state==='open'?'completed':'archived',background_jobs_running:0};};
 try{
 const first=await job(r);await l.reply(first.id,first.token,'');await l.cleanup();assert.equal(stops,0);assert.equal((await l.status('owner',r.id)).runtimeSessionId,'retained-session');
 const second=await job(r);assert.equal(second.saved.session_id,'retained-session');assert.equal(second.saved.runtime_reused,true);assert.equal(creates,1);assert.equal(inputs[0].client_mutation_id,`chat-${second.id}`);assert.ok(inputs[0].input.includes(second.token));assert.ok(!inputs[0].input.includes(first.token));
 await assert.rejects(l.reply(first.id,first.token,'Stale turn.'),/differs/);await l.reply(second.id,second.token,'');await l.cleanup();assert.equal(stops,0);assert.equal(new Set(inputs.map(b=>b.client_mutation_id)).size,1);
 await l.configure('owner',r.id,{enabled:false});await l.cleanup();assert.equal(stops,1);assert.equal((await l.status('owner',r.id)).runtimeSessionId,null);
 }finally{l.fairyRequest=original;}
});

test('lost follow-up response retries exact input after restart, busy sessions wait and receipts stay turn-scoped',async()=>{
 const r=await row(),original=l.fairyRequest;let state='open',lost=true,inputs=[];
 await l.cleanup();l.fairyRequest=async(url,options)=>{if(url.endsWith('/api/app-sessions'))return {session_id:'reuse-retry'};if(url.endsWith('/input')){inputs.push(options.body);if(lost){lost=false;throw Error('Lost response');}return {session_id:'reuse-retry',turn:{turn_id:'receipt',client_mutation_id:options.body.client_mutation_id,state:'running'}};}if(url.includes('/turns/'))return {session_id:'reuse-retry',turn:{client_mutation_id:url.split('/').at(-1),state:'failed'}};if(url.endsWith('/stop')){state='stopped';return {};}return {status:state,upstream_status:state==='open'?'completed':'archived',background_jobs_running:0};};
 try{
 const first=await job(r);await l.reply(first.id,first.token,'');await l.cleanup();state='running';
 const message={id:'followup-retry',author:{id:'123456789012345678',bot:false},content:'hello',timestamp:new Date(clock).toISOString()};const id=await l.enqueue(r,channel,message.id,[message]);await l.jobs(r);let saved=(await pool.query('SELECT * FROM discord_chat_job WHERE id=$1',[id])).rows[0];assert.equal(saved.state,'starting');assert.equal(saved.dispatch_attempted,false);assert.equal(inputs.length,0);
 state='open';await assert.rejects(l.jobs(r),/Lost response/);saved=(await pool.query('SELECT * FROM discord_chat_job WHERE id=$1',[id])).rows[0];assert.equal(saved.runtime_reused,true);assert.equal(saved.session_id,'reuse-retry');
 const restarted=new ChatListener(pool,relay,vault,{origin:'https://chat.example.com',now:()=>clock,fairyRequest:l.fairyRequest});await restarted.jobs(r);assert.equal(inputs.length,2);assert.deepEqual(inputs[0],inputs[1]);await restarted.jobs(r);saved=(await pool.query('SELECT * FROM discord_chat_job WHERE id=$1',[id])).rows[0];assert.equal(saved.state,'failed');assert.match(saved.error,/follow-up failed/);await restarted.cleanup();
 }finally{l.fairyRequest=original;}
});

test('nonreusable and lifetime-budget sessions rotate, while daily replacement limits remain authoritative',async()=>{
 const r=await row(),original=l.fairyRequest;await l.cleanup();let stopped=0;
 await pool.query('UPDATE discord_chat_listener SET runtime_session_id=$2 WHERE relay=$1',[r.id,'exhausted-runtime']);
 l.fairyRequest=async(url)=>{if(url.endsWith('/input'))throw Object.assign(Error('Lifetime budget reached.'),{httpStatus:429,errorCode:'app_session_budget',retryAt:null});if(url.endsWith('/stop')){stopped++;return {};}if(url.endsWith('/api/app-sessions'))throw Object.assign(Error('Daily starts exhausted.'),{httpStatus:429,errorCode:'app_session_daily_limit',retryAt:(clock+3600000)/1000});return {status:'open',upstream_status:'completed',background_jobs_running:0};};
 try{const id=await l.enqueue(r,channel,'rotate-after-budget',[]);await l.jobs(r);let j=(await pool.query('SELECT * FROM discord_chat_job WHERE id=$1',[id])).rows[0];assert.equal(stopped,1);assert.equal(j.state,'starting');assert.equal(j.session_id,null);assert.equal((await l.status('owner',r.id)).runtimeSessionId,null);await assert.rejects(l.jobs(r),/Daily starts/);j=(await pool.query('SELECT * FROM discord_chat_job WHERE id=$1',[id])).rows[0];assert.equal(j.state,'failed');assert.equal(j.stop_confirmed,true);assert.equal((await l.status('owner',r.id)).state,'blocked');}finally{l.fairyRequest=original;}
});

test('busy input rejection is not an ambiguous dispatch and pause never submits new work',async()=>{
 const r=await row(),original=l.fairyRequest;await l.cleanup();let inputs=0,stopped=false;
 await pool.query('UPDATE discord_chat_listener SET runtime_session_id=$2 WHERE relay=$1',[r.id,'busy-reuse']);
 l.fairyRequest=async(url)=>{if(url.endsWith('/input')){inputs++;throw Object.assign(Error('Runtime busy.'),{httpStatus:409,errorCode:'session_busy'});}if(url.endsWith('/stop')){stopped=true;return {};}return {status:stopped?'stopped':'open',upstream_status:stopped?'archived':'completed',background_jobs_running:0};};
 try{const id=await l.enqueue(r,channel,'busy-followup',[]);await l.jobs(r);const j=(await pool.query('SELECT * FROM discord_chat_job WHERE id=$1',[id])).rows[0];assert.equal(j.dispatch_attempted,false);assert.equal(inputs,1);await l.configure('owner',r.id,{enabled:false});await l.cleanup();assert.equal(inputs,1);assert.equal(stopped,true);assert.equal((await l.status('owner',r.id)).runtimeSessionId,null);}finally{l.fairyRequest=original;}
});

test('pause reconciles an uncertain follow-up exactly once before cancelling its retained session',async()=>{
 const r=await row(),original=l.fairyRequest;await l.cleanup();let lost=true,inputs=[],stops=0,state='open';
 l.fairyRequest=async(url,options)=>{if(url.endsWith('/api/app-sessions'))return {session_id:'cancel-reuse'};if(url.endsWith('/input')){inputs.push(options.body);if(lost){lost=false;throw Error('Uncertain admission');}return {session_id:'cancel-reuse',turn:{turn_id:'accepted',client_mutation_id:options.body.client_mutation_id,state:'running'}};}if(url.endsWith('/stop')){stops++;state='stopped';return {};}return {status:state,upstream_status:state==='open'?'completed':'archived',background_jobs_running:0};};
 try{const first=await job(r);await l.reply(first.id,first.token,'');await l.cleanup();const id=await l.enqueue(r,channel,'uncertain-cancel',[]);await assert.rejects(l.jobs(r),/Uncertain admission/);await l.configure('owner',r.id,{enabled:false});await l.cleanup();assert.equal(inputs.length,2);assert.deepEqual(inputs[0],inputs[1]);assert.equal(stops,1);const j=(await pool.query('SELECT * FROM discord_chat_job WHERE id=$1',[id])).rows[0];assert.equal(j.state,'cancelled');assert.equal(j.stop_confirmed,true);assert.equal(j.request_secret,null);assert.equal((await l.status('owner',r.id)).runtimeSessionId,null);}finally{l.fairyRequest=original;}
});

test('a cancelled unknown initial admission is reconciled before the next job can start',async()=>{
 const r=await row();await l.cleanup();const unknown=await l.enqueue(r,channel,'unknown-create',[]);await pool.query("UPDATE discord_chat_job SET state='cancelled',dispatch_attempted=true,finished_at=now() WHERE id=$1",[unknown]);const next=await l.enqueue(r,channel,'next-after-unknown',[]);const before=calls.length;await l.jobs(r);assert.equal(calls.slice(before).some(c=>c.opts.body?.client_mutation_id===`chat-${next}`),false);await l.cleanup();assert.equal(calls.slice(before).filter(c=>c.opts.body?.client_mutation_id===`chat-${unknown}`).length,1);await l.jobs(r);assert.equal(calls.slice(before).filter(c=>c.opts.body?.client_mutation_id===`chat-${next}`).length,1);
});
test('messages queued behind a busy turn fold into one turn that keeps every verified trigger',async()=>{
 const r=await row();await l.workRequests('owner',r.id,'channel');calls=[];
 const msg=(n,content,author='269751214026129409')=>({id:snowflakeAt(clock+n),author:{id:author,bot:false},content,timestamp:new Date(clock+n).toISOString()});
 const work=msg(1,'Semi check the board'),first=await l.enqueue(r,channel,work.id,[work]);await l.jobs(r);
 assert.equal((await pool.query('SELECT state FROM discord_chat_job WHERE id=$1',[first])).rows[0].state,'running');
 const queued=[msg(2,'Semi are you awake?'),msg(3,'lol','816894571693735946'),msg(4,'ok')],ids=[];
 for(const m of queued)ids.push(await l.enqueue(r,channel,m.id,queued.filter(x=>BigInt(x.id)<=BigInt(m.id))));
 assert.equal((await pool.query("SELECT count(*)::int AS n FROM discord_chat_job WHERE id=ANY($1::uuid[]) AND state='queued'",[ids])).rows[0].n,3);
 await pool.query("UPDATE discord_chat_job SET state='skipped',finished_at=now(),stop_confirmed=true,request_secret=NULL WHERE id=$1",[first]);
 await l.jobs(r);
 const rows=(await pool.query('SELECT state,error,folded_message_ids,request_secret,allowed_work FROM discord_chat_job WHERE id=ANY($1::uuid[]) ORDER BY created_at',[ids])).rows;
 assert.deepEqual(rows.map(x=>x.state),['skipped','skipped','running']);
 assert.ok(rows.slice(0,2).every(x=>x.error===`Folded into listener turn ${ids[2]}.`&&x.request_secret===null));
 assert.deepEqual(rows[2].folded_message_ids,[queued[0].id,queued[1].id]);assert.equal(rows[2].allowed_work,true);
 const objective=JSON.parse(await vault.decrypt('owner',`chat-job:${ids[2]}`,rows[2].request_secret)).objective;
 assert.match(objective,/Queued while you were busy/);assert.ok(objective.includes('Semi are you awake?')&&objective.includes(queued[1].id));
 const sent=calls.filter(c=>c.opts?.body?.client_mutation_id===`chat-${ids[2]}`).at(-1)?.opts.body;assert.ok((sent.objective||sent.input).includes('Semi are you awake?'));
 assert.equal(calls.filter(c=>ids.slice(0,2).some(id=>c.opts?.body?.client_mutation_id===`chat-${id}`)).length,0);
});
