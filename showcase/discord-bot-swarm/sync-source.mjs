import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';

export function syncSource(repository,reference,root=path.dirname(fileURLToPath(import.meta.url))){
if(!repository||!reference)throw Error('SOURCE_REPO and SOURCE_REV are required. Use a committed revision.');
const deadline=Date.now()+60000;
const git=(...args)=>{const remaining=deadline-Date.now();if(remaining<=0)throw Error('Source import timed out.');return execFileSync('git',['-C',repository,...args],{timeout:Math.min(30000,remaining),maxBuffer:32*1024*1024});};
const revision=git('rev-parse','--verify',`${reference}^{commit}`).toString().trim();
const upstream=git('remote','get-url','origin').toString().trim().replace(/\.git$/,'');
if(upstream!=='https://github.com/QualityCopperShovel/discord-bot-swarm')throw Error('The source repository MUST be Discord Swarm.');
const entries=git('ls-tree','-rz','--full-tree',revision).toString().split('\0').filter(Boolean);
const files=new Map(),excluded=[];
for(const entry of entries){
 const [metadata,name]=entry.split('\t');
 if(!name||name.startsWith('/')||name.split('/').includes('..'))throw Error('Invalid source path.');
 if(path.basename(name)==='AGENTS.md'){excluded.push(name);continue;}
 const [mode,type,blob]=metadata.split(' ');
 if(type!=='blob'||!['100644','100755'].includes(mode))throw Error(`Unsupported source entry: ${name}`);
 files.set(name,{bytes:git('cat-file','blob',blob),mode:mode==='100755'?0o755:0o644});
}
const version=files.get('VERSION')?.bytes.toString().trim();
if(!version||!files.has('package-lock.json'))throw Error('Required source files are missing.');
const previous=JSON.parse(fs.readFileSync(path.join(root,'SOURCE.json'),'utf8'));
const target=path.join(root,'discord-bot-swarm');
for(const name of Object.keys(previous.sha256)){
 if(name.startsWith('/')||name.split('/').includes('..'))throw Error('Invalid previous source path.');
 if(!files.has(name))fs.rmSync(path.join(target,name),{force:true});
}
const sha256={};
for(const [name,{bytes,mode}] of files){
 const destination=path.join(target,name);fs.mkdirSync(path.dirname(destination),{recursive:true});
 fs.writeFileSync(destination,bytes,{mode});fs.chmodSync(destination,mode);
 sha256[name]=crypto.createHash('sha256').update(bytes).digest('hex');
}
fs.writeFileSync(path.join(root,'SOURCE.json'),JSON.stringify({repository:upstream,revision,version,excluded,sha256},null,2)+'\n');
console.log(`Imported ${files.size} committed files from ${revision} (${version}).`);
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url))syncSource(...process.argv.slice(2));
