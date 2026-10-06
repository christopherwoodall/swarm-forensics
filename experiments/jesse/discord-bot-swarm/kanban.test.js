import test from 'node:test';
import assert from 'node:assert/strict';
import {OperationClient as Client,linkedPair,testOperations} from './operation-test-client.js';

import {agentOperations} from './agent-api.js';
const coordinationServer=deps=>testOperations(deps,agentOperations);
import {Kanban,createTaskInput,changeTaskInput} from './kanban.js';
test('board inputs reject unknown fields, invalid IDs and unbounded leases',()=>{assert.throws(()=>createTaskInput.parse({title:' ',mutationId:'valid-mutation-01'}));assert.throws(()=>createTaskInput.parse({title:'task',mutationId:'valid-mutation-01',owner:'other'}));assert.throws(()=>changeTaskInput.parse({taskId:'bad',revision:1,action:'claim',mutationId:'valid-mutation-01'}));assert.throws(()=>changeTaskInput.parse({taskId:'550e8400-e29b-41d4-a716-446655440000',revision:1,action:'claim',leaseSeconds:3601,mutationId:'valid-mutation-01'}));});
test('agent credentials cannot fall through to human authentication',async()=>{let called=false;const board=new Kanban({query:async()=>({rows:[]})});await assert.rejects(board.principal('swarm_agent_invalid',async()=>{called=true;return 'owner';}),/invalid/);assert.equal(called,false);assert.deepEqual(await board.principal('jwt',async()=> 'owner'),{owner:'owner',actor:'owner',kind:'owner'});});
test('agent HTTPS API exposes only scoped board tools and concrete conflicts',async()=>{const principal={owner:'alice',actor:'agent',kind:'agent'},board={list:async p=>{assert.equal(p,principal);return {tasks:[]};},mutate:async()=>{throw Error('Task already claimed.');}};const server=coordinationServer({board,principal,owner:'alice',version:'test'}),client=new Client({name:'test',version:'1'});const [a,b]=linkedPair();await server.connect(a);await client.connect(b);try{const tools=(await client.listTools()).tools.map(t=>t.name);assert.deepEqual(tools,['board_list_tasks','board_create_task','board_update_task','board_read_events']);assert.equal((await client.callTool({name:'board_list_tasks',arguments:{}})).isError,undefined);const r=await client.callTool({name:'board_update_task',arguments:{taskId:'550e8400-e29b-41d4-a716-446655440000',revision:1,action:'claim',mutationId:'valid-mutation-01'}});assert.equal(r.isError,true);assert.match(r.content[0].text,/already claimed/);}finally{await client.close();await server.close();}});

test('agent board tools reject an explicit server override',async()=>{let called=false;const principal={owner:'alice',actor:'agent',kind:'agent'},board={list:async()=>{called=true;return {tasks:[]};}},server=coordinationServer({board,principal,owner:'alice',version:'test'}),client=new Client({name:'scope-test',version:'1'});const [a,b]=linkedPair();await server.connect(a);await client.connect(b);try{const result=await client.callTool({name:'board_list_tasks',arguments:{guildId:'123456789012345678'}});assert.equal(result.isError,true);assert.match(result.content[0].text,/fixed by its swarm credential/);assert.equal(called,false);}finally{await client.close();await server.close();}});

test('direct relay API keys are scoped, hashed, seven-day and reject foreign or unverified relays',async()=>{
 const crypto=await import('node:crypto'),relayId='550e8400-e29b-41d4-a716-446655440000';let insert;
 const board=new Kanban({query:async(sql,args)=>{if(sql.startsWith('SELECT config')){assert.deepEqual(args,[relayId,'alice']);assert.ok(sql.includes("verifiedAt"));return {rows:[{guild_id:'123456789012345678'}]};}insert=args;return {rows:[{id:args[0],relay_id:args[6]}]};}});
 const key=await board.issue('alice',{name:'Coding agent',relayId});assert.match(key.token,/^swarm_agent_[\w-]{43}$/);assert.equal(insert[3],crypto.createHash('sha256').update(key.token).digest('hex'));assert.equal(insert[4],168);assert.equal(insert[5],'guild:123456789012345678');assert.equal(insert[6],relayId);
 await assert.rejects(board.issue('alice',{name:'Agent',relayId,guildId:'unassigned'}),/not both/);
 await assert.rejects(board.issue('alice',{name:'',relayId}));
 await assert.rejects(new Kanban({query:async()=>({rows:[]})}).issue('foreign',{name:'Agent',relayId}),/not found/);
});

test('archive reads pass view and cursor without changing agent scope',async()=>{
 const principal={owner:'alice',actor:'agent',kind:'agent'},cursor='550e8400-e29b-41d4-a716-446655440000';let input;
 const board={list:async(p,args)=>{assert.equal(p,principal);input=args;return {tasks:[],nextCursor:null};}},server=coordinationServer({board,principal,owner:'alice',version:'test'}),client=new Client({name:'archive-test',version:'1'});const [a,b]=linkedPair();await server.connect(a);await client.connect(b);
 try{assert.equal((await client.callTool({name:'board_list_tasks',arguments:{view:'archive',cursor}})).isError,undefined);assert.deepEqual(input,{view:'archive',cursor});assert.equal((await client.callTool({name:'board_list_tasks',arguments:{view:'invalid'}})).isError,true);assert.equal((await client.callTool({name:'board_list_tasks',arguments:{cursor:'invalid'}})).isError,true);}finally{await client.close();await server.close();}
});
