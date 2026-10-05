import test from 'node:test';
import assert from 'node:assert/strict';
import {agentPrompt,firstTaskPrompt,checkAgent} from './frontend/agent-setup.js';
const id='550e8400-e29b-41d4-a716-446655440000';
test('connection prompt supplies only connection instructions and HTTPS guide',()=>{const s=agentPrompt('https://swarm.example',id,'private-key');assert.ok(s.includes('https://swarm.example/agent-guide.md'));assert.ok(!s.includes('private-key'));assert.ok(!s.includes('Swarm API key:'));assert.ok(s.includes('Authorization: Bearer <API key>'));assert.ok(firstTaskPrompt(id,'https://swarm.example').includes('POST /agent/v1/discord_read_messages'));assert.throws(()=>agentPrompt('https://swarm.example',''));});
test('connection check validates profile, channel and propagates failures with bounded requests',async()=>{const seen=[];await checkAgent(async(url,opts)=>{seen.push([url,JSON.parse(opts.body)]);assert.equal(opts.timeoutMs,10000);assert.ok(opts.signal);return url.endsWith('profile')?{id:'bot',username:'Bot'}:{messages:[]};},id);assert.deepEqual(seen.map(x=>x[0]),['/agent/v1/discord_get_bot_profile','/agent/v1/discord_read_messages']);await assert.rejects(checkAgent(async()=>({}),id),/invalid bot profile/);await assert.rejects(checkAgent(async url=>url.endsWith('profile')?{id:'bot',username:'Bot'}:{},id),/invalid channel/);await assert.rejects(checkAgent(async()=>{throw Error('denied');},id),/denied/);});

test('onboarding checks saved keys before using the supplied key and persists only a private locator',()=>{
 const prompt=agentPrompt('https://swarm.example',id,'once');
 assert.ok(prompt.indexOf('First look for your saved')<prompt.indexOf('If no valid matching key exists'));
 for(const text of ['discord_list_relays','Stop on scope mismatch','server error does not','Record only its locator','read it back','onboarding incomplete','0600'])assert.ok(prompt.includes(text),text);
 assert.ok(firstTaskPrompt(id,'https://swarm.example').includes('saved API key lookup and validation'));
});

test('new runtimes discover documented owner authentication before reporting missing credentials',()=>{const prompt=agentPrompt('https://swarm.example',id);assert.ok(prompt.includes('documented app-authentication mechanism'));assert.ok(prompt.includes('before declaring that access unavailable'));assert.ok(!prompt.includes('Swarm API key:'));});
