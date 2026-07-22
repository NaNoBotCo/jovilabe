"""The page around the instrument: its stylesheet, its script, and its essay."""

from __future__ import annotations

CSS = """
:root{
  --ink:#20180d; --sub:#5b5040; --plate:#f6efe0; --paper:#e8dcc4;
  --brass:#96723a; --brassdk:#6d5027; --brasslt:#c8a765;
  --night:#111d31; --rule:#cbb98f; --card:#fffaf0;
  --io:#c8632f; --eu:#a8863f; --ga:#6f695c; --ca:#5d5346;
}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);
  font:17px/1.62 Georgia,'Iowan Old Style','Times New Roman',serif;
  -webkit-text-size-adjust:100%}
.wrap{max-width:1240px;margin:0 auto;padding:22px 18px 90px}
header.top{border-bottom:3px double var(--brassdk);margin-bottom:26px;padding-bottom:16px}
h1{font-size:clamp(28px,5vw,46px);margin:.1em 0 .1em;letter-spacing:.01em}
h1 small{display:block;font-size:.42em;letter-spacing:.22em;color:var(--sub);
  text-transform:uppercase;margin-top:.7em;font-weight:400}
.sub{color:var(--sub);font-size:1.06em;margin:.4em 0 0;max-width:64ch}
h2{font-size:clamp(21px,3vw,29px);margin:1.9em 0 .5em;border-bottom:1px solid var(--rule);
  padding-bottom:.25em}
h3{font-size:1.12em;margin:1.6em 0 .35em}
p{max-width:70ch}
a{color:var(--brassdk)}

/* ---- the instrument ---- */
.instrument{background:var(--card);border:2px solid var(--brassdk);border-radius:16px;
  padding:20px;box-shadow:0 3px 0 rgba(109,80,39,.18)}
.dial{display:block;width:100%;max-width:720px;margin:0 auto;height:auto}
.dial .bead,.scope .smoon{transition:transform .45s cubic-bezier(.4,0,.2,1)}
.noanim .bead,.noanim .smoon,.noanim #shadow,.noanim #juplit,.noanim .rot{transition:none!important}
#shadow,#juplit,#jhand,#ehand,.rot,.reshand,#resarg,#lighthand{
  transition:transform .45s cubic-bezier(.4,0,.2,1)}
.rot{transform-box:view-box}

text{font-family:Georgia,'Times New Roman',serif;fill:#20180d}
.zsign{font-size:19px;text-anchor:middle;letter-spacing:.13em;fill:#4a3d28}
.ringlab{font-size:17px;text-anchor:middle;fill:#6d5027;letter-spacing:.09em}
.beadlab{font-size:16px;text-anchor:middle;fill:#3a3021;font-weight:bold}
.smlab{font-size:15px;text-anchor:middle;fill:#e6d6b4}
.sig{font-size:17px;text-anchor:middle;letter-spacing:.3em;fill:#6d5027}
.teeth{font-size:14px;text-anchor:middle;fill:#5b5040}
.trainname{font-size:17px;fill:#3a3021;letter-spacing:.06em}
.compass{font-size:14px;fill:#9a8a6a;letter-spacing:.16em}
.subnum{font-size:15px;text-anchor:middle;fill:#3a3021}
.sublab{font-size:12px;text-anchor:middle;letter-spacing:.18em;fill:#6d5027}
.sublab2{font-size:12px;text-anchor:middle;fill:#8a7a5c}
.subread{font-size:26px;text-anchor:middle;fill:#20180d}

/* ---- panels ---- */
.panels{display:grid;grid-template-columns:1fr;gap:16px;margin-top:18px}
.scopewrap{overflow-x:auto}
.scope{display:block;width:100%;min-width:620px;height:auto;border-radius:10px}
.lower{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:16px;
  align-items:start}
.disc,.sub{display:block;width:100%;max-width:300px;margin:0 auto;height:auto}
.movement{display:block;width:100%;min-width:760px;height:auto}
.movewrap{overflow-x:auto;background:var(--card);border:2px solid var(--brassdk);
  border-radius:14px;padding:14px}

/* ---- controls & readout ---- */
.ctrls{display:flex;flex-wrap:wrap;gap:9px;align-items:center;justify-content:center;
  margin:18px 0 6px}
button{font:inherit;font-size:16px;padding:9px 15px;border-radius:9px;cursor:pointer;
  border:1.5px solid var(--brassdk);background:var(--brassdk);color:#fdf7e8}
button.secondary{background:var(--card);color:var(--ink)}
button:hover{filter:brightness(1.08)}
button:focus-visible{outline:3px solid var(--io);outline-offset:2px}
.when{font-size:19px;min-width:20ch;text-align:center;font-variant-numeric:tabular-nums}
.scrub{width:100%;margin:8px 0 2px;accent-color:var(--brassdk);height:30px}
.readout{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:10px;
  margin:16px 0 0}
.r{background:var(--plate);border:1px solid var(--rule);border-radius:10px;padding:10px 12px;
  text-align:center}
.r b{display:block;font-size:25px;font-variant-numeric:tabular-nums;line-height:1.15}
.r span{display:block;font-size:13.5px;color:var(--sub);margin-top:3px}

/* ---- the moons' table ---- */
table{border-collapse:collapse;width:100%;margin:12px 0;font-size:16px}
th,td{text-align:left;padding:8px 10px;border-bottom:1px solid var(--rule)}
th{font-size:13.5px;letter-spacing:.09em;text-transform:uppercase;color:var(--sub);
  font-weight:normal}
td.state{font-size:15px}
.tag{display:inline-block;padding:2px 8px;border-radius:20px;font-size:13.5px;
  border:1px solid currentColor;margin-right:5px;white-space:nowrap}
.dot{display:inline-block;width:13px;height:13px;border-radius:50%;margin-right:8px;
  vertical-align:-1px}
.events{max-height:340px;overflow-y:auto;border:1px solid var(--rule);border-radius:10px}
.events table{margin:0}
.events th{position:sticky;top:0;background:var(--plate)}
.caveat{background:var(--plate);border-left:5px solid var(--brass);padding:14px 18px;
  border-radius:0 10px 10px 0;margin:20px 0;max-width:none}
.caveat b{letter-spacing:.02em}
figcaption{color:var(--sub);font-size:15px;margin-top:10px;max-width:78ch}
.mono{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:14.5px}
.num{font-variant-numeric:tabular-nums}
@media (max-width:640px){
  .wrap{padding:14px 12px 70px}
  .when{min-width:100%;order:-1}
}
@media (prefers-reduced-motion:reduce){
  .bead,.smoon,#shadow,#juplit,.rot,#jhand,#ehand,.reshand,#resarg,#lighthand{
    transition:none!important}
}
"""


