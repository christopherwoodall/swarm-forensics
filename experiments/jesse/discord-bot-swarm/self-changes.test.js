import test from 'node:test';
import assert from 'node:assert/strict';
import {authorizedSelfFields,requestedSelfFields,validateSelfProposal,selfWorkerInstructions} from './self-changes.js';
const human={author:{id:'269751214026129409',bot:false},content:'Semi can you change your profile pic to a griffin?'};
test('explicit owner policy allows channel participants and supports later restriction without trusting names',()=>{
 assert.deepEqual(authorizedSelfFields({},'channel',human,'Semi'),['avatar']);assert.deepEqual(authorizedSelfFields({},'off',human,'Semi'),[]);assert.deepEqual(authorizedSelfFields({},'owner',human,'Semi'),[]);assert.deepEqual(authorizedSelfFields({commandOwnerId:human.author.id},'owner',human,'Semi'),['avatar']);
 for(const source of [{...human,author:{...human.author,bot:true}},{...human,synthetic:true},{...human,author:{name:'Jessald'}},{...human,content:'Semi please build a website'},{...human,content:'change Alice avatar'}])assert.deepEqual(authorizedSelfFields({},'channel',source,'Semi'),[]);
});
test('only requested self fields can be proposed; no raw URLs or controller commands',()=>{
 assert.deepEqual(requestedSelfFields({...human,content:'Semi change your personality to be quieter and your name to Semington'},'Semi'),['username','personality']);
 assert.deepEqual(validateSelfProposal({personality:'quieter'},['personality']),{personality:'quieter'});
 for(const change of [{username:'Other'},{command:'shell'},{avatar:'https://example.com/image.png'},{avatar:null},{}])assert.throws(()=>validateSelfProposal(change,['avatar']));
 assert.equal(validateSelfProposal(undefined,[]),null);
});
test('self-change worker gets narrowly scoped image generation, source field limits and receipt instructions',()=>{
 const text=selfWorkerInstructions(['avatar']);for(const phrase of ['ONLY these changes','avatar','built-in image_gen','350000','256×256','selfChangeReceipt','Do not alter Discord directly'])assert.ok(text.includes(phrase));assert.equal(selfWorkerInstructions([]),'');
});
