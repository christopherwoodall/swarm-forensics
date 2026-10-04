import test from 'node:test';
import assert from 'node:assert/strict';
import express from 'express';
import {chromium} from 'playwright';
test('space escape rejects wrong codes, gives hints, completes sequentially and resets in both themes',{timeout:20000},async()=>{
 const app=express();app.use(express.static('frontend'));const server=app.listen(0,'127.0.0.1');await new Promise(r=>server.once('listening',r));let browser;
 try{browser=await chromium.launch({headless:true});const page=await browser.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));await page.goto(`http://127.0.0.1:${server.address().port}/escape-room.html`,{timeout:10000});
 for(const scheme of ['light','dark']){await page.emulateMedia({colorScheme:scheme});await page.setViewportSize({width:390,height:844});assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));const palette=await page.locator('#clue').evaluate(e=>({fg:getComputedStyle(e).color,bg:getComputedStyle(e).backgroundColor}));assert.notEqual(palette.fg,palette.bg);}
 await page.locator('#answer').fill('000');await page.getByRole('button',{name:'Unlock →'}).click();assert.match(await page.locator('#feedback').innerText(),/Access denied/);assert.equal(await page.locator('#next').isVisible(),false);
 await page.getByRole('button',{name:'Need a hint?'}).click();assert.match(await page.locator('#hint-text').innerText(),/Count legs/);
 for(const [i,code] of ['463',' crisp ','ham'].entries()){await page.locator('#answer').fill(code);await page.getByRole('button',{name:'Unlock →'}).click();assert.equal(await page.locator('#answer-form').isVisible(),false);await page.locator('#next').click();assert.equal(await page.locator('li.done').count(),i+1);}
 assert.equal(await page.locator('#victory').isVisible(),true);await page.getByRole('button',{name:'Play again'}).click();assert.equal(await page.locator('li.done').count(),0);assert.equal(await page.locator('#answer').inputValue(),'');assert.equal(await page.locator('#hint-text').isVisible(),false);assert.deepEqual(errors,[]);
 }finally{await browser?.close();await new Promise(r=>server.close(r));}
});
