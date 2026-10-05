import {DiscordMessageContentError} from './discord.js';
import test from 'node:test';
import assert from 'node:assert/strict';
import {OperationClient as Client,linkedPair,testOperations} from './operation-test-client.js';

import {agentOperations,agentHandler} from './agent-api.js';
const coordinationServer=deps=>testOperations(deps,agentOperations);

test('HTTPS API discovers tools, scopes relays, validates input and hides internal errors',async()=>{
 const queries=[];let posts=0;
 const pool={query:async(sql,args)=>{queries.push(args);return {rows:sql.includes('AND owner')?[]:[{id:'a',config:{name:'Relay',channelId:'123',secret:'hidden'}}]};}};
 const server=coordinationServer({pool,relay:{post:async()=>{posts++;}},owner:'owner-a',version:'test'});
 const client=new Client({name:'test',version:'1'});const [a,b]=linkedPair();await server.connect(a);await client.connect(b);
 try{assert.equal((await client.listTools()).tools.length,13);
 const list=await client.callTool({name:'discord_list_relays',arguments:{}});assert.ok(!list.content[0].text.includes('hidden'));assert.deepEqual(queries[0],['owner-a',null]);
 const denied=await client.callTool({name:'discord_post_message',arguments:{relayId:'550e8400-e29b-41d4-a716-446655440000',content:'hello',nonce:'123'}});assert.equal(denied.isError,true);assert.equal(posts,0);assert.equal(queries[1][1],'owner-a');
 const invalid=await client.callTool({name:'discord_read_messages',arguments:{relayId:'wrong',limit:101}});assert.equal(invalid.isError,true);
 }finally{await client.close();await server.close();}
});
test('Discord read and post both reject a channel in another server',async()=>{
 const {DiscordRelay}=await import('./discord.js');const original=globalThis.fetch;let calls=0;
 globalThis.fetch=async()=>{calls++;return {ok:true,status:200,json:async()=>({type:0,guild_id:'other-guild',permission_overwrites:[]})};};
 try{const relay=new DiscordRelay({query:async sql=>({rows:sql.includes('SELECT owner')?[{owner:'owner'}]:sql.includes('FROM bots')?[{secret:'cipher'}]:[{config:{guildId:'guild',channelId:'channel'}}]})},{decrypt:async()=> 'synthetic'});
 await assert.rejects(relay.messages({swarm:'relay',owner:'owner'},undefined,30),/configured server/);await assert.rejects(relay.post({swarm:'relay',owner:'owner'},'hello','123'),/configured server/);assert.equal(calls,2);
 }finally{globalThis.fetch=original;}
});

test('profile writes require relay ownership and board agents cannot discover profile tools',async()=>{
 let writes=0;const relay={profile:async()=>{writes++;return {username:'Jeremy'};}};
 for(const kind of ['owner','agent']){
 const server=coordinationServer({pool:{query:async()=>({rows:[]})},relay,owner:'owner',principal:{kind,owner:'owner'},version:'test'});
 const client=new Client({name:'profile-test',version:'1'});const [a,b]=linkedPair();await server.connect(a);await client.connect(b);
 try{if(kind==='agent'){await assert.rejects(client.listTools());continue;}const tools=(await client.listTools()).tools;assert.equal(tools.some(t=>t.name==='discord_update_bot_profile'),true);if(kind==='owner'){const denied=await client.callTool({name:'discord_update_bot_profile',arguments:{relayId:'550e8400-e29b-41d4-a716-446655440000',username:'Jeremy'}});assert.equal(denied.isError,true);}}finally{await client.close();await server.close();}
 }assert.equal(writes,0);
});

test('bot profile updates Discord and cached name; rejects empty and remote URL avatars',async()=>{
 const {DiscordRelay}=await import('./discord.js');const original=globalThis.fetch;const updates=[];let calls=0;
 const pool={query:async(sql,args)=>{if(sql.startsWith('UPDATE')){updates.push(args);return {rows:[]};}return {rows:sql.includes('SELECT owner')?[{owner:'owner'}]:sql.includes('FROM bots')?[{bot_id:'123',secret:'cipher'}]:[{id:'relay'}]};}};
 globalThis.fetch=async(url,options)=>{calls++;assert.equal(url,'https://discord.com/api/v10/users/@me');assert.equal(options.method,'PATCH');assert.deepEqual(JSON.parse(options.body),{username:'Jeremy'});return {ok:true,status:200,json:async()=>({id:'123',bot:true,username:'Jeremy',avatar:null})};};
 try{const relay=new DiscordRelay(pool,{decrypt:async()=> 'synthetic'});const run={swarm:'relay',owner:'owner'};assert.deepEqual(await relay.profile(run,{username:'Jeremy'}),{id:'123',username:'Jeremy',avatarUrl:null});assert.deepEqual(updates,[['Jeremy','relay','123']]);await assert.rejects(relay.profile(run,{}),/Specify/);await assert.rejects(relay.profile(run,{avatar:'https://example.com/image.png'}),/data URI/);assert.equal(calls,1);}finally{globalThis.fetch=original;}
});

