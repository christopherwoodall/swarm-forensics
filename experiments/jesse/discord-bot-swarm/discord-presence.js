import {Client,GatewayIntentBits} from 'discord.js';
import crypto from 'node:crypto';
export function presenceStatus(row){return row.config?.verifiedAt&&row.config?.chat?.mode!=='off'&&!['blocked','failed','paused','stopped','stalled'].includes(row.state)?'online':'idle';}
export class DiscordPresence{
 constructor(pool,relay,{clientFactory=options=>new Client(options),now=()=>Date.now(),loginTimeout=30000}={}){this.pool=pool;this.relay=relay;this.clientFactory=clientFactory;this.now=now;this.loginTimeout=loginTimeout;this.clients=new Map();this.errors=new Map();this.closed=false;}
 status(id){const entry=this.clients.get(id),error=this.errors.get(id);return {state:entry?.client.isReady()?entry.status:entry?'connecting':error?'failed':'offline',error:error?.message||null};}
 async sync(){if(this.closed)return;let rows;try{rows=(await this.pool.query({text:"SELECT s.id,s.config,CASE WHEN l.heartbeat_at IS NULL OR l.heartbeat_at<now()-interval '90 seconds' THEN 'stalled' ELSE l.state END AS state FROM discord_chat_listener l JOIN swarms s ON s.id=l.relay WHERE l.enabled=true",query_timeout:10000})).rows;}catch{for(const entry of this.clients.values()){entry.client.user?.setPresence({status:'idle'});entry.status='idle';}throw Error('Discord presence inventory unavailable.');}
 const wanted=new Set(rows.map(r=>r.id));for(const [id,entry] of this.clients){if(!wanted.has(id)){entry.client.destroy();this.clients.delete(id);this.errors.delete(id);}}
 for(const row of rows){if(this.closed)return;const previous=this.errors.get(row.id);if(previous?.retryAt>this.now())continue;let client,timer;try{
 const {token}=await this.relay.bot(row.id);const fingerprint=crypto.createHash('sha256').update(token).digest('hex'),status=presenceStatus(row);let entry=this.clients.get(row.id);
 if(entry&&entry.fingerprint!==fingerprint){entry.client.destroy();this.clients.delete(row.id);entry=null;}
 if(entry){if(!entry.client.isReady()&&this.now()-entry.connectedAt>60000){client=entry.client;throw Error('Gateway reconnect timed out');}if(entry.client.isReady()){if(entry.status!==status)entry.client.user.setPresence({status});entry.status=status;}continue;}
 client=this.clientFactory({intents:[GatewayIntentBits.Guilds],presence:{status},waitGuildTimeout:5000,rest:{timeout:10000,retries:0},ws:{handshakeTimeout:10000}});
 client.on('interactionCreate',interaction=>{void this.relay.messageView?.interaction(row.id,interaction).catch(()=>{});});
 client.on('error',()=>{this.errors.set(row.id,{message:'Discord Gateway connection failed.',retryAt:this.now()+60000});client.destroy();if(this.clients.get(row.id)?.client===client)this.clients.delete(row.id);});
 const ready=new Promise(resolve=>client.once('clientReady',resolve));this.clients.set(row.id,{client,status,fingerprint,connectedAt:this.now()});await Promise.race([(async()=>{await client.login(token);if(!client.isReady())await ready;})(),new Promise((_,reject)=>{timer=setTimeout(()=>reject(Error('timeout')),this.loginTimeout);})]);if(this.closed){client.destroy();this.clients.delete(row.id);return;}if(!client.isReady())throw Error('not ready');this.errors.delete(row.id);
 }catch{client?.destroy();this.clients.delete(row.id);this.errors.set(row.id,{message:'Discord Gateway login failed or timed out.',retryAt:this.now()+60000});}finally{clearTimeout(timer);}}
 }
 start(){let busy=false;const tick=async()=>{if(busy||this.closed)return;busy=true;try{await this.sync();}catch{}finally{busy=false;}};const timer=setInterval(tick,20000);timer.unref();void tick();return ()=>{this.closed=true;clearInterval(timer);for(const entry of this.clients.values())entry.client.destroy();this.clients.clear();};}
}
