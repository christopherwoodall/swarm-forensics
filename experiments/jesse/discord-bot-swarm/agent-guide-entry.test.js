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
  r=await get('/?setup=agent');assert.equal(r.headers.get('location'),'/agent-guide.md');
  for(const p of ['/?setup=agent&relay=wrong','/agent-guide.md?relay=wrong','/agent-guide.md?relay='])assert.equal((await get(p)).status,400);
  for(const p of ['/','/?setup=bot','/?setup=test&relay='+id])assert.equal((await get(p)).status,418);
  r=await get('/agent-guide.md');assert.equal(await r.text(),'# Join Discord Swarm\n\n## Connect\nSaved key instructions.');
 }finally{await new Promise(r=>server.close(r));}
});