JS = r"""
(function(){
'use strict';
var D=Math.PI/180, DAYMS=86400000, J1970=2440587.5;
var TH=THEORY, EP=EPHEM, K=CONST;
var RM=TH.rmean, MOONS=K.MOONS, ROMAN=K.ROMAN;

function jdOf(ms){return ms/DAYMS + J1970;}
function msOf(jd){return (jd - J1970)*DAYMS;}

/* --- the periodic tables ------------------------------------------------
   Same structure the Python evaluates: amplitude, sparse coefficients on the
   argument vector, and a constant. Sines for the longitudes and latitudes,
   cosines for the radii. */
function ev(tbl,v,isSin){
  var s=0;
  for(var k=0;k<tbl.length;k++){
    var t=tbl[k], a=t[2], c=t[1];
    for(var j=0;j<c.length;j++) a+=c[j][1]*v[c[j][0]];
    s += t[0]*(isSin?Math.sin(a*D):Math.cos(a*D));
  }
  return s;
}

/* --- Lieske's E5 --------------------------------------------------------- */
function e5(jd){
  var t=jd-2443000.5, i;
  var l=[106.07719+203.488955790*t, 175.73161+101.374724735*t,
         120.55883+50.317609207*t,   84.44459+21.571071177*t];
  var p=[97.0881+0.16138586*t, 154.8663+0.04726307*t,
         188.1840+0.00712734*t, 335.2868+0.00184000*t];
  var w=[312.3346-0.13279386*t, 100.4411-0.03263064*t,
         119.1942-0.00717703*t, 322.6186-0.00175934*t];
  var gamma=0.33033*Math.sin((163.679+0.0010512*t)*D)
           +0.03439*Math.sin((34.486-0.0161731*t)*D);
  var phiLam=199.6766+0.17379190*t;
  var psi=316.5182-0.00000208*t;
  var G=30.23756+0.0830925701*t+gamma, Gp=31.97853+0.0334597339*t, P=13.469942;
  var base=l.concat(p,w,[G,Gp,P,psi,phiLam]);

  var sig=[],L=[];
  for(i=0;i<4;i++){sig.push(ev(TH.sigma[i],base,true)); L.push(l[i]+sig[i]);}
  var ext=base.concat(L,sig);
  var B=[],R=[];
  for(i=0;i<4;i++){
    B.push(Math.atan(ev(TH.tanb[i],ext,true)));
    R.push(RM[i]*(1+ev(TH.radius[i],base,false)));
  }
  /* The theory comes out referred to B1950; carry it to the equinox of date,
     which is the frame the planetary series is already in. */
  var T0=(jd-2433282.423)/36525, prec=1.3966626*T0+0.0003088*T0*T0;
  for(i=0;i<4;i++) L[i]+=prec;
  var psid=psi+prec;

  var T=(jd-2451545.0)/36525;
  var I=3.120262+0.0006*((jd-2433282.5)/36525);
  var Om=100.464441+1.0209550*T+0.00040117*T*T+0.000000569*T*T*T;
  var inc=1.303270-0.0054966*T+0.00000465*T*T-0.000000004*T*T*T;
  var cI=Math.cos(I*D), sI=Math.sin(I*D);
  var f=(psid-Om)*D, cF=Math.cos(f), sF=Math.sin(f);
  var ci=Math.cos(inc*D), si=Math.sin(inc*D);
  var cO=Math.cos(Om*D), sO=Math.sin(Om*D);
  function toEcl(x,y,z){
    var b1=y*cI-z*sI, c1=y*sI+z*cI;
    var a2=x*cF-b1*sF, b2=x*sF+b1*cF;
    var b3=b2*ci-c1*si, c3=b2*si+c1*ci;
    return [a2*cO-b3*sO, a2*sO+b3*cO, c3];
  }
  var basis=[toEcl(1,0,0),toEcl(0,1,0),toEcl(0,0,1)];
  var u=[],sats=[],plan=[];
  for(i=0;i<4;i++){
    var uu=((L[i]-psid)%360+360)%360; u.push(uu);
    var ur=uu*D;
    sats.push(toEcl(R[i]*Math.cos(ur)*Math.cos(B[i]),
                    R[i]*Math.sin(ur)*Math.cos(B[i]), R[i]*Math.sin(B[i])));
    plan.push([R[i]*Math.cos(ur)*Math.cos(B[i]), R[i]*Math.sin(ur)*Math.cos(B[i])]);
  }
  return {sats:sats, pole:basis[2], basis:basis, L:L, lmean:l, R:R, B:B,
          u:u, psi:psid, plan:plan};
}

/* --- Jupiter and the Earth, from the series fitted to DE440 -------------- */
function series(b,d){
  var tau=d/36525, v=0, k;
  for(k=0;k<b.poly.length;k++) v+=b.poly[k]*Math.pow(tau,k);
  for(k=0;k<b.t.length;k++){
    var q=b.t[k], th=(q[1]+q[0]*d)*D;
    v += q[2]*Math.sin(th)+q[3]*Math.cos(th);
  }
  return v;
}
function helio(body,jd){
  var b=EP[body], d=jd-2451545.0;
  var lon=b.L0+b.rate*d+series(b.lon,d);
  return [((lon%360)+360)%360, series(b.lat,d), series(b.r,d)];
}
function helioVec(body,jd){
  var s=helio(body,jd), la=s[0]*D, be=s[1]*D, r=s[2];
  return [r*Math.cos(be)*Math.cos(la), r*Math.cos(be)*Math.sin(la), r*Math.sin(be)];
}
function dot(a,b){return a[0]*b[0]+a[1]*b[1]+a[2]*b[2];}
function cross(a,b){return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];}
function norm(a){var m=Math.sqrt(dot(a,a));return [a[0]/m,a[1]/m,a[2]/m];}

function jupiterFrom(jd,obsName){
  var obs = obsName==='sun' ? [0,0,0] : helioVec('earth',jd);
  var tau=0, v, dist;
  for(var k=0;k<3;k++){
    var j=helioVec('jupiter',jd-tau);
    v=[j[0]-obs[0],j[1]-obs[1],j[2]-obs[2]];
    dist=Math.sqrt(dot(v,v));
    tau=dist/K.C;
  }
  return {v:v, dist:dist, tau:tau, seen:jd-tau};
}

function observe(jd,obsName,skipLT){
  var jf=jupiterFrom(jd,obsName);
  var look=norm([-jf.v[0],-jf.v[1],-jf.v[2]]);   /* Jupiter -> observer */
  var st=e5(jf.seen), fixed=[];
  for(var i=0;i<4;i++){
    /* Light from a moon in front of Jupiter left it later than light from one
       behind. Six seconds at most, and skippable while scanning coarsely. */
    fixed.push(skipLT ? st.sats[i]
      : e5(jf.seen + dot(st.sats[i],look)*K.LT_PER_RJUP).sats[i]);
  }
  var d0=dot(st.pole,look);
  var yh=norm([st.pole[0]-d0*look[0], st.pole[1]-d0*look[1], st.pole[2]-d0*look[2]]);
  var xh=cross(look,yh);
  var x=[],y=[],z=[];
  for(i=0;i<4;i++){x.push(dot(fixed[i],xh)); y.push(dot(fixed[i],yh)); z.push(dot(fixed[i],look));}
  return {x:x,y:y,z:z, tilt:Math.asin(Math.max(-1,Math.min(1,d0)))/D,
          dist:jf.dist, seen:jf.seen, look:look, xh:xh, yh:yh,
          pole:st.pole, state:st, vecs:fixed, jup:jf.v};
}

function semiMinor(tiltDeg){
  var s=Math.sin(tiltDeg*D);
  return Math.sqrt(s*s + K.FLATTEN*K.FLATTEN*(1-s*s));
}
function intoEquator(basis,v){
  return [dot(basis[0],v), dot(basis[1],v), dot(basis[2],v)];
}

function phenomena(jd,skipLT){
  var e=observe(jd,'earth',skipLT), s=observe(jd,'sun',skipLT);
  var rHelio=Math.sqrt(dot(s.jup,s.jup));
  var sunAng=K.RSUN_KM/(rHelio*K.AU_KM);
  var be=semiMinor(e.tilt), bs=semiMinor(s.tilt), out=[];
  for(var i=0;i<4;i++){
    var onDisc = (e.x[i]*e.x[i] + (e.y[i]/be)*(e.y[i]/be)) < 1;
    var depth = -s.z[i];
    var umbra = depth>0 ? 1-sunAng*depth : 0;
    var pen   = depth>0 ? 1+sunAng*depth : 0;
    var rho = Math.hypot(s.x[i], s.y[i]/bs);
    out.push({
      moon:MOONS[i], roman:ROMAN[i], i:i,
      transit: onDisc && e.z[i]>0,
      occulted: onDisc && e.z[i]<0,
      eclipsed: depth>0 && rho<umbra,
      penumbral: depth>0 && rho>=umbra && rho<pen,
      shadow: (s.x[i]*s.x[i]+(s.y[i]/bs)*(s.y[i]/bs))<1 && s.z[i]>0,
      x:e.x[i], y:e.y[i], z:e.z[i]
    });
  }
  var sunDir=intoEquator(e.state.basis, norm(s.look));
  var earthDir=intoEquator(e.state.basis, e.look);
  return {moons:out, e:e, s:s, tilt:e.tilt, dist:e.dist, rHelio:rHelio,
          semiMinor:be, seen:e.seen, sunAng:sunAng,
          lightMin:(jd-e.seen)*1440,
          plan:e.state.plan, u:e.state.u, R:e.state.R, L:e.state.L,
          lmean:e.state.lmean,
          sunAz:((Math.atan2(sunDir[1],sunDir[0])/D)%360+360)%360,
          earthAz:((Math.atan2(earthDir[1],earthDir[0])/D)%360+360)%360,
          angRadius:Math.asin(K.RJUP_AU/e.dist)/D*3600};
}

/* Where a moon's shadow strikes the cloud tops: the first crossing of the
   oblate globe by the ray running away from the Sun. Solved in Jupiter's own
   frame, because that is the frame the flattening is defined in. */
function shadowPoint(ph,i){
  var st=ph.e.state, f=K.FLATTEN;
  var M=intoEquator(st.basis, ph.e.vecs[i]);
  var S=intoEquator(st.basis, norm(ph.s.look));
  var a=S[0]*S[0]+S[1]*S[1]+S[2]*S[2]/(f*f);
  var b=-2*(M[0]*S[0]+M[1]*S[1]+M[2]*S[2]/(f*f));
  var c=M[0]*M[0]+M[1]*M[1]+M[2]*M[2]/(f*f)-1;
  var disc=b*b-4*a*c;
  if(disc<0) return null;
  var t=(-b-Math.sqrt(disc))/(2*a);
  if(t<0) return null;
  var Pe=[M[0]-t*S[0], M[1]-t*S[1], M[2]-t*S[2]];
  /* back to the ecliptic: the basis vectors ARE the equatorial axes */
  var P=[0,0,0];
  for(var k=0;k<3;k++) for(var j=0;j<3;j++) P[j]+=Pe[k]*st.basis[k][j];
  var z=dot(P,ph.e.look);
  if(z<0) return null;                     /* fell on the far side */
  return {x:dot(P,ph.e.xh), y:dot(P,ph.e.yh)};
}

/* --- the phenomena as events, found by scan and bisection ---------------- */
var KINDS=['eclipsed','occulted','transit','shadow'];
var KINDNAME={eclipsed:'eclipse',occulted:'occultation',
              transit:'transit',shadow:'shadow transit'};
function findEvents(jd0,days,stepMin){
  var step=(stepMin||6)/1440, n=Math.round(days/step), out=[];
  var prev=phenomena(jd0,true).moons;
  for(var k=1;k<=n;k++){
    var jd=jd0+k*step, cur=phenomena(jd,true).moons;
    for(var i=0;i<4;i++) for(var q=0;q<KINDS.length;q++){
      var kind=KINDS[q];
      if(cur[i][kind]===prev[i][kind]) continue;
      var lo=jd-step, hi=jd, want=cur[i][kind];
      for(var b=0;b<13;b++){
        var mid=(lo+hi)/2;
        if(phenomena(mid,true).moons[i][kind]===want) hi=mid; else lo=mid;
      }
      out.push({jd:(lo+hi)/2, i:i, moon:MOONS[i], roman:ROMAN[i],
                kind:kind, name:KINDNAME[kind], begins:want});
    }
    prev=cur;
  }
  out.sort(function(a,b){return a.jd-b.jd;});
  return out;
}
"""

