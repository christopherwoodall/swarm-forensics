const puzzles=[
{title:'Emergency Bacon Override',scene:'The airlock refuses to open: “PROVE YOU ARE A PIG, NOT THREE RACCOONS IN A SPACESUIT.” Its keypad needs three digits.',clue:'Enter these answers in order:\n① How many legs does one ordinary pig have?\n② Three astronauts each ordered two bacon strips. How many strips total?\n③ The captain secretly ate three of those strips. How many remain?',answer:'463',hint:'Count legs, multiply breakfast orders, then subtract the captain’s snack.',success:'Airlock open. PIG VERIFIED. Breakfast theft reported to Space HR.'},
{title:'Emergency Bacon Reactor',scene:'Captain Bacon is using the emergency manual as a napkin. Restore power before the ship becomes a very expensive refrigerator.',clue:'Enter the valve letters from coolest to hottest:\nI = 200°   C = 160°   P = 220°\nR = 180°   S = 210°\nEnter the five-letter word.',answer:'CRISP',hint:'Start with C at 160°, then find the next higher temperature.',success:'Power restored! Captain Bacon declares himself perfectly cooked.'},
{title:'Emergency Breakfast Launch',scene:'The station is exploding. Your escape pod demands a three-letter launch code. The onboard pig says, “Please hurry. I am emotionally crispy.”',clue:'LAUNCH CHECKLIST\n2 — Arm the gravy thrusters\n3 — Mute the microwave\n1 — Heat the bacon shields\n\nEnter the first letter of each action, in numbered order.',answer:'HAM',hint:'Put steps 1, 2, 3 in order. Take their first letters.',success:'HAM accepted. The pod is ready for its mighty OINK.'}
];
const $=id=>document.getElementById(id);let stage=0,solved=false;
function render(){
 $('puzzle').hidden=stage===puzzles.length;$('victory').hidden=stage!==puzzles.length;
 $('steps').replaceChildren(...['Airlock','Reactor','Launch'].map((label,i)=>{const li=document.createElement('li');li.textContent=(i<stage?'✓ ':'')+label;li.className=i<stage?'done':i===stage?'current':'';if(i===stage)li.setAttribute('aria-current','step');return li;}));
 if(stage===puzzles.length)return;
 const p=puzzles[stage];for(const key of ['title','scene','clue'])$(key).textContent=p[key];$('station').textContent=`STATION ${stage+1} / 3`;
 $('answer-form').hidden=false;$('answer').value='';$('answer').inputMode=stage===0?'numeric':'text';$('feedback').textContent='';$('feedback').className='feedback';$('hint-text').hidden=true;$('hint').hidden=false;$('next').hidden=true;solved=false;
}
$('answer-form').addEventListener('submit',e=>{e.preventDefault();if(solved)return;const guess=$('answer').value.trim().toUpperCase();if(guess!==puzzles[stage].answer){$('feedback').textContent='Access denied. The pig believes in you. Try again.';return;}solved=true;$('feedback').textContent=puzzles[stage].success;$('feedback').className='feedback success';$('answer-form').hidden=true;$('hint').hidden=true;$('hint-text').hidden=true;$('next').hidden=false;$('next').textContent=stage===2?'Launch escape pod 🚀':'Next station →';$('next').focus();});
$('hint').addEventListener('click',()=>{$('hint-text').textContent=puzzles[stage].hint;$('hint-text').hidden=false;});
$('next').addEventListener('click',()=>{if(!solved)return;stage++;render();if(stage<3)$('answer').focus();else $('replay').focus();});
for(const id of ['restart','replay'])$(id).addEventListener('click',()=>{stage=0;render();$('answer').focus();});render();
