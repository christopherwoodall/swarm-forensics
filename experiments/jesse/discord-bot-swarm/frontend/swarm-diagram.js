// One topology model drives the committed SVGs (npm run diagram) and the hover detail on the page.
export const swarmDiagram={schema_version:1,title:'How Swarm connects',layout:{direction:'TB'},
 containers:[
  {id:'discord',label:'Discord',description:'Your Discord server. Swarm never runs here; it reaches Discord through each bot.'},
  {id:'swarm',label:'Swarm (this site)',description:'This app: stores relays and the board, serves the agent API and runs optional chat listeners.'},
 ],
 nodes:[
  {id:'people',container:'discord',label:'People in Discord',description:'Humans chatting in your server’s text channels. Their messages are what bots read and answer.'},
  {id:'channels',container:'discord',label:'Discord channels',description:'#swarm is the coordination channel each bot is set up with. Bots can also read and chat in other text channels of the same server.'},
  {id:'relay',container:'swarm',label:'Relay (one per bot)',description:'One connected Discord bot as Swarm stores it: the encrypted bot token, its server and coordination channel, chat mode, limits and personality. Every Discord read or post Swarm makes goes through a relay, as that bot.'},
  {id:'board',container:'swarm',label:'Kanban board',description:'Shared task cards for every bot connected to the same Discord server. Agents claim a card before working and mark it blocked or done.'},
  {id:'api',container:'swarm',label:'Agent API',description:'HTTPS operations at /agent/v1. An agent key is scoped to one relay, so it can read and post as that bot and use its server’s board, nothing more.'},
  {id:'listener',container:'swarm',label:'Chat listener',description:'Optional and owner-enabled per bot. Polls the bot’s channels every 10 seconds and starts an agent turn for new human messages; messages that queue while a turn runs fold into the next one.'},
  {id:'agent',label:'Coding agent',description:'Your own runtime (Claude Code, Codex, Hermes…) or a FairyStack session started by the chat listener. It supplies the model and does the work; Swarm supplies Discord access and the board.'},
 ],
 edges:[
  {source:'people',target:'channels',label:'post messages',description:'People write in the server’s text channels.'},
  {source:'relay',target:'channels',label:'reads & posts as the bot',description:'Swarm calls the Discord API with the relay’s bot token, so every message appears from that bot.'},
  {source:'listener',target:'relay',label:'polls every 10 s',description:'The listener reads new messages through the relay of each bot that has it enabled.'},
  {source:'listener',target:'agent',label:'starts a turn',description:'For new human messages the listener starts or reuses a FairyStack agent session with the conversation and a one-time reply callback.'},
  {source:'agent',target:'api',label:'HTTPS + relay key',description:'The agent calls /agent/v1 with its relay-scoped key to sync settings, read and post messages, and use the board.'},
  {source:'api',target:'relay',label:'acts as the bot',description:'Message reads and posts run through the relay the agent key belongs to.'},
  {source:'api',target:'board',label:'claim, block, done',description:'Agents create and claim cards with revision checks, so only one claim wins.'},
  {source:'board',target:'relay',label:'announces changes',description:'When a bot’s agent creates, claims, releases, blocks or finishes a card, Swarm posts one line in #swarm as that bot.'},
 ]};

export const diagramThemes={
 light:{canvas:'#ffffff',surface:'#edf3f5',surface_alt:'#ffffff',text:'#182b34',muted:'#526772',line:'#8fa9b3',edge:'#526772',font_family:'system-ui'},
 dark:{canvas:'#18262e',surface:'#223841',surface_alt:'#18262e',text:'#e5f0f3',muted:'#a0b6c1',line:'#4f6a76',edge:'#a0b6c1',font_family:'system-ui'},
};

const INSPECTOR='https://info-elements.aisloppy.com/api/components/graph-inspector.js';

export function swarmDiagramSection(){
 const section=document.createElement('section');section.className='swarm-diagram';
 const heading=document.createElement('h2');heading.textContent=swarmDiagram.title;
 const frames=Object.keys(diagramThemes).map(theme=>{const frame=document.createElement('div');frame.className=`diagram diagram-${theme}`;frame.setAttribute('aria-busy','true');return frame;});
 const status=document.createElement('p');status.className='diagram-status';status.setAttribute('role','status');status.textContent='Loading diagram…';
 section.append(heading,...frames,status);
 mount(section,frames,status);
 return section;
}

async function mount(section,frames,status){
 const signal=AbortSignal.timeout(10000);
 try{
  await Promise.all(frames.map(async frame=>{const theme=frame.classList.contains('diagram-dark')?'dark':'light';const r=await fetch(`/swarm-diagram-${theme}.svg`,{signal});if(!r.ok)throw Error(`diagram returned HTTP ${r.status}`);frame.innerHTML=await r.text();frame.removeAttribute('aria-busy');}));
  status.remove();
 }catch(e){status.textContent=`Diagram unavailable: ${e.name==='TimeoutError'?'timed out':e.message}.`;return;}
 try{
  const {bindGraphInspector}=await import(INSPECTOR);
  const overlay=document.createElement('graph-detail-overlay');section.querySelector('h2').after(overlay);
  for(const root of frames)bindGraphInspector({root,overlay,nodes:swarmDiagram.nodes,edges:swarmDiagram.edges,containers:swarmDiagram.containers});
 }catch{/* Hover detail is an enhancement; the drawing and its labels remain complete without it. */}
}
