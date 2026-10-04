import crypto from 'node:crypto';
export const idPattern = /^\d{17,20}$/;
export function text(value, name, max=200) { if(typeof value !== 'string' || !value.trim() || value.length>max) throw new Error(`${name} is required (maximum ${max} characters).`); return value.trim(); }
export function snowflake(value,name) {if(!idPattern.test(value||'')) throw new Error(`${name} must be a Discord ID (17–20 digits).`);return value;}
export function provider(p){if(!['openai','anthropic'].includes(p))throw new Error('Choose OpenAI or Anthropic API access.');return p;}
export async function request(url,{headers={},body,signal,method}={},fetcher=fetch){
 const timeout=AbortSignal.timeout(25000); const s=signal?AbortSignal.any([signal,timeout]):timeout;
 let r;try{r=await fetcher(url,{method:method||(body?'POST':'GET'),headers:{'Content-Type':'application/json',...headers},body:body?JSON.stringify(body):undefined,signal:s,redirect:'error'});}catch(e){throw new Error(s.aborted?'External request timed out or was cancelled.':'External service could not be reached.');}
 if(!r.ok){const service=new URL(url).hostname;throw new Error(`${service} returned HTTP ${r.status}${r.status===429?' (rate limited; try later).':'. Check the credential, model and permissions.'}`);}
 if(r.status===204)return null;
 try{return await r.json();}catch{throw new Error('External service returned invalid JSON.');}
}
export async function models(p,key,fetcher=fetch){provider(p);const d=await request(p==='openai'?'https://api.openai.com/v1/models':'https://api.anthropic.com/v1/models',{headers:p==='openai'?{Authorization:`Bearer ${key}`}:{'x-api-key':key,'anthropic-version':'2023-06-01'}},fetcher);return (d.data||[]).map(m=>m.id).sort();}
