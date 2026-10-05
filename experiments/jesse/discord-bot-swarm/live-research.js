import crypto from 'node:crypto';
import {z} from 'zod';
import {traceHash} from './research.js';
const fail=(message,status=400)=>{throw Object.assign(Error(message),{status});};
const cursor=z.string().regex(/^(0|[1-9][0-9]{0,18})$/);
export const reportInput=z.object({eventId:z.string().regex(/^[\w-]{16,128}$/),type:z.enum(['turn','tool_call','artifact','annotation']),source:z.string().trim().min(1).max(120),sourceTime:z.string().datetime({offset:true}),sessionId:z.string().trim().min(1).max(160),turnId:z.string().max(160).optional(),sourceRefs:z.array(cursor).max(50).default([]),data:z.record(z.string(),z.unknown())}).strict();
export const exportInput=z.object({after:cursor.default('0'),through:cursor.optional(),limit:z.number().int().min(1).max(200).default(100)}).strict();
// Redact known credential fields and formats; retain markers for evaluation.
export function sanitize(value){
 if(value instanceof Date)return value.toISOString();
 if(Array.isArray(value))return value.map(sanitize);
 if(value&&typeof value==='object')return Object.fromEntries(Object.entries(value).map(([k,v])=>[k,/^(?:(?:access|refresh|id|bot|callback|bearer)[_-]?)?token$|secret|password|authorization|api.?key|credential|cookie/i.test(k)?'[redacted]':sanitize(v)]));
 if(typeof value==='string')return value.replace(/Bearer\s+[^\s"<>]+/gi,'Bearer [redacted]').replace(/(?:swarm_agent_|fs_agent_|fs_cap_)[A-Za-z0-9_-]+/g,'[redacted]').replace(/([?&](?:token|key|secret|password|credential|code)=)[^&#\s]+/gi,'$1[redacted]').replace(/data:image\/[^;]+;base64,[A-Za-z0-9+/=]+/g,'[image omitted]');
 return value;
}
export function capture(value,maxBytes=12000){const safe=sanitize(value),raw=JSON.stringify(safe);return Buffer.byteLength(raw)>maxBytes?{omitted:true,reason:`Capture exceeds ${maxBytes} bytes`,sha256:crypto.createHash('sha256').update(raw).digest('hex'),bytes:Buffer.byteLength(raw)}:safe;}
export async function liveResearchSchema(pool){await pool.query(`
 CREATE TABLE IF NOT EXISTS research_installation(id integer PRIMARY KEY CHECK(id=1),installed_at timestamptz NOT NULL DEFAULT now());
 INSERT INTO research_installation(id) VALUES(1) ON CONFLICT DO NOTHING;
 CREATE TABLE IF NOT EXISTS research_streams(owner text NOT NULL,actor text NOT NULL,seq integer NOT NULL DEFAULT 0,head text NOT NULL DEFAULT '',PRIMARY KEY(owner,actor));
 CREATE TABLE IF NOT EXISTS research_events(id bigserial PRIMARY KEY,owner text NOT NULL,actor text NOT NULL,seq integer NOT NULL,event_key text NOT NULL,input_hash text NOT NULL,raw text NOT NULL,previous text NOT NULL,hash text NOT NULL,UNIQUE(owner,actor,seq),UNIQUE(owner,actor,event_key));
 CREATE INDEX IF NOT EXISTS research_owner_cursor ON research_events(owner,id);
 CREATE OR REPLACE FUNCTION research_immutable() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN RAISE EXCEPTION 'Research events are append-only'; END $$;
 DROP TRIGGER IF EXISTS immutable_research ON research_events;
 CREATE TRIGGER immutable_research BEFORE UPDATE OR DELETE ON research_events FOR EACH ROW EXECUTE FUNCTION research_immutable();
 `);}
export class LiveResearch{
 constructor(pool,{version}={}){this.pool=pool;this.version=version||'unknown';}
 actor(p){return p.kind==='agent'?p.actor:'owner:'+p.owner;}
 async append(p,key,event){
 const safe=sanitize(event),inputHash=crypto.createHash('sha256').update(JSON.stringify(safe)).digest('hex');
 const c=await this.pool.connect(),actor=this.actor(p);
 try{await c.query('BEGIN');await c.query("SET LOCAL lock_timeout='3s'");await c.query('INSERT INTO research_streams(owner,actor) VALUES($1,$2) ON CONFLICT DO NOTHING',[p.owner,actor]);const stream=(await c.query('SELECT seq,head FROM research_streams WHERE owner=$1 AND actor=$2 FOR UPDATE',[p.owner,actor])).rows[0];
 const prior=(await c.query('SELECT id,input_hash,raw,previous,hash FROM research_events WHERE owner=$1 AND actor=$2 AND event_key=$3',[p.owner,actor,key])).rows[0];if(prior){if(prior.input_hash!==inputHash)fail('Event ID already used with different input.',409);await c.query('COMMIT');return this.decode(prior);}
 for(const ref of safe.sourceRefs||[]){const r=await c.query('SELECT id FROM research_events WHERE id=$1 AND owner=$2 AND ($3::text IS NULL OR actor=$3)',[ref,p.owner,p.kind==='agent'?actor:null]);if(!r.rowCount)fail('Source reference not found in your research scope.',403);}
 const raw=JSON.stringify({schemaVersion:1,seq:stream.seq+1,recordedAt:new Date().toISOString(),actor,relayId:p.relayId||null,softwareVersion:this.version,...safe}),hash=traceHash(stream.head,raw);
 const row=(await c.query('INSERT INTO research_events(owner,actor,seq,event_key,input_hash,raw,previous,hash) VALUES($1,$2,$3,$4,$5,$6,$7,$8) RETURNING id,raw,previous,hash',[p.owner,actor,stream.seq+1,key,inputHash,raw,stream.head,hash])).rows[0];await c.query('UPDATE research_streams SET seq=$3,head=$4 WHERE owner=$1 AND actor=$2',[p.owner,actor,stream.seq+1,hash]);await c.query('COMMIT');return this.decode(row);
 }catch(e){await c.query('ROLLBACK');throw e;}finally{c.release();}
 }
 decode(row){return {id:String(row.id),...JSON.parse(row.raw),raw:row.raw,previous:row.previous,hash:row.hash};}
 async report(p,input){const a=reportInput.parse(input);if(Buffer.byteLength(JSON.stringify(a.data))>24000)fail('Research data exceeds 24000 bytes.');return this.append(p,a.eventId,{...a,provenance:'runtime-reported',verification:'Authenticated submitter; runtime contents and source time are not independently verified.'});}
 async start(p,name,input){const callId=crypto.randomUUID();const e=await this.append(p,callId+'-start',{type:'tool_call',source:'swarm-agent-api',provenance:'server-observed',callId,operation:name,state:'running',deadlineAt:new Date(Date.now()+25000).toISOString(),sourceTime:new Date().toISOString(),data:{input:capture(input)}});return {callId,id:e.id};}
 async finish(p,call,name,result,error){return this.append(p,call.callId+'-finish',{type:'tool_call',source:'swarm-agent-api',provenance:'server-observed',callId:call.callId,operation:name,state:error?'failed':'completed',sourceTime:new Date().toISOString(),sourceRefs:[call.id],data:error?{error:error.status?error.message:'Operation failed.',status:error.status||503}:{result:capture(result)}});}
 async listenerJobs(){
 const deadline=Date.now()+15000;
 const rows=(await this.pool.query(`SELECT j.id,j.relay,j.state,j.created_at,j.deadline_at,j.finished_at,j.session_id,j.channel_id,j.message_id,j.messages,j.content,j.message_receipt,j.error,j.self_change_receipt,j.context,j.allowed_work,s.owner FROM discord_chat_job j JOIN swarms s ON s.id=j.relay WHERE j.created_at>=(SELECT installed_at FROM research_installation WHERE id=1) AND NOT EXISTS(SELECT 1 FROM research_events e WHERE e.owner=s.owner AND e.actor='listener:'||j.relay::text AND e.event_key=j.id::text||'-'||j.state) ORDER BY j.created_at LIMIT 50`)).rows;
 for(const j of rows){if(Date.now()>=deadline)break;await this.append({owner:j.owner,kind:'agent',actor:'listener:'+j.relay,relayId:j.relay},j.id+'-'+j.state,{type:'turn',source:'swarm-chat-listener',provenance:'server-observed',sessionId:j.session_id,turnId:j.id,sourceTime:new Date(j.finished_at||j.created_at).toISOString(),state:j.state,data:{channelId:j.channel_id,triggerMessageId:j.message_id,createdAt:j.created_at,deadlineAt:j.deadline_at,finishedAt:j.finished_at,input:capture(j.context||j.messages,24000),workDelegated:j.allowed_work,output:j.content,messageReceipt:j.message_receipt,error:j.error,selfChangeReceipt:j.self_change_receipt}});}
 }
 async export(p,input={}){const a=exportInput.parse(input),actor=p.kind==='agent'?this.actor(p):null;
 const high=(await this.pool.query('SELECT COALESCE(max(id),0)::text AS id FROM research_events WHERE owner=$1 AND ($2::text IS NULL OR actor=$2)',[p.owner,actor])).rows[0].id;
 const through=a.through||high;if(BigInt(through)>BigInt(high))fail('Export snapshot exceeds your current research cursor.');
 const rows=(await this.pool.query('SELECT id,raw,previous,hash FROM research_events WHERE owner=$1 AND ($2::text IS NULL OR actor=$2) AND id>$3 AND id<=$4 ORDER BY id LIMIT $5',[p.owner,actor,a.after,through,a.limit+1])).rows;
 const events=rows.slice(0,a.limit).map(r=>{if(traceHash(r.previous,r.raw)!==r.hash)fail('Research integrity check failed.',503);return this.decode(r);});
 return {schemaVersion:1,exportedAt:new Date().toISOString(),scope:p.kind==='agent'?'authenticated-agent':'authenticated-owner',coverage:{automatic:'Authenticated Swarm agent API operation attempts (except research ingestion/export controls) and observed chat-listener turn states since research recording was installed.',reported:'External runtime turns, other tools and artifacts require research_record_event. No historical backfill or access to private runtime traces.',pending:'A running call with no outcome has an unknown outcome; process interruption is not success.',redaction:'Credential fields and recognized credential strings redacted; large automatic payloads represented by a content hash.'},events,nextCursor:events.at(-1)?.id||a.after,through,hasMore:rows.length>a.limit};
 }
}
export function registerResearchOperations(operations,research,p){
 operations.registerOperation('research_record_event',{description:'Append a timestamped external runtime turn, tool call, artifact or annotation. Reuse eventId for exact retries. Submit only shareable evidence, never credentials. Runtime reports are not server-verified execution.',inputSchema:reportInput.shape},a=>research.report(p,a));
 operations.registerOperation('research_export',{annotations:{readOnlyHint:true},description:'Export a bounded JSON research page. Keep through fixed and follow nextCursor while hasMore. Agent keys see only their own journal; owners see their own agents. No cross-owner disclosure.',inputSchema:exportInput.shape},a=>research.export(p,a));
}
