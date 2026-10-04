// One bounded lifecycle per image source; obsolete decodes cannot complete a newer load.
export function wizardImage(image,frame,{onState=()=>{},timeoutMs=15000}={}){
 const overlay=document.createElement('div');overlay.className='image-loading';overlay.setAttribute('role','status');
 const spinner=document.createElement('span');spinner.className='image-spinner';spinner.setAttribute('aria-hidden','true');
 const text=document.createElement('span');const retry=document.createElement('button');retry.type='button';retry.className='secondary';retry.textContent='Retry image';retry.hidden=true;
 overlay.append(spinner,text,retry);frame.classList.add('wizard-image');frame.append(overlay);
 let generation=0,timer,source,alternative;
 function state(value,message){frame.dataset.imageState=value;frame.setAttribute('aria-busy',String(value==='loading'));image.style.visibility=value==='ready'?'visible':'hidden';overlay.hidden=value==='ready';spinner.hidden=value!=='loading';retry.hidden=value!=='failed';text.textContent=message;onState(value);}
 function load(src,alt){source=src;alternative=alt;const current=++generation;clearTimeout(timer);state('loading','Loading image…');
  const fail=message=>{if(current!==generation)return;clearTimeout(timer);generation++;image.onload=image.onerror=null;state('failed',message);};
  image.onload=async()=>{try{await image.decode();if(current!==generation)return;clearTimeout(timer);image.onload=image.onerror=null;state('ready','');}catch{fail('Image could not be displayed.');}};
  image.onerror=()=>fail('Image could not load.');timer=setTimeout(()=>fail('Image loading timed out.'),timeoutMs);image.alt=alt;image.src=src;
 }
 retry.onclick=()=>{const u=new URL(source,document.baseURI);u.searchParams.set('image_retry',String(Date.now()));load(u.href,alternative);};
 return {load};
}
