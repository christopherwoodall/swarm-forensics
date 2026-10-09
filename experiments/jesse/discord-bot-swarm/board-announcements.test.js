import {test} from 'node:test';
import assert from 'node:assert/strict';
import {announcementText,announcementNonce} from './board-announcements.js';

test('announcements are one bounded line with a board link',()=>{
 const origin='https://swarm.example',task={title:'Fix   the\nqueue',note:'Shipped in v1.\nVerified over HTTPS. '+'x'.repeat(400)};
 assert.equal(announcementText('claim',task,origin),'Claimed “Fix the queue” <https://swarm.example/board.html>');
 const done=announcementText('done',task,origin);assert.match(done,/^Finished “Fix the queue”: Shipped in v1\. Verified over HTTPS\. x+… <https:\/\/swarm\.example\/board\.html>$/);assert.ok(done.length<=400);assert.ok(!/[\r\n]/.test(done));
 assert.equal(announcementText('blocked',{title:'T',note:''},origin),'Blocked on “T” <https://swarm.example/board.html>');
 assert.throws(()=>announcementText('renew',task,origin),/Unknown board announcement action/);
});

test('nonces are stable per event and fit Discord limits',()=>{
 assert.equal(announcementNonce(7),announcementNonce(7));assert.notEqual(announcementNonce(7),announcementNonce(8));assert.match(announcementNonce(7),/^\d{1,25}$/);
});