JS_RENDER = r"""
/* ======================================================================
   Drawing. Every number below comes out of the model above; nothing on the
   instrument is decoration pretending to be a reading.
   ====================================================================== */
var $=function(id){return document.getElementById(id);};
var offset=0, playing=null, rate=0.12, evCache=null, evBase=null;
var fmtD=new Intl.DateTimeFormat(undefined,{weekday:'short',day:'numeric',
          month:'short',year:'numeric',hour:'2-digit',minute:'2-digit'});
var fmtE=new Intl.DateTimeFormat(undefined,{day:'numeric',month:'short',
          hour:'2-digit',minute:'2-digit'});
var GEARS=[].slice.call(document.querySelectorAll('.rot'));
var EPOCH=jdOf(Date.now());

function setT(el,t){ if(el) el.setAttribute('transform',t); }

function draw(){
  var jd=jdOf(Date.now())+offset;
  var ph=phenomena(jd);

  /* --- the plan dial: four beads on four rings ------------------------- */
  for(var i=0;i<4;i++){
    var px=DIAL.CX + DIAL.SCALE*ph.plan[i][0];
    var py=DIAL.CY - DIAL.SCALE*ph.plan[i][1];
    setT($('bead'+i),'translate('+px.toFixed(2)+' '+py.toFixed(2)+')');
  }
  /* The shadow points away from the Sun; the lit half of the globe faces it.
     Screen bearings run the other way round from orbital azimuth, hence the
     minus signs. */
  setT($('shadow'),'rotate('+(-(ph.sunAz+180)).toFixed(3)+' '+DIAL.CX+' '+DIAL.CY+')');
  setT($('juplit'),'rotate('+(-ph.sunAz).toFixed(3)+' '+DIAL.CX+' '+DIAL.CY+')');

  /* --- zodiac hands: where Jupiter and the Earth stand in longitude ----- */
  var jl=helio('jupiter',jd)[0], el=helio('earth',jd)[0];
  setT($('jhand'),'rotate('+(-jl).toFixed(3)+' '+DIAL.CX+' '+DIAL.CY+')');
  setT($('ehand'),'rotate('+(-el).toFixed(3)+' '+DIAL.CX+' '+DIAL.CY+')');

  /* --- the wheelwork turns at its true rates --------------------------- */
  var days=jd-EPOCH;
  for(var g=0;g<GEARS.length;g++){
    var rev=parseFloat(GEARS[g].getAttribute('data-turns'));
    GEARS[g].style.transform='rotate('+(rev*days*360%360).toFixed(2)+'deg)';
  }

  /* --- the telescopic strip -------------------------------------------- */
  for(i=0;i<4;i++){
    var sx=DIAL.SCOPE_CX - DIAL.SCOPE_R*ph.moons[i].x;   /* east to the left */
    var sy=DIAL.SCOPE_CY - DIAL.SCOPE_R*ph.moons[i].y;
    var el2=$('sm'+i);
    setT(el2,'translate('+sx.toFixed(2)+' '+sy.toFixed(2)+')');
    /* A moon behind the disc is not there to be seen. */
    el2.style.opacity = ph.moons[i].occulted ? 0.16
                      : (ph.moons[i].eclipsed ? 0.16 : 1);
  }

  /* --- the magnified disc: transits and the shadows they throw ---------- */
  var marks='';
  for(i=0;i<4;i++){
    var m=ph.moons[i];
    if(m.transit){
      marks += "<circle cx='"+(160-DIAL.DISC_R*m.x).toFixed(2)+"' cy='"
            +(160-DIAL.DISC_R*m.y).toFixed(2)+"' r='6' fill='"+DIAL.MOON_INK[i]
            +"' stroke='#2b2114' stroke-width='1'/>";
    }
    if(m.shadow){
      var sp=shadowPoint(ph,i);
      if(sp) marks += "<circle cx='"+(160-DIAL.DISC_R*sp.x).toFixed(2)+"' cy='"
            +(160-DIAL.DISC_R*sp.y).toFixed(2)+"' r='7' fill='#16203300' "
            +"style='fill:#141d2e;fill-opacity:.88'/>";
    }
  }
  $('discmarks').innerHTML=marks;

  /* The Great Red Spot rides round at the System II rate. Where it sits in
     that system is NOT predictable — it wanders tens of degrees a year — so
     this is indicative, and the caption says so. */
  var grsLon=((jd-2451545.0)*870.27001 + DIAL.GRS0)%360;
  var gr=grsLon*Math.PI/180;
  var grs=$('grs');
  grs.setAttribute('cx',(160 - DIAL.DISC_R*0.86*Math.sin(gr)).toFixed(2));
  grs.setAttribute('rx',(DIAL.DISC_R*0.17*Math.max(0,Math.cos(gr))).toFixed(2));
  grs.style.opacity = Math.cos(gr)>0.08 ? 0.85 : 0;

  /* The night sliver. Jupiter is never more than about twelve degrees off
     full from here, but which limb the sliver is on is which side the Sun is. */
  var cosPsi=Math.max(-1,Math.min(1,dot(ph.e.look,norm(ph.s.look))));
  var w=DIAL.DISC_R*(1-cosPsi);
  var sunX=dot(norm(ph.s.look),ph.e.xh);
  var t=$('termin');
  t.setAttribute('width',w.toFixed(2));
  t.setAttribute('x',(sunX>0 ? 160-DIAL.DISC_R : 160+DIAL.DISC_R-w).toFixed(2));
  t.setAttribute('y','0'); t.setAttribute('height','320');

  /* --- sub-dial: the light equation ------------------------------------ */
  var lm=ph.lightMin;
  var la=-120+240*(lm-30)/26;
  setT($('lighthand'),'rotate('+la.toFixed(3)+' 130 130)');
  $('lightread').textContent=lm.toFixed(1)+' min';

  /* --- sub-dial: the Laplace resonance --------------------------------- */
  for(i=0;i<3;i++) setT($('rh'+i),'rotate('+(ph.L[i]%360).toFixed(2)+' 130 130)');
  /* Two arguments, and the difference between them is the point. From the MEAN
     longitudes the relation is exact and the needle never stirs; from the TRUE
     longitudes the real moons swing about four degrees either side of it. */
  var ml=ph.lmean;
  var argM=((ml[0]-3*ml[1]+2*ml[2])%360+360)%360;
  var argT=((ph.L[0]-3*ph.L[1]+2*ph.L[2])%360+360)%360;
  setT($('resarg'),'rotate('+argM.toFixed(4)+' 130 130)');
  setT($('restrue'),'rotate('+argT.toFixed(3)+' 130 130)');
  $('resread').textContent=argT.toFixed(2)+'°';

  /* --- readout --------------------------------------------------------- */
  $('when').textContent=(Math.abs(offset)<1e-6?'now — ':'')+fmtD.format(new Date(msOf(jd)));
  $('rDist').textContent=ph.dist.toFixed(3);
  $('rLight').textContent=lm.toFixed(1);
  $('rSize').textContent=(ph.angRadius*2).toFixed(1)+'″';
  $('rTilt').textContent=ph.tilt.toFixed(2)+'°';
  $('rArg').textContent=argT.toFixed(2)+'°';
  /* Elongation is the angle at the EARTH between the Sun and Jupiter, not the
     angle at the Sun between the Earth and Jupiter. Those two are supplementary,
     and using the wrong one labelled a 6.3 AU conjunction "near opposition". */
  var ev0=helioVec('earth',jd), jv=ph.e.jup;
  var sunFromEarth=norm([-ev0[0],-ev0[1],-ev0[2]]);
  var elong=Math.acos(Math.max(-1,Math.min(1,dot(sunFromEarth,norm(jv)))))/D;
  $('rElong').textContent=elong.toFixed(0)+'°';
  $('rElongNote').textContent = elong>150?'near opposition':(elong<30?'near conjunction':'');

  /* --- the four moons, and what each is doing -------------------------- */
  var rows='';
  for(i=0;i<4;i++){
    var m=ph.moons[i], tags=[];
    if(m.transit) tags.push("<span class='tag'>in transit</span>");
    if(m.shadow)  tags.push("<span class='tag'>casting a shadow</span>");
    if(m.occulted)tags.push("<span class='tag'>hidden behind</span>");
    if(m.eclipsed)tags.push("<span class='tag'>eclipsed</span>");
    if(m.penumbral)tags.push("<span class='tag'>in the penumbra</span>");
    if(!tags.length) tags.push("<span style='color:#8a7a5c'>clear of the disc</span>");
    rows += "<tr><td><span class='dot' style='background:"+DIAL.MOON_INK[i]+"'></span>"
         + m.roman+" · "+m.moon+"</td>"
         + "<td class='num'>"+ph.R[i].toFixed(2)+"</td>"
         + "<td class='num'>"+(m.x*ph.angRadius).toFixed(1)+"″</td>"
         + "<td class='state'>"+tags.join(' ')+"</td></tr>";
  }
  $('moonrows').innerHTML=rows;
  $('scrub').value=offset;
}

/* --- the events list, recomputed when the date moves far enough --------- */
function refreshEvents(){
  var jd=jdOf(Date.now())+offset;
  if(evBase!==null && Math.abs(jd-evBase)<0.5 && evCache) return paintEvents();
  evBase=jd;
  var t0=performance.now();
  evCache=findEvents(jd,7,6);
  $('evtime').textContent='seven days computed in '
    +Math.round(performance.now()-t0)+' ms';
  paintEvents();
}
function paintEvents(){
  var rows='';
  for(var k=0;k<evCache.length;k++){
    var e=evCache[k];
    rows += "<tr><td class='num'>"+fmtE.format(new Date(msOf(e.jd)))+"</td>"
         + "<td><span class='dot' style='background:"+DIAL.MOON_INK[e.i]+"'></span>"
         + e.roman+"</td><td>"+e.name+"</td><td>"+(e.begins?'begins':'ends')
         + "</td><td><button class='secondary go' data-jd='"+e.jd+"'>go</button></td></tr>";
  }
  $('evrows').innerHTML=rows || "<tr><td colspan=5>nothing in the next seven days</td></tr>";
  [].forEach.call(document.querySelectorAll('.go'),function(b){
    b.onclick=function(){
      stop();
      offset=parseFloat(this.dataset.jd)-jdOf(Date.now());
      noanim(draw);
      document.querySelector('.instrument').scrollIntoView({behavior:'smooth',block:'start'});
    };
  });
}

function noanim(fn){
  var d=document.querySelector('.instrument');
  d.classList.add('noanim'); fn();
  setTimeout(function(){d.classList.remove('noanim');},60);
}
function stop(){ if(playing){cancelAnimationFrame(playing);playing=null;
  $('play').textContent='▶ Run';} }
function nudge(d){ offset+=d; stop(); draw(); }

$('back').onclick=function(){nudge(-0.25);};
$('fwd').onclick=function(){nudge(0.25);};
$('backd').onclick=function(){nudge(-1);};
$('fwdd').onclick=function(){nudge(1);};
$('nowb').onclick=function(){offset=0;stop();noanim(draw);refreshEvents();};
$('scrub').oninput=function(){offset=+this.value;stop();draw();};
$('scrub').onchange=function(){refreshEvents();};
$('play').onclick=function(){
  if(playing){stop();return;}
  this.textContent='■ Stop';
  var d=document.querySelector('.instrument');
  d.classList.add('noanim');
  var tick=function(){
    offset+=rate;
    if(offset>30){offset=-30;}
    draw();
    playing=requestAnimationFrame(tick);
  };
  playing=requestAnimationFrame(tick);
};

draw();
refreshEvents();
})();
"""


