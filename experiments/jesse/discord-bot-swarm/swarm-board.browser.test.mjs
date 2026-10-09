import {test} from 'node:test';
import assert from 'node:assert/strict';
import http from 'node:http';
import fs from 'node:fs';
import {chromium} from 'playwright';
import {swarmGroups} from './frontend/connections.js';
test('Connections groups channels by server and keeps unfinished bots unassigned',()=>{const groups=swarmGroups([{id:'a',config:{guildId:'one',verifiedAt:'now'}},{id:'b',config:{guildId:'one',verifiedAt:'now'}},{id:'c',config:{guildId:'two',verifiedAt:'now'}},{id:'d',config:{guildId:'one'}}]);assert.deepEqual(groups.map(g=>[g.id,g.relays.map(r=>r.id)]),[['one',['a','b']],['two',['c']],['unassigned',['d']]]);});
test('board server selection rejects stale polls, stays responsive and shows shared agents',async()=>{
 let hold=false,resolve,pending=new Promise(r=>resolve=r);const one='123456789012345678',two='123456789012345679';
 const server=http.createServer(async(req,res)=>{const url=new URL(req.url,'http://localhost');const json=x=>{res.setHeader('Content-Type','application/json');res.end(JSON.stringify(x));};if(url.pathname==='/api/config')return json({});if(url.pathname==='/api/swarms')return json({swarms:[{id:one,name:'First server'},{id:two,name:'Second server'}]});if(url.pathname==='/api/board'){const id=url.searchParams.get('guildId');if(url.searchParams.get('view')==='archive')return json({tasks:[{id:'archive-'+(url.searchParams.get('cursor')||'first'),title:url.searchParams.get('cursor')?'Older archived task':'Archived completion',description:'Preserved evidence',note:'Result link',dependencies:[],effective_state:'done',state:'done',revision:3,updated_at:'2026-09-01T00:00:00Z'}],limit:500,nextCursor:url.searchParams.get('cursor')?null:'550e8400-e29b-41d4-a716-446655440000'});if(hold&&id===one)await pending;return json({tasks:[{id, title:id===one?'First server task':'Second server task',description:'',dependencies:[],effective_state:'queued',revision:1}],limit:500});}if(url.pathname==='/api/board/agents')return json({agents:[{id:'a',name:'Other account agent',relay_id:'relay',expires_at:new Date(Date.now()+3600000).toISOString(),can_revoke:false}]});if(url.pathname==='/auth.js'){res.setHeader('Content-Type','text/javascript');return res.end(`export async function initAuth(config,{onLogin}){document.getElementById('signed-in').hidden=false;document.getElementById('signed-out').hidden=true;queueMicrotask(onLogin);return {getValidToken:async()=> 'synthetic'};}`);}const file='frontend'+(url.pathname==='/'?'/board.html':url.pathname);if(!fs.existsSync(file)){res.statusCode=404;return res.end();}res.setHeader('Content-Type',file.endsWith('.js')?'text/javascript':file.endsWith('.css')?'text/css':'text/html');res.end(fs.readFileSync(file));});server.requestTimeout=5000;await new Promise(r=>server.listen(0,'127.0.0.1',r));let browser;
 try{browser=await chromium.launch({headless:true});const page=await browser.newPage();await page.goto(`http://127.0.0.1:${server.address().port}`,{timeout:10000});await page.getByRole('heading',{name:'First server task',exact:true}).waitFor({timeout:5000});hold=true;await page.getByRole('button',{name:'Refresh',exact:true}).click();await page.locator('#swarm').selectOption(two);resolve();await page.getByRole('heading',{name:'Second server task',exact:true}).waitFor({timeout:5000});assert.equal(await page.getByRole('heading',{name:'First server task',exact:true}).count(),0);assert.equal(await page.locator('#swarm').inputValue(),two);await page.getByRole('button',{name:'Connected agents',exact:true}).click();await page.getByText('Other account agent',{exact:false}).waitFor({timeout:5000});assert.equal(await page.getByRole('button',{name:'Revoke',exact:true}).count(),0);await page.getByRole('button',{name:'Close',exact:true}).click();await page.locator('#view').selectOption('archive');await page.getByRole('heading',{name:'Archived completion',exact:true}).waitFor({timeout:5000});assert.equal(await page.locator('.column').count(),1);await page.getByRole('button',{name:'Load older cards',exact:true}).click();await page.getByRole('heading',{name:'Older archived task',exact:true}).waitFor({timeout:5000});assert.equal(await page.getByRole('heading',{name:'Archived completion',exact:true}).count(),1);assert.equal(await page.locator('#older').isVisible(),false);await page.locator('#view').selectOption('active');await page.getByRole('heading',{name:'Second server task',exact:true}).waitFor({timeout:5000});assert.equal(await page.getByRole('heading',{name:'Archived completion',exact:true}).count(),0);hold=true;pending=new Promise(r=>resolve=r);await page.locator('#swarm').selectOption(one);await page.locator('#view').selectOption('archive');resolve();await page.getByRole('heading',{name:'Archived completion',exact:true}).waitFor({timeout:5000});assert.equal(await page.getByRole('heading',{name:'First server task',exact:true}).count(),0);for(const colorScheme of ['light','dark']){await page.emulateMedia({colorScheme});await page.setViewportSize({width:390,height:844});assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));const colors=await page.locator('#swarm').evaluate(n=>{const s=getComputedStyle(n);return [s.color,s.backgroundColor];});assert.notEqual(colors[0],colors[1]);}}
 finally{resolve();await browser?.close();server.closeAllConnections();await new Promise(r=>server.close(r));}
});

