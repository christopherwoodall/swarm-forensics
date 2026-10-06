import crypto from 'node:crypto';
export const idPattern = /^\d{17,20}$/;
export function text(value, name, max=200) { if(typeof value !== 'string' || !value.trim() || value.length>max) throw new Error(`${name} is required (maximum ${max} characters).`); return value.trim(); }
export function snowflake(value,name) {if(!idPattern.test(value||'')) throw new Error(`${name} must be a Discord ID (17–20 digits).`);return value;}
export async function request(url,{headers={},body,signal,method}={},fetcher=fetch){
 const timeout=AbortSignal.timeout(25000); const s=signal?AbortSignal.any([signal,timeout]):timeout;
 let r;try{r=await fetcher(url,{method:method||(body?'POST':'GET'),headers:{'Content-Type':'application/json',...headers},body:body?JSON.stringify(body):undefined,signal:s,redirect:'error'});}catch(e){throw new Error(s.aborted?'External request timed out or was cancelled.':'External service could not be reached.');}
 if(!r.ok){let retryAt,errorCode;try{const payload=await r.json();if(Number.isFinite(payload.retry_at)&&payload.retry_at>0)retryAt=payload.retry_at;if(typeof payload.error==='string'&&/^app_session_[a-z_]+$/.test(payload.error))errorCode=payload.error;}catch{}
 if(r.status===429&&!retryAt){const value=r.headers?.get('retry-after');if(value){const seconds=Number(value);const date=Date.parse(value);if(Number.isFinite(seconds)&&seconds>=0)retryAt=Date.now()/1000+seconds;else if(Number.isFinite(date))retryAt=date/1000;}}
 const service=new URL(url).hostname;throw Object.assign(new Error(`${service} returned HTTP ${r.status}${errorCode?` (${errorCode})`:r.status===429?' (rate limited; try later).':'. Check the credential, model and permissions.'}`),{httpStatus:r.status,retryAt,errorCode});}
 if(r.status===204)return null;
 try{return await r.json();}catch{throw new Error('External service returned invalid JSON.');}
}