def body(gd, gear_rows, validation_rows, vjson) -> str:
    """The page: the instrument, its readings, its movement, and the essay."""
    import dial
    worst = vjson["worst_overall_rjup"]
    near = vjson["windows"]["2026-06-01..2026-09-01"]["worst_rjup"]
    return f"""
<header class=top>
  <h1>The Jovilabe<small>Iovilabium &#183; Mediceorum Siderum</small></h1>
  <p class=sub>Jupiter&#8217;s four great moons, where they stand tonight and where
  their shadows fall &#8212; on the instrument that was once the only clock the
  whole world could read at once.</p>
</header>

<div class=instrument>
  {dial.dial_svg()}

  <div class=ctrls>
    <button class=secondary id=backd>&#9664;&#9664; Day</button>
    <button class=secondary id=back>&#9664; 6h</button>
    <span class=when id=when>&#8212;</span>
    <button class=secondary id=fwd>6h &#9654;</button>
    <button class=secondary id=fwdd>Day &#9654;&#9654;</button>
    <button id=nowb>Now</button>
    <button class=secondary id=play>&#9654; Run</button>
  </div>
  <input class=scrub id=scrub type=range min=-30 max=30 step=0.02 value=0
     aria-label='Scrub the date, thirty days either side of now'>

  <div class=readout>
    <div class=r><b id=rDist>&#8212;</b><span>astronomical units away</span></div>
    <div class=r><b id=rLight>&#8212;</b><span>minutes of light-time</span></div>
    <div class=r><b id=rSize>&#8212;</b><span>Jupiter&#8217;s width</span></div>
    <div class=r><b id=rTilt>&#8212;</b><span>tilt of the orbits to us</span></div>
    <div class=r><b id=rElong>&#8212;</b><span>from the Sun <i id=rElongNote></i></span></div>
    <div class=r><b id=rArg>&#8212;</b><span>the resonance argument</span></div>
  </div>

  <div class=panels>
    <div class=scopewrap>{dial.scope_svg()}</div>
    <div class=lower>
      <div>{dial.disc_svg()}</div>
      <div>{dial.light_dial_svg()}</div>
      <div>{dial.resonance_dial_svg()}</div>
    </div>
  </div>

  <table>
    <thead><tr><th>moon</th><th>radii out</th><th>offset</th><th>what it is doing</th></tr></thead>
    <tbody id=moonrows></tbody>
  </table>
</div>

<p class=caveat><b>What you are looking at.</b> The big dial is the system seen from
above Jupiter&#8217;s north pole, and <b>the orbits are drawn to true scale</b> &#8212;
which is why Jupiter is a bead. Callisto really does ride twenty-six Jupiter radii
out. The dark wedge is the planet&#8217;s shadow, drawn as the narrowing cone it
really is; a moon crossing it is being eclipsed, and you can watch it happen. The
dark strip below is the same instant through a telescope, also to true scale, east
to the left. The outer ring is the zodiac in <b>heliocentric</b> longitude: the brass
pointer is Jupiter, the steel bead the Earth. When the two coincide the Earth stands
between the Sun and Jupiter and it is opposition; when they sit opposite each other it
is conjunction, Jupiter is on the far side of the Sun, and the light equation runs to
its longest. The small round panel magnifies the disc, because a shadow crawling
across the cloud tops is the finest thing this instrument predicts and at true scale
it would be two pixels wide.</p>

<h2>The next seven days</h2>
<p>Every beginning and ending of the four phenomena &#8212; a moon slipping into the
shadow, passing behind the planet, crossing in front of it, or dragging its shadow
over the cloud tops. Found by scanning the model at six-minute steps and then
bisecting each crossing down to the second. <span class=mono id=evtime></span></p>
<div class=events>
  <table>
    <thead><tr><th>when</th><th>moon</th><th>phenomenon</th><th></th><th></th></tr></thead>
    <tbody id=evrows></tbody>
  </table>
</div>
<p class=caveat><b>The limit of a six-minute scan.</b> Anything that begins and ends
inside six minutes can be stepped straight over and never appear in this table. That
is rare &#8212; ingress and egress are what is brief, not the events themselves &#8212;
but it is a real hole and worth knowing about rather than trusting the list blindly.</p>

<h2>The movement</h2>
<p>If the four rings are to be carried round by wheels from a single arbor turning
once a day, somebody has to choose whole numbers of teeth &#8212; and no ratio of
whole numbers is 1.769137786. These are the best trains available with pinions of
six to twenty leaves and wheels up to a hundred and eighty teeth. They are drawn at
one common module, so every mesh in the picture is a mesh that would actually work,
and they turn at their true relative rates.</p>
<div class=movewrap>{dial.movement_svg(gd)}</div>
<table>
  <thead><tr><th>hand</th><th>period, days</th><th>train</th>
  <th>drift/century</th><th>a whole turn out in</th></tr></thead>
  <tbody>{gear_rows}</tbody>
</table>
<figcaption>A train written 12/11 means a pinion of eleven leaves driving a wheel of
twelve teeth. Io&#8217;s ring loses about four degrees a century &#8212; roughly a
third of a Jupiter radius in its apparent place, which you could see. Callisto&#8217;s
is a fortieth of that. Ganymede&#8217;s has no error at all, for the reason below.</figcaption>

<h2>Why anyone built one</h2>
<p>A ship at sea in 1650 could find its latitude with a quadrant and a table. Longitude
was the unsolved problem, and it was unsolved for a specific reason: to know how far
east or west you are, you need to know what time it is <i>somewhere else</i> at the
same moment. There were no clocks that would keep time on a rolling deck.</p>
<p>Galileo saw the answer within two years of first pointing a telescope at Jupiter.
The four moons he found there eclipse, one after another, hundreds of times a year,
and each eclipse happens at one instant for the entire Earth. Publish the predicted
times in Florence; observe the actual time where you stand; the difference is your
longitude. He called them the Medicean Stars, and he designed an instrument &#8212; the
<i>giovilabio</i> &#8212; for computing where they would be. Two of them survive in
Florence. This is one of their descendants.</p>
<p>It never worked at sea. Finding a moon of Jupiter in a telescope from a pitching
deck defeated everyone who tried, Galileo included, and the longitude prize eventually
went to Harrison&#8217;s chronometers. But on land it worked beautifully, and for a
century and a half the map of the world was redrawn by it. France came out noticeably
narrower than anyone had thought.</p>

<h2>The error that turned out to be physics</h2>
<p>The tables were always a little wrong, in a way nobody could shake. Io&#8217;s
eclipses ran late for part of the year and early for the rest, by up to a
quarter of an hour, and the pattern repeated annually. In 1676 Ole R&#248;mer, working
at the Paris Observatory, said the obvious and unwelcome thing: the eclipses were not
late. The light was.</p>
<p>When the Earth is on the far side of its orbit, the news of an eclipse has an extra
three hundred million kilometres to cross, and it arrives about sixteen and a half
minutes behind schedule. That is the whole of the discrepancy, and dividing the
distance by the delay gives the speed of light &#8212; the first time anybody had a
number for it. The <b>Light Equation</b> sub-dial is that hand: it reads how long ago
the arrangement you are looking at actually happened. It runs from about
thirty-three minutes to about fifty-three, and the difference between those two
readings is R&#248;mer&#8217;s discovery.</p>
<p>This instrument applies the correction rather than suffering from it. Each moon is
even shown at its own instant, because light from one in front of Jupiter left it a few
seconds later than light from one behind &#8212; the same effect as R&#248;mer&#8217;s,
on a baseline a thousand times shorter.</p>

<h2>The resonance that gears itself</h2>
<p>Io, Europa and Ganymede are locked together. Io goes round almost exactly twice for
each turn of Europa, and Europa almost exactly twice for each turn of Ganymede &#8212;
but only <i>almost</i>, and the near-misses are not independent. What holds exactly is
a relation Laplace published in 1805 between the three mean motions:</p>
<p class=mono style='font-size:17px;text-align:center'>n&#8321; &#8722; 3n&#8322; + 2n&#8323; = 0</p>
<p>It is true to about a part in a hundred billion. The three moons are held there by
their own gravity; nudge one and the others pull it back.</p>
<p>The <b>Resonantia</b> sub-dial has three coloured hands at the three moons&#8217;
true longitudes, and two needles for the combination. The <b>black</b> one takes it
from the <i>mean</i> longitudes: it sits at half a turn and never stirs &#8212; over
five years it does not move in the fifth decimal place. The <b>red</b> one takes it
from the true longitudes, with every periodic term left in, and that one breathes:
measured over the same five years it swings between <b>176.06&deg; and 183.87&deg;</b>.
Run the instrument for a month and watch the two of them. The black needle is the law;
the red needle is the three moons actually obeying it, tugging at the leash by about
four degrees either way.</p>
<p>And it has a mechanical consequence that is too good to pass up. If the relation
holds, then Ganymede&#8217;s rate is not an independent quantity &#8212; it is
<span class=mono>(3n&#8322; &#8722; n&#8321;) / 2</span>, and a bevel differential
whose carrier turns at the mean of its two inputs computes exactly that. So in this
movement Ganymede is <b>not geared at all</b>. It is derived, from Europa geared up
three times and Io running backwards. Where the other three rings drift by degrees a
century, that one is out by a degree in five million years. The physics does the
engineering&#8217;s work.</p>

<h2>How wrong it is</h2>
<p>The satellites come from Lieske&#8217;s E5 theory, in the form Meeus sets out;
Jupiter&#8217;s and the Earth&#8217;s own places come from a compact series fitted here
against JPL&#8217;s DE440 ephemeris. Neither is taken on trust. The whole chain was
run against JPL Horizons &#8212; the actual, published, best-available positions of
Jupiter and its four moons &#8212; and the difference measured in Jupiter radii, the
unit the dial is drawn in.</p>
<table>
  <thead><tr><th>window checked</th><th>epochs</th><th>worst error, R<sub>Jup</sub></th>
  <th>in kilometres</th></tr></thead>
  <tbody>{validation_rows}</tbody>
</table>
<p>So: better than <b>{near:.03f} Jupiter radii</b> near the present, degrading to about
<b>{worst:.03f}</b> by the end of the century as the theory drifts away from the epoch
it was fitted to. For scale, that worst case is about a twentieth of the planet&#8217;s
own width &#8212; smaller than the beads this page draws the moons with.</p>
<p>Two things went wrong on the way here and are worth writing down. The planetary
series is referred to the <b>ecliptic of date</b>, and for a while the code precessed
it a second time on the way to the satellites. A third of a degree is invisible on the
sky and it is a fifth of a Jupiter radius in Callisto&#8217;s projected place; the
error looked exactly like a plausible theory limitation until it was measured against
Horizons and turned out to track the precession angle to four figures. Second, the
first fit of the planetary series was garbage &#8212; an eighty-five-year span cannot
tell two frequencies apart if they differ by less than about 0.012&deg; a day, and
the candidate list was full of unresolvable near-duplicates crowding out the real
terms. <b>Both were found by measuring, not by reading the code.</b></p>

<h2>What is drawn true and what is not</h2>
<p><b>True:</b> the orbit radii and Jupiter&#8217;s globe on the plan dial, to one
common scale. The telescopic strip, likewise. The shadow&#8217;s width, and its taper
&#8212; the Sun is not a point from Jupiter, so the umbra closes by about a fortieth of
its width by the time it reaches Callisto. Jupiter&#8217;s flattening, one part in
fifteen, which is why the disc is visibly an ellipse and why transit timings need it.
Every tooth count in the movement, and every mesh.</p>
<p><b>Enlarged, and said so:</b> the moons themselves, which at true scale would be
under a pixel; and the magnified disc panel, at about six times the strip&#8217;s
scale.</p>
<p><b>Indicative only:</b> the Great Red Spot. The globe turns at the true System II
rate, 9h 55m 40.6s, but <i>where the spot sits</i> in that system is not something
any theory predicts &#8212; it wanders tens of degrees a year and has to be re-set from
observation. So it is placed at a stated longitude and left to run, which is exactly
what you would have to do with a real one.</p>
<p>Nothing here is loaded from the network. No fonts, no images, no scripts from
elsewhere. Open the file with the wifi off and the instrument works, which is the least
an instrument should promise.</p>
"""
