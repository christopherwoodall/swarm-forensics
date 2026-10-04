import test from 'node:test';
import assert from 'node:assert/strict';
import {agentPrompt,firstTaskPrompt,checkMcp} from './frontend/mcp-setup.js';
const content=value=>({content:[{type:'text',text:JSON.stringify(value)}]});
const authorized={tools:['discord_get_bot_profile','discord_update_bot_profile','discord_read_messages'].map(name=>({name}))};
function fixture(req){if(req.method==='initialize')return {capabilities:{tools:{}}};if(req.method==='tools/list')return authorized;if(req.params.name==='discord_get_bot_profile')return content({id:'123',username:'Jeremy'});return content({messages:[]});}
test('agent prompt supplies native setup, bot authorization and private temporary credential handling',()=>{
 const prompt=agentPrompt('https://example.com','relay');assert.ok(prompt.includes('https://example.com/mcp'));assert.ok(prompt.includes('YOUR_SINGLE_USE_SETUP_TOKEN'));assert.ok(prompt.includes('Streamable HTTP'));assert.ok(prompt.includes('relayId "relay"'));assert.ok(prompt.includes('do not post'));assert.ok(prompt.includes('does not use an OAuth'));assert.ok(prompt.includes('discord_update_bot_profile'));assert.ok(prompt.includes('authorizes the selected relay'));assert.ok(prompt.includes('read the profile back'));assert.ok(prompt.includes('across all Discord servers'));
 assert.ok(prompt.includes('Kanban Board: https://example.com/board.html'));assert.ok(prompt.includes('Call board_list_tasks'));assert.ok(prompt.includes('Do not create, claim or modify tasks'));assert.ok(prompt.includes('never authorization'));assert.ok(prompt.includes('readOnlyHint: true'));assert.ok(prompt.includes('do not bypass the guard'));assert.ok(prompt.includes('refresh tool discovery'));
 const copied=agentPrompt('https://example.com','relay','synthetic-token');assert.ok(copied.includes('Single-use setup token: synthetic-token'));assert.ok(!copied.includes('YOUR_SINGLE_USE_SETUP_TOKEN'));assert.ok(copied.includes('https://example.com/mcp/connect'));assert.ok(copied.includes('redeemed only once'));assert.ok(copied.includes('discard the setup token'));assert.ok(!copied.includes('app login token'));
 assert.throws(()=>agentPrompt('https://example.com',''));assert.throws(()=>agentPrompt('https://example.com','relay',''));
});
test('connection check verifies configuration tools and profile before bounded channel read, without writing',async()=>{
 const calls=[];await checkMcp(async(url,options)=>{const req=JSON.parse(options.body);calls.push(req);assert.equal(url,'/mcp');assert.ok(options.signal);assert.equal(options.timeoutMs,10000);return {result:fixture(req)};},'relay');assert.deepEqual(calls.map(r=>r.method),['initialize','tools/list','tools/call','tools/call']);assert.equal(calls[2].params.name,'discord_get_bot_profile');assert.equal(calls[2].params.arguments.relayId,'relay');assert.equal(calls[3].params.name,'discord_read_messages');assert.equal(calls[3].params.arguments.limit,1);
});
test('read-only or board-only credentials cannot pass configuration authorization',async()=>{
 for(const tools of [[],[{name:'discord_read_messages'}],[{name:'discord_get_bot_profile'},{name:'discord_read_messages'}]])await assert.rejects(checkMcp(async(url,opts)=>{const req=JSON.parse(opts.body);assert.notEqual(req.method,'tools/call');return {result:req.method==='tools/list'?{tools}:fixture(req)};},'relay'),/configuration authorization/);
});
test('failed and malformed profile or channel reads do not appear verified',async()=>{
 for(const name of ['discord_get_bot_profile','discord_read_messages'])for(const bad of [{isError:true}, {content:[{type:'text',text:'not JSON'}]},content({})])await assert.rejects(checkMcp(async(url,opts)=>{const req=JSON.parse(opts.body);return {result:req.params?.name===name?bad:fixture(req)};},'relay'));
});

test('setup and first-task prompts install routine coordination without inventing goals or runtime activity',()=>{
 const prompt=firstTaskPrompt('fixture-relay'),setup=agentPrompt('https://example.com','fixture-relay');
 for(const phrase of ['persistent instruction mechanism','claim it before starting','claim conflict','Renew your lease','never authorization','do not ask me to assign individual roles','when idle']){assert.ok(prompt.includes(phrase),phrase);assert.ok(setup.includes(phrase),phrase);}
 for(const phrase of ['relayId "fixture-relay"','limit 10','discord_post_message','stable numeric nonce','never post twice','message ID','already given you a goal','Otherwise ask only what I want','Do not invent a goal'])assert.ok(prompt.includes(phrase),phrase);
 assert.ok(!prompt.includes('Authorization:'));assert.throws(()=>firstTaskPrompt(''));
});


test('new and existing agent instructions teach readable Discord messages without forcing headings on chatter',()=>{
 for(const prompt of [agentPrompt('https://example.com','relay'),firstTaskPrompt('relay')]){assert.match(prompt,/Discord Markdown/);assert.match(prompt,/blank lines/);assert.match(prompt,/inline code/);assert.match(prompt,/actual newline characters/);assert.match(prompt,/short conversational replies simple/);}
});
