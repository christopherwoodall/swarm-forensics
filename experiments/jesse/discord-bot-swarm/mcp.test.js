import {DiscordMessageContentError} from './discord.js';
import test from 'node:test';
import assert from 'node:assert/strict';
import {Client} from '@modelcontextprotocol/sdk/client/index.js';
import {InMemoryTransport} from '@modelcontextprotocol/sdk/inMemory.js';
import {coordinationServer,mcpHandler} from './mcp.js';

test('MCP discovers tools, scopes relays, validates input and hides internal errors',async()=>{
 const queries=[];let posts=0;
 const pool={query:async(sql,args)=>{queries.push(args);return {rows:sql.includes('AND owner')?[]:[{id:'a',config:{name:'Relay',channelId:'123',secret:'hidden'}}]};}};
 const server=coordinationServer({pool,relay:{post:async()=>{posts++;}},owner:'owner-a',version:'test'});
 const client=new Client({name:'test',version:'1'});const [a,b]=InMemoryTransport.createLinkedPair();await server.connect(a);await client.connect(b);
 try{assert.equal((await client.listTools()).tools.length,12);
 const list=await client.callTool({name:'discord_list_relays',arguments:{}});assert.ok(!list.content[0].text.includes('hidden'));assert.deepEqual(queries[0],['owner-a',null]);
 const denied=await client.callTool({name:'discord_post_message',arguments:{relayId:'550e8400-e29b-41d4-a716-446655440000',content:'hello',nonce:'123'}});assert.equal(denied.isError,true);assert.equal(posts,0);assert.equal(queries[1][1],'owner-a');
 const invalid=await client.callTool({name:'discord_read_messages',arguments:{relayId:'wrong',limit:101}});assert.equal(invalid.isError,true);
 }finally{await client.close();await server.close();}
});
test('remote MCP rejects foreign origins and missing identity',async()=>{
 const handler=mcpHandler({publicOrigin:'https://example.com',authenticate:async()=>{throw Error('private');}});
 for(const [headers,status] of [[{origin:'https://evil.example'},403],[{},401]]){let actual;const res={status(n){actual=n;return this;},json(){return this;}};await handler({method:'POST',headers},res);assert.equal(actual,status);}
});

test('HTTP MCP initializes and lists tools with authenticated identity',async()=>{
 const {default:express}=await import('express');
 const app=express();app.use(express.json());app.all('/mcp',mcpHandler({publicOrigin:'https://example.com',authenticate:async t=>{assert.equal(t,'synthetic');return 'owner';},pool:{query:async()=>({rows:[]})},relay:{},version:'test'}));
 const http=app.listen(0,'127.0.0.1');await new Promise(r=>http.once('listening',r));
 try{const {StreamableHTTPClientTransport}=await import('@modelcontextprotocol/sdk/client/streamableHttp.js');const client=new Client({name:'http-test',version:'1'});await client.connect(new StreamableHTTPClientTransport(new URL(`http://127.0.0.1:${http.address().port}/mcp`),{requestInit:{headers:{Authorization:'Bearer synthetic'}},fetch:(url,options)=>fetch(url,{...options,signal:AbortSignal.timeout(5000)})}));assert.equal((await client.listTools()).tools.length,12);assert.equal((await client.callTool({name:'discord_list_relays',arguments:{}})).isError,undefined);await client.close();}finally{http.closeAllConnections();await new Promise(r=>http.close(r));}
});

test('Discord read and post both reject a channel in another server',async()=>{
 const {DiscordRelay}=await import('./discord.js');const original=globalThis.fetch;let calls=0;
 globalThis.fetch=async()=>{calls++;return {ok:true,status:200,json:async()=>({type:0,guild_id:'other-guild',permission_overwrites:[]})};};
 try{const relay=new DiscordRelay({query:async sql=>({rows:sql.includes('SELECT owner')?[{owner:'owner'}]:sql.includes('FROM bots')?[{secret:'cipher'}]:[{config:{guildId:'guild',channelId:'channel'}}]})},{decrypt:async()=> 'synthetic'});
 await assert.rejects(relay.messages({swarm:'relay',owner:'owner'},undefined,30),/configured server/);await assert.rejects(relay.post({swarm:'relay',owner:'owner'},'hello','123'),/configured server/);assert.equal(calls,2);
 }finally{globalThis.fetch=original;}
});