test('channel memory tools share owner context and enforce ownership before collecting or searching',async()=>{
 const id='550e8400-e29b-41d4-a716-446655440000';let allowed=true;const calls=[];
 const server=coordinationServer({pool:{query:async()=>({rows:allowed?[{id,config:{}}]:[]})},relay:{collect:async(...args)=>{calls.push(args);return {state:'completed',nextBefore:'12345678901234567'};},search:async(...args)=>{calls.push(args);return {messages:[{content:'Shared context'}],untrusted:true};}},owner:'alice',version:'test'});
 const client=new Client({name:'memory-test',version:'1'}),[a,b]=linkedPair();await server.connect(a);await client.connect(b);
 try{const collected=await client.callTool({name:'discord_collect_messages',arguments:{relayId:id}});assert.equal(JSON.parse(collected.content[0].text).state,'completed');const search=await client.callTool({name:'discord_search_messages',arguments:{relayId:id,query:'context'}});assert.equal(JSON.parse(search.content[0].text).messages[0].content,'Shared context');assert.deepEqual(calls[0][0],{swarm:id,owner:'alice'});assert.deepEqual(calls[1][0],{swarm:id,owner:'alice'});allowed=false;for(const name of ['discord_collect_messages','discord_search_messages'])assert.equal((await client.callTool({name,arguments:{relayId:id,...(name.includes('search')?{query:'context'}:{})}})).isError,true);assert.equal(calls.length,2);}finally{await client.close();await server.close();}
});

test('personality HTTPS API persists, clears, validates and rejects other owners',async()=>{
 const id='550e8400-e29b-41d4-a716-446655440000';let config={name:'Keep setup',channelId:'123'},writes=0;
 const pool={query:async(sql,args)=>{if(args[0]!==id||args[1]!=='owner')return {rows:[]};if(sql.startsWith('UPDATE')){writes++;config={...config,personality:args[2]};}return {rows:[{config}]};}};
 const server=coordinationServer({pool,relay:{},owner:'owner',version:'test'}),client=new Client({name:'personality-test',version:'1'});const [a,b]=linkedPair();await server.connect(a);await client.connect(b);
 const call=(name,args)=>client.callTool({name,arguments:{relayId:id,...args}});const value=r=>JSON.parse(r.content[0].text);
 try{
 assert.equal(value(await call('discord_get_agent_personality',{})).personality,'');
 const text='Curious, concise, and warm. 🌊';assert.equal(value(await call('discord_set_agent_personality',{personality:text})).personality,text);assert.equal(value(await call('discord_get_agent_personality',{})).personality,text);assert.equal(config.name,'Keep setup');
 for(const personality of ['x'.repeat(4001),null,42])assert.equal((await call('discord_set_agent_personality',{personality})).isError,true);
 assert.equal((await call('discord_set_agent_personality',{relayId:'11111111-1111-4111-8111-111111111111',personality:'unauthorized'})).isError,true);assert.equal(writes,1);
 assert.equal(value(await call('discord_set_agent_personality',{personality:''})).personality,'');
 }finally{await client.close();await server.close();}
});


test('HTTPS API chat preferences are relay scoped and never return legacy provider settings',async()=>{
 const relayId='550e8400-e29b-41d4-a716-446655440000';const queries=[];
 const pool={query:async(sql,args)=>{queries.push(args);return {rows:args[0]===relayId&&args[1]==='owner'?[{id:relayId,config:{personality:'Friendly',chat:{mode:'normal',provider:'openai',model:'legacy',cooldownSeconds:20,maxRepliesPerHour:10}}}]:[]};}};
 const server=coordinationServer({pool,relay:{},owner:'owner',principal:{kind:'agent',relayId},version:'test'});const client=new Client({name:'chat-settings',version:'test'});const [a,b]=linkedPair();await server.connect(a);await client.connect(b);
 try{const response=await client.callTool({name:'discord_get_chat_config',arguments:{relayId}});const data=JSON.parse(response.content[0].text);assert.deepEqual(data.chat,{mode:'normal',cooldownSeconds:20,maxRepliesPerHour:10});assert.equal(data.replyOwner,'connected agent');assert.equal(data.personality,'Friendly');assert.ok(!response.content[0].text.includes('openai'));const denied=await client.callTool({name:'discord_get_chat_config',arguments:{relayId:'550e8400-e29b-41d4-a716-446655440001'}});assert.equal(denied.isError,true);assert.equal(queries.length,1);}finally{await client.close();await server.close();}
});

