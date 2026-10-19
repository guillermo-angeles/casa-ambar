const VERSION = "2.1.2";

const RUTA_FUENTES = "/local/casa-ambar/fonts/";
const FUENTES_CSS = `
@font-face { font-family: "Inter"; font-style: normal; font-weight: 100 900; font-display: swap; src: url(${RUTA_FUENTES}inter-latin-ext.woff2) format("woff2"); unicode-range: U+0100-02BA, U+02BD-02C5, U+02C7-02CC, U+02CE-02D7, U+02DD-02FF, U+0304, U+0308, U+0329, U+1D00-1DBF, U+1E00-1E9F, U+1EF2-1EFF, U+2020, U+20A0-20AB, U+20AD-20C4, U+2113, U+2C60-2C7F, U+A720-A7FF; }
@font-face { font-family: "Inter"; font-style: normal; font-weight: 100 900; font-display: swap; src: url(${RUTA_FUENTES}inter-latin.woff2) format("woff2"); unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD; }
`;

if (!document.getElementById("casa-ambar-fuentes")) {
  const estiloFuentes = document.createElement("style");
  estiloFuentes.id = "casa-ambar-fuentes";
  estiloFuentes.textContent = FUENTES_CSS;
  document.head.appendChild(estiloFuentes);
}

const TIEMPO_ES = {
  "clear-night": "Despejado",
  cloudy: "Nublado",
  exceptional: "Aviso excepcional",
  fog: "Niebla",
  hail: "Granizo",
  lightning: "Tormenta",
  "lightning-rainy": "Tormenta con lluvia",
  partlycloudy: "Intervalos nubosos",
  pouring: "Lluvia intensa",
  rainy: "Lluvia",
  snowy: "Nieve",
  "snowy-rainy": "Aguanieve",
  sunny: "Soleado",
  windy: "Viento",
  "windy-variant": "Viento y nubes",
};

const SVG_DEFS = `<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>
<radialGradient id="ca-sol" cx="40%" cy="38%" r="70%"><stop offset="0" stop-color="#FFF1A8"/><stop offset=".55" stop-color="#FFC93D"/><stop offset="1" stop-color="#FF9F1C"/></radialGradient>
<linearGradient id="ca-luna" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FFFBEF"/><stop offset="1" stop-color="#CFC8B6"/></linearGradient>
<linearGradient id="ca-nube" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFFFFF"/><stop offset="1" stop-color="#D5DDE8"/></linearGradient>
<linearGradient id="ca-nube-osc" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#C9D1DD"/><stop offset="1" stop-color="#8793A6"/></linearGradient>
<linearGradient id="ca-gota" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#9AD4FF"/><stop offset="1" stop-color="#4AA3FF"/></linearGradient>
</defs></svg>`;

const P = {
  sol: '<g><circle cx="32" cy="32" r="12.5" fill="url(#ca-sol)"/><g stroke="#FFC23A" stroke-width="3.2" stroke-linecap="round"><path d="M32 7.5v5M32 51.5v5M7.5 32h5M51.5 32h5M14.7 14.7l3.5 3.5M45.8 45.8l3.5 3.5M14.7 49.3l3.5-3.5M45.8 18.2l3.5-3.5"/></g></g>',
  solPeq: '<g><circle cx="23" cy="23" r="10" fill="url(#ca-sol)"/><g stroke="#FFC23A" stroke-width="2.8" stroke-linecap="round"><path d="M23 4.5v4M4.5 23h4M9.9 9.9l2.8 2.8M36.1 9.9l-2.8 2.8M9.9 36.1l2.8-2.8"/></g></g>',
  luna: '<path d="M44 38.5A17 17 0 0 1 25.5 14a17 17 0 1 0 18.5 24.5z" fill="url(#ca-luna)"/>',
  lunaPeq: '<path d="M33 27A12 12 0 0 1 19.5 9.5a12 12 0 1 0 13.5 17.5z" fill="url(#ca-luna)"/>',
  nube: '<path d="M19 50h28a10.5 10.5 0 0 0 1.6-20.9A15 15 0 0 0 20 31.6 9.3 9.3 0 0 0 19 50z" fill="url(#ca-nube)"/>',
  nubeOsc: '<path d="M19 46h28a10.5 10.5 0 0 0 1.6-20.9A15 15 0 0 0 20 27.6 9.3 9.3 0 0 0 19 46z" fill="url(#ca-nube-osc)"/>',
  nubeAlta: '<path d="M19 44h28a10.5 10.5 0 0 0 1.6-20.9A15 15 0 0 0 20 25.6 9.3 9.3 0 0 0 19 44z" fill="url(#ca-nube)"/>',
  nubeTrasera: '<path d="M33 34h18a8 8 0 0 0 1.2-15.9A11.5 11.5 0 0 0 31 20.3 7 7 0 0 0 33 34z" fill="#AEB9C8" opacity=".85"/>',
  lluvia: '<g stroke="url(#ca-gota)" stroke-width="3.2" stroke-linecap="round"><path d="M24 51l-2 6M33 51l-2 6M42 51l-2 6"/></g>',
  chaparron: '<g stroke="url(#ca-gota)" stroke-width="3.2" stroke-linecap="round"><path d="M21 50l-2.5 8M29 50l-2.5 8M37 50l-2.5 8M45 50l-2.5 8"/></g>',
  nieve: '<g fill="#F2F7FF"><circle cx="23" cy="53" r="2.6"/><circle cx="32" cy="57" r="2.6"/><circle cx="41" cy="53" r="2.6"/></g>',
  aguanieve: '<g><path d="M23 50l-2 6" stroke="url(#ca-gota)" stroke-width="3.2" stroke-linecap="round"/><circle cx="32" cy="55" r="2.6" fill="#F2F7FF"/><path d="M42 50l-2 6" stroke="url(#ca-gota)" stroke-width="3.2" stroke-linecap="round"/></g>',
  granizo: '<g fill="#E4F1FF" stroke="#9CC9F2" stroke-width="1"><circle cx="23" cy="54" r="3"/><circle cx="32" cy="57" r="3"/><circle cx="41" cy="54" r="3"/></g>',
  rayo: '<path d="M34 43l-8 11h6l-3 9 10-13h-6l3-7z" fill="#FFD23F"/>',
  niebla: '<g stroke="#E6ECF3" stroke-width="3.2" stroke-linecap="round"><path d="M14 52h36M18 58h28"/></g>',
  viento: '<g fill="none" stroke="#EAF1F8" stroke-width="3.2" stroke-linecap="round"><path d="M8 26h30a6 6 0 1 0-6-6"/><path d="M8 35h40a6 6 0 1 1-6 6"/><path d="M8 44h20"/></g>',
  aviso: '<path d="M32 9l25 44H7z" fill="#FFB020"/><path d="M32 25v14M32 45.5v.5" stroke="#3A2400" stroke-width="4" stroke-linecap="round"/>',
};

const dibujoTiempo = (cond, deNoche) => {
  const astro = deNoche ? P.lunaPeq : P.solPeq;
  const map = {
    sunny: deNoche ? P.luna : P.sol,
    "clear-night": P.luna,
    partlycloudy: astro + P.nube,
    cloudy: P.nubeTrasera + P.nube,
    rainy: P.nubeAlta + P.lluvia,
    pouring: P.nubeOsc + P.chaparron,
    snowy: P.nubeAlta + P.nieve,
    "snowy-rainy": P.nubeAlta + P.aguanieve,
    hail: P.nubeAlta + P.granizo,
    lightning: P.nubeOsc + P.rayo,
    "lightning-rainy": P.nubeOsc + P.lluvia + P.rayo,
    fog: P.nubeAlta + P.niebla,
    windy: P.viento,
    "windy-variant": P.nubeTrasera + P.viento,
    exceptional: P.aviso,
  };
  return `<svg viewBox="0 0 64 64" aria-hidden="true">${map[cond] || P.nube}</svg>`;
};

