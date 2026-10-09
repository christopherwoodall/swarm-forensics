import test from 'node:test';
import assert from 'node:assert/strict';
import {agentPrompt,firstTaskPrompt,checkAgent} from './frontend/agent-setup.js';
const id='550e8400-e29b-41d4-a716-446655440000';
test('connection prompt supplies only connection instructions and HTTPS guide',()=>{const s=agentPrompt('https://swarm.example',id,'private-key');assert.ok(s.includes('https://swarm.example/agent-guide.md'));assert.ok(!s.includes('private-key'));assert.ok(!s.includes('Swarm API key:'));assert.ok(s.includes('Never share credentials'));assert.ok(firstTaskPrompt(id,'https://swarm.example').includes('POST /agent/v1/discord_read_messages'));assert.throws(()=>agentPrompt('https://swarm.example',''));});
test('connection check validates profile, channel and propagates failures with bounded requests',async()=>{const seen=[];await checkAgent(async(url,opts)=>{seen.push([url,JSON.parse(opts.body)]);assert.equal(opts.timeoutMs,10000);assert.ok(opts.signal);return url.endsWith('profile')?{id:'bot',username:'Bot'}:{messages:[]};},id);assert.deepEqual(seen.map(x=>x[0]),['/agent/v1/discord_get_bot_profile','/agent/v1/discord_read_messages']);await assert.rejects(checkAgent(async()=>({}),id),/invalid bot profile/);await assert.rejects(checkAgent(async url=>url.endsWith('profile')?{id:'bot',username:'Bot'}:{},id),/invalid channel/);await assert.rejects(checkAgent(async()=>{throw Error('denied');},id),/denied/);});

test('guide-first handoff carries validated connection context without duplicating the guide',()=>{
 const prompt=agentPrompt('https://swarm.example/path?token=private',id);
 assert.ok(prompt.startsWith(`Read https://swarm.example/agent-guide.md?relay=${id}`));
 assert.ok(prompt.length<650);
 for(const text of ['saved matching API key','documented owner authentication','register and save one privately','Verify the connection','exact failed step','Never share credentials'])assert.ok(prompt.includes(text),text);
 for(const text of ['token=private','POST /agent/v1/','FairyStack'])assert.ok(!prompt.includes(text),text);
 assert.throws(()=>agentPrompt('https://swarm.example','not-a-relay'),/Invalid relay ID/);
 assert.throws(()=>agentPrompt('https://swarm.example',''),/Bot connection is required/);
});

test('guide retains saved-key recovery, verification and work completion contracts',async()=>{
 const {readFile}=await import('node:fs/promises');
 const guide=await readFile(new URL('./frontend/agent-guide.md',import.meta.url),'utf8');
 for(const text of ['GET /agent/v1','discord_list_relays','POST /api/board/agents','atomic file outside Git','project-scoped persistent instructions','onboarding incomplete','discord_sync_agent','discord_get_bot_profile','discord_read_messages','discord_discover_channels','Verify the requested bot connection belongs','A 401 requires replacement','30-second HTTP timeouts','atomically claim','execute the task','concrete blocker on the board',"Don't repeat these updates",'continue with the next eligible task'])assert.ok(guide.includes(text),text);
});

test('guide requires independent credential storage and refuses scope collisions before overwriting',async()=>{
 const {readFile}=await import('node:fs/promises');
 const guide=await readFile(new URL('./frontend/agent-guide.md',import.meta.url),'utf8');
 for(const text of ['never use a single shared key file','Check the saved origin and `relayId` before making requests','registration response’s `relay_id` matches','<encoded-origin>/<relayId>/<credentialId>.json','without replacing existing files','refuse mismatches and preserve its contents','Atomic replacement alone does not prevent overwriting another identity','without replacing other connections’ locators or instructions','replace only the affected bot’s lost credential','cannot inspect or protect another runtime’s local secret store'])assert.ok(guide.includes(text),text);
});

test('joining prompt retains coordination and completion requirements',()=>{
 const prompt=firstTaskPrompt(id,'https://swarm.example');
 for(const text of ['saved API key lookup and validation','post one short hello','completed dependencies','owner-authorized project scope','atomically claim','begin work in this attempt','report idle with the reason','A greeting or claim is not completion','execute the task','concrete blocker on the board','do not repeat them','continue with the next eligible task','specific blockers'])assert.ok(prompt.includes(text),text);
});
