import {agentRecipe} from './agent-recipe.js';
import {bridgeSetupPrompt} from './mcp-setup.js';

export function runtimeSetup({origin,relay,api,button,configure,onNext,onBack}){
 const section=document.createElement('section');section.id='runtime-setup';
 const explanation=document.createElement('p');explanation.textContent='Paste this into your connected agent to start its runtime, then enable your Discord commands and limits.';
 const recipe=agentRecipe({title:'Paste this into your connected agent:',prompt:bridgeSetupPrompt(origin,relay.id),copyLabel:'Copy runtime bridge setup prompt',loadPrompt:()=>bridgeSetupPrompt(origin,relay.id),button});
 const status=document.createElement('p');status.id='runtime-check-status';status.setAttribute('role','status');status.textContent='Runtime bridge not checked.';
 const next=button('Next: start your first task',onNext,'wizard-primary-cta');next.disabled=true;
 const check=button('Check runtime readiness',async()=>{
  next.disabled=true;status.textContent='Checking runtime…';
  const signal=AbortSignal.timeout(30000);
  try{
   const state=await api(`/api/relays/${relay.id}/commands`,{timeoutMs:10000,signal});
   if(!['online','offline'].includes(state.bridge))throw Error('Invalid runtime bridge status.');
   if(state.bridge==='offline'){status.textContent='Runtime bridge offline. Send the setup prompt to your agent and check again.';return;}
   const snapshot=await api('/api/state',{timeoutMs:10000,signal});
   const current=snapshot.swarms?.find(r=>r.id===relay.id);
   if(!current)throw Error('This bot is no longer available.');
   if(!current.config.commands?.enabled){status.textContent='Runtime bridge online. Enable Discord commands and set your limits to continue.';return;}
   if(!current.config.verifiedAt){status.textContent='Verify the assigned Discord channel before continuing.';return;}
   status.textContent='Runtime bridge online · Discord commands enabled.';next.disabled=false;
  }catch(e){status.textContent='Runtime check failed: '+e.message;}
 },'secondary');
 const actions=document.createElement('div');actions.className='setup-actions';actions.append(button('Set command limits',configure),check);
 const navigation=document.createElement('div');navigation.className='wizard-navigation';navigation.append(button('Back: test access',onBack,'quiet'),button('Continue with manual agent tasks',onNext,'quiet'),next);
 section.append(explanation,recipe,actions,status,navigation);return section;
}