test('tool discovery explicitly distinguishes reads from mutations for owner and board-only clients',async()=>{
 const reads=new Set(['discord_sync_agent','discord_discover_channels','discord_list_relays','discord_get_chat_config','discord_get_agent_personality','discord_get_bot_profile','discord_read_messages','discord_search_messages','board_list_tasks','board_read_events']);
 for(const principal of [{kind:'owner',owner:'alice'},{kind:'agent',owner:'alice',actor:'agent'}]){
 const server=coordinationServer({pool:{query:async()=>({rows:[]})},relay:{},board:{},principal,owner:'alice',version:'test'}),client=new Client({name:'annotation-test',version:'1'}),[a,b]=linkedPair();
 await server.connect(a);await client.connect(b);
 try{const tools=(await client.listTools()).tools;assert.equal(tools.length,principal.kind==='owner'?17:4);for(const tool of tools)assert.equal(tool.annotations?.readOnlyHint,reads.has(tool.name),tool.name);}
 finally{await client.close();await server.close();}
 }
});

test('reading bot profile performs GET and no database update',async()=>{
 const {DiscordRelay}=await import('./discord.js');const original=globalThis.fetch;const queries=[];
 const pool={query:async(sql)=>{queries.push(sql);assert.ok(!/^(UPDATE|INSERT|DELETE)/.test(sql));return {rows:sql.includes('SELECT owner')?[{owner:'alice'}]:sql.includes('FROM bots')?[{bot_id:'123',secret:'cipher'}]:[{id:'relay'}]};}};
 globalThis.fetch=async(url,options)=>{assert.equal(options.method,'GET');return {ok:true,status:200,json:async()=>({id:'123',bot:true,username:'Bacon',avatar:null})};};
 try{const relay=new DiscordRelay(pool,{decrypt:async()=> 'synthetic'});assert.equal((await relay.profile({swarm:'relay',owner:'alice'},undefined,AbortSignal.timeout(1000))).username,'Bacon');assert.equal(queries.length,3);}finally{globalThis.fetch=original;}
});

test('ordinary chat tools forward channel selection while retaining owner and relay scope',async()=>{
 const relayId='550e8400-e29b-41d4-a716-446655440000',channelId='123456789012345678',seen=[];
 const server=coordinationServer({pool:{query:async()=>({rows:[{id:relayId,config:{guildId:'server'}}]})},relay:{messages:async run=>{seen.push(run);return {messages:[]};},post:async run=>{seen.push(run);return {id:'123456789012345679'};}},owner:'owner',principal:{kind:'agent',relayId},version:'test'}),client=new Client({name:'multi-channel',version:'1'}),[a,b]=linkedPair();await server.connect(a);await client.connect(b);
 try{assert.equal((await client.callTool({name:'discord_read_messages',arguments:{relayId,channelId,limit:10}})).isError,undefined);assert.equal((await client.callTool({name:'discord_post_message',arguments:{relayId,channelId,content:'hello',nonce:'123'}})).isError,undefined);assert.deepEqual(seen,[{swarm:relayId,owner:'owner',channelId},{swarm:relayId,owner:'owner',channelId}]);assert.equal((await client.callTool({name:'discord_post_message',arguments:{relayId:'550e8400-e29b-41d4-a716-446655440001',channelId,content:'hello',nonce:'124'}})).isError,true);assert.equal(seen.length,2);}finally{await client.close();await server.close();}
});

 test('sync preserves settings, rejects foreign relays and exposes migration guidance to board-only agents',async()=>{
 const relayId='550e8400-e29b-41d4-a716-446655440000';
 const pool={query:async sql=>{assert.ok(sql.startsWith('SELECT'));return {rows:[{id:relayId,config:{channelId:'123456789012345678',chat:{mode:'off',cooldownSeconds:80},personality:'Calm'}}]};}};
 const server=coordinationServer({pool,relay:{},owner:'owner',principal:{kind:'agent',relayId},version:'0.16.0'}),client=new Client({name:'sync-test',version:'1'}),[a,b]=linkedPair();await server.connect(a);await client.connect(b);
 try{const call=async id=>client.callTool({name:'discord_sync_agent',arguments:{relayId:id,protocolVersion:0}});const r=JSON.parse((await call(relayId)).content[0].text);assert.equal(r.compatible,false);assert.equal(r.chat.mode,'off');assert.equal(r.chat.cooldownSeconds,80);assert.equal(r.chat.maxRepliesPerHour,30);assert.equal(r.channelId,'123456789012345678');assert.match(r.participation,/User-prompted/);assert.match(r.coordinationInstructions,/Post short progress, handoff and completion/);assert.match(r.coordinationInstructions,/Honor Off/);assert.equal(r.configurationVersion,5);assert.equal((await call('550e8400-e29b-41d4-a716-446655440001')).isError,true);}finally{await client.close();await server.close();}
 });

