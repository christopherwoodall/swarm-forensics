import test from 'node:test';
import assert from 'node:assert/strict';
import {syncNeeded,runChecks,verifyMerge} from './auto-sync.mjs';
test('only committed changes require synchronization',()=>{const a='a'.repeat(40),b='b'.repeat(40);assert.equal(syncNeeded(a,a),false);assert.equal(syncNeeded(a,b),true);assert.throws(()=>syncNeeded('invalid',b),/Invalid/);});
test('failed checks stop publication',()=>{const steps=[];assert.throws(()=>runChecks((command,args)=>{steps.push(args[0]);if(args[0]==='lint')throw Error('lint failed');}),/lint failed/);assert.deepEqual(steps,['test','lint']);});
test('target or pull request movement prevents merge',()=>{assert.throws(()=>verifyMerge('new','old','head','head'),/main changed/);assert.throws(()=>verifyMerge('base','base','new','old'),/Pull request changed/);assert.doesNotThrow(()=>verifyMerge('base','base','head','head'));});
