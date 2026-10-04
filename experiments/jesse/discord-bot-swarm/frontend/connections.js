export function connectionRow({relay:r,button,channels,setup,runtime,disconnect}){
 const row=document.createElement('div');row.className='connection-row';
 const label=document.createElement('span');label.className='connection-label';label.textContent=`${r.bots[0]?.name||r.config.name} · ${r.config.channelId?'Swarm: #'+(r.config.channelName||r.config.channelId):'No swarm channel'}`;
 const status=document.createElement('small');status.textContent=r.config.verifiedAt?'Connected':r.config.channelId?'Setup unfinished':'Disconnected';label.append(status);
 const actions=document.createElement('div');actions.className='connection-actions';
 if(!r.config.verifiedAt)actions.append(button('Connect swarm channel',setup,'secondary'));
 if(channels)actions.append(button(r.config.channelId?'Change swarm channel':'Choose swarm channel',channels,'secondary'));
 if(r.config.verifiedAt&&runtime)actions.append(button('Runtime bridge setup',runtime,'secondary'));
 if(r.config.channelId){const controls=document.createElement('a');controls.className='header-button';controls.href='/agent.html?relay='+encodeURIComponent(r.id);controls.textContent='Agent controls';actions.append(controls);if(r.config.verifiedAt){if(r.agentConnected){const connected=document.createElement('span');connected.className='agent-connected';connected.textContent='● Connected!';connected.setAttribute('aria-label','MCP agent connected');actions.append(connected);}else actions.append(button('Connect agent',setup,'secondary'));}actions.append(button('Disconnect swarm channel',disconnect,'secondary disconnect-channel'));}
 row.append(label,actions);return row;
}

export function swarmGroups(relays){const groups=new Map();for(const relay of relays){const id=relay.config.verifiedAt&&relay.config.guildId?relay.config.guildId:'unassigned';if(!groups.has(id))groups.set(id,{id,name:id==='unassigned'?'Unassigned bots':relay.config.guildName||'Discord server '+id,relays:[]});groups.get(id).relays.push(relay);}return [...groups.values()];}
