import test from 'node:test';
import assert from 'node:assert/strict';
import {wizardRoute,wizardUrl,resolveWizardRoute} from './frontend/wizard-route.js';
const id='550e8400-e29b-41d4-a716-446655440000';
test('all wizard steps have round-trip URLs without credentials or inherited query data',()=>{for(let step=1;step<=7;step++){const value=wizardUrl('https://example.com/?token=secret#private',{step,relayId:id,path:'existing'});assert.ok(!value.includes('secret'));assert.deepEqual(wizardRoute(value),{step,relayId:id,path:step===1?'existing':null});}assert.equal(wizardRoute('https://example.com/'),null);assert.equal(wizardUrl('https://example.com'), 'https://example.com/?setup=agent');});
test('recipe links resolve only owned relays and respect unfinished prerequisites',()=>{const recipe=wizardRoute('https://example.com/?setup=agent');assert.equal(resolveWizardRoute(recipe,[]).step,1);const relay={id,config:{setupStage:'invite'}};assert.equal(resolveWizardRoute(recipe,[relay]).step,2);relay.config.setupStage='channel';assert.equal(resolveWizardRoute(recipe,[relay]).step,3);relay.config.verifiedAt='fixture';assert.equal(resolveWizardRoute(recipe,[relay]).step,4);assert.throws(()=>resolveWizardRoute({...recipe,relayId:id},[]),/signed-in account/);});
test('invalid or unrecognized deep links fail visibly',()=>{for(const tail of ['setup=unknown','setup=agent&relay=wrong','setup=bot&bot=unknown'])assert.throws(()=>wizardRoute('https://example.com/?'+tail),/invalid/);assert.throws(()=>wizardUrl('https://example.com',{step:8}),/Unknown/);});

test('generic setup links resume saved progress while deliberate relay navigation stays available',()=>{
 const relay={id,config:{verifiedAt:'saved'}};
 for(const step of [1,2,3,4])assert.equal(resolveWizardRoute({step,relayId:null,path:null},[relay]).step,4);
 assert.equal(resolveWizardRoute({step:1,relayId:id,path:null},[relay]).step,1);
 assert.equal(resolveWizardRoute({step:1,relayId:null,path:'new'},[relay]).step,1);
 delete relay.config.verifiedAt;relay.config.setupStage='invite';assert.equal(resolveWizardRoute({step:1,relayId:null,path:null},[relay]).step,2);
 relay.config.setupStage='channel';assert.equal(resolveWizardRoute({step:1,relayId:null,path:null},[relay]).step,3);
 assert.equal(resolveWizardRoute({step:1,relayId:null,path:null},[]).step,1);
});

test('test and first-task links preserve their stage only after channel verification',()=>{
 for(const step of [5,6,7]){
  const route={step,relayId:id,path:null};
  assert.equal(resolveWizardRoute(route,[{id,config:{verifiedAt:'saved'}}]).step,step);
  assert.equal(resolveWizardRoute({...route,relayId:null},[{id,config:{verifiedAt:'saved'}}]).step,step);
  assert.equal(resolveWizardRoute(route,[{id,config:{setupStage:'channel'}}]).step,3);
 }
});

test('existing installation branch survives reload without accepting unknown choices',()=>{for(const installation of ['present','needed']){const route=wizardRoute(wizardUrl('https://example.com',{step:1,path:'existing',installation}));assert.equal(route.installation,installation);assert.equal(resolveWizardRoute(route,[]).installation,installation);}assert.throws(()=>wizardRoute('https://example.com/?setup=bot&installation=wrong'),/invalid/);});

test('saved task and finish links keep their meaning after the retired runtime stage redirects to joining',()=>{assert.equal(wizardRoute('https://example.com/?setup=runtime').step,6);assert.equal(wizardRoute('https://example.com/?setup=task').step,6);assert.equal(wizardRoute('https://example.com/?setup=finish').step,7);});
