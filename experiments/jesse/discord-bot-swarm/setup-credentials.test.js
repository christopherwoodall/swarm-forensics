import test from 'node:test';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import {SetupCredentials,setupExchangeHandler} from './setup-credentials.js';
import {Kanban} from './kanban.js';
import {agentOperations} from './agent-api.js';
const coordinationServer=deps=>testOperations(deps,agentOperations);
import {OperationClient as Client,linkedPair,testOperations} from './operation-test-client.js';

const relayId='11111111-1111-4111-8111-111111111111',other='22222222-2222-4222-8222-222222222222';
function fixture(){let issued,used=false;const agents=[];const query=async(sql,args)=>{
 if(sql.startsWith('INSERT INTO mcp_setup_tokens')){issued=args[0];return {rows:[{expires_at:new Date()}]};}
 if(sql.startsWith('UPDATE mcp_setup_tokens')){if(used||args[0]!==issued)return {rows:[]};used=true;return {rows:[{owner:'alice',relay_id:relayId}]};}
 if(sql.startsWith('INSERT INTO kanban_agents')){agents.push(args);return {rows:[{id:args[0],expires_at:new Date()}]};}
 return {rows:[]};};return {setup:new SetupCredentials({query,connect:async()=>({query,release(){}})}),agents};}
test('setup tokens are opaque, hashed, one-use under competing exchanges, and create scoped credentials',async()=>{
 const {setup,agents}=fixture(),once=await setup.issue('alice',relayId);assert.match(once.token,/^swarm_setup_[\w-]{43}$/);
 const results=await Promise.allSettled([setup.exchange(once.token),setup.exchange(once.token)]);assert.equal(results.filter(r=>r.status==='fulfilled').length,1);assert.equal(agents.length,1);
 const result=results.find(r=>r.status==='fulfilled').value;assert.equal(result.relayId,relayId);assert.match(result.credential,/^swarm_agent_[\w-]{43}$/);assert.equal(agents[0][4],relayId);assert.equal(agents[0][3],crypto.createHash('sha256').update(result.credential).digest('hex'));
 await assert.rejects(setup.exchange(once.token),/already used/);await assert.rejects(setup.exchange('jwt'),/invalid/);
});
test('malformed exchange does not consume a valid token; expiry and missing owner relay fail closed',async()=>{
 const {setup}=fixture(),once=await setup.issue('alice',relayId);await assert.rejects(setup.exchange(once.token,{name:''}));await setup.exchange(once.token);
 const empty=new SetupCredentials({query:async()=>({rows:[]}),connect:async()=>({query:async()=>({rows:[]}),release(){}})});await assert.rejects(empty.issue('foreign',relayId),/not found/);await assert.rejects(empty.exchange('swarm_setup_'+'a'.repeat(43)),/expired/);
 const board=new Kanban({query:async()=>({rows:[]})});let auth=false;await assert.rejects(board.principal(once.token,async()=>{auth=true;}),/Exchange/);assert.equal(auth,false);
});
test('scoped agent exposes Discord tools but cannot use another relay or list other relays',async()=>{
 const calls=[];const pool={query:async(sql,args)=>{calls.push(args);return {rows:[{id:relayId,config:{name:'Test'}}]};}};
 const server=coordinationServer({pool,owner:'alice',version:'test',principal:{owner:'alice',kind:'agent',actor:'a',relayId},relay:{profile:async()=>({id:'bot',username:'Test'})}}),client=new Client({name:'test',version:'1'});const [a,b]=linkedPair();await server.connect(a);await client.connect(b);
 try{const names=(await client.listTools()).tools.map(t=>t.name);assert.ok(names.includes('discord_update_bot_profile'));for(const name of ['discord_get_bot_profile','discord_get_agent_personality','discord_set_agent_personality']){const r=await client.callTool({name,arguments:{relayId:other,...(name==='discord_set_agent_personality'?{personality:'test'}:{})}});assert.equal(r.isError,true);}assert.equal(calls.length,0);await client.callTool({name:'discord_list_relays',arguments:{}});assert.deepEqual(calls[0],['alice',relayId]);const r=await client.callTool({name:'discord_get_bot_profile',arguments:{relayId}});assert.ok(!r.isError);}finally{await client.close();await server.close();}
});
test('exchange rejects foreign origins and hides storage errors',async()=>{
 const handler=setupExchangeHandler({exchange:async()=>{throw Error('private SQL credentials');}},'https://example.com');const res={status(n){this.code=n;return this;},json(x){this.body=x;return this;}};await handler({headers:{origin:'https://evil.test'}},res);assert.equal(res.code,403);await handler({headers:{authorization:'Bearer bad'},body:{}},res);assert.equal(res.code,503);assert.ok(!JSON.stringify(res.body).includes('SQL'));
});
