import crypto from 'node:crypto';
import {z} from 'zod';
const hash=value=>crypto.createHash('sha256').update(value).digest('hex');
const fail=(message,status=401)=>{throw Object.assign(Error(message),{status});};
export async function setupCredentialSchema(pool){await pool.query(`
DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='kanban_agent_relay_fk' AND conrelid='kanban_agents'::regclass) THEN ALTER TABLE kanban_agents ADD CONSTRAINT kanban_agent_relay_fk FOREIGN KEY(relay_id) REFERENCES swarms(id) ON DELETE CASCADE; END IF; END $$;
CREATE TABLE IF NOT EXISTS mcp_setup_tokens(token_hash text PRIMARY KEY,owner text NOT NULL,relay_id uuid NOT NULL REFERENCES swarms(id) ON DELETE CASCADE,expires_at timestamptz NOT NULL,consumed_at timestamptz,created_at timestamptz NOT NULL DEFAULT now());
`);}
export class SetupCredentials{
 constructor(pool){this.pool=pool;}
 async issue(owner,relayId){
  relayId=z.string().uuid().parse(relayId);
  const token='swarm_setup_'+crypto.randomBytes(32).toString('base64url');
  const r=await this.pool.query(`INSERT INTO mcp_setup_tokens(token_hash,owner,relay_id,expires_at) SELECT $1,owner,id,now()+interval '10 minutes' FROM swarms WHERE id=$2 AND owner=$3 AND config->>'verifiedAt' IS NOT NULL RETURNING expires_at`,[hash(token),relayId,owner]);
  if(!r.rows[0])fail('Verified relay not found.',404);
  return {token,expires_at:r.rows[0].expires_at,relayId};
 }
 async exchange(token,input={}){
  if(typeof token!=='string'||!/^swarm_setup_[A-Za-z0-9_-]{43}$/.test(token))fail('Setup token expired, already used or invalid. Copy a fresh prompt.');
  const {name}=z.object({name:z.string().trim().min(1).max(80).default('Connected coding agent')}).strict().parse(input);
  const c=await this.pool.connect();try{
   await c.query('BEGIN');await c.query("SET LOCAL lock_timeout='3s'");
   const r=await c.query(`UPDATE mcp_setup_tokens SET consumed_at=now() WHERE token_hash=$1 AND consumed_at IS NULL AND expires_at>now() RETURNING owner,relay_id`,[hash(token)]);
   if(!r.rows[0])fail('Setup token expired, already used or invalid. Copy a fresh prompt.');
   const {owner,relay_id}=r.rows[0],id=crypto.randomUUID(),credential='swarm_agent_'+crypto.randomBytes(32).toString('base64url');
   const a=await c.query(`INSERT INTO kanban_agents(id,owner,name,token_hash,expires_at,relay_id) VALUES($1,$2,$3,$4,now()+interval '7 days',$5) RETURNING id,expires_at`,[id,owner,name,hash(credential),relay_id]);
   await c.query('COMMIT');return {credential,credentialId:id,relayId:relay_id,expires_at:a.rows[0].expires_at};
  }catch(e){await c.query('ROLLBACK');throw e;}finally{c.release();}
 }
}
export function setupExchangeHandler(setup,publicOrigin){return async(req,res)=>{
 if(req.headers.origin&&req.headers.origin!==publicOrigin)return res.status(403).json({error:'Untrusted request origin.'});
 try{const token=req.headers.authorization?.match(/^Bearer (.+)$/)?.[1];return res.json(await setup.exchange(token,req.body));}
 catch(e){return res.status(e instanceof z.ZodError?400:e.status||503).json({error:e instanceof z.ZodError?'Invalid agent name.':e.status?e.message:'Credential exchange unavailable. Copy a fresh prompt before retrying.'});}
};}
