import crypto from 'node:crypto';
export const idPattern = /^\d{17,20}$/;
export function text(value, name, max=200) { if(typeof value !== 'string' || !value.trim() || value.length>max) throw new Error(`${name} is required (maximum ${max} characters).`); return value.trim(); }
export function snowflake(value,name) {if(!idPattern.test(value||'')) throw new Error(`${name} must be a Discord ID (17–20 digits).`);return value;}
export async function request(url,{headers={},body,signal,method}={},fetcher=fetch){
 const timeout=AbortSignal.timeout(25000); const s=signal?AbortSignal.any([signal,timeout]):timeout;
 let r;try{r=await fetcher(url,{method:method||(body?'POST':'GET'),headers:{'Content-Type':'application/json',...headers},body:body?JSON.stringify(body):undefined,signal:s,redirect:'error'});}catch(e){throw new Error(s.aborted?'External request timed out or was cancelled.':'External service could not be reached.');}
 if(!r.ok){const service=new URL(url).hostname;throw Object.assign(new Error(`${service} returned HTTP ${r.status}${r.status===429?' (rate limited; try later).':'. Check the credential, model and permissions.'}`),{httpStatus:r.status});}
 if(r.status===204)return null;
 try{return await r.json();}catch{throw new Error('External service returned invalid JSON.');}
}
