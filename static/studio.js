
const form=document.querySelector('#composer'),status=document.querySelector('#generation-status'),button=form.querySelector('button[type=submit]'),progress=document.querySelector('.generation-progress'),history=document.querySelector('#generation-history');
const controls=['instructions','model','max_tokens','temperature','style'];
function syncTemperature(){document.querySelector('#temperature-value').value=document.querySelector('#temperature').value;}
try{const saved=JSON.parse(localStorage.getItem('sam-generation-settings')||'null');if(saved)for(const key of controls){if(typeof saved[key]==='string')document.getElementById(key).value=saved[key];}}catch{}
syncTemperature();document.querySelector('#temperature').addEventListener('input',syncTemperature);
function saveSettings(){try{localStorage.setItem('sam-generation-settings',JSON.stringify(Object.fromEntries(controls.map(key=>[key,document.getElementById(key).value]))));}catch{}}
controls.forEach(key=>document.getElementById(key).addEventListener('change',saveSettings));
document.querySelector('#original-preset').addEventListener('click',e=>{document.querySelector('#instructions').value=e.currentTarget.dataset.preset;saveSettings();});
let busy=false,db,count=0;
const ready=new Promise(resolve=>{try{const opening=indexedDB.open('sam-generation-history',1);opening.onupgradeneeded=()=>opening.result.createObjectStore('results',{keyPath:'id'});opening.onsuccess=()=>{db=opening.result;const read=db.transaction('results').objectStore('results').getAll();read.onsuccess=()=>{read.result.sort((a,b)=>a.created-b.created).forEach(renderEntry);resolve();};read.onerror=()=>resolve();};opening.onerror=opening.onblocked=()=>resolve();}catch{resolve();}});
function downloadLink(text,href,name){const a=document.createElement('a');a.textContent=text;a.href=href;a.download=name;return a;}
function renderEntry(entry){
 const article=document.createElement('article');article.className='generation'+(entry.image&&entry.result?'':' single');
 const meta=document.createElement('div');meta.className='generation-meta';const kind=document.createElement('span');kind.textContent=entry.image&&entry.result?'Image + text':entry.error?'Partial generation':entry.image?'Earlier image result':'Earlier text result';
 const date=document.createElement('time');date.dateTime=new Date(entry.created).toISOString();date.textContent=new Date(entry.created).toLocaleString(undefined,{month:'short',day:'numeric',hour:'numeric',minute:'2-digit'});meta.append(kind,date);
 const h=document.createElement('h3');h.textContent=entry.prompt;article.append(meta,h);
 const pair=document.createElement('div');pair.className='generation-pair';const actions=document.createElement('div');actions.className='generation-actions';
 if(entry.image){const src='data:image/png;base64,'+entry.image;const figure=document.createElement('figure'),img=document.createElement('img');img.src=src;img.alt=entry.prompt;img.loading='lazy';img.width=1024;img.height=1024;figure.append(img);pair.append(figure);actions.append(downloadLink('Download image',src,'image-'+entry.id+'.png'));}
 if(entry.result){const response=document.createElement('div');response.className='generation-response';response.textContent=entry.result;pair.append(response);const content=entry.prompt+'\n\n'+entry.result;actions.append(downloadLink('Download text','data:text/plain;charset=utf-8,'+encodeURIComponent(content),'text-'+entry.id+'.txt'));}
 article.append(pair,actions);if(entry.error){const note=document.createElement('p');note.className='generation-note';note.textContent=entry.error;article.append(note);}history.prepend(article);count++;document.querySelector('#empty-history').hidden=true;document.querySelector('#history-count').textContent=count;document.querySelector('#nav-count').textContent=count;
}
function saveEntry(entry){return new Promise(resolve=>{if(!db){resolve(false);return;}try{const tx=db.transaction('results','readwrite');tx.objectStore('results').put(entry);tx.oncomplete=()=>resolve(true);tx.onerror=tx.onabort=()=>resolve(false);}catch{resolve(false);}});}
function setStatus(message,error=false){status.textContent=message;status.dataset.error=String(error);}
form.addEventListener('submit',async e=>{
 e.preventDefault();if(busy)return;await ready;if(busy)return;
 const data=new FormData(form);if(!String(data.get('prompt')||'').trim()){setStatus('Write a prompt first, then generate both.',true);document.querySelector('#prompt').focus();return;}
 if(Number(document.querySelector('#remaining').textContent)<=0){setStatus('No image attempts remain on this server. Your saved generations are still below.',true);return;}
 busy=true;button.disabled=true;button.querySelector('span').textContent='Generating…';progress.hidden=false;saveSettings();setStatus('Making your text and image. The image may take a little longer.');
 try{
  const response=await fetch(window.location.pathname,{method:'POST',body:data,headers:{Accept:'application/json'}});
  if(!response.headers.get('content-type')?.includes('application/json'))throw new Error('The server could not finish this request. Your previous generations are still here.');
  const payload=await response.json();if(Number.isInteger(payload.remaining))document.querySelector('#remaining').textContent=payload.remaining;
  if(payload.result||payload.image){const entry={id:crypto.randomUUID(),created:Date.now(),prompt:data.get('prompt'),result:payload.result,image:payload.image,error:payload.error||null};renderEntry(entry);const saved=await saveEntry(entry);if(payload.error)setStatus(payload.error+' The completed part was kept'+(saved?' in your history.':' on this page.'),true);else setStatus(saved?'Your image and text are saved below.':'Your results are below. Browser storage is unavailable; download them before leaving.');}
  else throw new Error(payload.error||'No result came back. Try again when you are ready.');
 }catch(error){setStatus(error.message||'Connection interrupted. Your previous generations are still here.',true);}
 finally{busy=false;button.disabled=false;button.querySelector('span').textContent='Generate both';progress.hidden=true;}
});