test('HTTPS API exposes only the typed message-content remedy and keeps unrelated failures private',async()=>{const relayId='550e8400-e29b-41d4-a716-446655440000';let failure=new DiscordMessageContentError('123456789012345678');const server=coordinationServer({pool:{query:async()=>({rows:[{id:relayId,config:{}}]})},relay:{messages:async()=>{throw failure;}},owner:'owner',version:'test'}),client=new Client({name:'intent-test',version:'1'}),[a,b]=linkedPair();await server.connect(a);await client.connect(b);try{const call=()=>client.callTool({name:'discord_read_messages',arguments:{relayId}});assert.match((await call()).content[0].text,/Message Content Intent is disabled.*developers\/applications\/123456789012345678\/bot/);failure=Error('private-token');assert.ok(!(await call()).content[0].text.includes('private-token'));}finally{await client.close();await server.close();}});


test('message editing is relay scoped and preserves exact formatted content',async()=>{
 const relayId='550e8400-e29b-41d4-a716-446655440000',messageId='123456789012345678',content='**Setup**\n\n- Call `discord_sync_agent`.';let edits=0;
 const server=coordinationServer({pool:{query:async()=>({rows:[{id:relayId,config:{}}]})},relay:{edit:async(run,id,text)=>{edits++;assert.deepEqual(run,{swarm:relayId,owner:'owner'});assert.equal(id,messageId);assert.equal(text,content);return {id,content:text};}},owner:'owner',principal:{kind:'agent',relayId},version:'test'}),client=new Client({name:'edit-test',version:'1'}),[a,b]=linkedPair();await server.connect(a);await client.connect(b);
 try{assert.equal((await client.callTool({name:'discord_edit_message',arguments:{relayId,messageId,content}})).isError,undefined);assert.equal((await client.callTool({name:'discord_edit_message',arguments:{relayId:'550e8400-e29b-41d4-a716-446655440001',messageId,content}})).isError,true);assert.equal(edits,1);}finally{await client.close();await server.close();}
});

