import {Client,GatewayIntentBits,PermissionFlagsBits} from 'discord.js';
import crypto from 'node:crypto';
import {request} from './core.js';
import {DiscordMemory} from './discord-memory.js';
import {DiscordMessageView} from './discord-message-view.js';
export class DiscordMessageContentError extends Error{constructor(applicationId){if(!/^\d{17,20}$/.test(applicationId))throw Error('Invalid Discord application identity.');super(`Discord Message Content Intent is disabled. Other users’ message text is hidden, so swarm coordination cannot read their work. Enable Message Content Intent on the Bot page at https://discord.com/developers/applications/${applicationId}/bot then retry.`);}}
export async function discordIdentity(token){
 const bot=await request('https://discord.com/api/v10/users/@me',{headers:{Authorization:`Bot ${token}`}});
 if(!bot.bot)throw Error('Use a bot token, never a personal account token.');
 const application=await request('https://discord.com/api/v10/oauth2/applications/@me',{headers:{Authorization:`Bot ${token}`}});
 if(application.id!==bot.id)throw Error('Application identity mismatch.');
 return {id:bot.id,name:bot.username,inviteUrl:`https://discord.com/oauth2/authorize?client_id=${bot.id}&permissions=68608&scope=bot`};
}
export class DiscordRelay{
 constructor(pool,vault,{clientFactory=options=>new Client(options)}={}){this.pool=pool;this.vault=vault;this.clientFactory=clientFactory;this.memory=new DiscordMemory(pool);this.messageView=new DiscordMessageView(pool);}
 async bot(swarm){const owner=(await this.pool.query('SELECT owner FROM swarms WHERE id=$1',[swarm])).rows[0]?.owner;const b=(await this.pool.query('SELECT * FROM bots WHERE swarm=$1 ORDER BY position LIMIT 1',[swarm])).rows[0];if(!b)throw Error('Configure one Discord relay bot first.');return {b,token:await this.vault.decrypt(owner,`discord:${swarm}`,b.secret)};}
 async profile(run,changes,signal){
 const owned=(await this.pool.query('SELECT id FROM swarms WHERE id=$1 AND owner=$2',[run.swarm,run.owner])).rows[0];if(!owned)throw Error('Relay not found.');
 if(changes){
  const keys=Object.keys(changes);if(!keys.length||keys.some(k=>!['username','avatar'].includes(k)))throw Error('Specify username or avatar.');
  if(changes.username!==undefined&&(typeof changes.username!=='string'||changes.username.trim().length<2||changes.username.length>32))throw Error('Bot name must be 2–32 characters.');
  if(changes.avatar!==undefined&&changes.avatar!==null&&(typeof changes.avatar!=='string'||changes.avatar.length>350000||!/^data:image\/(png|jpeg);base64,[A-Za-z0-9+/]+={0,2}$/.test(changes.avatar)))throw Error('Avatar must be a PNG/JPEG base64 data URI up to 350000 characters, or null to clear.');
 }
 const {token,b}=await this.bot(run.swarm);
 const user=await request('https://discord.com/api/v10/users/@me',{headers:{Authorization:`Bot ${token}`},method:changes?'PATCH':'GET',body:changes,signal});
 if(user.id!==b.bot_id||!user.bot)throw Error('Discord bot identity mismatch.');
 if(changes)await this.pool.query('UPDATE bots SET name=$1 WHERE swarm=$2 AND bot_id=$3',[user.username,run.swarm,user.id]);
 return {id:user.id,username:user.username,avatarUrl:user.avatar?`https://cdn.discordapp.com/avatars/${user.id}/${user.avatar}.png`:null};
 }
 async discover(run,signal){
 const owned=(await this.pool.query('SELECT id FROM swarms WHERE id=$1 AND owner=$2',[run.swarm,run.owner])).rows[0];if(!owned)throw Error('Relay not found.');
 const {token}=await this.bot(run.swarm),client=this.clientFactory({intents:[GatewayIntentBits.Guilds],rest:{timeout:10000,retries:0},ws:{handshakeTimeout:10000}});
 const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),25000);const bounded=signal?AbortSignal.any([signal,controller.signal]):controller.signal;
 let abort;const cancelled=new Promise((_,reject)=>{abort=()=>reject(Error('Discord channel discovery timed out or was cancelled.'));bounded.addEventListener('abort',abort,{once:true});if(bounded.aborted)abort();});
 try{return await Promise.race([(async()=>{await client.login(token);const list=await client.guilds.fetch();if(list.size>25)throw Error('Channel discovery supports up to 25 servers per bot.');const guilds=[],channels=[];for(const entry of list.values()){if(run.guildId&&entry.id!==run.guildId)continue;if(bounded.aborted)throw Error('Discovery cancelled.');const guild=await client.guilds.fetch(entry.id);guilds.push({id:guild.id,name:guild.name});const rows=await guild.channels.fetch();for(const c of rows.values()){if(c?.type===0&&c.permissionsFor(client.user)?.has([PermissionFlagsBits.ViewChannel,PermissionFlagsBits.SendMessages,PermissionFlagsBits.ReadMessageHistory]))channels.push({id:c.id,name:c.name,guildId:guild.id,guildName:guild.name});}}const matches=channels.filter(c=>c.name.toLowerCase()==='swarm');return {guilds,channels,defaultChannel:matches.length===1?matches[0]:null,ambiguous:matches.length>1};})(),cancelled]);}finally{clearTimeout(timer);bounded.removeEventListener('abort',abort);client.destroy();}
 }
 async check(swarm){const row=(await this.pool.query('SELECT * FROM swarms WHERE id=$1',[swarm])).rows[0];if(!row)throw Error('Relay not found.');if(!row.config.guildId||!row.config.channelId)throw Error('Complete channel setup before using this bot.');const {b,token}=await this.bot(swarm);const client=this.clientFactory({intents:[GatewayIntentBits.Guilds],rest:{timeout:10000,retries:0},ws:{handshakeTimeout:10000}});let timer;try{await Promise.race([client.login(token),new Promise((_,reject)=>{timer=setTimeout(()=>reject(Error('Discord login timed out.')),15000);})]);const channel=await client.channels.fetch(row.config.channelId);if(!channel||channel.guildId!==row.config.guildId||channel.type!==0)throw Error('Select a text channel in the configured server.');if(!channel.permissionsFor(client.user)?.has([PermissionFlagsBits.ViewChannel,PermissionFlagsBits.SendMessages,PermissionFlagsBits.ReadMessageHistory]))throw Error('Relay needs View Channel, Send Messages and Read Message History.');return {bot:b.name,channel:channel.name,guildName:channel.guild?.name,permissions:'verified'};}finally{clearTimeout(timer);client.destroy();}}
 async channel(run,signal){const {token,b}=await this.bot(run.swarm);const cfg=(await this.pool.query('SELECT config FROM swarms WHERE id=$1 AND owner=$2',[run.swarm,run.owner])).rows[0]?.config;if(!cfg)throw Error('Relay unavailable.');if(!cfg.guildId||!cfg.channelId)throw Error('Complete channel setup before using this bot.');const channelId=run.channelId??cfg.channelId;if(run.channelId!==undefined&&!/^\d{17,20}$/.test(run.channelId))throw Error('Invalid Discord channel ID.');const channel=await request(`https://discord.com/api/v10/channels/${channelId}`,{headers:{Authorization:`Bot ${token}`},signal});if(channel.type!==0||channel.guild_id!==cfg.guildId)throw Error('Select a text channel in the configured server.');return {token,cfg:{...cfg,channelId,botId:b.bot_id}};}
 async fetchMessages(run,{after,before,limit},signal){const {token,cfg}=await this.channel(run,signal);const query=new URLSearchParams({limit:String(limit),...(after?{after}:{}),...(before?{before}:{})});const displayed=await request(`https://discord.com/api/v10/channels/${cfg.channelId}/messages?${query}`,{headers:{Authorization:`Bot ${token}`},method:'GET',signal});const rows=await this.messageView.restore({...run,channelId:cfg.channelId},displayed,cfg.botId);if(rows.some(m=>!m.content&&m.author?.id!==cfg.botId)){const application=await request('https://discord.com/api/v10/oauth2/applications/@me',{headers:{Authorization:`Bot ${token}`},method:'GET',signal});const flags=BigInt(application.flags_new??application.flags??0);if((flags&((1n<<18n)|(1n<<19n)))===0n)throw new DiscordMessageContentError(application.id);}const messages=rows.map(m=>({id:m.id,author:{id:m.author.id,name:m.author.username,bot:!!m.author.bot},content:m.content,...(m.preview!==undefined?{preview:m.preview}:{}),components:m.components||[],timestamp:m.timestamp,replyToBot:m.referenced_message?.author?.id===cfg.botId})).sort((a,b)=>BigInt(a.id)<BigInt(b.id)?-1:1);return {messages,untrusted:true};}
 async messages(run,after,limit,signal){return this.fetchMessages(run,{after,limit},signal);}
 async collect(run,before,limit,signal){const cfg=(await this.pool.query('SELECT config FROM swarms WHERE id=$1 AND owner=$2',[run.swarm,run.owner])).rows[0]?.config;if(!cfg)throw Error('Relay unavailable.');await this.memory.status(run.owner,cfg.channelId,'running');try{const after=before?undefined:await this.memory.latest(run.owner,cfg.channelId);const result=await this.fetchMessages(run,{before,after,limit},signal);await this.memory.save(run.owner,cfg,result.messages);await this.memory.status(run.owner,cfg.channelId,'completed');return {...result,state:'completed',collected:result.messages.length,nextBefore:result.messages[0]?.id||null,nextAfter:result.messages.at(-1)?.id||after||null};}catch(e){await this.memory.status(run.owner,cfg.channelId,signal?.aborted?'timed_out':'failed',e.message);throw e;}}
 async search(run,query,limit){const cfg=(await this.pool.query('SELECT config FROM swarms WHERE id=$1 AND owner=$2',[run.swarm,run.owner])).rows[0]?.config;if(!cfg)throw Error('Relay unavailable.');return this.memory.search(run.owner,cfg,query,limit);}
 async edit(run,messageId,content,signal){
 if(!/^\d{17,20}$/.test(messageId||'')||typeof content!=='string'||!content.trim()||content.length>2000)throw Error('Specify a Discord message ID and 1–2000 characters of content.');
 const {token,cfg}=await this.channel(run,signal),url=`https://discord.com/api/v10/channels/${cfg.channelId}/messages/${messageId}`,headers={Authorization:`Bot ${token}`};
 const previous=await request(url,{headers,method:'GET',signal});if(previous.author?.id!==cfg.botId)throw Error('Only this relay bot’s own messages can be edited.');
 const scoped={...run,channelId:cfg.channelId},nonce=BigInt('0x'+crypto.createHash('sha256').update(messageId+'\n'+content).digest('hex').slice(0,20)).toString();
 const view=await this.messagePayload(scoped,content,nonce);
 const edited=await request(url,{headers,method:'PATCH',body:{...view,components:view.components||[],allowed_mentions:{parse:[]}},signal});
 if(view.components)await this.messageView.delivered(run,nonce,messageId);
 await this.messageView.clear(scoped,messageId,view.components?nonce:null);return edited;
 }
 async messagePayload(run,content,nonce){return ['online','idle'].includes(this.presence?.status(run.swarm).state)?this.messageView.prepare(run,content,nonce):{content};}
 async post(run,message,nonce,signal){const {token,cfg}=await this.channel(run,signal);
 const view=await this.messagePayload({...run,channelId:cfg.channelId},message,nonce);
 const posted=await request(`https://discord.com/api/v10/channels/${cfg.channelId}/messages`,{headers:{Authorization:`Bot ${token}`},body:{...view,nonce,enforce_nonce:true,allowed_mentions:{parse:[]}},signal});
 if(view.components)await this.messageView.delivered(run,nonce,posted.id);return posted;}
}
// This collector has only fixed-channel GET access and no posting operation.
export class DiscordCapture{
 constructor(pool,vault){this.pool=pool;this.vault=vault;}
 async read(run,id,signal){if(!/^\d{17,20}$/.test(id||''))throw Error('Invalid Discord delivery receipt.');const cfg=(await this.pool.query('SELECT config FROM swarms WHERE id=$1 AND owner=$2',[run.swarm,run.owner])).rows[0]?.config;const b=(await this.pool.query('SELECT secret FROM bots WHERE swarm=$1 ORDER BY position LIMIT 1',[run.swarm])).rows[0];if(!cfg||!b)throw Error('Capture unavailable.');return request(`https://discord.com/api/v10/channels/${cfg.channelId}/messages/${id}`,{headers:{Authorization:`Bot ${await this.vault.decrypt(run.owner,`discord:${run.swarm}`,b.secret)}`},method:'GET',signal});}
}
