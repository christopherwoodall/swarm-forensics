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
