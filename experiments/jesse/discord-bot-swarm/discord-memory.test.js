import test from 'node:test';
import assert from 'node:assert/strict';
import {DiscordRelay} from './discord.js';
import {DiscordMemory,startCollection} from './discord-memory.js';
const cfg={guildId:'12345678901234567',channelId:'22345678901234567'},run={swarm:'relay',owner:'alice'};
const message={id:'32345678901234567',author:{id:'42345678901234567',username:'Bob'},content:'shared context',timestamp:'2026-10-04T00:00:00Z'};
test('reads do not persist; explicit collection saves normalized messages and uses the historical cursor',async()=>{
 const original=globalThis.fetch,urls=[],saved=[],states=[];
 globalThis.fetch=async url=>{urls.push(url);return {ok:true,status:200,json:async()=>url.includes('/messages?')?[message]:{type:0,guild_id:cfg.guildId}};};
 const pool={query:async sql=>({rows:sql.includes('SELECT owner')?[{owner:'alice'}]:sql.includes('FROM bots')?[{secret:'cipher'}]:[{config:cfg}]})};
 const relay=new DiscordRelay(pool,{decrypt:async()=> 'synthetic'});relay.memory={save:async(...a)=>saved.push(a),latest:async()=> '52345678901234567',status:async(...a)=>states.push(a)};
 try{await relay.messages(run,undefined,30,AbortSignal.timeout(1000));assert.equal(saved.length,0);const backfill=await relay.collect(run,'62345678901234567',100,AbortSignal.timeout(1000));assert.equal(backfill.nextBefore,message.id);assert.equal(backfill.state,'completed');assert.equal(saved.length,1);assert.equal(saved[0][0],'alice');assert.equal(saved[0][2][0].author.name,'Bob');assert.ok(urls.at(-1).includes('before=62345678901234567'));assert.ok(!urls.at(-1).includes('after='));await relay.collect(run,undefined,100,AbortSignal.timeout(1000));assert.ok(urls.at(-1).includes('after=52345678901234567'));assert.equal(states.at(-1)[2],'completed');}finally{globalThis.fetch=original;}
});
test('failed collection remains visible and does not save a fake page',async()=>{
 const states=[],relay=new DiscordRelay({query:async()=>({rows:[{config:cfg}]})},{});relay.memory={latest:async()=>undefined,status:async(...a)=>states.push(a)};relay.fetchMessages=async()=>{throw Error('Discord rate limited');};await assert.rejects(relay.collect(run,undefined,100),/rate limited/);assert.equal(states.at(-1)[2],'failed');assert.match(states.at(-1)[3],/rate limited/);
});
test('search validates input, scopes owner and channel, and returns provenance',async()=>{
 const calls=[],memory=new DiscordMemory({query:async(sql,args)=>{calls.push({sql,args});return {rows:sql.includes('SELECT state')?[{state:'failed',error:'rate limited'}]:[{...message}]};}});
 const result=await memory.search('alice',cfg,'shared context',20);assert.deepEqual(calls[0].args,['alice',cfg.guildId,cfg.channelId,'shared context',20]);assert.match(result.messages[0].url,/discord.com\/channels/);assert.equal(result.untrusted,true);assert.equal(result.collection.state,'failed');await assert.rejects(memory.search('alice',cfg,'',20));await assert.rejects(memory.search('alice',cfg,'hello',101));
});
test('periodic collector never overlaps and stops',async()=>{
 let calls=0,resolve;const gate=new Promise(r=>resolve=r);const stop=startCollection({query:async()=>({rows:[{id:'relay',owner:'alice',config:cfg}]})},{collect:async()=>{calls++;await gate;}},{intervalMs:5});await new Promise(r=>setTimeout(r,30));assert.equal(calls,1);stop();resolve();await new Promise(r=>setTimeout(r,15));assert.equal(calls,1);
});
