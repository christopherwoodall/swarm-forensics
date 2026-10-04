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
 try{assert.equal((await client.listTools()).tools.length,5);
 const list=await client.callTool({name:'discord_list_relays',arguments:{}});assert.ok(!list.content[0].text.includes('hidden'));assert.deepEqual(queries[0],['owner-a']);
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
 try{const {StreamableHTTPClientTransport}=await import('@modelcontextprotocol/sdk/client/streamableHttp.js');const client=new Client({name:'http-test',version:'1'});await client.connect(new StreamableHTTPClientTransport(new URL(`http://127.0.0.1:${http.address().port}/mcp`),{requestInit:{headers:{Authorization:'Bearer synthetic'}},fetch:(url,options)=>fetch(url,{...options,signal:AbortSignal.timeout(5000)})}));assert.equal((await client.listTools()).tools.length,5);assert.equal((await client.callTool({name:'discord_list_relays',arguments:{}})).isError,undefined);await client.close();}finally{http.closeAllConnections();await new Promise(r=>http.close(r));}
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
