export const CLIENTS={hermes:{name:'Hermes CLI',file:'~/.hermes/config.yaml',docs:'https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp'},droid:{name:'Droid',file:'Run in your terminal',docs:'https://docs.factory.com/harness/mcp'},opencode:{name:'OpenCode',file:'Your private OpenCode user config',docs:'https://opencode.ai/docs/mcp-servers/'},antigravity:{name:'Antigravity',file:'MCP server configuration',docs:'https://antigravity.google/docs/mcp'}};
export function clientConfig(client,origin){
 const url=new URL('/mcp',origin).href,header='Bearer YOUR_APPLICATION_TOKEN';
 if(client==='hermes')return `mcp_servers:\n  discord_swarm:\n    url: "${url}"\n    headers:\n      Authorization: "${header}"\n    timeout: 30`;
 if(client==='droid')return `droid mcp add discord-swarm ${url} --type http --header "Authorization: ${header}" --no-oauth`;
 if(client==='opencode')return JSON.stringify({mcp:{discord_swarm:{type:'remote',url,oauth:false,headers:{Authorization:header},timeout:30000}}},null,2);
 if(client==='antigravity')return JSON.stringify({mcpServers:{discord_swarm:{serverUrl:url,headers:{Authorization:header}}}},null,2);
 throw Error('Choose a supported MCP client.');
}
export async function checkMcp(api,relayId){
 const controller=new AbortController();let timer;
 try{return await Promise.race([checkConnection(api,relayId,controller.signal),new Promise((_,reject)=>{timer=setTimeout(()=>{controller.abort();reject(Error('MCP connection check timed out.'));},35000);})]);}finally{clearTimeout(timer);}
}
async function checkConnection(api,relayId,signal){
 const call=async(id,method,params)=>{const data=await api('/mcp',{method:'POST',headers:{Accept:'application/json, text/event-stream','MCP-Protocol-Version':'2025-11-25'},signal,timeoutMs:10000,body:JSON.stringify({jsonrpc:'2.0',id,method,params})});if(data.error)throw Error('MCP protocol request failed.');return data.result;};
 const init=await call(1,'initialize',{protocolVersion:'2025-11-25',capabilities:{},clientInfo:{name:'discord-swarm-onboarding',version:'1'}});if(!init?.capabilities?.tools)throw Error('MCP tools are unavailable.');
 const result=await call(2,'tools/call',{name:'discord_read_messages',arguments:{relayId,limit:1}});
 if(result?.isError)throw Error('Channel read failed. Recheck bot permissions in Connections.');
 let data;try{data=JSON.parse(result?.content?.find(x=>x.type==='text')?.text);}catch{throw Error('MCP returned an invalid channel response.');}
 if(!Array.isArray(data.messages))throw Error('MCP returned an invalid channel response.');
 return true;
}