const paths={home:'<path d="M3 10l9-7 9 7v10H4V10M9 20v-7h6v7"/>',clock:'<circle cx="12" cy="12" r="9"/><path d="M12 6v6l4 2"/>',sun:'<circle cx="12" cy="12" r="4"/><path d="M12 1v2M12 21v2M1 12h2M21 12h2M4 4l2 2M18 18l2 2M4 20l2-2M18 6l2-2"/>',sunset:'<path d="M7 16a5 5 0 0 1 10 0M2 17h20M5 21h14M12 3v3M4 8l2 2M20 8l-2 2"/>',bulb:'<path d="M9 18h6M10 21h4M8 15a7 7 0 1 1 8 0l-1 3H9z"/>',floor:'<path d="M7 3h10l3 9H4zM12 12v9M7 21h10"/>',led:'<rect x="3" y="4" width="18" height="12" rx="2"/><path d="M7 20h10M12 16v4M6 8h12"/>',sofa:'<path d="M6 11V8a3 3 0 0 1 3-3h6a3 3 0 0 1 3 3v3M6 15h12M4 20v-2M20 20v-2M3 12a2 2 0 0 1 4 0v3h10v-3a2 2 0 0 1 4 0v6H3z"/>',dining:'<path d="M12 2v5M6 15a6 6 0 0 1 12 0H6zM3 18h18M12 18v4"/>',tune:'<path d="M3 6h18M3 18h18M8 3v6M16 15v6"/>',tv:'<rect x="2" y="4" width="20" height="14" rx="3"/><path d="M8 22h8M12 18v4"/>',music:'<path d="M9 18V5l11-2v12"/><ellipse cx="6" cy="18" rx="3" ry="2.5"/><ellipse cx="17" cy="15" rx="3" ry="2.5"/>',power:'<path d="M12 2v10M6 5a9 9 0 1 0 12 0"/>',lock:'<rect x="5" y="10" width="14" height="11" rx="3"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/>',unlock:'<rect x="5" y="10" width="14" height="11" rx="3"/><path d="M8 10V7a4 4 0 0 1 7.5-2"/>',camera:'<rect x="2" y="5" width="14" height="14" rx="3"/><path d="M16 10l6-4v12l-6-4"/>',moon:'<path d="M21 14a9 9 0 0 1-11-11 9 9 0 1 0 11 11z"/>',bed:'<path d="M3 20V10h18v10M3 16h18M6 10V5h12v5M12 5v5"/>',cine:'<rect x="3" y="7" width="18" height="14" rx="3"/><path d="M3 7l3-4h15l-3 4M9 3L6 7M15 3l-3 4"/>'};
paths.play='<path d="M8 4l12 8-12 8z" fill="currentColor" stroke="none"/>';
paths.pause='<path d="M8 5v14M16 5v14" stroke-width="5"/>';
paths.next='<path d="M5 5l10 7-10 7z" fill="currentColor" stroke="none"/><path d="M19 5v14" stroke-width="3"/>';
const icon=name=>`<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${paths[name]||paths.bulb}</svg>`;