test('compact cards expand accessibly, retain details through refresh and identify claims without inferring from descriptions',async()=>{
 const guild='123456789012345678',long='Long retained evidence '.repeat(100),note='Full completion note '+ 'receipt '.repeat(100);
 const base={description:long,note,dependencies:[],revision:3,updated_at:'2026-10-09T00:00:00Z'};
 const tasks=[
  {...base,id:'unclaimed',title:'Bacon setup requirement',description:'Bacon needs setup '+long,assignee:null,effective_state:'queued'},
  {...base,id:'semi',title:'Bot claim',assignee:'credential-a',agent_name:'FairyStack project agent',claimant_kind:'bot',claimant_bot_name:'Semi',effective_state:'in_progress'},
  {...base,id:'expired',title:'Expired bot claim',assignee:'credential-b',claimant_kind:'bot',claimant_bot_name:'Stig',lease_until:'2020-01-01T00:00:00Z',effective_state:'stalled'},
  {...base,id:'human',title:'Human claim',assignee:'owner:synthetic',claimant_kind:'human',effective_state:'in_progress'},
  {...base,id:'board-only',title:'Board agent claim',assignee:'credential-c',claimant_kind:'agent',agent_name:'Board worker',effective_state:'in_progress'},
  {...base,id:'note-only',title:'Completed note only',description:'',assignee:'credential-d',claimant_kind:'bot',claimant_bot_name:'Semi',effective_state:'done'},
  {...base,id:'missing',title:'Disconnected bot claim',assignee:'credential-e',claimant_kind:'bot',claimant_bot_name:null,effective_state:'stalled'},
 ];
 const server=http.createServer((req,res)=>{
  const url=new URL(req.url,'http://localhost'),json=x=>{res.setHeader('Content-Type','application/json');res.end(JSON.stringify(x));};
  if(url.pathname==='/api/config')return json({});
  if(url.pathname==='/api/swarms')return json({swarms:[{id:guild,name:'Synthetic server'}]});
  if(url.pathname==='/api/board')return json({tasks,nextCursor:null});
  if(url.pathname==='/auth.js'){res.setHeader('Content-Type','text/javascript');return res.end(`export async function initAuth(config,{onLogin}){document.getElementById('signed-in').hidden=false;document.getElementById('signed-out').hidden=true;queueMicrotask(onLogin);return {getValidToken:async()=> 'synthetic'};}`);}
  const file='frontend'+(url.pathname==='/'?'/board.html':url.pathname);
  if(!fs.existsSync(file)){res.statusCode=404;return res.end();}
  res.setHeader('Content-Type',file.endsWith('.js')?'text/javascript':file.endsWith('.css')?'text/css':'text/html');res.end(fs.readFileSync(file));
 });server.requestTimeout=5000;await new Promise(r=>server.listen(0,'127.0.0.1',r));let browser;
 try{
  browser=await chromium.launch({headless:true});const page=await browser.newPage();await page.goto(`http://127.0.0.1:${server.address().port}`,{timeout:10000});await page.getByRole('heading',{name:'Bot claim',exact:true}).waitFor({timeout:5000});
  const card=id=>page.locator(`.card[data-task-id="${id}"]`),semi=card('semi');
  assert.equal(await card('unclaimed').locator('.claimant').textContent(),'Unclaimed');
  assert.equal(await semi.locator('.claimant').textContent(),'Claimed by Semi');
  assert.equal(await card('expired').locator('.claimant').textContent(),'Last claimed by Stig');
  assert.equal(await card('expired').getByText('Claim expired',{exact:true}).count(),1);
  assert.equal(await card('human').locator('.claimant').textContent(),'Claimed by Human');
  assert.equal(await card('board-only').locator('.claimant').textContent(),'Claimed by Board worker');
  assert.equal(await card('note-only').locator('.claimant').textContent(),'Completed by Semi');
  assert.equal(await card('missing').locator('.claimant').textContent(),'Last claimed by Bot connection unavailable');
  assert.equal(await semi.locator('.card-details').isVisible(),false);
  assert.ok((await semi.locator('.card-preview').textContent()).length<=160);
  assert.ok((await semi.boundingBox()).height<200);
  const toggle=semi.getByRole('button',{name:'Show details for Bot claim',exact:true});await toggle.focus();await page.keyboard.press('Enter');
  const hide=semi.getByRole('button',{name:'Hide details for Bot claim',exact:true});assert.equal(await hide.getAttribute('aria-expanded'),'true');assert.equal(await semi.locator('.card-details').isVisible(),true);
  assert.ok((await semi.locator('.card-details').textContent()).includes(long));assert.ok((await semi.locator('.card-details').textContent()).includes(note));assert.equal(await semi.locator('.card-preview').isVisible(),false);
  tasks[1].note='New retained server evidence';await page.evaluate(()=>document.getElementById('refresh').click());await semi.getByText('New retained server evidence',{exact:true}).waitFor({timeout:5000});
  assert.equal(await semi.getByRole('button',{name:'Hide details for Bot claim',exact:true}).getAttribute('aria-expanded'),'true');assert.equal(await page.locator(':focus').getAttribute('data-task-id'),'semi');
  await page.keyboard.press('Space');assert.equal(await semi.locator('.card-details').isVisible(),false);assert.equal(await semi.getByRole('button',{name:'Show details for Bot claim',exact:true}).getAttribute('aria-expanded'),'false');
  for(const colorScheme of ['light','dark']){
   await page.emulateMedia({colorScheme});await page.setViewportSize({width:390,height:844});assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
   for(const selector of ['.claimant','.card-toggle','.column']){const colors=await page.locator(selector).first().evaluate(n=>{const s=getComputedStyle(n);return [s.color,s.backgroundColor];});assert.notEqual(colors[0],colors[1]);}
  }
 }finally{await browser?.close();server.closeAllConnections();await new Promise(r=>server.close(r));}
});
