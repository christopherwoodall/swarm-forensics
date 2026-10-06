import test from 'node:test';
import assert from 'node:assert/strict';
import {DiscordRelay} from './discord.js';
const config={guildId:'guild',channelId:'channel'};
const pool={query:async(sql,args)=>({rows:sql.includes('SELECT owner')?[{owner:'owner'}]:sql.includes('FROM bots')?[{name:'Bot',secret:'cipher'}]:[{config}]})};
const vault={decrypt:async()=> 'synthetic-token'};

test('setup accepts public and private text channels but still requires bot permissions',async()=>{
 for(const visibility of ['public','private']){
  let destroyed=false;const channel={type:0,guildId:'guild',name:visibility,permissionsFor:()=>({has:()=>true})};
  const relay=new DiscordRelay(pool,vault,{clientFactory:()=>({user:{id:'bot'},login:async()=>{},channels:{fetch:async()=>channel},destroy(){destroyed=true;}})});
  const result=await relay.check('relay');assert.equal(result.channel,visibility);assert.equal(result.permissions,'verified');assert.equal(result.private,undefined);assert.equal(destroyed,true);
 }
});

test('setup rejects missing permissions, wrong servers and unsupported channel types',async()=>{
 for(const [channel,error] of [[{type:0,guildId:'guild',permissionsFor:()=>({has:()=>false})},/Relay needs/],[{type:0,guildId:'other'},/configured server/],[{type:2,guildId:'guild'},/text channel/]]){
  let destroyed=false;const relay=new DiscordRelay(pool,vault,{clientFactory:()=>({user:{},login:async()=>{},channels:{fetch:async()=>channel},destroy(){destroyed=true;}})});
  await assert.rejects(relay.check('relay'),error);assert.equal(destroyed,true);
 }
});

test('read and post work without an everyone deny override and propagate Discord permission errors',async()=>{
 const original=globalThis.fetch;let denied=false;const sent=[];
 globalThis.fetch=async(url,options)=>{
  if(url.endsWith('/channel'))return {ok:true,status:200,json:async()=>({type:0,guild_id:'guild',permission_overwrites:[]})};
  if(denied)return {ok:false,status:403};
  if(options.method==='POST'){sent.push(JSON.parse(options.body));return {ok:true,status:200,json:async()=>({id:'100000000000000003'})};}
  return {ok:true,status:200,json:async()=>[{id:'100000000000000002',content:'hello',author:{id:'author',username:'Agent',bot:true},timestamp:'fixture'}]};
 };
 try{const relay=new DiscordRelay(pool,vault);const run={swarm:'relay',owner:'owner'};assert.equal((await relay.messages(run,undefined,30)).messages[0].content,'hello');assert.equal((await relay.post(run,'update','123')).id,'100000000000000003');assert.deepEqual(sent[0].allowed_mentions,{parse:[]});assert.equal(sent[0].enforce_nonce,true);denied=true;await assert.rejects(relay.messages(run,undefined,30),/HTTP 403/);await assert.rejects(relay.post(run,'update','123'),/HTTP 403/);}finally{globalThis.fetch=original;}
});

import {announceJoined} from './relay-records.js';
test('join announcement uses a bounded post, stable nonce, persists receipt and skips rechecks',async()=>{
 let config={channelId:'channel'},posts=[],released=0;
 const client={query:async(sql,args)=>{if(sql.startsWith('SELECT config'))return {rows:[{config}]};if(sql.startsWith('UPDATE swarms'))config={...config,...JSON.parse(args[0])};return {rows:[]};},release(){released++;}};
 const pool={connect:async()=>client},relay={post:async(run,content,nonce,signal)=>{assert.equal(run.owner,'owner');assert.ok(signal);posts.push({content,nonce});return {id:'100000000000000001'};}};
 await announceJoined(pool,relay,'owner','relay','https://example.com');assert.equal(posts.length,1);assert.equal(posts[0].content,'I have joined the swarm!\nConnect your own bot to the swarm! Go to: https://example.com/\nKanban Board: https://example.com/board.html');assert.match(posts[0].nonce,/^\d{1,25}$/);
 await announceJoined(pool,relay,'owner','relay','https://example.com');assert.equal(posts.length,1);
 config={channelId:'other'};await announceJoined(pool,relay,'owner','relay','https://example.com');assert.equal(posts.length,2);assert.notEqual(posts[0].nonce,posts[1].nonce);assert.equal(released,3);
});
test('failed announcement is visible and retry reuses nonce without recording success',async()=>{
 let config={channelId:'channel'},nonces=[],release=0;
 const client={query:async(sql,args)=>{if(sql.startsWith('SELECT config'))return {rows:[{config}]};if(sql.startsWith('UPDATE swarms'))throw Error('should not persist failure');return {rows:[]};},release(){release++;}};
 const relay={post:async(run,content,nonce)=>{nonces.push(nonce);throw Error('HTTP 403');}};
 for(let i=0;i<2;i++)await assert.rejects(announceJoined({connect:async()=>client},relay,'owner','relay','https://example.com'),/Welcome announcement failed: HTTP 403/);
 assert.equal(nonces[0],nonces[1]);assert.equal(config.joinAnnouncement,undefined);assert.equal(release,2);
});

