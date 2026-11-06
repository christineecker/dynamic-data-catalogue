/* Small 3D network component on three.js: tube edges, sphere or logo nodes, HTML labels, drag to turn, hover to trace.
   The page's vertical scroll is never captured: the wheel stays with the page and touch drags only turn sideways. */
/* even points on a sphere, in the order given, so related nodes sit together and nothing clumps */
function layoutSphere(nodes,R){nodes.forEach((n,i)=>{const y=1-2*(i+.5)/nodes.length,r=Math.sqrt(1-y*y),p=i*2.39996;n.x=Math.cos(p)*r*R;n.y=y*R;n.z=Math.sin(p)*r*R});return nodes}
function graph3d(host,spec){if(host.__g3)return host.__g3;const RM=matchMedia("(prefers-reduced-motion: reduce)").matches;
 host.classList.add("g3d");host.style.position="relative";host.style.height=spec.height+"px";
 let gl;try{gl=new THREE.WebGLRenderer({antialias:true})}catch(e){gl=null}
 if(!gl||typeof THREE==="undefined"){host.style.height="auto";host.innerHTML=`<p class="small muted">3D could not start in this browser. The same numbers are in the table below.</p>`;return null}
 gl.setPixelRatio(Math.min(devicePixelRatio,2));host.appendChild(gl.domElement);gl.domElement.style.cssText="display:block;width:100%;height:100%;cursor:grab;touch-action:pan-y";gl.domElement.tabIndex=0;gl.domElement.setAttribute("role","img");gl.domElement.setAttribute("aria-label",spec.aria||"3D network. Arrow keys turn it.");
 const ov=document.createElement("div");ov.style.cssText="position:absolute;inset:0;pointer-events:none;overflow:hidden";host.appendChild(ov);
 const scene=new THREE.Scene();scene.background=new THREE.Color(0xFCFCFC);const cam=new THREE.PerspectiveCamera(38,1,1,2000);
 scene.add(new THREE.HemisphereLight(0xffffff,0xc9d2dc,.76));const dl=new THREE.DirectionalLight(0xffffff,.48);dl.position.set(40,70,60);scene.add(dl);
 const g=new THREE.Group();g.rotation.set(spec.tilt??.22,spec.turn??.5,0);scene.add(g);
 const geo=new THREE.SphereGeometry(1,24,16),by=new Map(),pick=[];
 spec.nodes.forEach(n=>{const logo=!!n.logo,m=new THREE.Mesh(geo,logo?new THREE.MeshBasicMaterial({transparent:true,opacity:0,depthWrite:false}):new THREE.MeshLambertMaterial({color:n.color}));m.position.set(n.x,n.y,n.z);m.scale.setScalar(n.r);m.userData.n=n;g.add(m);pick.push(m);by.set(n.id,m);
  const d=document.createElement("div");d.className=logo?"g3l g3logo":"g3l";d.innerHTML=logo?`<img src="${n.logo}" alt="${esc(n.label)}">`:`${esc(n.label)}${n.sub?`<small>${esc(n.sub)}</small>`:""}`;ov.appendChild(d);n.el=d});
 const eds=spec.links.map(e=>{const a=by.get(e.a).position,b=by.get(e.b).position,mat=new THREE.MeshBasicMaterial({color:e.color,transparent:true,opacity:e.op||.34,depthWrite:false}),t=new THREE.Mesh(new THREE.TubeGeometry(new THREE.LineCurve3(a,b),1,e.t,7,false),mat);t.userData={e,base:mat.opacity};g.add(t);return t});
 const big=Math.max(...spec.nodes.map(n=>Math.hypot(n.x,n.y,n.z)+n.r));const maxY=Math.max(...spec.nodes.map(n=>Math.abs(n.y)+n.r));
 const size=()=>{const w=host.clientWidth||600,h=spec.height;gl.setSize(w,h,false);cam.aspect=w/h;const tan=Math.tan(19*Math.PI/180),hN=(maxY+big*.14)*1.08/tan,wN=big*1.08/tan/cam.aspect,fit=Math.max(hN,wN)+big*.12;cam.position.set(0,0,fit);cam.near=fit*.2;cam.far=fit*4;cam.updateProjectionMatrix();if(!RM)dirty=true};
 let dirty=true,vis=false,raf=0,over=false,drag=null,hit=null;const v=new THREE.Vector3(),ray=new THREE.Raycaster(),mp=new THREE.Vector2(),clock=new THREE.Clock();
 const paint=()=>{const hl=hit?hit.userData.n.id:null;eds.forEach(t=>{const on=hl&&(t.userData.e.a===hl||t.userData.e.b===hl);t.material.opacity=hl?(on?Math.min(.95,t.userData.base*2.4):.05):t.userData.base});spec.nodes.forEach(n=>{const lit=!hl||n.id===hl||spec.links.some(e=>(e.a===hl&&e.b===n.id)||(e.b===hl&&e.a===n.id));by.get(n.id).material.transparent=!n.logo&&!lit?true:!!n.logo;if(!n.logo)by.get(n.id).material.opacity=lit?1:.18;n.dim=!lit});dirty=true};
 const draw=()=>{g.updateMatrixWorld();const w=host.clientWidth,h=spec.height,zs=[];spec.nodes.forEach(n=>{v.set(n.x,n.y,n.z).applyMatrix4(g.matrixWorld);const depth=(v.z+big)/(2*big);v.project(cam);const X=(v.x+1)/2*w,Y=(1-v.y)/2*h,px=n.r/(cam.position.z-(depth*2*big-big))*h/(2*Math.tan(19*Math.PI/180));n.el.style.transform=n.logo?`translate(-50%,-50%) translate(${X.toFixed(1)}px,${Y.toFixed(1)}px)`:`translate(-50%,0) translate(${X.toFixed(1)}px,${(Y+px+2).toFixed(1)}px)`;n.el.style.opacity=(n.dim?.2:.3+.7*Math.max(0,Math.min(1,(depth-.18)/.5))).toFixed(2);n.el.style.zIndex=Math.round(depth*100)});gl.render(scene,cam);dirty=false};
 const loop=()=>{raf=vis?requestAnimationFrame(loop):0;const dt=Math.min(.05,clock.getDelta());if(!RM&&!over&&!drag){g.rotation.y+=dt*.09;dirty=true}if(dirty)draw()};
 const start=()=>{if(!raf&&vis){clock.getDelta();raf=requestAnimationFrame(loop)}};
 new IntersectionObserver(es=>{vis=es[0].isIntersecting;if(vis){dirty=true;start()}}).observe(host);new ResizeObserver(()=>{size();if(!vis)draw()}).observe(host);
 const c=gl.domElement,tt=()=>document.getElementById("tt");
 c.addEventListener("pointerdown",e=>{drag={x:e.clientX,y:e.clientY};c.setPointerCapture(e.pointerId);c.style.cursor="grabbing"});
 c.addEventListener("pointerup",()=>{drag=null;c.style.cursor="grab"});c.addEventListener("pointercancel",()=>{drag=null});
 c.addEventListener("pointermove",e=>{if(drag){const dx=e.clientX-drag.x,dy=e.clientY-drag.y;drag={x:e.clientX,y:e.clientY};g.rotation.y+=dx*.008;g.rotation.x=Math.max(-1.3,Math.min(1.3,g.rotation.x+dy*.008));dirty=true;return}
  const b=c.getBoundingClientRect();mp.set((e.clientX-b.left)/b.width*2-1,-(e.clientY-b.top)/b.height*2+1);ray.setFromCamera(mp,cam);const h=ray.intersectObjects(pick)[0],m=h?h.object:null;if(m!==hit){hit=m;paint()}if(m)showTip(e,m.userData.n.tip);else tt().style.display="none";c.style.cursor=m?"pointer":"grab"});
 c.addEventListener("pointerenter",()=>{over=true});c.addEventListener("pointerleave",()=>{over=false;hit=null;paint();tt().style.display="none"});
 c.addEventListener("keydown",e=>{const k={ArrowLeft:[0,-.14],ArrowRight:[0,.14],ArrowUp:[-.14,0],ArrowDown:[.14,0]}[e.key];if(!k)return;e.preventDefault();g.rotation.x=Math.max(-1.3,Math.min(1.3,g.rotation.x+k[0]));g.rotation.y+=k[1];dirty=true});
 size();draw();host.__g3={size,scene,spec,get rot(){return g.rotation.y},project(id){const n=by.get(id);v.copy(n.position).applyMatrix4((g.updateMatrixWorld(),g.matrixWorld)).project(cam);const b=c.getBoundingClientRect();return[(v.x+1)/2*b.width+b.left,(1-v.y)/2*b.height+b.top]}};return host.__g3}
