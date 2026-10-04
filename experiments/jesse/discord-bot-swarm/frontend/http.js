// Never expose response bodies or parser excerpts in user-facing errors.
export async function readJsonResponse(response){
  const unavailable=response.status>=500;
  const type=response.headers.get('content-type')||'';
  if(!/\bapplication\/(?:[\w.-]+\+)?json\b/i.test(type))
    throw Error(unavailable?'Server temporarily unavailable. Please try again shortly.':'The server returned an unexpected response. Please try again.');
  let data;
  try{data=await response.json();}catch{throw Error('The server returned an invalid response. Please try again.');}
  if(!response.ok)throw Error(unavailable?'Server temporarily unavailable. Please try again shortly.':(typeof data?.error==='string'?data.error:'Request failed.'));
  return data;
}
