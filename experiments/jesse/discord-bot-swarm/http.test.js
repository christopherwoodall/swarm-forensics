import test from 'node:test';
import assert from 'node:assert/strict';
import {readJsonResponse} from './frontend/http.js';
test('HTML gateway failures do not expose response bodies',async()=>{
  await assert.rejects(readJsonResponse(new Response('<html>private upstream detail</html>',{status:502,headers:{'content-type':'text/html'}})),{message:'Server temporarily unavailable. Please try again shortly.'});
});
test('unexpected success bodies and malformed JSON fail safely',async()=>{
  await assert.rejects(readJsonResponse(new Response('<html>secret</html>',{headers:{'content-type':'text/html'}})),/unexpected response/);
  await assert.rejects(readJsonResponse(new Response('{secret',{headers:{'content-type':'application/json'}})),/invalid response/);
});
test('JSON successes and client errors retain their meaning',async()=>{
  assert.deepEqual(await readJsonResponse(Response.json({ok:true})),{ok:true});
  await assert.rejects(readJsonResponse(Response.json({error:'Sign in required.'},{status:401})),{message:'Sign in required.'});
  await assert.rejects(readJsonResponse(Response.json({error:'private upstream detail'},{status:503})),/temporarily unavailable/);
});
