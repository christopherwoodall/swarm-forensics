export function connectionRow({relay:r,button,configure,channels,setup,recheck,disconnect}){
 const row=document.createElement('div');row.className='connection-row';
 const label=document.createElement('span');label.className='connection-label';label.textContent=`${r.bots[0]?.name||r.config.name} · ${r.config.channelId?'Swarm: #'+(r.config.channelName||r.config.channelId):'No swarm channel'}`;
 const status=document.createElement('small');status.textContent=r.config.verifiedAt?'Connected':r.config.channelId?'Setup unfinished':'Disconnected';label.append(status);
 const actions=document.createElement('div');actions.className='connection-actions';
 actions.append(button(r.config.verifiedAt?'Recheck':'Connect swarm channel',r.config.verifiedAt?recheck:setup,'secondary'));
 if(channels)actions.append(button(r.config.channelId?'Change swarm channel':'Choose swarm channel',channels,'secondary'));
 if(r.config.channelId){actions.append(button('Agent controls',configure,'secondary'));if(r.config.verifiedAt)actions.append(button('Connect agent',setup,'secondary'));actions.append(button('Disconnect swarm channel',disconnect,'secondary disconnect-channel'));}
 row.append(label,actions);return row;
}

export function swarmGroups(relays){const groups=new Map();for(const relay of relays){const id=relay.config.verifiedAt&&relay.config.guildId?relay.config.guildId:'unassigned';if(!groups.has(id))groups.set(id,{id,name:id==='unassigned'?'Unassigned bots':relay.config.guildName||'Discord server '+id,relays:[]});groups.get(id).relays.push(relay);}return [...groups.values()];}
