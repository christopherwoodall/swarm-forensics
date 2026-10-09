import {initAuth} from './auth.js';
import {readJsonResponse} from './http.js';
const $=id=>document.getElementById(id),node=(tag,text)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;return n;};let auth,signed=false,loading=false,epoch=0,started=0,selected=null,view='active',cards=[],nextCursor=null;const expandedCards=new Set();
function notice(text,error=false){$('notice').textContent=text;$('notice').classList.toggle('error',error);}
async function api(url,options={}){let timer;try{const token=await Promise.race([auth.getValidToken(),new Promise((_,reject)=>timer=setTimeout(()=>reject(Error('Sign-in refresh timed out.')),10000))]);return await readJsonResponse(await fetch(url,{...options,headers:{'Content-Type':'application/json',Authorization:`Bearer ${token}`},signal:AbortSignal.timeout(10000)}));}finally{clearTimeout(timer);}}
async function action(button,fn){button.disabled=true;notice('');try{await fn();}catch(e){notice(e.name==='TimeoutError'?'Request timed out. Refresh to check its outcome before retrying.':e.message,true);}finally{button.disabled=false;}}
function claimantLabel(task,state){
 if(!task.assignee)return 'Unclaimed';
 const who=task.claimant_kind==='bot'?task.claimant_bot_name||'Bot connection unavailable':task.claimant_kind==='human'?'Human':task.agent_name||'Unavailable agent';
 return (state==='done'?'Completed by ':state==='stalled'?'Last claimed by ':'Claimed by ')+who;
}
function render(tasks){
 const board=$('board'),focusedTask=board.contains(document.activeElement)?document.activeElement.dataset.taskId:null;
 board.replaceChildren();const names=new Map(tasks.map(t=>[t.id,t.title]));board.classList.toggle('archive',view==='archive');
 for(const [state,label]of (view==='archive'?[['done','Archive']]:[['queued','Queued'],['in_progress','In progress'],['blocked','Blocked'],['stalled','Stalled'],['done','Done']])){
  const col=node('section');col.className='column';col.append(node('h2',label));
  if(state==='done'&&view==='active'){const policy=node('p','Latest 10 · up to 7 days');policy.className='meta';col.append(policy);}
  const rows=tasks.filter(t=>t.effective_state===state);
  if(!rows.length){const empty=node('p','No tasks');empty.className='empty';col.append(empty);}
  for(const t of rows){
   const card=node('article');card.className='card';card.dataset.taskId=t.id;card.append(node('h3',t.title));
   const claimant=node('p',claimantLabel(t,state));claimant.className='claimant';card.append(claimant);
   if(state==='stalled'){const status=node('p',t.lease_until&&Date.parse(t.lease_until)<=Date.now()?'Claim expired':'Claim unavailable');status.className='meta';card.append(status);}
   const text=(t.description||t.note||'').replace(/\s+/g,' ').trim();
   if(text){const preview=node('p',text.length>160?text.slice(0,157)+'…':text);preview.className='card-preview';card.append(preview);}
   const details=node('div');details.className='card-details';details.id='task-details-'+t.id;
   if(t.description)details.append(node('p',t.description));
   if(t.note)details.append(node('p',t.note));
   if(t.dependencies.length)details.append(node('p','Depends on: '+t.dependencies.map(id=>names.get(id)||id).join(', ')));
   if(t.lease_until)details.append(node('p','Claim expires '+new Date(t.lease_until).toLocaleString()));
   if(state==='done')details.append(node('p','Completed '+new Date(t.updated_at).toLocaleString()));
   const meta=node('p',`Revision ${t.revision} · ${t.id}`);meta.className='meta';details.append(meta);
   const toggle=node('button');toggle.className='card-toggle';toggle.dataset.taskId=t.id;toggle.setAttribute('aria-controls',details.id);toggle.setAttribute('aria-label','Show details for '+t.title);
   const setExpanded=open=>{details.hidden=!open;toggle.textContent=open?'Hide details':'Show details';toggle.setAttribute('aria-expanded',String(open));toggle.setAttribute('aria-label',(open?'Hide':'Show')+' details for '+t.title);const preview=card.querySelector('.card-preview');if(preview)preview.hidden=open;};
   setExpanded(expandedCards.has(t.id));toggle.onclick=()=>{const open=!expandedCards.has(t.id);if(open)expandedCards.add(t.id);else expandedCards.delete(t.id);setExpanded(open);};
   card.append(toggle,details);col.append(card);if(t.id===focusedTask)queueMicrotask(()=>toggle.focus({preventScroll:true}));
  }
  board.append(col);
 }
}
async function loadSwarms(){const generation=epoch;const data=await api('/api/swarms');if(!signed||generation!==epoch)return;const options=data.swarms;const fromUrl=new URL(location.href).searchParams.get('guildId');selected=options.find(s=>s.id===fromUrl)?.id||options[0]?.id||'unassigned';$('swarm').replaceChildren(...options.map(s=>new Option(s.name,s.id)));$('swarm').value=selected;await refresh();}
const scoped=url=>url+'?guildId='+encodeURIComponent(selected||'unassigned');
function clearBoard(){expandedCards.clear();cards=[];nextCursor=null;$('board').replaceChildren();$('older').hidden=true;}
async function refresh(append=false){if(!signed||loading)return;loading=true;const generation=epoch;try{const query=new URLSearchParams({guildId:selected||'unassigned',view,...(append&&nextCursor?{cursor:nextCursor}:{})});const data=await api('/api/board?'+query);if(!signed||epoch!==generation)return;cards=append?[...cards,...data.tasks]:data.tasks;nextCursor=data.nextCursor||null;render(cards);$('older').hidden=!nextCursor;$('updated').textContent='Updated '+new Date().toLocaleTimeString();notice('');}catch(e){if(epoch===generation)notice(e.name==='TimeoutError'?'Board refresh timed out.':e.message,true);}finally{loading=false;if(signed&&epoch!==generation)queueMicrotask(refresh);}}
async function agents(){const generation=epoch;const data=await api(scoped('/api/board/agents'));if(!signed||generation!==epoch)return;$('agents').replaceChildren();if(!data.agents.length)$('agents').append(node('p','No agents connected to this swarm.'));for(const a of data.agents){const line=node('div');line.className='agent';const active=!a.revoked_at&&Date.parse(a.expires_at)>Date.now();line.append(node('span',`${a.name}${a.relay_id?' · relay '+a.relay_id:' · board only'} · ${a.revoked_at?'revoked':active?'expires '+new Date(a.expires_at).toLocaleString():'expired'}`));if(active&&a.can_revoke){const b=node('button','Revoke');b.onclick=()=>action(b,async()=>{await api('/api/board/agents/'+a.id,{method:'DELETE'});await agents();await refresh();});line.append(b);}$('agents').append(line);}}
$('research-export').onclick=()=>action($('research-export'),async()=>{
 const generation=epoch,deadline=Date.now()+60000;let after='0',through,metadata,bytes=0;const events=[];
 while(true){if(Date.now()>=deadline)throw Error('Research export exceeded its 60-second deadline. Use research_export to download bounded pages.');const query=new URLSearchParams({after,limit:'200',...(through?{through}:{})});const page=await api('/api/research/export?'+query);if(!signed||generation!==epoch)throw Error('Sign-in changed during research export.');metadata=page;through=page.through;events.push(...page.events);bytes+=JSON.stringify(page.events).length;if(bytes>32000000)throw Error('Research export exceeds the browser download limit. Use research_export for paginated evaluation.');notice('Exporting research: '+events.length+' events');if(!page.hasMore)break;if(BigInt(page.nextCursor)<=BigInt(after))throw Error('Research export cursor did not advance.');after=page.nextCursor;}
 const blob=new Blob([JSON.stringify({...metadata,events},null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),link=node('a');link.href=url;link.download='swarm-research.json';document.body.append(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);notice('Research JSON exported: '+events.length+' events.');
});
$('refresh').onclick=()=>action($('refresh'),()=>{started=Date.now();return refresh();});$('access').onclick=()=>action($('access'),async()=>{await agents();$('access-dialog').showModal();});
$('swarm').onchange=()=>{selected=$('swarm').value;epoch++;clearBoard();$('agents').replaceChildren();$('access-dialog').close();const url=new URL(location.href);url.searchParams.set('guildId',selected);history.replaceState(null,'',url);refresh();};
$('view').onchange=()=>{view=$('view').value;epoch++;clearBoard();refresh();};
$('older').onclick=()=>action($('older'),()=>refresh(true));
$('close').onclick=()=>$('access-dialog').close();
try{const config=await readJsonResponse(await fetch('/api/config',{signal:AbortSignal.timeout(10000)}));auth=await initAuth(config,{onLogin(){signed=true;epoch++;started=Date.now();setTimeout(()=>loadSwarms().catch(e=>notice(e.message,true)),0);},onLogout(){signed=false;epoch++;selected=null;$('swarm').replaceChildren();clearBoard();$('agents').replaceChildren();$('access-dialog').close();},onError:e=>notice(e.message||'Sign-in failed.',true)});}catch(e){notice(e.message,true);}
setInterval(()=>{if(signed&&!document.hidden&&view==='active'&&cards.length<=500){if(Date.now()-started<30*60*1000)refresh();else $('updated').textContent='Automatic refresh paused. Refresh to resume.';}},10000);
