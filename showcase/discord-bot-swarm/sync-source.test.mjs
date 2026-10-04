import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
import {syncSource} from './sync-source.mjs';

test('snapshot imports committed files, excludes directives, removes obsolete files, and preserves local data',()=>{
 const dir=fs.mkdtempSync(path.join(os.tmpdir(),'jesse-sync-test-'));const repository=path.join(dir,'repo'),root=path.join(dir,'snapshot');
 fs.mkdirSync(repository);fs.mkdirSync(root);fs.writeFileSync(path.join(root,'SOURCE.json'),JSON.stringify({sha256:{}}));
 const git=(...args)=>execFileSync('git',['-C',repository,...args],{timeout:5000,stdio:'pipe'}).toString().trim();
 try{
  git('init');git('config','user.name','Synthetic test');git('config','user.email','test@example.invalid');git('remote','add','origin','https://github.com/QualityCopperShovel/discord-bot-swarm.git');
  for(const [name,content] of [['VERSION','1.0.0\n'],['package-lock.json','{}\n'],['AGENTS.md','Exclude directives.'],['obsolete.txt','Old source.']])fs.writeFileSync(path.join(repository,name),content);
  git('add','.');git('commit','-m','test: create source fixture');const revision=git('rev-parse','HEAD');
  fs.writeFileSync(path.join(repository,'VERSION'),'uncommitted change');syncSource(repository,revision,root);
  const target=path.join(root,'discord-bot-swarm');assert.equal(fs.readFileSync(path.join(target,'VERSION'),'utf8'),'1.0.0\n');assert.equal(fs.existsSync(path.join(target,'AGENTS.md')),false);
  assert.equal(JSON.parse(fs.readFileSync(path.join(root,'SOURCE.json'))).revision,revision);
  fs.writeFileSync(path.join(target,'local-data.txt'),'Preserve local data.');fs.unlinkSync(path.join(repository,'obsolete.txt'));fs.writeFileSync(path.join(repository,'VERSION'),'1.1.0\n');git('add','.');git('commit','-m','test: remove obsolete fixture');syncSource(repository,'HEAD',root);
  assert.equal(fs.existsSync(path.join(target,'obsolete.txt')),false);assert.equal(fs.readFileSync(path.join(target,'local-data.txt'),'utf8'),'Preserve local data.');
  git('remote','set-url','origin','https://example.invalid/other.git');assert.throws(()=>syncSource(repository,'HEAD',root),/MUST be Discord Swarm/);
  assert.equal(JSON.parse(fs.readFileSync(path.join(root,'SOURCE.json'))).version,'1.1.0');
 }finally{fs.rmSync(dir,{recursive:true,force:true});}
});
test('snapshot rejects missing revision or repository',()=>{assert.throws(()=>syncSource(),/are required/);assert.throws(()=>syncSource('/unused'),/are required/);});
