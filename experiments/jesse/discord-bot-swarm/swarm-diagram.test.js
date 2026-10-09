import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {swarmDiagram,diagramThemes} from './frontend/swarm-diagram.js';

const svgs=Object.keys(diagramThemes).map(theme=>[theme,fs.readFileSync(new URL(`./frontend/swarm-diagram-${theme}.svg`,import.meta.url),'utf8')]);
const unescape=text=>text.replaceAll('&amp;','&');

test('committed diagrams match the topology model (run npm run diagram after editing it)',()=>{
 const nodeIds=swarmDiagram.nodes.map(n=>n.id).sort(),containers=new Set(swarmDiagram.containers.map(c=>c.id));
 for(const n of swarmDiagram.nodes){assert.ok(n.description,`${n.id} needs hover detail`);if(n.container)assert.ok(containers.has(n.container),`${n.id} names an unknown container`);}
 for(const e of swarmDiagram.edges){assert.ok(nodeIds.includes(e.source)&&nodeIds.includes(e.target),`${e.source}->${e.target}`);assert.ok(e.description);}
 for(const [theme,svg] of svgs){
  assert.deepEqual([...new Set([...svg.matchAll(/data-node-id="([^"]+)"/g)].map(m=>m[1]))].sort(),nodeIds,theme);
  const edges=new Set([...svg.matchAll(/data-edge-source="([^"]+)" data-edge-target="([^"]+)"/g)].map(m=>m[1]+'>'+m[2]));
  for(const e of swarmDiagram.edges)assert.ok(edges.has(e.source+'>'+e.target),`${theme} missing ${e.source}->${e.target}`);
  const text=unescape([...svg.matchAll(/>([^<>]+)</g)].map(m=>m[1]).join(' ')).replace(/\s+/g,' ');
  for(const label of [...swarmDiagram.nodes,...swarmDiagram.containers].map(x=>x.label))assert.ok(text.includes(label),`${theme} missing ${label}`);
 }
});

test('both themes can be inlined on one page without ID collisions',()=>{
 const [light,dark]=svgs.map(([,svg])=>new Set([...svg.matchAll(/\sid="([^"]+)"/g)].map(m=>m[1])));
 assert.ok(light.size&&dark.size);assert.deepEqual([...light].filter(id=>dark.has(id)),[]);
 for(const [theme,svg] of svgs)for(const [,ref] of svg.matchAll(/url\(#([^)]+)\)/g))assert.ok(ref.startsWith(theme+'-'),`${theme} references ${ref}`);
});
