import test from 'node:test';
import assert from 'node:assert/strict';
import express from 'express';
import {agentGuideEntry} from './agent-guide-entry.js';
const id='7f3b7fb7-4977-4347-88b5-820dbb719d9e';
test('agent entry redirects without authentication and guide preserves validated public scope',async()=>{
 const app=express();app.use(agentGuideEntry({origin:'https://swarm.example',guide:'# Join Discord Swarm\n\n## Connect\nSaved key instructions.'}));app.use((req,res)=>res.status(418).send('human wizard'));
 const server=app.listen(0,'127.0.0.1');await new Promise(r=>server.once('listening',r));
 const origin=`http://127.0.0.1:${server.address().port}`;
 const get=path=>fetch(origin+path,{redirect:'manual',signal:AbortSignal.timeout(3000)});
 try{
  let r=await get('/?setup=agent&relay='+id+'&token=private');assert.equal(r.status,302);assert.equal(r.headers.get('location'),'/agent-guide.md?relay='+id);
  r=await get(r.headers.get('location'));assert.equal(r.status,200);assert.match(r.headers.get('content-type'),/text\/plain/);const text=await r.text();assert.ok(text.includes(id));assert.ok(text.includes('https://swarm.example'));assert.ok(text.includes('Saved key instructions'));assert.ok(!text.includes('private'));
  assert.ok(text.includes(`Secret-store namespace: discord-swarm/https%3A%2F%2Fswarm.example/${id}/<credentialId>`));
  r=await get('/?setup=agent');assert.equal(r.headers.get('location'),'/agent-guide.md');
  for(const p of ['/?setup=agent&relay=wrong','/agent-guide.md?relay=wrong','/agent-guide.md?relay='])assert.equal((await get(p)).status,400);
  for(const p of ['/','/?setup=bot','/?setup=test&relay='+id])assert.equal((await get(p)).status,418);
  r=await get('/agent-guide.md');assert.equal(await r.text(),'# Join Discord Swarm\n\n## Connect\nSaved key instructions.');
 }finally{await new Promise(r=>server.close(r));}
});

test('scoped guides isolate two bot identities and origins without trusting query storage hints',async()=>{
 const otherId='550e8400-e29b-41d4-a716-446655440000';
 const render=(origin,relay,query='')=>{
  let text;
  const res={type(){return this;},send(value){text=value;return this;}};
  agentGuideEntry({origin,guide:'# Join Discord Swarm\n\n## Connect\nSaved key instructions.'})({method:'GET',originalUrl:'/agent-guide.md?relay='+relay+query},res,()=>assert.fail('guide was skipped'));
  return text;
 };
 const first=render('https://swarm.example',id,'&origin=https://other.example&credentialId=not-trusted&token=private');
 const second=render('https://swarm.example',otherId);
 const otherOrigin=render('https://other.example',id);
 const namespace=text=>text.split('\n').find(line=>line.startsWith('Secret-store namespace: '));
 assert.equal(namespace(first),`Secret-store namespace: discord-swarm/https%3A%2F%2Fswarm.example/${id}/<credentialId>`);
 assert.notEqual(namespace(first),namespace(second));
 assert.notEqual(namespace(first),namespace(otherOrigin));
 for(const value of ['other.example','not-trusted','private'])assert.ok(!first.includes(value),value);
 assert.ok(first.includes('preserve keys and locators for other connections'));
});
