import {spawn} from 'node:child_process';
import fs from 'node:fs';
let child,timer,killTimer,finished=false,output,stopReason,deadline=0;
function stop(reason){if(!child||finished||stopReason)return;stopReason=reason;try{process.kill(-child.pid,'SIGTERM');}catch{}killTimer=setTimeout(()=>{try{process.kill(-child.pid,'SIGKILL');}catch{}finish({state:reason,error:'Runtime stopped by cancellation or deadline.'});},Math.max(0,Math.min(2000,deadline-Date.now())));}
function finish(result){if(finished)return;finished=true;clearTimeout(timer);if(output)output.end(()=>process.send?.(result));else process.send?.(result);setTimeout(()=>process.exit(0),2500).unref();}
process.on('disconnect',()=>stop('cancelled'));
process.on('message',message=>{
 if(message.type==='stop'){stop('cancelled');return;}
 if(message.type!=='run'||child)return;
 const {command,args,cwd,prompt,deadlineAt,outputFile}=message;deadline=deadlineAt;
 try{const fd=fs.openSync(outputFile,'wx',0o600);output=fs.createWriteStream(outputFile,{fd});let bytes=0;const write=chunk=>{if(!finished&&bytes<1048576){const bounded=chunk.subarray(0,1048576-bytes);output.write(bounded);bytes+=bounded.length;}};
 child=spawn(command,args,{cwd,detached:true,stdio:['pipe','pipe','pipe'],env:process.env});child.stdout.on('data',write);child.stderr.on('data',write);child.stdin.on('error',()=>{});child.stdin.end(prompt);
 child.on('error',()=>finish({state:'failed',error:'Configured runtime executable could not start.'}));child.on('exit',code=>{if(stopReason)return;try{process.kill(-child.pid,'SIGKILL');}catch{}clearTimeout(killTimer);finish({state:code===0?'awaiting_verification':'failed',error:code===0?null:'Runtime exited unsuccessfully.'});});
 timer=setTimeout(()=>stop('timed_out'),Math.max(1,deadlineAt-Date.now()-2000));
 }catch{finish({state:'failed',error:'Private runtime output could not be created.'});}
});
