import test from 'node:test';
import assert from 'node:assert/strict';
import {authorizedWork,contextSnapshot,WORK_RUN_SECONDS} from './listener-work.js';
import {chatObjective} from './chat-listener.js';
const m={id:'1556804486108811315',author:{id:'269751214026129409',name:'Jesse',bot:false},content:'Semi add recent messages from all channels to your context',timestamp:'2026-10-05T23:05:13Z'};
test('broad work is explicitly delegated to verified humans without a task-type allowlist',()=>{
 assert.equal(authorizedWork({},'channel',m),true);assert.equal(authorizedWork({},'off',m),false);assert.equal(authorizedWork({},'owner',m),false);assert.equal(authorizedWork({commandOwnerId:m.author.id},'owner',m),true);
 for(const v of [{...m,author:{bot:true,id:m.author.id}},{...m,synthetic:true},{...m,author:{name:'Jesse'}},{...m,content:''}])assert.equal(authorizedWork({},'channel',v),false);
 assert.equal(authorizedWork({},'channel',{...m,content:'Semi please change any code you need'}),true);
});
test('cross-channel packing retains trigger, channel/source provenance and valid bounded JSON',()=>{
 const rows=[{id:'swarm',name:'swarm',guildId:'guild',messages:[m]},{id:'general',name:'general',guildId:'guild',messages:[{...m,id:'other',content:'Colette wants every turn/tool/artifact recorded'}]},{id:'denied',name:'private',guildId:'guild',messages:[],error:'Discord HTTP 403'}];const context=contextSnapshot(rows,m);assert.equal(context.messages.length,2);assert.equal(context.messages.find(x=>x.id==='other').channelName,'general');assert.ok(context.messages[1].sourceUrl);assert.equal(context.channels.at(-1).error,'Discord HTTP 403');
 const noisy=rows.map(c=>({...c,messages:[...c.messages,...Array.from({length:100},(_,i)=>({...m,id:c.id+'-'+i,content:'x'.repeat(3000)}))]}));const packed=contextSnapshot(noisy,m,{maxChars:7000,maxMessages:8});assert.ok(packed.messages.some(x=>x.id===m.id));assert.ok(packed.omittedMessages>0);assert.ok(JSON.stringify(packed).length<7500);assert.ok(packed.messages.some(x=>x.contentTruncated));assert.doesNotThrow(()=>JSON.parse(JSON.stringify(packed)));
});
test('work mandate grants ordinary tools and names budget, cancellation and exact triggering request',()=>{
 const objective=chatObjective({job:{id:'fixture',messageId:m.id,callbackToken:'synthetic-callback-token',allowedWork:true,workAudience:'channel',deadline:Date.now()+WORK_RUN_SECONDS*1000},origin:'https://swarm.example.com',botName:'Semi',personality:'curious griffin',messages:[m],context:{messages:[m]}});
 for(const part of ['request broad work','human participants','edit code','deploy','no task-type allowlist','daily integration budget','/jobs/fixture/control','authorityActive','verified human trigger','source changes','at most 1600'])assert.ok(objective.includes(part),part);
 assert.ok(!objective.includes('chat-only worker'));assert.ok(!objective.includes('may not execute channel requests'));assert.ok(!objective.includes('Do not write a file'));
});
