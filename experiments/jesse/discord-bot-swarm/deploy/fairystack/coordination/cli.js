#!/usr/bin/env node
import {configuration,privateFile,Store,connections,Adapter} from './adapter.js';
const usage='Usage: node deploy/fairystack/coordination/cli.js <check|list|dispatch|watch|status|finish|stop> /absolute/private-config.json [task-uuid] [absolute-private-objective-or-result-file]';
const [command,file,id,textFile]=process.argv.slice(2);
let connection,unlock,adapter,store;
try{
 if(!['check','list','dispatch','watch','status','finish','stop'].includes(command)||!file)throw Error(usage);
 const config=configuration(file);store=new Store(config.stateDir);
 if(!['check','list'].includes(command))unlock=store.lock(id);
 const signal=AbortSignal.timeout(['dispatch','watch'].includes(command)?(config.deadlineSeconds+60)*1000:60000);
 connection=await connections(config,signal);adapter=new Adapter({config,store,...connection});
 let result;
 if(['check','list'].includes(command)){result=await connection.mcp('board_list_tasks');if(!Array.isArray(result.tasks))throw Error('The service does not expose the shared board contract.');if(command==='check')result={status:'completed',tasksVisible:result.tasks.length,scope:'Read-only MCP board check; no session or model call was started.'};}
 if(command==='dispatch')result=await adapter.dispatch(id,privateFile(textFile));
 if(command==='status')result=await adapter.status(id);
 if(command==='stop')result=await adapter.stop(id);
 if(command==='finish')result=await adapter.finish(id,privateFile(textFile).trim());
 if(['dispatch','watch'].includes(command)){
  for(;;){result=await adapter.status(id);console.error(JSON.stringify({taskId:id,state:result.state,sessionUrl:result.sessionUrl||null,step:result.sessionStep||null}));if(!['running'].includes(result.state))break;await new Promise((resolve,reject)=>{const abort=()=>{clearTimeout(timer);reject(Error('Command deadline reached. Run stop to reconcile cancellation.'));};const timer=setTimeout(()=>{signal.removeEventListener('abort',abort);resolve();},5000);signal.addEventListener('abort',abort,{once:true});if(signal.aborted)abort();});}
 }
 // Trusted objective and pending API requests stay private, never in stdout.
 console.log(JSON.stringify(command==='list'?result:{status:result.state||result.status,taskId:result.taskId,sessionId:result.sessionId,sessionUrl:result.sessionUrl,sessionStatus:result.sessionStatus,scope:result.scope,tasksVisible:result.tasksVisible},null,2));
 if(['failed','timed_out','cancelled'].includes(result.state))process.exitCode=1;
}catch(e){
 if(store&&id){try{const j=store.read(id);if(j){j.lastError=e.message;j.lastErrorAt=Date.now();store.write(j);}}catch{}}
 console.error(JSON.stringify({status:'failed',step:command,error:e.message}));process.exitCode=1;
}finally{await connection?.close().catch(()=>{});unlock?.();}
