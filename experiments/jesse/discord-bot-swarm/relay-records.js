import crypto from 'node:crypto';
// Verification creates a durable owner record before installation or channel setup.
export async function saveVerifiedBot(pool,vault,owner,identity,token){
 const client=await pool.connect();
 try{
  await client.query('BEGIN');
  await client.query('SELECT pg_advisory_xact_lock(hashtextextended($1,0))',[identity.id]);
  const existing=(await client.query('SELECT s.id,s.owner,s.config,b.name,b.bot_id FROM swarms s JOIN bots b ON b.swarm=s.id WHERE b.bot_id=$1',[identity.id])).rows[0];
  if(existing&&existing.owner!==owner)throw Object.assign(Error('This bot is already connected to another account.'),{status:409});
  let record;
  if(existing){
   const secret=await vault.encrypt(owner,`discord:${existing.id}`,token);
   await client.query('UPDATE bots SET secret=$1,name=$2 WHERE bot_id=$3',[secret,identity.name,identity.id]);
   record={id:existing.id,config:existing.config,bots:[{name:identity.name,bot_id:existing.bot_id}]};
  }
  else{
   const id=crypto.randomUUID(),config={name:identity.name,setupStage:'invite'};
   const secret=await vault.encrypt(owner,`discord:${id}`,token);
   await client.query('INSERT INTO swarms(id,owner,config) VALUES($1,$2,$3)',[id,owner,config]);
   await client.query('INSERT INTO bots VALUES($1,$2,$3,$4,$5,$6,$7)',[crypto.randomUUID(),id,identity.id,identity.name,'unassigned',secret,0]);
   record={id,config,bots:[{name:identity.name,bot_id:identity.id}]};
  }
  await client.query('COMMIT');return record;
 }catch(e){await client.query('ROLLBACK');throw e;}finally{client.release();}
}

export async function announceJoined(pool,relay,owner,id,origin){
 const client=await pool.connect();
 try{
  await client.query('BEGIN');await client.query("SET LOCAL lock_timeout='5s'");
  const row=(await client.query('SELECT config FROM swarms WHERE id=$1 AND owner=$2 FOR UPDATE',[id,owner])).rows[0];
  if(!row)throw Error('Relay not found.');
  if(row.config.joinAnnouncement?.channelId===row.config.channelId){await client.query('COMMIT');return row.config.joinAnnouncement;}
  const content=`I have joined the swarm!\nConnect your own bot to the swarm! Go to: ${new URL('/',origin).href}\nKanban Board: ${new URL('/board.html',origin).href}`;
  const nonce=BigInt('0x'+crypto.createHash('sha256').update(`join:${id}:${row.config.channelId}`).digest('hex').slice(0,20)).toString();
  const receipt=await relay.post({swarm:id,owner},content,nonce,AbortSignal.timeout(20000));
  if(!/^\d{17,20}$/.test(receipt?.id||''))throw Error('Discord did not return a valid welcome message receipt.');
  const announcement={channelId:row.config.channelId,messageId:receipt.id,at:new Date().toISOString()};
  await client.query('UPDATE swarms SET config=config||$1::jsonb WHERE id=$2 AND owner=$3',[JSON.stringify({joinAnnouncement:announcement}),id,owner]);
  await client.query('COMMIT');return announcement;
 }catch(e){await client.query('ROLLBACK');throw Error('Welcome announcement failed: '+e.message);}finally{client.release();}
}
