import {MessageFlags} from 'discord.js';

const prefix='swarm:expand:';
export const COLLAPSE_CHARACTERS=700;
export function messagePreview(content){
 if(content.length<=COLLAPSE_CHARACTERS&&content.split('\n').length<=12)return null;
 const paragraph=content.split(/\n\s*\n/)[0];
 let preview=paragraph.slice(0,350);
 if(preview.length<paragraph.length){const boundary=preview.lastIndexOf(' ');if(boundary>200)preview=preview.slice(0,boundary);}
 // Avoid cutting a surrogate pair or leaving a preview's code fence open.
 preview=preview.replace(/[\uD800-\uDBFF]$/,'').trimEnd();
 if((preview.match(/```/g)||[]).length%2)preview+='\n```';
 return preview+'\n…';
}

export async function messageViewSchema(pool){await pool.query(`CREATE TABLE IF NOT EXISTS discord_message_view(
 relay uuid NOT NULL REFERENCES swarms ON DELETE CASCADE,nonce text NOT NULL,channel_id text NOT NULL,
 message_id text,content text NOT NULL CHECK(length(content)<=2000),created_at timestamptz NOT NULL DEFAULT now(),
 PRIMARY KEY(relay,nonce));`);}

export class DiscordMessageView{
 constructor(pool){this.pool=pool;}
 async prepare(run,content,nonce){
 const preview=messagePreview(content);if(!preview)return {content};
 if(!/^\d{1,25}$/.test(nonce))throw Error('Expandable messages require a stable numeric nonce.');
 const result=await this.pool.query({text:`INSERT INTO discord_message_view(relay,nonce,channel_id,content) VALUES($1,$2,$3,$4)
 ON CONFLICT(relay,nonce) DO UPDATE SET nonce=excluded.nonce
 WHERE discord_message_view.channel_id=excluded.channel_id AND discord_message_view.content=excluded.content RETURNING nonce`,
 values:[run.swarm,nonce,run.channelId,content],query_timeout:3000});
 if(!result.rows.length)throw Error('Message nonce already belongs to different content or channel.');
 return {content:preview,components:[{type:1,components:[{type:2,style:2,label:'Show more',custom_id:prefix+nonce}]}]};
 }
 async delivered(run,nonce,id){await this.pool.query({text:'UPDATE discord_message_view SET message_id=$3 WHERE relay=$1 AND nonce=$2 AND (message_id IS NULL OR message_id=$3)',values:[run.swarm,nonce,id],query_timeout:3000});}
 async clear(run,id,keepNonce=null){await this.pool.query({text:'DELETE FROM discord_message_view WHERE relay=$1 AND channel_id=$2 AND message_id=$3 AND ($4::text IS NULL OR nonce<>$4)',values:[run.swarm,run.channelId,id,keepNonce],query_timeout:3000});}
 async restore(run,messages,botId){
 const ids=messages.filter(m=>m.author?.id===botId).map(m=>m.id);if(!ids.length)return messages;
 const rows=(await this.pool.query({text:'SELECT message_id,content,nonce FROM discord_message_view WHERE relay=$1 AND channel_id=$2 AND message_id=ANY($3::text[])',values:[run.swarm,run.channelId,ids],query_timeout:3000})).rows;
 const saved=new Map(rows.map(r=>[r.message_id,r]));
 return messages.map(m=>{const row=saved.get(m.id);return row&&m.author?.id===botId&&m.components?.some(c=>c.components?.some(b=>b.custom_id===prefix+row.nonce))?{...m,preview:m.content,content:row.content}:m;});
 }
 async interaction(relay,interaction){
 if(!interaction.isButton()||!interaction.customId.startsWith(prefix))return;
 const nonce=interaction.customId.slice(prefix.length);
 // Acknowledge before database access; expansion never changes the public message.
 try{await interaction.deferReply({flags:MessageFlags.Ephemeral});}catch{return;}
 let content='This message is no longer available.';
 try{
 if(/^\d{1,25}$/.test(nonce)&&interaction.guildId&&interaction.message?.author?.id===interaction.client.user.id){
 const row=(await this.pool.query({text:`SELECT v.content FROM discord_message_view v
 JOIN swarms s ON s.id=v.relay JOIN bots b ON b.swarm=s.id JOIN discord_chat_listener l ON l.relay=s.id
 WHERE v.relay=$1 AND v.nonce=$2 AND v.channel_id=$3 AND v.message_id=$4
 AND s.config->>'guildId'=$5 AND b.bot_id=$6 AND l.enabled=true`,
 values:[relay,nonce,interaction.channelId,interaction.message.id,interaction.guildId,interaction.client.user.id],query_timeout:3000})).rows[0];
 if(row)content=row.content;
 }
 }catch{content='Could not open this message. Try again.';}
 try{await interaction.editReply({content,allowedMentions:{parse:[]}});}catch{}
 }
}
