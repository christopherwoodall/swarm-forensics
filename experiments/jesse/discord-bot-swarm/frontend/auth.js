async function script(src){await new Promise((resolve,reject)=>{const s=document.createElement('script');s.src=src;let timer=setTimeout(()=>{s.remove();reject(Error('Sign-in component timed out.'));},10000);s.onload=()=>{clearTimeout(timer);resolve();};s.onerror=()=>{clearTimeout(timer);s.remove();reject(Error('Sign-in component unavailable.'));};document.head.append(s);});}
export async function initAuth(config,handlers){
 const options={headerEl:'#auth-area',landingButtonsEl:'#auth-buttons',showWhenLoggedIn:'#signed-in',showWhenLoggedOut:'#signed-out',...handlers};
 if(config.auth.mode==='authreturn'){await script(config.auth.script);return window.AuthReturn.init({...options,appId:config.auth.appId,theme:matchMedia('(prefers-color-scheme:light)').matches?'light':'dark'});}
 const {initOidc}=await import('./auth-oidc.js');return initOidc(config.auth,options);
}
