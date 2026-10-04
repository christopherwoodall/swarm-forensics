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