const ESTILOS = `

*{box-sizing:border-box}:host{margin:0;background:#302721;font-family:Inter,system-ui,sans-serif;color:#483630}button,input{font:inherit}button{border:0;cursor:pointer;color:inherit;-webkit-tap-highlight-color:transparent}button:focus-visible,input:focus-visible{outline:3px solid #6d444c;outline-offset:5px}button:active{box-shadow:inset 0 0 0 3px #bf9364}button:disabled{cursor:default}[hidden]{display:none!important}h1,h2,p{margin:0}svg{width:100%;height:100%;display:block}.icon{width:36px;height:36px;display:block;flex:none}.screen{position:relative;width:1280px;height:800px;overflow:hidden;background:linear-gradient(115deg,#f0d5aa,#f0c0a9);padding:32px;touch-action:manipulation}.top{display:flex;align-items:center;gap:12px;height:52px}.brand-icon{width:44px;height:44px;padding:10px;border-radius:16px;background:#f9e7cb}.brand{font-size:25px;font-weight:650;letter-spacing:-1px}.demo{margin-left:auto;font-size:16px;color:#725444}.ambient{position:absolute;left:32px;top:120px;width:296px;bottom:32px;display:flex;flex-direction:column}.hello{font-size:23px;font-weight:500}.clock{font-size:114px;font-weight:500;letter-spacing:-8px;line-height:1.12;margin:12px 0 0 -5px;font-variant-numeric:tabular-nums}.date{font-size:21px;color:#725444;margin-top:8px}.weather{display:flex;gap:16px;align-items:center;margin-top:26px}.weather .icon{width:64px;height:64px;color:#a46c2d}.temperature{font-size:48px;letter-spacing:-2px;font-weight:500}.conditions{font-size:21px;line-height:1.5;color:#725444;margin-top:5px}.weather-detail{margin-top:15px;font-size:18px;color:#725444}.player{margin-top:auto;background:#f9ead5;border-radius:28px;padding:22px}.track-name{font-size:23px;line-height:1.35;font-weight:600;letter-spacing:-.5px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;min-height:62px}.player-controls{display:flex;gap:16px;margin-top:14px}.play{width:80px;height:80px;border-radius:50%;background:#79515a;color:#fff4e8;display:grid;place-items:center}.play .icon{width:30px;height:30px}.next{width:80px;height:80px;border-radius:50%;background:#e9d8bf;display:grid;place-items:center}.room-strip{position:absolute;left:360px;top:120px;right:32px;bottom:32px;overflow-x:auto;overflow-y:hidden;touch-action:pan-x;scrollbar-width:none;overscroll-behavior-x:contain;contain:layout paint;user-select:none;-webkit-user-select:none}.room-strip::-webkit-scrollbar{display:none}.track{display:flex;gap:28px;width:max-content;height:100%;padding-right:0}.room{width:392px;flex:none}.room h2{font-size:33px;letter-spacing:-1px;font-weight:600;margin-bottom:8px}.room-sub{font-size:18px;color:#775747;margin-bottom:24px}.grid{display:grid;grid-template-columns:188px 188px;gap:16px}.light{width:188px;height:188px;border-radius:28px;background:#815760;color:#fff1e5;padding:22px;text-align:left;display:flex;flex-direction:column;align-items:flex-start;touch-action:pan-x}.light.on{background:#fff8ed;color:#4a3730}.light .icon{width:44px;height:44px;color:#ffdfae}.light.on .icon{color:#9b6c2d}.light-name{font-size:24px;font-weight:600;letter-spacing:-.7px;margin-top:auto}.light-state{font-size:18px;opacity:.8;margin-top:7px}.light.unavailable{background:#a88383;color:#fff6ef}.light.unavailable .icon{color:#eed5c9}.device{border-radius:28px;background:#f8e7ce;padding:22px;margin-top:16px;display:flex;align-items:center;gap:14px;min-height:110px}.device-name{font-size:23px;font-weight:600;letter-spacing:-.6px}.device-state{font-size:18px;color:#7a5e49;margin-top:6px}.device-body{flex:1}.device button{height:66px;min-width:100px;border-radius:22px;background:#79515a;color:#fff4e8;padding:0 16px;font-size:19px}.hall .grid{align-items:start}.lock-card{width:188px;height:188px;border-radius:28px;background:#f8e7ce;padding:22px;display:flex;flex-direction:column;justify-content:space-between}.lock-card .icon{color:#96703d}.lock-card p{font-size:23px;font-weight:600}.lock-card small{font-size:18px;color:#765d48;display:block;margin-top:7px}.camera{width:100%;text-align:left}.camera .icon{color:#896346}.room-note{font-size:18px;line-height:1.6;color:#765747;margin-top:24px}.overlay{position:absolute;inset:0;z-index:10;background:rgba(63,39,38,.40);display:grid;place-items:center}.modal{width:560px;height:694px;border-radius:38px;background:#fbf1e2;padding:30px;position:relative;display:flex;align-items:center;flex-direction:column}.modal h2{font-size:31px;letter-spacing:-1px;margin-top:3px}.modal-sub{font-size:19px;color:#795f4b;margin-top:8px}.close{position:absolute;right:22px;top:22px;width:64px;height:64px;border-radius:50%;background:#e9d8c1;font-size:30px}.percent{font-size:55px;letter-spacing:-2px;font-weight:550;margin-top:22px}.brightness-control{display:flex;align-items:center;gap:28px;margin-top:20px}.step{width:72px;height:72px;border-radius:50%;font-size:34px;background:#e9d8c1}.slider{position:relative;width:148px;height:345px;overflow:hidden;border-radius:37px;background:#e3d1b8;touch-action:none;cursor:ns-resize}.slider-fill{position:absolute;bottom:0;left:0;right:0;background:#b17a39;pointer-events:none}.slider .icon{position:absolute;bottom:22px;left:52px;width:44px;height:44px;color:#fff8e8;pointer-events:none}.done{height:64px;width:220px;border-radius:24px;background:#79515a;color:#fff4e8;font-size:22px;font-weight:550;margin-top:24px}.toast{position:absolute;left:390px;bottom:42px;padding:18px 24px;background:#fff6e7;border-radius:22px;font-size:20px;z-index:20}

.lock{height:212px;margin-top:16px;padding:23px;background:linear-gradient(145deg,#f7ecdb,#e4ceb1);color:#44362c}.lock-top{display:flex;gap:14px;align-items:center}.lock .icon{width:40px;height:40px;color:#966a2c}.lock-title{font-size:21px;color:#66513e}.lock-state{font-size:30px;font-weight:600;letter-spacing:-.03em;margin-top:4px}.lock-action{height:53px;margin-top:21px;border-radius:27px;background:#5e4637;color:#fff5e6;width:100%;font-size:22px;font-weight:600}.lock-action:disabled{background:#ddd0bc;color:#5f503e}.camera{height:128px;width:100%;margin-top:16px;padding:22px;text-align:left;background:linear-gradient(145deg,#75564e,#59414a)}.camera-head{display:flex;align-items:center;gap:12px}.camera .icon{width:34px;height:34px;color:#ffdfb2}.camera-name{font-size:25px;font-weight:600;letter-spacing:-.02em}.camera-copy{font-size:20px;color:#f1dccb;margin-top:13px}.camera-link{font-size:19px;color:#ffe8c6;margin-top:7px;font-weight:600}.local-panel{position:absolute;z-index:6;right:32px;top:180px;width:356px;padding:24px;background:#f9efdf;color:#44352d;border-radius:30px;box-shadow:0 0 0 1px #e1cdb2}.local-panel h2{font-size:28px}.local-panel p{font-size:21px;line-height:1.5;margin-top:14px}.panel-close{height:52px;margin-top:20px;border-radius:26px;background:#5e4637;color:#fff5e6;padding:0 24px;font-size:21px}.panel-modes{display:grid;gap:10px;margin-top:20px}.panel-modes button{height:50px;background:#e6d7c2;color:#4a372c;border-radius:18px;font-size:22px}.reposo{position:absolute;inset:0;padding:55px;display:flex;flex-direction:column;justify-content:space-between;cursor:pointer}.rest-top{display:flex;justify-content:space-between;align-items:flex-start}.rest-greeting{font-size:32px;color:#f9e5d5;letter-spacing:-.025em}.rest-date{font-size:34px;margin-top:10px;font-weight:500;letter-spacing:-.025em}.rest-weather{text-align:right;display:flex;align-items:center;gap:20px}.rest-weather .icon{width:96px;height:96px;color:#ffda9d}.rest-temp{font-size:76px;letter-spacing:-.055em;font-weight:500}.rest-cond{font-size:25px;color:#f1dcca;margin-top:3px}.rest-time{font-size:260px;line-height:.9;letter-spacing:-.075em;font-weight:500;font-variant-numeric:tabular-nums;margin-left:-12px}.rest-bottom{display:flex;align-items:flex-end;justify-content:space-between}.rest-status{display:flex;gap:12px;margin-top:30px}.rest-chip{padding:14px 22px;border-radius:28px;font-size:23px;background:rgba(49,31,39,.76);border:1px solid var(--line)}.rest-open{border-radius:50%;width:76px;height:76px;background:#f5e5d0;color:#634a38;padding:23px}.night{position:absolute;inset:0;background:#070504;display:flex;align-items:center;justify-content:center;flex-direction:column;cursor:pointer}.night-time{font-size:240px;letter-spacing:-.07em;font-weight:400;color:#ae6e39;font-variant-numeric:tabular-nums}.night-copy{font-size:26px;color:#ad7950}.night-open{background:none;font-size:18px;color:#966b49;position:absolute;bottom:40px}.lock-actions{display:flex;gap:10px;margin-top:21px}.lock-actions .lock-action{margin-top:0;flex:1;width:auto}.lock-cancel{height:53px;padding:0 13px;font-size:19px;background:#d9c4a7;color:#4f3d2e;border-radius:27px}.camera{color:#fff5ea}.lock{height:212px;background:#fff1d9;color:#44302c}.lock-action{height:80px;margin-top:0;border-radius:25px;background:#725044;font-size:23px}.lock-actions{margin-top:19px;gap:16px}.lock-cancel{height:80px;padding:0 18px;font-size:22px;border-radius:25px}.lock-state{font-size:30px}.lock-title{color:#66513e}.lock-action:disabled{background:#e3d1b8;color:#614b3a}.camera{background:#80565c}.camera-copy,.camera-link{color:#fff0e3}.camera-copy{margin-top:9px}.camera-link{margin-top:5px}.local-panel{top:190px;background:#fff7e8;width:356px;padding:24px}.panel-close{height:80px;width:100%;font-size:24px;border-radius:25px}.panel-modes{grid-template-columns:1fr 1fr;gap:16px}.panel-modes button{height:80px;font-size:23px;border-radius:24px}.mode-panel{right:32px;width:500px}.mode-panel .panel-modes{grid-template-columns:repeat(2,1fr)}.rest-greeting,.rest-date,.rest-time{color:#4c3431}.rest-weather .icon{color:#915b20}.rest-temp{color:#4c3431}.rest-cond{color:#694b40}.rest-chip{background:#775057;color:#fff5e9;border-color:#775057}.rest-open{width:88px;height:88px;background:#fff1d9;padding:27px}.night-open{min-height:80px;padding:0 24px;border-radius:25px}.camera-name{font-size:24px}.camera-preview{width:100%;height:190px;object-fit:contain;border-radius:18px;margin-top:14px;background:#e6d6c1}.camera-retry{height:80px;width:100%;border-radius:25px;background:#e6d6c1;color:#4d372c;font-size:23px;margin-top:16px}.reposo,.night{touch-action:manipulation}
:host{display:block;height:var(--ca-alto,800px)}.screen{width:100%;height:var(--ca-alto,800px);line-height:normal}.ambient{top:120px;height:auto}.room-strip{display:flex;gap:28px;width:auto;height:auto;scroll-behavior:auto;scroll-snap-type:none}.room-column{width:392px;flex:none}.light-grid{display:grid;grid-template-columns:188px 188px;gap:16px}.light-main{width:100%;height:100%;padding:22px;display:flex;flex-direction:column;align-items:flex-start;text-align:left;background:none;color:inherit;border-radius:28px;touch-action:pan-x}.light{padding:0;overflow:hidden;position:relative}.light-adjust{position:absolute;right:10px;top:10px;width:72px;height:72px;display:grid;place-items:center;border-radius:22px;background:#ead8bc;color:#775330}.light-adjust .icon{width:28px;height:28px;color:inherit}.light.off .light-adjust{background:#69434e;color:#ffdfae}.light.unavailable .light-adjust{background:#a88383;color:#eed5c9}.light-main .light-name{margin-top:auto}.light-body{display:contents}.light-state{white-space:nowrap}.greeting{font-size:23px;font-weight:500}.weather-copy{font-size:19px;line-height:1.6;color:#725444}.degrees{font-size:44px;letter-spacing:-2px}.sun{width:56px;height:56px;flex:none}.weather{gap:10px}.ambient .weather{flex-wrap:wrap}.weather-copy{flex-basis:100%}.top-right{margin-left:auto;display:flex;gap:14px}.header-modes,.tiny{height:72px;border-radius:24px;padding:0 20px;background:#f8e7ce;font-size:20px}.tiny .icon{display:none}.brandmark{width:44px;height:44px;padding:10px;background:#f9e7cb;border-radius:16px}.section-title{font-size:33px;font-weight:600;height:69px;margin:0;display:flex;align-items:flex-start}.section-sub{display:none}.media{display:flex;align-items:center;gap:14px;margin-top:16px;height:110px;padding:18px;background:#f8e7ce;border-radius:28px}.media-art{width:36px;height:36px;flex:none}.media-text{flex:1;min-width:0}.media-name{font-size:23px;font-weight:600}.media-state{font-size:18px;margin-top:6px;color:#7a5e49}.tv-power{height:72px;padding:0 16px;background:#79515a;color:#fff4e8;border-radius:24px;font-size:20px}.recibidor .lock{height:212px;margin-top:16px;border-radius:28px}.lock-actions{display:flex;gap:12px;margin-top:15px}.lock-actions .lock-action{flex:1;width:auto;height:80px;margin:0;font-size:22px}.lock-cancel{height:80px;border-radius:24px;font-size:20px}.camera{height:110px;margin-top:16px;border-radius:28px;background:#f8e7ce;color:#483630}.camera-copy,.camera-link{display:none}.camera-name{font-size:23px}.camera .icon{color:#896346}.camera-head{display:flex;align-items:center;gap:14px}.local-panel{z-index:15}.brightness{position:absolute;inset:0;z-index:12;background:rgba(63,39,38,.4);display:grid;place-items:center}.brightness-title{font-size:31px;letter-spacing:-1px;margin-top:3px}.brightness-current{font-size:55px;letter-spacing:-2px;font-weight:550;margin-top:22px}.brightness-close{height:64px;width:220px;border-radius:24px;background:#79515a;color:#fff4e8;font-size:22px;margin-top:24px}.brightness .modal{height:694px}.brightness-message{font-size:17px;color:#795f4b;min-height:22px;margin-top:8px}.brightness .done{margin-top:8px}.player button:disabled{opacity:.45}.toast{max-width:800px}.room-strip button{touch-action:pan-x}.rest-time{line-height:1}.reposo{background:linear-gradient(115deg,#f0d5aa,#f0c0a9)}.rest-greeting,.rest-cond,.rest-date{color:#725444}.rest-chip{background:#f8e7ce;color:#483630}.night{background:#070504}.room-strip:focus-visible{outline:3px solid #79515a;outline-offset:4px}
`;

