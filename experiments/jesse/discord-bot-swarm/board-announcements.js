import crypto from 'node:crypto';
import {savedChat} from './chat-settings.js';

const MAX_ATTEMPTS=5,RETRY_SECONDS=30;
const clip=(text,max)=>{const flat=String(text||'').replace(/\s+/gu,' ').trim();return flat.length>max?flat.slice(0,max-1).trimEnd()+'…':flat;};

export function announcementText(action,task,origin){
 const title=`“${clip(task.title,120)}”`,note=clip(task.note,200),board=`<${new URL('/board.html',origin).href}>`;
 const line={
  created:`Added task ${title} to the board`,
  claim:`Claimed ${title}`,
  release:`Released ${title} back to the queue`,
  blocked:`Blocked on ${title}${note?': '+note:''}`,
  done:`Finished ${title}${note?': '+note:''}`,
 }[action];
 if(!line)throw Error(`Unknown board announcement action: ${action}`);
 return `${line} ${board}`;
}

export const announcementNonce=seq=>BigInt('0x'+crypto.createHash('sha256').update(`board-event:${seq}`).digest('hex').slice(0,20)).toString();

// Delivers pending board announcements in event order per relay; Discord's enforced nonce makes retries within its window exact.
export async function deliverAnnouncements(pool,relay,origin,{limit=20,onError=()=>{}}={}){
 const rows=(await pool.query(`SELECT e.seq,e.payload,e.announce_action,e.announce_attempts,e.announce_relay,s.owner,s.config,
  (e.announce_tried_at IS NULL OR e.announce_tried_at<now()-make_interval(secs=>$1*e.announce_attempts)) AS ready
  FROM kanban_events e LEFT JOIN swarms s ON s.id=e.announce_relay WHERE e.announce_state='pending' ORDER BY e.seq LIMIT $2`,[RETRY_SECONDS,limit])).rows;
 const waiting=new Set();
 for(const e of rows){
  if(waiting.has(e.announce_relay))continue;
  if(!e.ready){waiting.add(e.announce_relay);continue;}
  const settle=(state,receipt,error)=>pool.query('UPDATE kanban_events SET announce_state=$2,announce_receipt=$3,announce_error=$4,announce_tried_at=now() WHERE seq=$1',[e.seq,state,receipt,error]);
  if(!e.config){await settle('failed',null,'Relay no longer exists.');continue;}
  if(savedChat(e.config).mode==='off'){await settle('skipped',null,'Owner chat mode is Off.');continue;}
  try{
   const posted=await relay.post({swarm:e.announce_relay,owner:e.owner},announcementText(e.announce_action,e.payload.task,origin),announcementNonce(e.seq),AbortSignal.timeout(20000));
   if(!/^\d{17,20}$/.test(posted?.id||''))throw Error('Discord did not return a valid message receipt.');
   await settle('posted',posted.id,null);
  }catch(error){
   const attempts=e.announce_attempts+1;waiting.add(e.announce_relay);
   await pool.query('UPDATE kanban_events SET announce_attempts=$2,announce_tried_at=now(),announce_error=$3,announce_state=$4 WHERE seq=$1',[e.seq,attempts,clip(error.message,500),attempts>=MAX_ATTEMPTS?'failed':'pending']);
   onError(Object.assign(Error(`Board event ${e.seq} attempt ${attempts}: ${error.message}`),{cause:error}));
  }
 }
 return rows.length;
}

export function startBoardAnnouncements(pool,relay,{origin,intervalMs=5000,onError=()=>{}}){
 let busy=false;
 const timer=setInterval(async()=>{if(busy)return;busy=true;try{await deliverAnnouncements(pool,relay,origin,{onError});}catch(e){onError(e);}finally{busy=false;}},intervalMs);
 timer.unref();return ()=>clearInterval(timer);
}
