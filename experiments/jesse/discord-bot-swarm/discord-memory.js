// Channel evidence is shared only within one authenticated owner account.
export async function memorySchema(pool){await pool.query(`CREATE TABLE IF NOT EXISTS discord_messages(
 owner text NOT NULL,guild_id text NOT NULL,channel_id text NOT NULL,id text NOT NULL,
 author jsonb NOT NULL,content text NOT NULL,sent_at timestamptz NOT NULL,collected_at timestamptz NOT NULL DEFAULT now(),
 PRIMARY KEY(owner,channel_id,id));
 CREATE TABLE IF NOT EXISTS discord_collection_status(owner text NOT NULL,channel_id text NOT NULL,state text NOT NULL,updated_at timestamptz NOT NULL DEFAULT now(),error text,PRIMARY KEY(owner,channel_id));
 CREATE INDEX IF NOT EXISTS discord_message_search ON discord_messages USING gin(to_tsvector('simple',content));`);}
export class DiscordMemory{
 constructor(pool){this.pool=pool;}
 async save(owner,cfg,messages){
  if(!messages.length)return;
  // One statement makes each fetched page atomic, including exact retries.
  await this.pool.query(`INSERT INTO discord_messages(owner,guild_id,channel_id,id,author,content,sent_at)
 SELECT $1,$2,$3,m.id,m.author,m.content,m.timestamp::timestamptz FROM jsonb_to_recordset($4::jsonb) AS m(id text,author jsonb,content text,timestamp text)
 ON CONFLICT(owner,channel_id,id) DO UPDATE SET author=excluded.author,content=excluded.content,sent_at=excluded.sent_at,collected_at=now()`,[owner,cfg.guildId,cfg.channelId,JSON.stringify(messages)]);
 }
 async status(owner,channel,state,error=null){await this.pool.query(`INSERT INTO discord_collection_status(owner,channel_id,state,error) VALUES($1,$2,$3,$4) ON CONFLICT(owner,channel_id) DO UPDATE SET state=excluded.state,error=excluded.error,updated_at=now()`,[owner,channel,state,error]);}
 async latest(owner,channel){return (await this.pool.query('SELECT id FROM discord_messages WHERE owner=$1 AND channel_id=$2 ORDER BY id::numeric DESC LIMIT 1',[owner,channel])).rows[0]?.id;}
 async search(owner,cfg,query,limit){
  if(typeof query!=='string'||!query.trim()||query.length>500||!Number.isInteger(limit)||limit<1||limit>100)throw Error('Search requires 1–500 characters and a limit of 1–100.');
  const rows=(await this.pool.query(`SELECT id,author,content,sent_at AS timestamp,collected_at FROM discord_messages
 WHERE owner=$1 AND guild_id=$2 AND channel_id=$3 AND to_tsvector('simple',content) @@ plainto_tsquery('simple',$4)
 ORDER BY ts_rank(to_tsvector('simple',content),plainto_tsquery('simple',$4)) DESC,sent_at DESC,id::numeric DESC LIMIT $5`,[owner,cfg.guildId,cfg.channelId,query,limit])).rows;
  const collection=(await this.pool.query('SELECT state,updated_at,error FROM discord_collection_status WHERE owner=$1 AND channel_id=$2',[owner,cfg.channelId])).rows[0]||{state:'not_collected'};
  if(collection.state==='running'&&Date.now()-Date.parse(collection.updated_at)>30000){collection.state='stalled';collection.error='Collection did not finish within its deadline; the next collection will retry.';}
  return {collection,messages:rows.map(m=>({...m,url:`https://discord.com/channels/${cfg.guildId}/${cfg.channelId}/${m.id}`})),untrusted:true,scope:'owner/channel',coverage:'Collected pages only; not a complete or live Discord archive. Deleted messages may remain until refreshed.'};
 }
}
// One relay per tick, no overlap, no model calls, and a finite external deadline.
export function startCollection(pool,relay,{intervalMs=10000,onError=()=>{}}={}){
 let stopped=false,busy=false,cursor='';
 const tick=async()=>{if(stopped||busy)return;busy=true;try{
  const row=(await pool.query(`SELECT s.id,s.owner,s.config FROM swarms s WHERE s.id::text>$1 AND EXISTS(SELECT 1 FROM bots b WHERE b.swarm=s.id) AND coalesce(s.config->>'channelId','')<>'' ORDER BY s.id LIMIT 1`,[cursor])).rows[0];
  if(!row){cursor='';return;}cursor=row.id;
  await relay.collect({swarm:row.id,owner:row.owner},undefined,100,AbortSignal.timeout(20000));
 }catch(e){onError(e);}finally{busy=false;}};
 const timer=setInterval(tick,intervalMs);timer.unref();return ()=>{stopped=true;clearInterval(timer);};
}