const PLANTILLA = `${SVG_DEFS}
<main class="screen" aria-label="Casa Ámbar">
<header class="top"><div class="brandmark" data-icon="home"></div><span class="brand">Casa Ámbar</span><div class="top-right"><span id="page-description">Estancias</span><button class="header-modes" data-action="modes">Modos</button><button class="tiny" data-action="rest"><span class="icon" data-icon="clock"></span>Reloj</button></div></header>
<aside class="ambient" id="ambient"><p class="greeting"></p><p class="clock"></p><p class="date"></p><div class="weather"><div class="sun" data-icon="sun"></div><span class="degrees">—</span><div class="weather-copy">Sin datos del tiempo<br><span class="extremos"></span></div></div><section class="player" aria-label="Reproductor Spotify"><p class="track-name" id="track-name">Spotify en espera</p><div class="player-controls"><button class="play" data-action="music" aria-label="Reproducir Spotify" disabled><span class="icon" id="music-icon"></span></button><button class="next" data-action="next" aria-label="Siguiente canción" disabled><span class="icon" data-icon="next"></span></button></div></section></aside>
<div class="room-strip" id="room-strip" tabindex="0" role="region" aria-label="Estancias. Desplazamiento horizontal: salón, recibidor, cocina y dormitorio.">
<section class="room-column salon"><h1 class="section-title">Salón<span class="section-sub" id="salon-count"></span></h1><div class="light-grid" id="lights"></div><div class="card media"><div class="media-art" data-icon="tv"></div><div class="media-text"><p class="media-name">TV del salón</p><p class="media-state" id="tv-state">Sin datos</p></div><button class="tv-power" data-action="tv">Encender</button></div></section>
<section class="room-column recibidor"><h2 class="section-title">Recibidor</h2><div id="hall-lights"></div>
<div class="card lock"><div class="lock-top"><span class="icon" id="lock-icon" data-icon="unlock"></span><div><p class="lock-title">Cerrojo</p><p class="lock-state" id="lock-state">Sin datos</p></div></div><div class="lock-actions"><button class="lock-action" data-action="lock">Echar llave</button><button class="lock-cancel" data-action="cancel-lock" hidden>Cancelar</button></div></div><button class="card camera" data-action="camera"><div class="camera-head"><span class="icon" data-icon="camera"></span><span class="camera-name">Cámara del recibidor</span></div><p class="camera-copy">Una imagen al tocar</p><p class="camera-link">Ver imagen</p></button></section>
<section class="room-column cocina"><h2 class="section-title">Cocina</h2><div class="light-grid" id="cocina-lights"></div>
</section>
<section class="room-column dormitorio"><h2 class="section-title">Dormitorio</h2><div class="light-grid" id="dormitorio-lights"></div>
</section>
</div>
</div>
<section class="reposo" id="reposo" hidden aria-label="Cara Reposo de demostración"><div class="rest-top"><div><p class="rest-greeting"></p><p class="rest-date"></p></div><div class="rest-weather"><span class="icon" data-icon="sun"></span><div><p class="rest-temp">—</p><p class="rest-cond">Sin datos del tiempo</p></div></div></div><div class="rest-bottom"><div><p class="rest-time"></p><div class="rest-status"><span class="rest-chip">Modo sin datos</span><span class="rest-chip">Cerrojo sin datos</span></div></div><button class="rest-open" aria-label="Abrir controles de casa" data-action="home" data-icon="home"></button></div></section>
<section class="night" id="night" hidden aria-label="Cara Noche de demostración"><p class="night-time"></p><p class="night-copy">Modo sin datos</p><button class="night-open" data-action="home">Toca para ver tu casa</button></section>
<div class="local-panel" id="panel" hidden role="dialog" aria-modal="true" aria-labelledby="panel-title"><h2 id="panel-title"></h2><div id="panel-content"></div><button class="panel-close" data-action="close">Volver</button></div><div class="toast" role="status" aria-live="polite" hidden></div>
</main>
`;

const LUCES = [
  { id: 'sofa', entity: 'light.lampara_sofa', name: 'Sofá', icon: 'sofa', dim: true, container: 'lights' },
  { id: 'comedor', entity: 'light.lampara_comedor', name: 'Comedor', icon: 'dining', dim: true, container: 'lights' },
  { id: 'pie', entity: 'light.lampara_pie', name: 'Pie', icon: 'floor', dim: true, container: 'lights' },
  { id: 'led', entity: 'light.led_tv', name: 'LED TV', icon: 'led', dim: false, container: 'lights' },
  { id: 'entrada', entity: 'light.lampara_recibidor', name: 'Entrada', icon: 'bulb', dim: true, container: 'hall-lights' },
  { id: 'cocina', entity: 'light.led_cocina', name: 'Encimera', icon: 'led', dim: true, container: 'cocina-lights' },
  { id: 'dormitorio', entity: 'light.lampara_dormitorio', name: 'Lámpara', icon: 'bed', dim: true, container: 'dormitorio-lights' },
];
const MODOS = ['Día', 'Tarde', 'Noche', 'Cine', 'Dormir', 'Fuera'];
const SCRIPTS = ['modo_dia', 'modo_tarde', 'modo_noche', 'modo_cine', 'modo_dormir', 'modo_fuera'];
const ENTIDADES = {
  recibidor: 'light.lampara_recibidor', modo: 'input_select.modo_casa', tiempo: 'weather.aemet', sol: 'sun.sun', presencia: 'binary_sensor.echo_salon_presence',
  cerradura: 'lock.recibidor_cerradura', camara: 'camera.recibidor', tv: 'media_player.tv_salon',
  favoritos: 'script.spotify_favoritos', encenderTv: 'button.tv_salon_encender', musica: 'media_player.spotify',
};

class CasaAmbarCard extends HTMLElement {
  constructor() {
    super();
    this._config = {};
    this._hass = null;
    this._vistos = {};
    this._pendientes = new Map();
    this._manual = false;
    this._descartarPresencia = false;
    this._caraActual = null;
    this._confirmar = false;
    this._hoja = null;
    this._pronostico = null;
    this._conexion = null;
    this._suscripcion = 0;
    this._imagen = 0;
    this._minuto = '';
    this._alto = null;
    this._resize = () => this._ajustarAlto();
  }

  static getStubConfig() { return {}; }
  getCardSize() { return 10; }
  getGridOptions() { return { columns: 'full', rows: 8 }; }
  setConfig(config) { this._config = { inactividad: 30, ...config }; }

