import test from 'node:test';
import assert from 'node:assert/strict';
import {syncNeeded,runChecks,verifyMerge,snapshotOnly,waitForMergeability} from './auto-sync.mjs';
test('only committed changes require synchronization',()=>{const a='a'.repeat(40),b='b'.repeat(40);assert.equal(syncNeeded(a,a),false);assert.equal(syncNeeded(a,b),true);assert.throws(()=>syncNeeded('invalid',b),/Invalid/);});
test('failed checks stop publication',()=>{const steps=[];assert.throws(()=>runChecks((command,args)=>{steps.push(args.at(-1));if(args.at(-1)==='lint')throw Error('lint failed');}),/lint failed/);assert.deepEqual(steps,['test','lint']);});
test('target or pull request movement prevents merge',()=>{assert.throws(()=>verifyMerge('new','old','head','head'),/main changed/);assert.throws(()=>verifyMerge('base','base','new','old'),/Pull request changed/);assert.doesNotThrow(()=>verifyMerge('base','base','head','head'));});

test('porcelain status preserves leading spaces and rejects changes outside Jesse',()=>{assert.equal(snapshotOnly(' M experiments/jesse/MODULE.md\0?? experiments/jesse/new.js\0'),true);assert.equal(snapshotOnly(' M README.md\0'),false);assert.equal(snapshotOnly('R  experiments/jesse/new.js\0README.md\0'),false);assert.equal(snapshotOnly('R  experiments/jesse/new.js\0experiments/jesse/old.js\0'),true);assert.equal(snapshotOnly('M experiments/jesse/MODULE.md'),false);assert.equal(snapshotOnly(''),true);});

test('mergeability waits for GitHub calculation but stops on conflicts or timeout',()=>{let reads=0,pauses=0;const result=waitForMergeability(()=>({mergeable:++reads===1?'UNKNOWN':'MERGEABLE',headRefOid:'tested'}),()=>pauses++);assert.equal(result.headRefOid,'tested');assert.equal(pauses,1);assert.throws(()=>waitForMergeability(()=>({mergeable:'CONFLICTING'}),()=>assert.fail('Conflict MUST stop')),/conflicts/);assert.throws(()=>waitForMergeability(()=>({mergeable:'UNKNOWN'}),()=>{},2),/Timed out/);});
