import fs from 'node:fs';
import {fileURLToPath} from 'node:url';

const folder=fileURLToPath(new URL('.',import.meta.url));
const tabs=await(await fetch('http://127.0.0.1:19329/json/list')).json();
const socket=new WebSocket(tabs.find(tab=>tab.type==='page').webSocketDebuggerUrl);
await new Promise(resolve=>socket.addEventListener('open',resolve,{once:true}));
const pending=new Map(), errors=[], events=[];
let id=0;
socket.addEventListener('message',event=>{
  const message=JSON.parse(event.data);
  if(message.method==='Runtime.exceptionThrown')errors.push(message.params.exceptionDetails.text);
  if(message.method==='Tracing.dataCollected')events.push(...message.params.value);
  if(message.id){const promise=pending.get(message.id);pending.delete(message.id);message.error?promise.reject(message.error):promise.resolve(message.result);}
});
const send=(method,params={})=>new Promise((resolve,reject)=>{const seq=++id;pending.set(seq,{resolve,reject});socket.send(JSON.stringify({id:seq,method,params}));});
const evaluate=async expression=>{const result=await send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(result.exceptionDetails)throw Error(result.exceptionDetails.text);return result.result.value;};
const pause=ms=>new Promise(resolve=>setTimeout(resolve,ms));
const checks={};
try{
  await send('Runtime.enable');
  await send('Emulation.setDeviceMetricsOverride',{width:1280,height:960,deviceScaleFactor:1,mobile:false});
  await send('Page.navigate',{url:'http://127.0.0.1:18766/test/echo-voz/index.html'});
  await pause(4500);
  await evaluate('document.fonts.ready');
  checks.casaRealCargada=await evaluate(`!!document.querySelector('iframe').contentWindow.card?.shadowRoot`);
  checks.states={};
  for(const state of ['idle','listening','thinking','replying','news','error']){
    await evaluate(`showVoiceState(${JSON.stringify(state)})`);
    await pause(100);
    checks.states[state]=await evaluate(`(()=>{const box=document.querySelector('.voice').getBoundingClientRect();const close=document.querySelector('.cancel').getBoundingClientRect();return{phase:document.querySelector('.screen').dataset.phase,visible:getComputedStyle(document.querySelector('.voice')).display!=='none',fits:box.top>=0&&box.right<=1280&&box.bottom<=800,cancelFinger:close.width>=72&&close.height>=72}})()`);
    const screenshot=await send('Page.captureScreenshot',{format:'png',clip:{x:0,y:0,width:1280,height:800,scale:1}});
    fs.writeFileSync(`${folder}${state}.png`,Buffer.from(screenshot.data,'base64'));
  }
  await evaluate(`document.querySelector('.cancel').click()`);
  checks.cancelReturnsHome=await evaluate(`document.querySelector('.screen').dataset.phase==='idle'`);
  await evaluate(`showVoiceState('replying')`);
  checks.noAnimationBlur=await evaluate(`[...document.querySelectorAll('.screen,.screen *')].every(node=>{const s=getComputedStyle(node);return s.animationName==='none'&&s.transitionDuration==='0s'&&s.backdropFilter==='none'&&s.filter==='none'})`);
  await send('Tracing.start',{categories:'devtools.timeline',transferMode:'ReportEvents'});
  await pause(2000);
  await send('Tracing.end');
  await pause(200);
  checks.idlePaints=events.filter(event=>event.name==='Paint').length;
  checks.errors=errors;
  if(!checks.casaRealCargada||!checks.cancelReturnsHome||!checks.noAnimationBlur||errors.length||checks.idlePaints)throw Error('Carga, reposo o estilos no verificados');
  if(Object.entries(checks.states).some(([state,c])=>state!=='idle'&&(!c.visible||!c.fits||!c.cancelFinger)))throw Error('Estado recortado o control pequeño');
  fs.writeFileSync(`${folder}checks.json`,JSON.stringify(checks,null,2));
  console.log(JSON.stringify(checks));
}finally{
  await send('Browser.close').catch(()=>{});
  socket.close();
}
