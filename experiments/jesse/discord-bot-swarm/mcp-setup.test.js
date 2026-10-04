import test from 'node:test';
import assert from 'node:assert/strict';
import {CLIENTS,clientConfig,checkMcp} from './frontend/mcp-setup.js';
test('all clients get correct remote endpoint and placeholder credentials',()=>{
 for(const id of Object.keys(CLIENTS)){const config=clientConfig(id,'https://example.com');assert.ok(config.includes('https://example.com/mcp'));assert.ok(config.includes('YOUR_APPLICATION_TOKEN'));}
 assert.equal(JSON.parse(clientConfig('opencode','https://example.com')).mcp.discord_swarm.oauth,false);
 assert.throws(()=>clientConfig('unknown','https://example.com'));
});
test('connection check initializes then verifies selected relay by bounded read',async()=>{
 const calls=[];await checkMcp(async(url,options)=>{const req=JSON.parse(options.body);calls.push(req);assert.equal(url,'/mcp');assert.ok(options.signal);assert.equal(options.timeoutMs,10000);return req.method==='initialize'?{result:{capabilities:{tools:{}}}}:{result:{content:[{type:'text',text:'{"messages":[]}' }]}};},'relay');assert.equal(calls[1].params.arguments.relayId,'relay');assert.equal(calls[1].params.arguments.limit,1);
});
test('failed and malformed reads do not appear verified',async()=>{
 for(const bad of [{isError:true}, {content:[{type:'text',text:'not JSON'}]}, {content:[{type:'text',text:'{}'}]}])await assert.rejects(checkMcp(async(url,opts)=>JSON.parse(opts.body).method==='initialize'?{result:{capabilities:{tools:{}}}}:{result:bad},'relay'));
});