test('real HTTPS API returns plain JSON, catalog schemas and scoped errors without initialization',async()=>{
 const {default:express}=await import('express');
 const id='550e8400-e29b-41d4-a716-446655440000',other='550e8400-e29b-41d4-a716-446655440001';let posts=0,claimed=0,enabled=0;
 const principal={owner:'alice',actor:'agent-a',kind:'agent',relayId:id};
 const board={principal:async(token)=>{if(token==='expired')throw Object.assign(Error('private-detail'),{status:401});if(token==='down')throw Object.assign(Error('private-storage'),{code:'57P01'});return token==='board'?{owner:'alice',actor:'board-a',kind:'agent'}:principal;},list:async()=>({tasks:[]}),mutate:async()=>{throw Object.assign(Error('Task already claimed.'),{status:409});}};
 const relay={profile:async()=>({id:'bot',username:'Fixture'}),messages:async()=>({messages:[]}),post:async(run,content)=>{posts++;return {id:'123456789012345678',content,timestamp:'now'};}};
 const commands={status:async()=>({bridge:'offline',policy:{enabled:false}}),claim:async(owner,relayId,actor)=>{claimed++;assert.equal(actor,principal.actor);return {command:null};},enable:async()=>{enabled++;}};
 const app=express();app.use(express.json());app.all(['/agent/v1','/agent/v1/:operation'],agentHandler({board,relay,commands,pool:{query:async()=>({rows:[{id,config:{commands:{enabled:false},secret:'private-config'}}]})},publicOrigin:'https://example.com',version:'test'}));
 const http=app.listen(0,'127.0.0.1');await new Promise(r=>http.once('listening',r));const url=`http://127.0.0.1:${http.address().port}`;
 const request=(path,body,token='existing',headers={})=>fetch(url+path,{method:body===undefined?'GET':'POST',headers:{...(token?{Authorization:'Bearer '+token}:{}),'Content-Type':'application/json',...headers},body:body===undefined?undefined:JSON.stringify(body),signal:AbortSignal.timeout(3000)});
 try{
  let response=await request('/agent/v1');assert.equal(response.status,200);const catalog=await response.json();assert.equal(catalog.transport,'HTTPS JSON');assert.equal(catalog.protocolVersion,2);assert.ok(catalog.operations.every(o=>o.method==='POST'&&o.input.additionalProperties===false));assert.ok(catalog.operations.some(o=>o.name==='discord_post_message'&&!o.readOnly));assert.equal(enabled,0);
  response=await request('/agent/v1/discord_read_messages',{relayId:id,limit:1});assert.deepEqual(await response.json(),{messages:[]});
  response=await request('/agent/v1/discord_post_message',{relayId:id,nonce:'123',content:'**Hello**\n\nSwarm.'});assert.equal(response.status,200);assert.equal((await response.json()).content,'**Hello**\n\nSwarm.');assert.equal(posts,1);
  for(const [body,status] of [[{relayId:other,nonce:'124',content:'deny'},403],[{relayId:id,nonce:'124',content:'deny',owner:'other'},400],[{relayId:id,nonce:'bad',content:'deny'},400]]){response=await request('/agent/v1/discord_post_message',body);assert.equal(response.status,status);assert.equal(posts,1);}
  response=await request('/agent/v1/board_update_task',{taskId:id,revision:1,action:'claim',mutationId:'stable-mutation-1'});assert.equal(response.status,409);assert.match((await response.json()).error,/already claimed/);
  response=await request('/agent/v1/discord_claim_command',{relayId:id,claimId:'stable-claim-0001'});assert.equal(response.status,200);assert.equal(claimed,1);
  response=await request('/agent/v1/discord_command_status',{relayId:id});const status=await response.json();assert.equal(status.listener,'offline');assert.equal(status.bridge,undefined);
  for(const [token,expected] of [['',401],['expired',401],['down',503]]){response=await request('/agent/v1',undefined,token);assert.equal(response.status,expected);assert.ok(!(await response.text()).includes('private-'));}
  response=await request('/agent/v1/discord_post_message',{relayId:id,content:'deny',nonce:'124'},'existing',{Origin:'https://evil.test'});assert.equal(response.status,403);assert.equal(posts,1);
  response=await request('/agent/v1',undefined,'board');assert.deepEqual((await response.json()).operations.map(o=>o.name),['board_list_tasks','board_create_task','board_update_task','board_read_events']);
  response=await request('/agent/v1/discord_get_bot_profile',{relayId:id},'board');assert.equal(response.status,404);
  response=await request('/agent/v1/discord_get_bot_profile');assert.equal(response.status,405);
  response=await request('/agent/v1/not_an_operation',{});assert.equal(response.status,404);
 }finally{http.closeAllConnections();await new Promise(r=>http.close(r));}
});

test('overall request deadline includes authentication and prevents late writes',async()=>{
 const {default:express}=await import('express');let release;const pending=new Promise(r=>{release=r;});let posts=0;
 const app=express();app.use(express.json());app.all('/agent/v1/:operation',agentHandler({timeoutMs:30,publicOrigin:'https://example.com',board:{principal:async()=>pending},relay:{post:async()=>{posts++;}},version:'test'}));
 const http=app.listen(0,'127.0.0.1');await new Promise(r=>http.once('listening',r));
 try{const response=await fetch(`http://127.0.0.1:${http.address().port}/agent/v1/discord_post_message`,{method:'POST',headers:{Authorization:'Bearer fixture','Content-Type':'application/json'},body:JSON.stringify({relayId:'550e8400-e29b-41d4-a716-446655440000',content:'must not post',nonce:'123'}),signal:AbortSignal.timeout(3000)});assert.equal(response.status,504);release({owner:'alice',kind:'owner'});await new Promise(r=>setImmediate(r));assert.equal(posts,0);}finally{http.closeAllConnections();await new Promise(r=>http.close(r));}
});
