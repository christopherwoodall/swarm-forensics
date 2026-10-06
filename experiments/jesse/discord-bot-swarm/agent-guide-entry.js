import {wizardRoute} from './frontend/wizard-route.js';

// Public instructions are available before owner authentication or JavaScript.
export function agentGuideEntry({origin,guide}){
 return (req,res,next)=>{
  if(!['GET','HEAD'].includes(req.method))return next();
  const url=new URL(req.originalUrl,origin);
  if(url.pathname==='/'&&url.searchParams.get('setup')==='agent'){
   try{
    const route=wizardRoute(url.href),target=new URL('/agent-guide.md',origin);
    if(route.relayId)target.searchParams.set('relay',route.relayId);
    return res.redirect(302,target.pathname+target.search);
   }catch(e){return res.status(400).type('text/plain').send(e.message);}
  }
  if(url.pathname!=='/agent-guide.md')return next();
  let context='';
  if(url.searchParams.has('relay')){
   try{
    const route=wizardRoute(new URL('/?setup=agent&relay='+encodeURIComponent(url.searchParams.get('relay')),origin).href);
    if(!route.relayId)throw Error('This setup link is invalid.');
    const namespace=`discord-swarm/${encodeURIComponent(new URL(origin).origin)}/${route.relayId}/<credentialId>`;
    context=`Connection origin: ${origin}\nBot connection ID (relayId): ${route.relayId}\nSecret-store namespace: ${namespace}\n\nReplace <credentialId> with the registration response’s id; preserve keys and locators for other connections. This namespace contains no secret. This ID is public connection context, not a credential or proof of access. Validate ownership and key scope before connecting.\n\n`;
   }catch(e){return res.status(400).type('text/plain').send(e.message);}
  }
  return res.type('text/plain').send(guide.replace('# Join Discord Swarm\n\n','# Join Discord Swarm\n\n'+context));
 };
}