  set hass(hass) {
    const primera = !this._hass;
    this._hass = hass;
    if (!this.shadowRoot) this._montar();
    const ids = [...LUCES.map(l => l.entity), ...Object.values(ENTIDADES)];
    const cambios = new Set(ids.filter(id => this._vistos[id] !== hass.states[id]));
    for (const id of ids) this._vistos[id] = hass.states[id];
    this._pintar(cambios);
    this._tic();
    this._suscribirPronostico();
    if (primera) this._ajustarAlto();
  }

  connectedCallback() {
    if (!this.shadowRoot) this._montar();
    window.addEventListener('resize', this._resize);
    this._programarMinuto();
    this._alturas = [500, 1500, 4000].map(ms => setTimeout(this._resize, ms));
    this._ajustarAlto();
    if (this._hass) {
      this._pintarTodo();
      this._suscribirPronostico();
    }
  }

  disconnectedCallback() {
    window.removeEventListener('resize', this._resize);
    for (const timer of this._alturas || []) clearTimeout(timer);
    clearTimeout(this._reloj);
    this._cancelarPulsacion();
    clearTimeout(this._brilloTimer);
    clearTimeout(this._inactivo);
    clearTimeout(this._avisoTimer);
    this._cancelarConfirmacion();
    this._imagen++;
    this._desuscribirPronostico();
  }

  _montar() {
    const root = this.attachShadow({ mode: 'open' });
    root.innerHTML = `<style>${ESTILOS}</style>${PLANTILLA}`;
    this.$ = selector => root.querySelector(selector);
        root.querySelectorAll('[data-icon]').forEach(el => el.innerHTML = icon(el.dataset.icon));
    for (const l of LUCES) {
      const el = document.createElement('div');
      el.className = 'card light';
      el.dataset.light = l.id;
      el.innerHTML = `<button class="light-main" data-toggle="${l.id}" disabled><span class="icon">${icon(l.icon)}</span><span class="light-name">${l.name}</span><span class="light-state">Sin datos</span></button>${l.dim?`<button class="light-adjust" data-adjust="${l.id}" aria-label="Ajustar intensidad de ${l.name}" disabled><span class="icon">${icon('tune')}</span></button>`:''}`;
      this.$(`#${l.container}`).append(el);
    }
    this._tarjetas = new Map(LUCES.map(l => [l.entity, this.$(`[data-light="${l.id}"]`)]));
    this._surface = this.$('#room-strip');

    this._surface.addEventListener('scroll', () => {
      this._actividad();
      if (this._confirmar) this._cancelarConfirmacion();
    }, { passive: true });
    root.addEventListener('pointerdown', ev => { this._actividad(); this._pulsarLuz(ev); }, { passive: true });
    root.addEventListener('pointermove', ev => { if (this._pulsacion && Math.hypot(ev.clientX-this._pulsacion.x, ev.clientY-this._pulsacion.y)>10) { this._sinClick=this._pulsacion.button; this._cancelarPulsacion(); } }, { passive: true });
    root.addEventListener('pointerup', () => this._cancelarPulsacion());
    root.addEventListener('pointercancel', () => { if (this._pulsacion) this._sinClick=this._pulsacion.button; this._cancelarPulsacion(); });
    root.addEventListener('contextmenu', ev => { const b=ev.target.closest('[data-toggle]'); if (b) { ev.preventDefault(); this._cancelarPulsacion(); const l=LUCES.find(l=>l.id===b.dataset.toggle); if(l?.dim&&!b.disabled) { this._sinClick=b; this._abrirBrillo(l,b); } } });
    root.addEventListener('click', ev => this._click(ev));
    root.addEventListener('keydown', ev => this._tecla(ev));
    this.$('#reposo').addEventListener('click', () => this._abrirCasa());
    this.$('#night').addEventListener('click', () => this._abrirCasa());
    this._tic();
    this._pintarTodo();
  }

  $$(selector) { return this.shadowRoot.querySelectorAll(selector); }
  _estado(id) { return this._hass?.states[id]; }
  _disponible(id) { const s = this._estado(id); return !!s && !['unknown', 'unavailable'].includes(s.state); }
  _texto(el, value) { if (el && el.textContent !== String(value)) el.textContent = String(value); }
  _html(el, value) { if (el && el._html !== value) { el._html = value; el.innerHTML = value; } }
  _clase(el, name, value) { if (el && el.classList.contains(name) !== !!value) el.classList.toggle(name, !!value); }
  _attr(el, name, value) { if (el && el.getAttribute(name) !== String(value)) el.setAttribute(name, String(value)); }
  _oculto(el, value) { if (el && el.hidden !== value) el.hidden = value; }
  _disabled(el, value) { if (el && el.disabled !== value) el.disabled = value; }
  _estilo(el, name, value) { if (el && el.style.getPropertyValue(name) !== value) el.style.setProperty(name, value); }

  _pintarTodo() {
    if (!this.$) return;
    this._pintar(new Set([...LUCES.map(l => l.entity), ...Object.values(ENTIDADES)]));
  }

  _pintar(cambios) {
    if (!this.$) return;
    for (const l of LUCES) if (cambios.has(l.entity)) this._pintarLuz(l);
    if (LUCES.some(l => cambios.has(l.entity))) {
      const n = LUCES.filter(l => this._estado(l.entity)?.state === 'on').length;
      this._texto(this.$('#salon-count'), `${n} ${n === 1 ? 'luz encendida' : 'luces encendidas'}`);
    }

    if (cambios.has(ENTIDADES.cerradura)) this._pintarCerrojo();
    if (cambios.has(ENTIDADES.tv) || cambios.has(ENTIDADES.encenderTv)) this._pintarTv();
    if (cambios.has(ENTIDADES.musica) || cambios.has(ENTIDADES.favoritos)) this._pintarMusica();
    if (cambios.has(ENTIDADES.modo)) this._pintarModo();
    if (cambios.has(ENTIDADES.tiempo) || cambios.has(ENTIDADES.sol)) this._pintarTiempo();
    this._aplicarCara();
    if (this._hoja && cambios.has(this._hoja.entity)) this._pintarBrillo();
  }

  _pintarLuz(l) {
    const el = this._tarjetas.get(l.entity);
    if (!el) return;
    const state = this._estado(l.entity);
    const available = this._disponible(l.entity);
    const on = state?.state === 'on';
    const pending = this._pendientes.get(l.entity);
    this._clase(el, 'on', on && available);
    this._clase(el, 'off', !on && available);
    this._clase(el, 'unavailable', !available);
    const status = pending || (!available ? 'No disponible' : on ? 'Encendido' : 'Apagado');
    this._texto(el.querySelector('.light-state'), status);
    this._disabled(el.querySelector('.light-main'), !available || !!pending);
    this._attr(el.querySelector('.light-main'), 'aria-pressed', on);
    if(l.dim)this._disabled(el.querySelector('.light-adjust'),!available||!!pending||!(state?.attributes.supported_color_modes||[]).some(m=>!['onoff','unknown'].includes(m)));
    this._attr(el.querySelector('.light-main'), 'aria-label', `${l.name}: ${status}${available ? `. ${on ? 'Apagar' : 'Encender'}` : ''}`);
    if (available && on && !pending && state.attributes.brightness != null && l.dim) this._texto(el.querySelector('.light-state'), `${Math.round(state.attributes.brightness / 2.55)} %`);
  }


  _puedeCerrar() { return ['unlocked', 'open', 'jammed'].includes(this._estado(ENTIDADES.cerradura)?.state); }
  _pintarCerrojo() {
    const state = this._estado(ENTIDADES.cerradura)?.state || 'unknown';
    const status = { locked: 'Echado', unlocked: 'Sin echar', locking: 'Cerrando…', unlocking: 'Abriendo…', open: 'Sin echar', opening: 'Abriendo…', jammed: 'Atascado', unavailable: 'No disponible', unknown: 'Sin datos' }[state] || 'Sin datos';
    if (!this._puedeCerrar()) this._confirmar = false;
    const pending = this._pendientes.has(ENTIDADES.cerradura);
    this._texto(this.$('#lock-state'), pending ? 'Cerrando…' : status);
    this._html(this.$('#lock-icon'), icon(state === 'locked' || state === 'locking' ? 'lock' : 'unlock'));
    this._texto(this.$('.lock-action'), state === 'locked' ? 'Cerrojo echado' : pending || state === 'locking' ? 'Cerrando…' : this._confirmar ? 'Confirmar' : 'Echar llave');
    this._disabled(this.$('.lock-action'), !this._puedeCerrar() || pending);
    this._oculto(this.$('.lock-cancel'), !this._confirmar || pending);
    this._texto(this.$('.rest-chip:last-child'), `Cerrojo ${status.toLocaleLowerCase('es-ES')}`);
  }

