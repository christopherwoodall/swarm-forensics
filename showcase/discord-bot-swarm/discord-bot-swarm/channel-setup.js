// Discovery is read-only. Assignment and verification use the existing owner routes.
export function registerChannelDiscovery(app,{route,getSwarm,relay}){
 app.get('/api/relays/:id/channels',route(async(req,res)=>{await getSwarm(req.params.id,req.owner);res.json(await relay.discover({swarm:req.params.id,owner:req.owner},AbortSignal.timeout(30000)));}));
}