test('MCP URL is readable in a browser while SSE GET remains unsupported',async()=>{
 const {default:express}=await import('express');const app=express();app.all('/mcp',mcpHandler({publicOrigin:'https://example.com'}));const http=app.listen(0,'127.0.0.1');await new Promise(r=>http.once('listening',r));
 try{const url=`http://127.0.0.1:${http.address().port}/mcp`;const browser=await fetch(url,{headers:{Accept:'text/html'},signal:AbortSignal.timeout(3000)});assert.equal(browser.status,200);assert.match(browser.headers.get('content-type'),/text\/html/);assert.match(await browser.text(),/Connect your agent/);const stream=await fetch(url,{headers:{Accept:'text/event-stream'},signal:AbortSignal.timeout(3000)});assert.equal(stream.status,405);const post=await fetch(url,{method:'POST',signal:AbortSignal.timeout(3000)});assert.equal(post.status,401);}finally{http.closeAllConnections();await new Promise(r=>http.close(r));}
});

test('profile writes require relay ownership and board agents cannot discover profile tools',async()=>{
 let writes=0;const relay={profile:async()=>{writes++;return {username:'Jeremy'};}};
 for(const kind of ['owner','agent']){
 const server=coordinationServer({pool:{query:async()=>({rows:[]})},relay,owner:'owner',principal:{kind,owner:'owner'},version:'test'});
 const client=new Client({name:'profile-test',version:'1'});const [a,b]=InMemoryTransport.createLinkedPair();await server.connect(a);await client.connect(b);
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
 const client=new Client({name:'memory-test',version:'1'}),[a,b]=InMemoryTransport.createLinkedPair();await server.connect(a);await client.connect(b);
 try{const collected=await client.callTool({name:'discord_collect_messages',arguments:{relayId:id}});assert.equal(JSON.parse(collected.content[0].text).state,'completed');const search=await client.callTool({name:'discord_search_messages',arguments:{relayId:id,query:'context'}});assert.equal(JSON.parse(search.content[0].text).messages[0].content,'Shared context');assert.deepEqual(calls[0][0],{swarm:id,owner:'alice'});assert.deepEqual(calls[1][0],{swarm:id,owner:'alice'});allowed=false;for(const name of ['discord_collect_messages','discord_search_messages'])assert.equal((await client.callTool({name,arguments:{relayId:id,...(name.includes('search')?{query:'context'}:{})}})).isError,true);assert.equal(calls.length,2);}finally{await client.close();await server.close();}
});

test('personality MCP persists, clears, validates and rejects other owners',async()=>{
 const id='550e8400-e29b-41d4-a716-446655440000';let config={name:'Keep setup',channelId:'123'},writes=0;
 const pool={query:async(sql,args)=>{if(args[0]!==id||args[1]!=='owner')return {rows:[]};if(sql.startsWith('UPDATE')){writes++;config={...config,personality:args[2]};}return {rows:[{config}]};}};
 const server=coordinationServer({pool,relay:{},owner:'owner',version:'test'}),client=new Client({name:'personality-test',version:'1'});const [a,b]=InMemoryTransport.createLinkedPair();await server.connect(a);await client.connect(b);
 const call=(name,args)=>client.callTool({name,arguments:{relayId:id,...args}});const value=r=>JSON.parse(r.content[0].text);
 try{
 assert.equal(value(await call('discord_get_agent_personality',{})).personality,'');
 const text='Curious, concise, and warm. 🌊';assert.equal(value(await call('discord_set_agent_personality',{personality:text})).personality,text);assert.equal(value(await call('discord_get_agent_personality',{})).personality,text);assert.equal(config.name,'Keep setup');
 for(const personality of ['x'.repeat(4001),null,42])assert.equal((await call('discord_set_agent_personality',{personality})).isError,true);
 assert.equal((await call('discord_set_agent_personality',{relayId:'11111111-1111-4111-8111-111111111111',personality:'unauthorized'})).isError,true);assert.equal(writes,1);
 assert.equal(value(await call('discord_set_agent_personality',{personality:''})).personality,'');
 }finally{await client.close();await server.close();}
});


test('MCP chat preferences are relay scoped and never return legacy provider settings',async()=>{
 const relayId='550e8400-e29b-41d4-a716-446655440000';const queries=[];
 const pool={query:async(sql,args)=>{queries.push(args);return {rows:args[0]===relayId&&args[1]==='owner'?[{id:relayId,config:{personality:'Friendly',chat:{mode:'normal',provider:'openai',model:'legacy',cooldownSeconds:20,maxRepliesPerHour:10}}}]:[]};}};
 const server=coordinationServer({pool,relay:{},owner:'owner',principal:{kind:'agent',relayId},version:'test'});const client=new Client({name:'chat-settings',version:'test'});const [a,b]=InMemoryTransport.createLinkedPair();await server.connect(a);await client.connect(b);
 try{const response=await client.callTool({name:'discord_get_chat_config',arguments:{relayId}});const data=JSON.parse(response.content[0].text);assert.deepEqual(data.chat,{mode:'normal',cooldownSeconds:20,maxRepliesPerHour:10});assert.equal(data.replyOwner,'connected MCP agent');assert.equal(data.personality,'Friendly');assert.ok(!response.content[0].text.includes('openai'));const denied=await client.callTool({name:'discord_get_chat_config',arguments:{relayId:'550e8400-e29b-41d4-a716-446655440001'}});assert.equal(denied.isError,true);assert.equal(queries.length,1);}finally{await client.close();await server.close();}
});

test('tool discovery explicitly distinguishes reads from mutations for owner and board-only clients',async()=>{
 const reads=new Set(['discord_sync_agent','discord_discover_channels','discord_list_relays','discord_get_chat_config','discord_get_agent_personality','discord_get_bot_profile','discord_read_messages','discord_search_messages','board_list_tasks','board_read_events']);
 for(const principal of [{kind:'owner',owner:'alice'},{kind:'agent',owner:'alice',actor:'agent'}]){
 const server=coordinationServer({pool:{query:async()=>({rows:[]})},relay:{},board:{},principal,owner:'alice',version:'test'}),client=new Client({name:'annotation-test',version:'1'}),[a,b]=InMemoryTransport.createLinkedPair();
 await server.connect(a);await client.connect(b);
 try{const tools=(await client.listTools()).tools;assert.equal(tools.length,principal.kind==='owner'?16:4);for(const tool of tools)assert.equal(tool.annotations?.readOnlyHint,reads.has(tool.name),tool.name);}
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
 const server=coordinationServer({pool:{query:async()=>({rows:[{id:relayId,config:{guildId:'server'}}]})},relay:{messages:async run=>{seen.push(run);return {messages:[]};},post:async run=>{seen.push(run);return {id:'123456789012345679'};}},owner:'owner',principal:{kind:'agent',relayId},version:'test'}),client=new Client({name:'multi-channel',version:'1'}),[a,b]=InMemoryTransport.createLinkedPair();await server.connect(a);await client.connect(b);
 try{assert.equal((await client.callTool({name:'discord_read_messages',arguments:{relayId,channelId,limit:10}})).isError,undefined);assert.equal((await client.callTool({name:'discord_post_message',arguments:{relayId,channelId,content:'hello',nonce:'123'}})).isError,undefined);assert.deepEqual(seen,[{swarm:relayId,owner:'owner',channelId},{swarm:relayId,owner:'owner',channelId}]);assert.equal((await client.callTool({name:'discord_post_message',arguments:{relayId:'550e8400-e29b-41d4-a716-446655440001',channelId,content:'hello',nonce:'124'}})).isError,true);assert.equal(seen.length,2);}finally{await client.close();await server.close();}
});

 test('sync preserves settings, rejects foreign relays and exposes migration guidance to board-only agents',async()=>{
 const relayId='550e8400-e29b-41d4-a716-446655440000';
 const pool={query:async sql=>{assert.ok(sql.startsWith('SELECT'));return {rows:[{id:relayId,config:{channelId:'123456789012345678',chat:{mode:'off',cooldownSeconds:80},personality:'Calm'}}]};}};
 const server=coordinationServer({pool,relay:{},owner:'owner',principal:{kind:'agent',relayId},version:'0.16.0'}),client=new Client({name:'sync-test',version:'1'}),[a,b]=InMemoryTransport.createLinkedPair();await server.connect(a);await client.connect(b);
 try{const call=async id=>client.callTool({name:'discord_sync_agent',arguments:{relayId:id,protocolVersion:0}});const r=JSON.parse((await call(relayId)).content[0].text);assert.equal(r.compatible,false);assert.equal(r.chat.mode,'off');assert.equal(r.chat.cooldownSeconds,80);assert.equal(r.chat.maxRepliesPerHour,30);assert.equal(r.channelId,'123456789012345678');assert.equal(r.runtime.bridge,'offline');assert.match(r.coordinationInstructions,/Post short progress, handoff and completion/);assert.match(r.coordinationInstructions,/Honor Off/);assert.equal(r.configurationVersion,2);assert.equal((await call('550e8400-e29b-41d4-a716-446655440001')).isError,true);const resource=await client.readResource({uri:'swarm://agent-sync'});assert.equal(JSON.parse(resource.contents[0].text).protocolVersion,1);assert.match(client.getInstructions(),/Never enable commands/);}finally{await client.close();await server.close();}
 });

test('credential rejection stays 401 while verification infrastructure failures stay 503',async()=>{
 for(const [code,status] of [['ERR_JWS_INVALID',401],['ERR_JWT_EXPIRED',401],['ERR_JWT_CLAIM_VALIDATION_FAILED',401],['ERR_JWS_SIGNATURE_VERIFICATION_FAILED',401],['ERR_JWKS_NO_MATCHING_KEY',401],['ERR_JWKS_TIMEOUT',503],['ECONNREFUSED',503],['57P01',503]]){
  const handler=mcpHandler({publicOrigin:'https://example.com',authenticate:async()=>{throw Object.assign(Error('private credential detail'),{code});}});let actual,body;const res={status(n){actual=n;return this;},json(v){body=v;return this;}};await handler({method:'POST',headers:{authorization:'Bearer invalid'}},res);assert.equal(actual,status,code);assert.ok(!JSON.stringify(body).includes('private credential detail'));
 }
});

 test('MCP exposes only the typed message-content remedy and keeps unrelated failures private',async()=>{const relayId='550e8400-e29b-41d4-a716-446655440000';let failure=new DiscordMessageContentError('123456789012345678');const server=coordinationServer({pool:{query:async()=>({rows:[{id:relayId,config:{}}]})},relay:{messages:async()=>{throw failure;}},owner:'owner',version:'test'}),client=new Client({name:'intent-test',version:'1'}),[a,b]=InMemoryTransport.createLinkedPair();await server.connect(a);await client.connect(b);try{const call=()=>client.callTool({name:'discord_read_messages',arguments:{relayId}});assert.match((await call()).content[0].text,/Message Content Intent is disabled.*developers\/applications\/123456789012345678\/bot/);failure=Error('private-token');assert.ok(!(await call()).content[0].text.includes('private-token'));}finally{await client.close();await server.close();}});
