// Renders the committed architecture SVGs from frontend/swarm-diagram.js through Info Elements.
import fs from 'node:fs';
import {swarmDiagram,diagramThemes} from '../frontend/swarm-diagram.js';

for(const [name,theme] of Object.entries(diagramThemes)){
 const r=await fetch('https://info-elements.aisloppy.com/api/render/graph',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({...swarmDiagram,containers:swarmDiagram.containers.map(({id,label})=>({id,label})),theme}),signal:AbortSignal.timeout(30000)});
 const body=await r.json();
 if(!r.ok)throw Error(`${name} render failed with HTTP ${r.status}: ${JSON.stringify(body).slice(0,500)}`);
 if(!body.diagnostics?.valid||body.quality_warning)throw Error(`${name} render failed quality checks: ${JSON.stringify(body.quality_warning||body.diagnostics).slice(0,800)}`);
 // Both themes are inlined on one page, so marker and gradient IDs must be unique per theme.
 const svg=body.svg.trim().replace(/(\s)id="([^"]+)"/g,(_,space,id)=>`${space}id="${name}-${id}"`).replace(/url\(#([^)]+)\)/g,(_,id)=>`url(#${name}-${id})`).replace(/href="#([^"]+)"/g,(_,id)=>`href="#${name}-${id}"`);
 fs.writeFileSync(`frontend/swarm-diagram-${name}.svg`,svg+'\n');
 console.log(`frontend/swarm-diagram-${name}.svg`,body.diagnostics.layout);
}
