import {test} from 'node:test';
import assert from 'node:assert/strict';
import {chatConfig,savedChat} from './chat-settings.js';
test('chat preferences contain no provider or model fields',()=>{assert.deepEqual(chatConfig(),{mode:'normal',cooldownSeconds:0,maxRepliesPerHour:30});for(const bad of [{provider:'openai'},{model:'any'},{mode:'always'},{cooldownSeconds:-1},{maxRepliesPerHour:121}])assert.throws(()=>chatConfig(bad));});
test('legacy chat settings preserve owner preferences while removing API key path',()=>{assert.deepEqual(savedChat({chat:{mode:'normal',provider:'openai',model:'legacy',cooldownSeconds:20,maxRepliesPerHour:10}}),{mode:'normal',cooldownSeconds:20,maxRepliesPerHour:10});});
test('brief reply style is saved per connection without changing existing defaults or budgets',()=>{
 const chat={mode:'normal',cooldownSeconds:20,maxRepliesPerHour:10,replyStyle:'brief'};
 assert.deepEqual(chatConfig(chat),chat);assert.deepEqual(savedChat({chat}),chat);
 assert.equal(savedChat({}).replyStyle,undefined);
 for(const replyStyle of [null,true,1,'long'])assert.throws(()=>chatConfig({replyStyle}));
});