test('disconnected channel rejects agent posts and checks before Discord calls',async()=>{
 const disconnected={query:async(sql)=>({rows:sql.includes('FROM bots')?[{name:'Bot',secret:'cipher'}]:sql.includes('SELECT owner')?[{owner:'owner'}]:[{config:{name:'Bot'}}]})};
 const relay=new DiscordRelay(disconnected,vault,{clientFactory:()=>{throw Error('must not connect');}});
 await assert.rejects(relay.check('relay'),/Complete channel setup/);
 await assert.rejects(relay.post({swarm:'relay',owner:'owner'},'hello','nonce'),/Complete channel setup/);
});

test('channel discovery filters permissions, respects ownership, and chooses only an unambiguous swarm',async()=>{
 for(const names of [['swarm'],['swarm','swarm'],['general']]){
  let destroyed=false;const rows=new Map(names.map((name,i)=>[String(i),{id:String(i),name,type:0,permissionsFor:()=>({has:()=>true})}]));rows.set('denied',{id:'denied',name:'swarm',type:0,permissionsFor:()=>({has:()=>false})});rows.set('voice',{type:2,name:'swarm'});
  const guild={id:'guild',name:'Server',channels:{fetch:async()=>rows}};
  const client={user:{},login:async()=>{},guilds:{fetch:async id=>id?guild:new Map([['guild',{id:'guild'}]])},destroy(){destroyed=true;}};
  const relay=new DiscordRelay(pool,vault,{clientFactory:()=>client});const data=await relay.discover({swarm:'relay',owner:'owner'},AbortSignal.timeout(5000));assert.equal(data.channels.length,names.length);assert.equal(!!data.defaultChannel,names.length===1&&names[0]==='swarm');assert.equal(data.ambiguous,names.length>1);assert.equal(destroyed,true);
 }
 const forbidden=new DiscordRelay({query:async()=>({rows:[]})},vault,{clientFactory:()=>{throw Error('must not connect');}});await assert.rejects(forbidden.discover({swarm:'relay',owner:'other'}),/Relay not found/);
});
test('discovery releases Discord client on external failure and cancellation',async()=>{
 for(const cancelled of [false,true]){let destroyed=false;const controller=new AbortController();if(cancelled)controller.abort();const relay=new DiscordRelay(pool,vault,{clientFactory:()=>({login:async()=>{throw Error('Discord unavailable');},destroy(){destroyed=true;}})});await assert.rejects(relay.discover({swarm:'relay',owner:'owner'},controller.signal));assert.equal(destroyed,true);}
});

test('ordinary chat can read and post in another channel without changing swarm coordination, but rejects other servers',async()=>{
 const original=globalThis.fetch,channelId='123456789012345678';let foreign=false;const urls=[];
 globalThis.fetch=async(url,options)=>{urls.push(url);if(url.endsWith('/'+channelId))return {ok:true,status:200,json:async()=>({type:0,guild_id:foreign?'other':'guild'})};if(options.method==='POST')return {ok:true,status:200,json:async()=>({id:'123456789012345679'})};return {ok:true,status:200,json:async()=>[]};};
 try{const relay=new DiscordRelay(pool,vault),run={swarm:'relay',owner:'owner',channelId};await relay.messages(run,undefined,10);await relay.post(run,'hello','123');assert.ok(urls.every(u=>u.includes('/'+channelId)));assert.equal(config.channelId,'channel');foreign=true;await assert.rejects(relay.post(run,'hello','124'),/configured server/);await assert.rejects(relay.messages(run,undefined,10),/configured server/);await assert.rejects(relay.post({...run,channelId:'wrong'},'hello','125'),/Invalid Discord channel/);}finally{globalThis.fetch=original;}
});

 test('hidden message bodies identify disabled intent, while enabled intent permits genuinely empty messages',async()=>{const original=globalThis.fetch;let flags=0;globalThis.fetch=async url=>({ok:true,status:200,json:async()=>url.includes('/oauth2/')?{id:'123456789012345678',flags}:url.endsWith('/channel')?{type:0,guild_id:'guild'}:[{id:'123456789012345679',author:{id:'other',username:'Other'},content:'',timestamp:'fixture'}]});try{const relay=new DiscordRelay(pool,vault),run={swarm:'relay',owner:'owner'};await assert.rejects(relay.messages(run,undefined,10),/Message Content Intent is disabled.*developers\/applications\/123456789012345678\/bot/);for(const allowed of [1<<18,1<<19]){flags=allowed;assert.equal((await relay.messages(run,undefined,10)).messages[0].content,'');}}finally{globalThis.fetch=original;}});