  _pintarTv() {
    const state = this._estado(ENTIDADES.tv);
    const available = this._disponible(ENTIDADES.tv);
    const on = available && !['off', 'standby'].includes(state.state);
    const pending = this._pendientes.has(ENTIDADES.tv);
    this._texto(this.$('#tv-state'), pending ? 'Enviando…' : !available ? 'No disponible' : on ? 'Encendida' : 'Apagada');
    this._texto(this.$('.tv-power'), on ? 'Apagar' : 'Encender');
    this._disabled(this.$('.tv-power'), pending || (on ? !(state.attributes.supported_features & 256) : !this._disponible(ENTIDADES.encenderTv)));
  }

  _pintarMusica() {
    const state=this._estado(ENTIDADES.musica), a=state?.attributes||{}, features=a.supported_features||0;
    const playing=state?.state==='playing', pending=this._pendientes.has(ENTIDADES.musica);
    this._texto(this.$('#track-name'), !this._disponible(ENTIDADES.musica)?'Spotify no disponible':a.media_title||'Favoritos · aleatorio');
    this._html(this.$('#music-icon'),icon(playing?'pause':'play'));
    this._attr(this.$('.play'),'aria-label',playing?'Pausar Spotify':state?.state==='paused'?'Reanudar Spotify':'Reproducir favoritos en el Echo');
    this._attr(this.$('.play'),'aria-pressed',playing);
    this._disabled(this.$('.play'),pending||!this._disponible(ENTIDADES.musica)||(playing?!(features&1):state?.state==='paused'?!(features&16384):!this._disponible(ENTIDADES.favoritos)));
    this._disabled(this.$('.next'),pending||!this._disponible(ENTIDADES.musica)||!(features&32));
  }

  _musica(next=false) {
    const s=this._estado(ENTIDADES.musica), f=s?.attributes.supported_features||0;
    if(!next&&s&&!['playing','paused'].includes(s.state)){
      if(!(s.attributes.source_list||[]).includes('Echo Salón')){this._aviso('Abre Spotify y selecciona Echo Salón en Conectar a un dispositivo una vez.');return;}
      if(this._disponible(ENTIDADES.favoritos))this._accion(ENTIDADES.favoritos,'script','spotify_favoritos',{tipo:this._config.spotify_favoritos_tipo||'current_user_saved_tracks',lista:this._config.spotify_favoritos_id||'current_user_saved_tracks'},ENTIDADES.musica);
      return;
    }
    const service=next?'media_next_track':s?.state==='playing'?'media_pause':'media_play';
    if(!this._disponible(ENTIDADES.musica)||!(f&(next?32:s.state==='playing'?1:16384)))return;
    this._accion(ENTIDADES.musica,'media_player',service);
  }

  _pintarModo() {
    const modo = this._estado(ENTIDADES.modo)?.state;
    const known = MODOS.includes(modo);
    this._texto(this.$('#mode-status'), known ? `Modo ${modo}` : 'Modo sin datos');
    this._texto(this.$('.rest-chip:first-child'), known ? `Modo ${modo}` : 'Modo sin datos');
    this._texto(this.$('.night-copy'), known ? `Modo ${modo}` : 'Modo sin datos');

    for (const b of this.$$('[data-mode]')) {
      this._attr(b, 'aria-pressed', b.dataset.mode === modo);
      this._disabled(b, !known || this._pendientes.has(ENTIDADES.modo));
    }
  }

  _pintarTiempo() {
    const state = this._estado(ENTIDADES.tiempo);
    const available = this._disponible(ENTIDADES.tiempo);
    const cond = available ? TIEMPO_ES[state.state] || 'Sin datos del tiempo' : 'Sin datos del tiempo';
    const n = available ? Number(state.attributes.temperature) : NaN;
    const temp = Number.isFinite(n) ? `${Math.round(n)}°` : '—';
    const deNoche = this._estado(ENTIDADES.sol)?.state === 'below_horizon';
    const svg = available ? dibujoTiempo(state.state, deNoche) : icon('sun');
    this._html(this.$('.sun'), svg);
    this._html(this.$('.rest-weather .icon'), svg);
    this._texto(this.$('.degrees'), temp);
    this._texto(this.$('.rest-temp'), temp);
    this._texto(this.$('.rest-cond'), cond);
    const w = this.$('.weather-copy');
    if (!w.querySelector('.condicion')) w.innerHTML = '<span class="condicion"></span><br><span class="extremos"></span>';
    this._texto(w.querySelector('.condicion'), cond);
    const p = this._pronostico?.[0];
    const max = p && Number.isFinite(Number(p.temperature)) ? Math.round(p.temperature) : null;
    const min = p && Number.isFinite(Number(p.templow)) ? Math.round(p.templow) : null;
    this._texto(w.querySelector('.extremos'), max != null ? `${max}°${min != null ? ` / ${min}°` : ''}` : '');
    this._attr(w.querySelector('.extremos'), 'aria-label', max != null ? `Máxima ${max} grados${min != null ? `, mínima ${min} grados` : ''}` : '');
  }

  _aplicarCara() {
    const modo = this._estado(ENTIDADES.modo)?.state;
    const night = ['Noche', 'Dormir'].includes(modo);
    const presence = this._estado(ENTIDADES.presencia)?.state === 'on';
    if (!presence) this._descartarPresencia = false;
    const cara = this._manual || (presence && !this._descartarPresencia && !night) ? 'casa' : night ? 'night' : 'reposo';
    if (cara === this._caraActual) return;
    this._caraActual = cara;
    for (const s of ['.top', '#ambient', '#room-strip']) this._oculto(this.$(s), cara !== 'casa');
    this._oculto(this.$('#reposo'), cara !== 'reposo');
    this._oculto(this.$('#night'), cara !== 'night');
    if (cara !== 'casa') this._cerrarPanel(false);
    else {
      this._surface.scrollLeft = 0;
      this._actividad();
    }
  }

  _abrirCasa() { this._manual = true; this._descartarPresencia = false; this._aplicarCara(); this._actividad(); }
  _volverReloj() { this._manual = false; this._descartarPresencia = true; clearTimeout(this._inactivo); this._cancelarConfirmacion(); this._aplicarCara(); }
  _actividad() {
    clearTimeout(this._inactivo);
    if (this._manual) this._inactivo = setTimeout(() => {
      if (this._hoja || !this.$('#panel').hidden || this._confirmar || this._pendientes.size) this._actividad();
      else { this._manual = false; this._descartarPresencia = true; this._aplicarCara(); }
    }, (this._config.inactividad || 30) * 1000);
  }

  _formatos() {
    const zone = this._hass?.config?.time_zone || undefined;
    if (!this._fmt || this._fmt.zone !== zone) this._fmt = {
      zone,
      hora: new Intl.DateTimeFormat('es-ES', { hour: '2-digit', minute: '2-digit', hourCycle: 'h23', timeZone: zone }),
      fecha: new Intl.DateTimeFormat('es-ES', { weekday: 'long', day: 'numeric', month: 'long', timeZone: zone }),
    };
    return this._fmt;
  }

  _tic() {
    if (!this.$) return;
    const now = new Date();
    const fmt = this._formatos();
    const time = fmt.hora.format(now);
    const stamp = `${fmt.zone || ''}:${time}`;
    if (stamp === this._minuto) return;
    this._minuto = stamp;
    for (const selector of ['.clock', '.rest-time', '.night-time']) this._texto(this.$(selector), time);
    const date = fmt.fecha.format(now);
    const fecha = date.charAt(0).toLocaleUpperCase('es-ES') + date.slice(1);
    this._texto(this.$('.date'), fecha);
    this._texto(this.$('.rest-date'), fecha);
    const hour = Number(time.split(':')[0]);
    const saludo = hour >= 6 && hour < 13 ? 'Buenos días' : hour >= 13 && hour < 21 ? 'Buenas tardes' : 'Buenas noches';
    this._texto(this.$('.greeting'), saludo);
    this._texto(this.$('.rest-greeting'), saludo);
    const block = hour * 12 + Math.floor(Number(time.split(':')[1]) / 5);
    this._estilo(this.$('.night-time'), 'transform', `translate(${((block % 5) - 2) * 4}px, ${((Math.floor(block / 5) % 3) - 1) * 4}px)`);
  }

