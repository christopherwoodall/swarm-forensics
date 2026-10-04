const steps=['bot','invite','channel','agent'];
const uuid=/^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$/i;
export function wizardRoute(value){
 const url=new URL(value),name=url.searchParams.get('setup');if(name===null)return null;
 const step=steps.indexOf(name)+1,relayId=url.searchParams.get('relay'),path=url.searchParams.get('bot');
 if(!step||(relayId&&!uuid.test(relayId))||(path&&!['new','existing'].includes(path)))throw Error('This setup link is invalid.');
 return {step,relayId,path};
}
export function wizardUrl(origin,{step=4,relayId=null,path=null}={}){
 if(!steps[step-1])throw Error('Unknown wizard step.');
 const url=new URL('/',origin);url.searchParams.set('setup',steps[step-1]);
 if(relayId){if(!uuid.test(relayId))throw Error('Invalid relay ID.');url.searchParams.set('relay',relayId);}
 if(step===1&&path)url.searchParams.set('bot',path);
 return url.href;
}
export function resolveWizardRoute(route,relays){
 const relay=route.relayId?relays.find(r=>r.id===route.relayId):relays.find(r=>r.config.verifiedAt)||relays[0]||null;
 if(route.relayId&&!relay)throw Error('This relay is not available to your signed-in account.');
 const ready=relay?.config.verifiedAt?4:relay?.config.setupStage==='invite'?2:relay?3:1;
 const resume=relay&&!route.relayId&&!route.path;
 return {relay,step:resume?ready:Math.min(route.step,ready),path:route.step===1?route.path:null};
}
