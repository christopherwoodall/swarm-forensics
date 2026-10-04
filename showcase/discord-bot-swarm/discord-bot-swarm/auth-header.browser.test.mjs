import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import {chromium} from '@playwright/test';

test('header identity remains visible and selectable across themes and mobile widths', {timeout:30000}, async()=>{
 const browser=await chromium.launch({headless:true});
 try {
  for(const colorScheme of ['light','dark']) for(const width of [375,1280]) {
   const page=await browser.newPage({viewport:{width,height:800},colorScheme});
   await page.setContent('<div class="workspace-bar"><a class="brand">Swarm</a><div class="workspace-actions"><div id="auth-area"><span class="ar-user-email">signed-in-account@example.com</span><button>Log out</button></div></div></div>');
   await page.addStyleTag({content:await fs.readFile('frontend/style.css','utf8')});
   assert.equal(await page.locator('.ar-user-email').isVisible(),true);
   const state=await page.locator('.ar-user-email').evaluate(el=>{const s=getComputedStyle(el),r=el.getBoundingClientRect();return {select:s.userSelect,right:r.right,left:r.left};});
   assert.notEqual(state.select,'none');assert.ok(state.left>=0 && state.right<=width);
   assert.equal(await page.getByRole('button',{name:'Log out'}).isVisible(),true);
   await page.locator('#auth-area').evaluate(el=>el.replaceChildren());
   assert.equal(await page.locator('.ar-user-email').count(),0);
   await page.close();
  }
 } finally {await browser.close();}
});