test('message edits preserve Markdown, suppress mentions and refuse foreign authors or servers',async()=>{
 const original=globalThis.fetch,messageId='123456789012345678';let author='bot',foreign=false,patches=0;const formatted='**Bridge setup**\n\n1. Call `discord_sync_agent`.\n2. Run the recipe.';
 const editPool={query:async query=>{const sql=query.text||query;return {rows:sql.includes('SELECT owner')?[{owner:'owner'}]:sql.includes('FROM bots')?[{bot_id:'bot',secret:'cipher'}]:[{config}]};}};
 globalThis.fetch=async(url,options)=>{if(url.endsWith('/channel'))return {ok:true,status:200,json:async()=>({type:0,guild_id:foreign?'foreign':'guild'})};if(options.method==='PATCH'){patches++;const body=JSON.parse(options.body);assert.equal(body.content,formatted);assert.deepEqual(body.allowed_mentions,{parse:[]});assert.ok(options.signal);return {ok:true,status:200,json:async()=>({id:messageId,content:body.content})};}return {ok:true,status:200,json:async()=>({id:messageId,author:{id:author}})};};
 try{const relay=new DiscordRelay(editPool,vault),run={swarm:'relay',owner:'owner'};assert.equal((await relay.edit(run,messageId,formatted)).content,formatted);author='human';await assert.rejects(relay.edit(run,messageId,formatted),/own messages/);foreign=true;await assert.rejects(relay.edit(run,messageId,formatted),/configured server/);await assert.rejects(relay.edit(run,'invalid',formatted),/message ID/);await assert.rejects(relay.edit(run,messageId,' '.repeat(4)),/content/);assert.equal(patches,1);}finally{globalThis.fetch=original;}
});

test('connected listener posts compact buttons and saves a delivery binding; disconnected bots retain full text',async()=>{
 const original=globalThis.fetch,queries=[],posted=[],body='Long original **message**. '.repeat(40),botId='123456789012345678';
 const viewPool={query:async query=>{const sql=query.text||query;if(sql.includes('discord_message_view')){queries.push(query);return {rows:[{nonce:'123'}]};}return {rows:sql.includes('SELECT owner')?[{owner:'owner'}]:sql.includes('FROM bots')?[{bot_id:botId,secret:'cipher'}]:[{config}]};}};
 globalThis.fetch=async(url,options)=>{if(url.endsWith('/channel'))return {ok:true,status:200,json:async()=>({type:0,guild_id:'guild'})};const payload=JSON.parse(options.body);posted.push(payload);assert.ok(options.signal);return {ok:true,status:200,json:async()=>({id:'123456789012345679',content:payload.content,components:payload.components||[]})};};
 try{const relay=new DiscordRelay(viewPool,vault),run={swarm:'relay',owner:'owner'};relay.presence={status:()=>({state:'online'})};const receipt=await relay.post(run,body,'123');assert.ok(receipt.content.length<400);assert.equal(receipt.components[0].components[0].label,'Show more');assert.deepEqual(posted[0].allowed_mentions,{parse:[]});assert.equal(queries[0].values[3],body);assert.equal(queries[1].values[2],receipt.id);
 relay.presence={status:()=>({state:'offline'})};await relay.post(run,body,'124');assert.equal(posted[1].content,body);assert.equal(posted[1].components,undefined);assert.equal(queries.length,2);
 }finally{globalThis.fetch=original;}
});

test('editing long messages replaces the saved body and editing short clears its button',async()=>{
 const original=globalThis.fetch,queries=[],patches=[],bot='123456789012345678',id='123456789012345679';
 const editPool={query:async query=>{const sql=query.text||query;if(sql.includes('discord_message_view')){queries.push(query);return {rows:[{nonce:'saved'}]};}return {rows:sql.includes('SELECT owner')?[{owner:'owner'}]:sql.includes('FROM bots')?[{bot_id:bot,secret:'cipher'}]:[{config}]};}};
 globalThis.fetch=async(url,options)=>({ok:true,status:200,json:async()=>{if(url.endsWith('/channel'))return {type:0,guild_id:'guild'};if(options.method==='GET')return {author:{id:bot}};const payload=JSON.parse(options.body);patches.push(payload);return {id,content:payload.content};}});
 try{const relay=new DiscordRelay(editPool,vault);relay.presence={status:()=>({state:'online'})};await relay.edit({swarm:'relay',owner:'owner'},id,'Updated long text. '.repeat(60));assert.equal(patches[0].components[0].components[0].label,'Show more');assert.equal(queries.length,3);assert.match(queries[2].values[3],/^\d{1,25}$/);
 await relay.edit({swarm:'relay',owner:'owner'},id,'Short correction.');assert.deepEqual(patches[1].components,[]);assert.equal(patches[1].content,'Short correction.');assert.equal(queries[3].values[3],null);
 }finally{globalThis.fetch=original;}
});