// Ambient motion never follows the pointer or competes with the composer.
(()=>{
 const video=document.querySelector('#ambient-video'),canvas=document.querySelector('#ambient-particles'),toggle=document.querySelector('#motion-toggle');
 if(!video||!canvas||!toggle)return;
 const ctx=canvas.getContext('2d'),reduced=matchMedia('(prefers-reduced-motion: reduce)');
 let paused=reduced.matches,frame=0,last=0,w=0,h=0,dots=[];
 try{const saved=localStorage.getItem('sam-ambient-motion');if(saved==='paused')paused=true;}catch{}
 function size(){w=innerWidth;h=innerHeight;const dpr=Math.min(devicePixelRatio||1,2);canvas.width=w*dpr;canvas.height=h*dpr;ctx?.setTransform(dpr,0,0,dpr,0,0);dots=Array.from({length:Math.min(72,Math.floor(w*h/16000))},()=>({x:Math.random()*w,y:Math.random()*h,r:.7+Math.random()*1.4,v:.007+Math.random()*.018,a:.25+Math.random()*.4}));draw(0);}
 function draw(delta){if(!ctx)return;ctx.clearRect(0,0,w,h);for(const p of dots){p.y-=p.v*delta;p.x+=Math.sin(p.y*.006)*delta*.002;if(p.y<0)p.y=h;ctx.beginPath();ctx.arc(p.x,p.y,p.r,0,Math.PI*2);ctx.fillStyle=`rgba(221,226,218,${p.a})`;ctx.fill();}}
 function tick(now){if(paused||document.hidden){frame=0;return;}draw(Math.min(now-last,50));last=now;frame=requestAnimationFrame(tick);}
 function sync(){cancelAnimationFrame(frame);frame=0;toggle.textContent=paused?'Play motion':'Pause motion';toggle.setAttribute('aria-pressed',String(paused));if(paused||document.hidden){video.pause();return;}video.preload='metadata';video.play().catch(()=>{});last=performance.now();frame=requestAnimationFrame(tick);}
 toggle.addEventListener('click',()=>{paused=!paused;try{localStorage.setItem('sam-ambient-motion',paused?'paused':'playing');}catch{}sync();});
 reduced.addEventListener('change',e=>{if(e.matches){paused=true;sync();}});
 document.addEventListener('visibilitychange',sync);window.addEventListener('resize',size,{passive:true});size();sync();
})();