  _programarMinuto() {
    clearTimeout(this._reloj);
    this._tic();
    this._reloj = setTimeout(() => { this._ajustarAlto(); this._programarMinuto(); }, 60000 - Date.now() % 60000 + 250);
  }

  _ajustarAlto() {
    const top = this.getBoundingClientRect().top + (window.scrollY || 0);
    const height = Math.max(300, Math.round(window.innerHeight - Math.max(0, top)));
    if (height !== this._alto) { this._alto = height; this.style.setProperty('--ca-alto', `${height}px`); }

  }

  _tecla(ev) {
    if (ev.key === 'Escape') { this._cerrarPanel(); this._cancelarConfirmacion(); }
    const dialog = this.$('.brightness') || (!this.$('#panel').hidden && this.$('#panel'));
    if (dialog && ev.key === 'Tab') {
      const buttons = [...dialog.querySelectorAll('button:not(:disabled),[role=slider]')];
      const first = buttons[0], last = buttons[buttons.length - 1];
      if (ev.shiftKey && this.shadowRoot.activeElement === first) { ev.preventDefault(); last?.focus(); }
      else if (!ev.shiftKey && this.shadowRoot.activeElement === last) { ev.preventDefault(); first?.focus(); }
    }
    if (ev.target === this._surface && ['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(ev.key)) {
      ev.preventDefault();
      if (ev.key === 'Home') this._surface.scrollLeft = 0;
      else if (ev.key === 'End') this._surface.scrollLeft = this._surface.scrollWidth;
      else this._surface.scrollLeft += ev.key === 'ArrowRight' ? 160 : -160;
    }
  }

  async _accion(entity, domain, service, data = {}, key = entity) {
    if (!this._hass || this._pendientes.has(key)) return;
    this._pendientes.set(key, domain === 'lock' ? 'Cerrando…' : 'Enviando…');
    this._pintar(new Set([key]));
    this._actividad();
    try { await this._hass.callService(domain, service, data, domain==='script'&&service!=='turn_on'?undefined:{ entity_id: entity }); }
    catch (error) { this._aviso(domain === 'lock' ? 'No se pudo echar el cerrojo. Comprueba su estado.' : key===ENTIDADES.musica ? 'No se pudo controlar Spotify. Comprueba que Echo Salón esté seleccionado en Spotify.' : 'No se pudo completar la acción. Vuelve a intentarlo.'); }
    finally { this._pendientes.delete(key); if (this.isConnected) this._pintar(new Set([key])); }
  }

  _alternar(entity) {
    if (!this._disponible(entity)) return;
    return this._accion(entity, 'light', this._estado(entity).state === 'on' ? 'turn_off' : 'turn_on');
  }

  _ponerBrillo(entity, value) {
    const state = this._estado(entity);
    if (!this._disponible(entity) || !(state.attributes.supported_color_modes || []).some(m => m !== 'onoff')) return;
    return this._accion(entity, 'light', 'turn_on', { brightness_pct: value });
  }

  _aviso(text) {
    this._texto(this.$('.toast'), text);
    this._oculto(this.$('.toast'), false);
    clearTimeout(this._avisoTimer);
    this._avisoTimer = setTimeout(() => this._oculto(this.$('.toast'), true), 5000);
  }

  _cerrarPanel(focus = true) {
    if (this._brilloTimer && this._hoja) this._enviarBrillo();
    this._imagen++;
    clearTimeout(this._brilloTimer);this._brilloTimer=null;
    this._brilloValor=null;this._brilloPendiente=null;
    this._hoja = null;
    this.$('.brightness')?.remove();
    this._oculto(this.$('#panel'), true);
    this._bloquearFondo(false);
    if (focus && this._foco?.isConnected && this._foco.getBoundingClientRect().width) this._foco.focus({ preventScroll: true });
    this._foco = null;
    this._actividad();
  }

  _bloquearFondo(value) {
    for (const selector of ['.top', '#ambient', '#room-strip']) this.$(selector).inert = value;
  }

  _cancelarPulsacion() { clearTimeout(this._pulsacion?.timer); this._pulsacion=null; }

  _pulsarLuz(ev) {
    this._cancelarPulsacion();
    this._sinClick=null;
    const button=ev.target.closest('[data-toggle]');
    if(!button||button.disabled)return;
    const l=LUCES.find(l=>l.id===button.dataset.toggle);
    if(!l?.dim)return;
    this._pulsacion={button,x:ev.clientX,y:ev.clientY,timer:setTimeout(()=>{this._pulsacion=null;this._sinClick=button;this._abrirBrillo(l,button);},480)};
  }

  _abrirBrillo(l, trigger) {
    if (!this._disponible(l.entity) || !(this._estado(l.entity).attributes.supported_color_modes||[]).some(m=>!['onoff','unknown'].includes(m))) return;
    this._cerrarPanel(false);
    this._foco=trigger;this._cancelarConfirmacion();this._bloquearFondo(true);this._hoja=l;
    const state=this._estado(l.entity);
    this._brilloValor=state.state==='on'?Math.round((state.attributes.brightness||0)/2.55):0;
    const box=document.createElement('section');box.className='brightness';box.setAttribute('role','dialog');box.setAttribute('aria-modal','true');box.setAttribute('aria-label',`Intensidad de ${l.name}`);
    box.innerHTML=`<div class="modal"><h2 class="brightness-title"></h2><p class="modal-sub">Intensidad</p><output class="brightness-current"></output><div class="brightness-control"><button class="step" data-step="-5" aria-label="Bajar intensidad">−</button><div class="slider" role="slider" tabindex="0" aria-label="Intensidad" aria-orientation="vertical" aria-valuemin="0" aria-valuemax="100"><div class="slider-fill"></div><span class="icon">${icon('sun')}</span></div><button class="step" data-step="5" aria-label="Subir intensidad">+</button></div><p class="brightness-message" role="status"></p><button class="done" data-action="close">Listo</button></div>`;
    box.querySelector('.brightness-title').textContent=l.name;this.$('.screen').append(box);
    const slider=box.querySelector('.slider');
    const point=ev=>{const r=slider.getBoundingClientRect();this._cambiarBrillo((r.bottom-ev.clientY)*100/r.height);};
    slider.addEventListener('pointerdown',ev=>{ev.preventDefault();slider.setPointerCapture(ev.pointerId);point(ev);});
    slider.addEventListener('pointermove',ev=>{if(slider.hasPointerCapture(ev.pointerId))point(ev);});
    slider.addEventListener('pointerup',ev=>{if(slider.hasPointerCapture(ev.pointerId))slider.releasePointerCapture(ev.pointerId);this._enviarBrillo();});
    slider.addEventListener('pointercancel',()=>{this._brilloValor=null;this._pintarBrillo();});
    slider.addEventListener('wheel',ev=>{ev.preventDefault();this._cambiarBrillo(this._brilloValor-Math.sign(ev.deltaY)*5);clearTimeout(this._brilloTimer);this._brilloTimer=setTimeout(()=>this._enviarBrillo(),180);},{passive:false});
    slider.addEventListener('keydown',ev=>{const d={ArrowUp:5,ArrowRight:5,ArrowDown:-5,ArrowLeft:-5}[ev.key];if(d!==undefined||['Home','End'].includes(ev.key)){ev.preventDefault();this._cambiarBrillo(ev.key==='Home'?0:ev.key==='End'?100:this._brilloValor+d);clearTimeout(this._brilloTimer);this._brilloTimer=setTimeout(()=>this._enviarBrillo(),180);}});
    for(const b of box.querySelectorAll('[data-step]'))b.onclick=()=>{this._cambiarBrillo(this._brilloValor+Number(b.dataset.step));this._enviarBrillo();};
    box.addEventListener('click',ev=>{if(ev.target===box)this._cerrarPanel();});
    this._pintarBrillo();slider.focus({preventScroll:true});this._actividad();
  }

  _cambiarBrillo(value) { const v=Math.max(0,Math.min(100,Math.round(value))); if(v===this._brilloValor)return; this._brilloValor=v;this._pintarBrillo(); }

  async _enviarBrillo() {
    clearTimeout(this._brilloTimer);this._brilloTimer=null;
    if(!this._hoja)return;
    const l=this._hoja, value=this._brilloValor;
    if(this._pendientes.has(l.entity)){this._brilloPendiente=value;return;}
    await this._ponerBrillo(l.entity,value);
    if(this._hoja===l){this._brilloValor=null;this._pintarBrillo();if(this._brilloPendiente!=null){const v=this._brilloPendiente;this._brilloPendiente=null;this._brilloValor=v;this._enviarBrillo();}}
  }

  _pintarBrillo() {
    if(!this._hoja)return;
    const state=this._estado(this._hoja.entity), available=this._disponible(this._hoja.entity), pending=this._pendientes.has(this._hoja.entity);
    const value=this._brilloValor??(state?.state==='on'?Math.round((state.attributes.brightness||0)/2.55):0);
    this._texto(this.$('.brightness-current'),available?`${value} %`:'No disponible');
    this._texto(this.$('.brightness-message'),pending?'Aplicando…':'');
    this._estilo(this.$('.slider-fill'),'height',`${value}%`);this._attr(this.$('.slider'),'aria-valuenow',value);
    this._attr(this.$('.slider'),'aria-disabled',!available);
    for(const b of this.$$('.brightness [data-step]'))this._disabled(b,!available);
  }

  _cancelarConfirmacion() {
    clearTimeout(this._confirmacionTimer);
    this._confirmar = false;
    if (this.$) this._pintarCerrojo();
  }

  _cerrarCerrojo() {
    if (!this._puedeCerrar() || this._pendientes.has(ENTIDADES.cerradura)) return;
    if (!this._confirmar) {
      this._confirmar = true;
      this._confirmacionTimer = setTimeout(() => this._cancelarConfirmacion(), 10000);
      this._pintarCerrojo();
    } else {
      this._cancelarConfirmacion();
      this._accion(ENTIDADES.cerradura, 'lock', 'lock');
    }
  }

  _abrirPanel(title, trigger, wide = false) {
    this._cerrarPanel(false);
    this._foco = trigger;
    this._cancelarConfirmacion();
    this._bloquearFondo(true);
    this._clase(this.$('#panel'), 'mode-panel', wide);
    this._texto(this.$('#panel-title'), title);
    this.$('#panel-content').replaceChildren();
    this._oculto(this.$('#panel'), false);
    this.$('.panel-close').focus({ preventScroll: true });
    this._actividad();
  }

  _abrirModos(trigger) {
    this._abrirPanel('Modos de casa', trigger, true);
    const list = document.createElement('div');
    list.className = 'panel-modes';
    for (const name of MODOS) {
      const button = document.createElement('button');
      button.dataset.mode = name;
      button.textContent = name;
      list.append(button);
    }
    this.$('#panel-content').append(list);
    this._pintarModo();
    list.querySelector('button:not(:disabled)')?.focus({ preventScroll: true });
  }

  _abrirCamara(trigger) {
    this._abrirPanel('Cámara del recibidor', trigger);
    const p = document.createElement('p');
    p.textContent = 'Cargando imagen…';
    const img = document.createElement('img');
    img.className = 'camera-preview';
    img.alt = 'Instantánea de la cámara del recibidor';
    img.hidden = true;
    const retry = document.createElement('button');
    retry.className = 'camera-retry';
    retry.textContent = 'Volver a intentar';
    retry.hidden = true;
    this.$('#panel-content').append(p, img, retry);
    retry.addEventListener('click', () => this._abrirCamara(trigger));
    const camera = this._estado(ENTIDADES.camara);
    const token = camera?.attributes.access_token;
    const generation = this._imagen;
    const fail = () => { if (generation !== this._imagen || !this.isConnected) return; this._texto(p, 'No se pudo obtener una imagen.'); this._oculto(retry, false); };
    if (!this._disponible(ENTIDADES.camara) || !token) { fail(); return; }
    const path = `/api/camera_proxy/${encodeURIComponent(ENTIDADES.camara)}?token=${encodeURIComponent(token)}&t=${Date.now()}`;
    const image = new Image();
    image.onload = () => {
      if (generation !== this._imagen || !this.isConnected) return;
      img.src = image.src;
      this._oculto(img, false);
      this._texto(p, `Imagen de las ${this._formatos().hora.format(new Date())}`);
    };
    image.onerror = fail;
    image.src = this._hass.hassUrl ? this._hass.hassUrl(path) : path;
  }

  _click(ev) {
    this._actividad();
    const el = ev.target.closest('button');
    if (!el || el.disabled) return;
    if(this._sinClick===el) {this._sinClick=null;return;}
    if (el.dataset.toggle) { const l = LUCES.find(x => x.id === el.dataset.toggle); if (l) this._alternar(l.entity); return; }
    if (el.dataset.adjust) { const l = LUCES.find(x => x.id === el.dataset.adjust); if (l) this._abrirBrillo(l, el); return; }
    if (el.dataset.level) { const l = LUCES.find(x => x.id === el.dataset.target); if (l) this._ponerBrillo(l.entity, Number(el.dataset.level)); return; }
    if (el.dataset.mode) { const i = MODOS.indexOf(el.dataset.mode); if (i >= 0) this._accion(`script.${SCRIPTS[i]}`, 'script', 'turn_on', {}, ENTIDADES.modo); return; }
    switch (el.dataset.action) {
      case 'music': this._musica(); break;
      case 'next': this._musica(true); break;
      case 'rest': this._volverReloj(); break;
      case 'home': this._abrirCasa(); break;
      case 'close': this._cerrarPanel(); break;
      case 'cine': this._accion('script.modo_cine', 'script', 'turn_on', {}, ENTIDADES.modo); break;
      case 'tv': {
        const state = this._estado(ENTIDADES.tv);
        const on = this._disponible(ENTIDADES.tv) && !['off', 'standby'].includes(state.state);
        if (on && state.attributes.supported_features & 256) this._accion(ENTIDADES.tv, 'media_player', 'turn_off');
        else if (!on && this._disponible(ENTIDADES.encenderTv)) this._accion(ENTIDADES.encenderTv, 'button', 'press', {}, ENTIDADES.tv);
        break;
      }
      case 'hall': this._alternar('light.lampara_recibidor'); break;
      case 'lock': this._cerrarCerrojo(); break;
      case 'cancel-lock': this._cancelarConfirmacion(); break;
      case 'camera': this._abrirCamara(el); break;
      case 'modes': this._abrirModos(el); break;
    }
  }

  async _suscribirPronostico() {
    const connection = this._hass?.connection;
    if (!connection || connection === this._conexion || !this.isConnected) return;
    this._desuscribirPronostico();
    this._conexion = connection;
    const generation = ++this._suscripcion;
    try {
      const unsubscribe = await connection.subscribeMessage(event => {
        if (generation !== this._suscripcion || !this.isConnected) return;
        this._pronostico = Array.isArray(event.forecast) ? event.forecast : null;
        this._pintarTiempo();
      }, { type: 'weather/subscribe_forecast', forecast_type: 'daily', entity_id: ENTIDADES.tiempo });
      if (generation !== this._suscripcion || !this.isConnected) unsubscribe();
      else this._desuscribir = unsubscribe;
    } catch (error) { this._pronostico = null; }
  }

  _desuscribirPronostico() {
    this._suscripcion++;
    if (this._desuscribir) this._desuscribir();
    this._desuscribir = null;
    this._conexion = null;
  }
}

if (!customElements.get('casa-ambar-card')) {
  customElements.define('casa-ambar-card', CasaAmbarCard);
  window.customCards = window.customCards || [];
  window.customCards.push({ type: 'casa-ambar-card', name: 'Casa Ámbar · HomeView', description: 'Salón y recibidor, con scroll táctil al resto de estancias.' });
  console.info(`CASA-ÁMBAR ${VERSION}`);
}
