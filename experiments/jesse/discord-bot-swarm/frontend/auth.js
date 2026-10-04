async function script(src){await new Promise((resolve,reject)=>{const s=document.createElement('script');s.src=src;let timer=setTimeout(()=>{s.remove();reject(Error('Sign-in component timed out.'));},10000);s.onload=()=>{clearTimeout(timer);resolve();};s.onerror=()=>{clearTimeout(timer);s.remove();reject(Error('Sign-in component unavailable.'));};document.head.append(s);});}
function markAgentAccount(){
 const header=document.querySelector('#auth-area');if(!header)return;
 const refresh=()=>{for(const item of header.querySelectorAll('*')){const agent=item.children.length===0&&item.textContent.trim()==='multi-agent@fairystack.com';if(agent&&!item.classList.contains('agent-account-badge')){item.classList.add('agent-account-badge');item.setAttribute('aria-label','Shared agent account: multi-agent@fairystack.com');}else if(!agent&&item.classList.contains('agent-account-badge')){item.classList.remove('agent-account-badge');item.removeAttribute('aria-label');}}};
 new MutationObserver(refresh).observe(header,{childList:true,subtree:true,characterData:true});refresh();
}
export async function initAuth(config,handlers){
 markAgentAccount();
 const options={headerEl:'#auth-area',landingButtonsEl:'#auth-buttons',showWhenLoggedIn:'#signed-in',showWhenLoggedOut:'#signed-out',...handlers};
 if(config.auth.mode==='authreturn'){await script(config.auth.script);return window.AuthReturn.init({...options,appId:config.auth.appId,theme:matchMedia('(prefers-color-scheme:light)').matches?'light':'dark'});}
 const {initOidc}=await import('./auth-oidc.js');return initOidc(config.auth,options);
}
