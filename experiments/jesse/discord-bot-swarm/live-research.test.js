import test from 'node:test';
import assert from 'node:assert/strict';
import {sanitize,capture,reportInput,exportInput,registerResearchOperations} from './live-research.js';
import {Operations,agentOperations} from './agent-api.js';
test('research strips nested credentials, bearer strings and signed query credentials',()=>{
 const v=sanitize({token:'private',nested:{API_key:'private',content:'Bearer abcdef swarm_agent_abcdef https://example.com/?token=private&x=1'},image:'data:image/png;base64,YWJj',sourceTime:new Date('2026-10-05T00:00:00Z')});assert.equal(v.token,'[redacted]');assert.equal(v.nested.API_key,'[redacted]');assert.ok(!JSON.stringify(v).includes('private'));assert.equal(v.sourceTime,'2026-10-05T00:00:00.000Z');assert.equal(v.image,'[image omitted]');
 assert.deepEqual(sanitize({inputTokens:123,output_tokens:45,accessToken:'private'}),{inputTokens:123,output_tokens:45,accessToken:'[redacted]'});
 const big=capture({content:'a'.repeat(15000)});assert.equal(big.omitted,true);assert.equal(big.sha256.length,64);assert.equal(capture({n:1}).n,1);
});
test('reports reject forged actors, missing provenance, invalid dates and unbounded pages',()=>{
 const a={eventId:'research-example-001',type:'turn',source:'test-runtime',sourceTime:'2026-10-05T00:00:00Z',sessionId:'test',data:{state:'completed'}};assert.equal(reportInput.parse(a).sourceRefs.length,0);assert.throws(()=>reportInput.parse({...a,actor:'another-agent'}));assert.throws(()=>reportInput.parse({...a,sourceTime:'yesterday'}));assert.throws(()=>reportInput.parse({...a,source:''}));assert.throws(()=>exportInput.parse({limit:201}));assert.throws(()=>exportInput.parse({after:'-1'}));
});
test('operation recording persists start and outcome, including failures, without recursion',async()=>{
 const seen=[];const s=new Operations({start:async(n,a)=>{seen.push(['start',n,a]);return {id:'1'};},finish:async(c,n,r,e)=>seen.push(['finish',n,r,e?.message])});s.registerOperation('work',{inputSchema:{}},()=>({ok:true}));s.registerOperation('bad',{inputSchema:{}},()=>{throw Object.assign(Error('Failed'),{status:422});});s.registerOperation('research_export',{inputSchema:{}},()=>({events:[]}));await s.invoke('work');await assert.rejects(s.invoke('bad'),/Failed/);await s.invoke('research_export');assert.deepEqual(seen.map(e=>e.slice(0,2)),[['start','work'],['finish','work'],['start','bad'],['finish','bad']]);assert.equal(seen[3][3],'Failed');
});
test('research operations are available to board-only credentials and bind authenticated principal',async()=>{
 const p={owner:'a',actor:'agent-a',kind:'agent'},calls=[];const research={report:async(principal,a)=>{calls.push(principal);return a;},export:async(principal,a)=>{calls.push(principal);return a;}};const s=agentOperations({principal:p,owner:p.owner,research});assert.deepEqual(s.catalog().map(o=>o.name),['research_record_event','research_export']);await s.invoke('research_export',{});assert.equal(calls[0],p);const catalog=s.catalog();assert.equal(catalog[0].readOnly,false);assert.equal(catalog[1].readOnly,true);
});
