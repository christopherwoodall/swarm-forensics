import fs from 'node:fs';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';

const sourceRepository='QualityCopperShovel/discord-bot-swarm';
const targetRepository='christopherwoodall/swarm-forensics';
export function syncNeeded(imported,current){
 if(![imported,current].every(value=>/^[a-f0-9]{40}$/.test(value)))throw Error('Invalid source revision.');
 return imported!==current;
}
export function runChecks(run){
 for(const target of ['test','lint','build','check'])run('make',['-C','experiments/jesse',target],600);
}
export function verifyMerge(base,testedBase,head,testedHead){
 if(base!==testedBase)throw Error('Target main changed during checks. Retry against the new revision.');
 if(head!==testedHead)throw Error('Pull request changed after checks. Retry with the current revision.');
}
export function snapshotOnly(status){
 const entries=status.split('\0').filter(Boolean);
 for(let i=0;i<entries.length;i++){
  const entry=entries[i];
  if(entry[2]!==' '||!entry.slice(3).startsWith('experiments/jesse/'))return false;
  if(/[RC]/.test(entry.slice(0,2))&&!entries[++i]?.startsWith('experiments/jesse/'))return false;
 }
 return true;
}
export function waitForMergeability(read,pause,attempts=10){
 for(let i=0;i<attempts;i++){
  const request=read();
  if(request.mergeable==='MERGEABLE')return request;
  if(request.mergeable==='CONFLICTING')throw Error('Pull request has merge conflicts.');
  if(i+1<attempts)pause();
 }
 throw Error('Timed out waiting for GitHub mergeability calculation.');
}
export function autoSync(configFile){
 const stat=fs.lstatSync(configFile);
 if(!stat.isFile()||stat.uid!==process.getuid()||(stat.mode&0o077))throw Error('Private configuration MUST be an owner-only file.');
 const config=JSON.parse(fs.readFileSync(configFile,'utf8'));
 if(typeof config.token!=='string'||!config.token||!path.isAbsolute(config.stateDir||''))throw Error('Private token and absolute stateDir are required.');
 fs.mkdirSync(config.stateDir,{recursive:true,mode:0o700});
 const stateStat=fs.lstatSync(config.stateDir);
 if(!stateStat.isDirectory()||stateStat.uid!==process.getuid()||(stateStat.mode&0o077))throw Error('State directory MUST be private and owner-owned.');
 const statusFile=path.join(config.stateDir,'status.json');const logFile=path.join(config.stateDir,'run.log');
 const log=fs.openSync(logFile,'w',0o600);const startedAt=new Date().toISOString();const deadline=Date.now()+15*60000;
 let step='inspect',revision,pr;
 const status=(state,extra={})=>{const temporary=statusFile+'.tmp';fs.writeFileSync(temporary,JSON.stringify({state,step,startedAt,updatedAt:new Date().toISOString(),deadlineAt:new Date(deadline).toISOString(),revision,pr,...extra},null,2)+'\n',{mode:0o600});fs.renameSync(temporary,statusFile);};
 const environment={...process.env,GH_TOKEN:config.token,GIT_TERMINAL_PROMPT:'0',UV_LINK_MODE:'copy'};
 const run=(command,args,seconds=30,cwd=config.stateDir)=>{
  const remaining=Math.floor((deadline-Date.now())/1000);if(remaining<=0)throw Error('Overall synchronization deadline expired.');
  status('running');
  fs.writeSync(log,`${new Date().toISOString()} ${step}: ${command}\n`);
  try{const output=execFileSync('timeout',['--kill-after=5s',`${Math.min(seconds,remaining)}s`,command,...args],{cwd,env:environment,timeout:(Math.min(seconds,remaining)+10)*1000,maxBuffer:32*1024*1024,stdio:['ignore','pipe',log]});fs.writeSync(log,output);return output.toString().trimEnd();}
  catch{throw Error(`${step} failed or timed out. Inspect the private run log.`);}
 };
 const gh=(...args)=>run('gh',args);
 const api=route=>JSON.parse(gh('api',route));
 const git=(cwd,...args)=>run('git',['-c','credential.helper=','-c','credential.helper=!gh auth git-credential',...args],60,cwd);
 try{
  status('running');
  revision=api(`repos/${sourceRepository}/commits/main`).sha;
  const imported=JSON.parse(Buffer.from(api(`repos/${targetRepository}/contents/experiments/jesse/SOURCE.json?ref=main`).content,'base64').toString());
  if(!syncNeeded(imported.revision,revision)){status('completed',{outcome:'already_current'});return;}
  step='prepare isolated source';
  const source=path.join(config.stateDir,'source');
  if(!fs.existsSync(source))git(config.stateDir,'clone','--bare',`https://github.com/${sourceRepository}.git`,source);
  git(source,'fetch','origin','main');git(source,'cat-file','-e',`${revision}^{commit}`);
  const working=path.join(config.stateDir,'working');fs.rmSync(working,{recursive:true,force:true});
  git(config.stateDir,'clone','--depth','1',`https://github.com/${targetRepository}.git`,working);
  const base=git(working,'rev-parse','HEAD');const branch=`auto-sync/jesse-${revision.slice(0,12)}-${Date.now()}`;
  git(working,'switch','-c',branch);git(working,'config','user.name','FairyStack Agent');git(working,'config','user.email','multi-agent@fairystack.com');
  step='import committed source';run('make',['-C','experiments/jesse','sync',`SOURCE_REPO=${source}`,`SOURCE_REV=${revision}`],60,working);
  const snapshot=JSON.parse(fs.readFileSync(path.join(working,'experiments/jesse/SOURCE.json'),'utf8'));
  const moduleFile=path.join(working,'experiments/jesse/MODULE.md');let module=fs.readFileSync(moduleFile,'utf8');
  module=module.replace(/- Imported version: .*/,`- Imported version: ${snapshot.version}.`).replace(/- Source revision: .*/,`- Source revision: ${revision}.`);fs.writeFileSync(moduleFile,module);
  step='checks';runChecks((command,args,seconds)=>run(command,args,seconds,working));
  if(!snapshotOnly(git(working,'status','--porcelain=v1','-z','--untracked-files=all')))throw Error('Checks modified files outside the snapshot directory.');
  step='publish pull request';
  verifyMerge(api(`repos/${targetRepository}/commits/main`).sha,base,revision,revision);
  git(working,'add','experiments/jesse');git(working,'commit','-m',`feat: synchronize Jesse source to ${snapshot.version}`);
  const testedHead=git(working,'rev-parse','HEAD');git(working,'push','origin',branch);
  const bodyFile=path.join(config.stateDir,'pull-request.md');fs.writeFileSync(bodyFile,`Synchronize Jesse source to Discord Swarm ${snapshot.version}.\n\nSource commit: ${revision}.\n\nValidation: Jesse make test, lint, build, and check passed.\n\nThe snapshot MUST preserve committed source hashes. Credentials and runtime data MUST remain excluded.\n`,{mode:0o600});
  pr=gh('pr','create','--repo',targetRepository,'--base','main','--head',branch,'--title',`Synchronize Jesse Discord Swarm to ${snapshot.version}`,'--body-file',bodyFile);
  step='required checks';
  const protection=api(`repos/${targetRepository}/branches/main`).protection?.required_status_checks;
  if((protection?.contexts?.length||0)+(protection?.checks?.length||0)>0)run('gh',['pr','checks',pr,'--repo',targetRepository,'--required','--watch','--interval','10','--fail-fast'],300);
  const request=waitForMergeability(()=>JSON.parse(gh('pr','view',pr,'--repo',targetRepository,'--json','headRefOid,mergeable')),()=>Atomics.wait(new Int32Array(new SharedArrayBuffer(4)),0,0,2000));
  verifyMerge(api(`repos/${targetRepository}/commits/main`).sha,base,request.headRefOid,testedHead);
  if(request.mergeable!=='MERGEABLE')throw Error('Pull request is conflicted or mergeability is unknown.');
  step='merge';gh('pr','merge',pr,'--repo',targetRepository,'--squash','--delete-branch','--match-head-commit',testedHead);
  step='verify main';
  const merged=JSON.parse(gh('pr','view',pr,'--repo',targetRepository,'--json','state,mergeCommit'));
  const published=JSON.parse(Buffer.from(api(`repos/${targetRepository}/contents/experiments/jesse/SOURCE.json?ref=main`).content,'base64').toString());
  if(merged.state!=='MERGED'||published.revision!==revision)throw Error('Published main does not contain the tested source snapshot.');
  status('completed',{outcome:'merged',version:snapshot.version,mergeCommit:merged.mergeCommit.oid});
 }catch(error){status(Date.now()>=deadline?'timed_out':'failed',{error:error.message});throw error;}
 finally{fs.closeSync(log);}
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 try{autoSync(process.argv[2]);}catch(error){process.stderr.write(error.message+'\n');process.exitCode=1;}
}
