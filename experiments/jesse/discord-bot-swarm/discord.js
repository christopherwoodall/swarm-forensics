import {Client,GatewayIntentBits,PermissionFlagsBits} from 'discord.js';
import {request} from './core.js';
export async function discordIdentity(token){
 const bot=await request('https://discord.com/api/v10/users/@me',{headers:{Authorization:`Bot ${token}`}});
 if(!bot.bot)throw Error('Use a bot token, never a personal account token.');
 const application=await request('https://discord.com/api/v10/oauth2/applications/@me',{headers:{Authorization:`Bot ${token}`}});
 if(application.id!==bot.id)throw Error('Application identity mismatch.');
 return {id:bot.id,name:bot.username,inviteUrl:`https://discord.com/oauth2/authorize?client_id=${bot.id}&permissions=68608&scope=bot`};
}
export class DiscordRelay{
 constructor(pool,vault,{clientFactory=options=>new Client(options)}={}){this.pool=pool;this.vault=vault;this.clientFactory=clientFactory;}
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
 await this.pool.query('UPDATE bots SET name=$1 WHERE swarm=$2 AND bot_id=$3',[user.username,run.swarm,user.id]);
 return {id:user.id,username:user.username,avatarUrl:user.avatar?`https://cdn.discordapp.com/avatars/${user.id}/${user.avatar}.png`:null};
 }
 async check(swarm){const row=(await this.pool.query('SELECT * FROM swarms WHERE id=$1',[swarm])).rows[0];if(!row)throw Error('Relay not found.');if(!row.config.guildId||!row.config.channelId)throw Error('Complete channel setup before using this bot.');const {b,token}=await this.bot(swarm);const client=this.clientFactory({intents:[GatewayIntentBits.Guilds],rest:{timeout:10000,retries:0},ws:{handshakeTimeout:10000}});let timer;try{await Promise.race([client.login(token),new Promise((_,reject)=>{timer=setTimeout(()=>reject(Error('Discord login timed out.')),15000);})]);const channel=await client.channels.fetch(row.config.channelId);if(!channel||channel.guildId!==row.config.guildId||channel.type!==0)throw Error('Select a text channel in the configured server.');if(!channel.permissionsFor(client.user)?.has([PermissionFlagsBits.ViewChannel,PermissionFlagsBits.SendMessages,PermissionFlagsBits.ReadMessageHistory]))throw Error('Relay needs View Channel, Send Messages and Read Message History.');return {bot:b.name,channel:channel.name,permissions:'verified'};}finally{clearTimeout(timer);client.destroy();}}
 async channel(run,signal){const {token}=await this.bot(run.swarm);const cfg=(await this.pool.query('SELECT config FROM swarms WHERE id=$1 AND owner=$2',[run.swarm,run.owner])).rows[0]?.config;if(!cfg)throw Error('Relay unavailable.');if(!cfg.guildId||!cfg.channelId)throw Error('Complete channel setup before using this bot.');const channel=await request(`https://discord.com/api/v10/channels/${cfg.channelId}`,{headers:{Authorization:`Bot ${token}`},signal});if(channel.type!==0||channel.guild_id!==cfg.guildId)throw Error('Select a text channel in the configured server.');return {token,cfg};}
 async messages(run,after,limit,signal){const {token,cfg}=await this.channel(run,signal);const query=new URLSearchParams({limit:String(limit),...(after?{after}:{})});const rows=await request(`https://discord.com/api/v10/channels/${cfg.channelId}/messages?${query}`,{headers:{Authorization:`Bot ${token}`},method:'GET',signal});return {messages:rows.map(m=>({id:m.id,author:{id:m.author.id,name:m.author.username,bot:!!m.author.bot},content:m.content,timestamp:m.timestamp})).sort((a,b)=>BigInt(a.id)<BigInt(b.id)?-1:1),untrusted:true};}
 async post(run,message,nonce,signal){const {token,cfg}=await this.channel(run,signal);
 return request(`https://discord.com/api/v10/channels/${cfg.channelId}/messages`,{headers:{Authorization:`Bot ${token}`},body:{content:message,nonce,enforce_nonce:true,allowed_mentions:{parse:[]}},signal});}
}
// This collector has only fixed-channel GET access and no posting operation.
export class DiscordCapture{
 constructor(pool,vault){this.pool=pool;this.vault=vault;}
 async read(run,id,signal){if(!/^\d{17,20}$/.test(id||''))throw Error('Invalid Discord delivery receipt.');const cfg=(await this.pool.query('SELECT config FROM swarms WHERE id=$1 AND owner=$2',[run.swarm,run.owner])).rows[0]?.config;const b=(await this.pool.query('SELECT secret FROM bots WHERE swarm=$1 ORDER BY position LIMIT 1',[run.swarm])).rows[0];if(!cfg||!b)throw Error('Capture unavailable.');return request(`https://discord.com/api/v10/channels/${cfg.channelId}/messages/${id}`,{headers:{Authorization:`Bot ${await this.vault.decrypt(run.owner,`discord:${run.swarm}`,b.secret)}`},method:'GET',signal});}
}
