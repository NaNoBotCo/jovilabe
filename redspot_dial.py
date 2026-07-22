"""The Red Spot dial: a lunation disc for somebody standing inside the storm.

A moonphase complication is a disc carrying a moon behind a plate with a hole in
it. The plate hides most of the moon; the shape of the plate's edge is the phase.
That is the whole machine, and it has been the whole machine since the sixteenth
century.

This is that machine with the four Galilean moons on it, and with one substitution:
the plate is no longer a stylised pair of clouds. It is Jupiter. The observer
stands at the centre of the Great Red Spot, 22 degrees south of the equator,
turning once every 9h55m40s, and the edge of the plate is that observer's horizon.
A moon goes behind the plate because it has set.

Why the dial is centred where it is
-----------------------------------
On the centre of the dial stands Jupiter's north pole. It is not an ornament and it
is not the middle of the sky — from 22 south the north pole is 22 degrees *below*
the horizon, due north. It is the centre because it is the axis: project the sky
stereographically from the pole and every daily track becomes a circle about that
point, traced at a uniform rate. Anything else, and the disc would have to speed up
and slow down. This is the astrolabe's one indispensable trick, borrowed intact.

So the moons ride four circles about one centre, and each turns once per its own
synodic day — the beat between Jupiter's rotation and the moon's orbit:

    Io  12h58m    Europa  11h14m    Ganymede  10h32m    Callisto  10h11m

Four discs, four rates, one arbor line. That is a mechanism, not a picture of one.

What the rings mean
-------------------
The four tracks lie within 5% of each other in truth, because all four moons hug
Jupiter's equator; the dial magnifies that spread about forty-fold so they can be
told apart, and the magnification is linear and stated. What it magnifies is worth
seeing, because the order of the rings is not the order of the orbits — it is the
order of *parallax*. Io is nearest, so standing on the planet displaces Io most,
and Io's ring is furthest in. The dial's radial axis measures the observer's own
offset from Jupiter's centre. You can watch Io swing in and out along it as the
Red Spot carries you sideways underneath it.

Everything moving is computed from Lieske's E5 theory in the page itself — the
same tables ``jove.py`` uses, shipped as data rather than retyped — so the file
works from a memory stick with the network off, which is the promise the rest of
this instrument makes too.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import jove
import redspot as rs

HERE = Path(__file__).resolve().parent

# ---------------------------------------------------------------------------
# Layout, in SVG units. 900 x 900, centre (450, 450).
# ---------------------------------------------------------------------------
CX = CY = 450.0
R_CASE_OUT = 442.0
R_CASE_IN = 398.0
R_SCALE_OUT = 394.0     # the outer graduation: local time, and the Sun rides it
R_SCALE_IN = 372.0
R_AP_OUT = 366.0        # the sky ring itself
R_AP_IN = 196.0
R_HUB = 190.0           # the readout in the middle

# The radial scale: drawn radius = R_A + R_K * (stereographic radius). Fixed by
# putting Io's mean track at 240 and Callisto's at 341, which spreads all four
# across the ring and leaves room for Io's parallax swing to stay clear of the hub.
R_K = 2061.0
R_A = 240.0 - R_K * 0.9382

INK = "#161f2b"
DEEP = "#0b1220"
GOLD = "#a9852f"
GOLD_LIGHT = "#d4b463"
PLATE = "#e9dfc8"
GUILLOCHE = "#d2c09a"
CLOUD_A = "#c9a583"     # the belts, engraved on the part of the plate that is Jupiter
CLOUD_B = "#e2c9ae"
SPOT = "#b4543a"
NIGHT = "#0d1a30"
DAY = "#b0bfc7"     # a convention, not a measurement — see the note on the page
MOONLIT = "#f5ead0"
COPPER = "#8a4a35"      # a moon inside Jupiter's shadow

MOON_TINT = ("#f3d99a", "#e8e4dc", "#d9c9ae", "#b7a793")  # Io is sulphur-yellow


def _f(v: float) -> str:
    return f"{v:.2f}".rstrip("0").rstrip(".")


def _p(r: float, deg: float) -> tuple[float, float]:
    """A point at radius r and angle ``deg`` measured from the top, towards the east
    (which is drawn on the right). Every angle on this dial is an hour angle."""
    t = math.radians(deg)
    return (CX + r * math.sin(t), CY - r * math.cos(t))


def _path(points, close=False) -> str:
    return ("M" + " L".join(f"{_f(x)} {_f(y)}" for x, y in points)
            + ("Z" if close else ""))


# ---------------------------------------------------------------------------
# The horizon, which is the edge of the plate.
#
# It is computed rather than drawn by eye: for each radius across the ring, the
# angle at which a body on that track actually crosses the apparent horizon —
# 1.4 degrees below the geometric one, because the Red Spot stands 8 km above the
# deck around it and Jupiter's air bends light over the edge. The two edges lean,
# and they lean by different amounts at different radii, because a nearer moon has
# more parallax. That lean is this dial's version of the moonphase plate's humps:
# it is the whole correction, cut into the metal.
# ---------------------------------------------------------------------------
HORIZON_ALT = -(rs.HORIZON_DIP + rs.HORIZON_REFRACTION)


def horizon_angle(r_true: float, alt: float = HORIZON_ALT) -> float:
    """The angle from the meridian at which a track of this radius crosses the
    horizon. Found by bisection on the projection's own inverse, so it inherits
    whatever the projection does and cannot drift from it."""
    lo, hi = 0.0, 179.9
    for _ in range(48):
        mid = 0.5 * (lo + hi)
        a, _az = rs.unproject(r_true * math.sin(math.radians(mid)),
                              r_true * math.cos(math.radians(mid)))
        if a > alt:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def _plate_path() -> str:
    """The fixed plate: everything in the ring that is below the horizon.

    Four sides — up the eastern horizon, round the bottom, down the western
    horizon, back round the inside. The two horizon edges are the only parts that
    had to be computed; they are what the moons disappear behind.
    """
    edge = [(R_AP_IN + (R_AP_OUT - R_AP_IN) * k / 40.0,
             horizon_angle((R_AP_IN + (R_AP_OUT - R_AP_IN) * k / 40.0 - R_A) / R_K))
            for k in range(41)]
    pts = [_p(rr, a) for rr, a in edge]                        # east edge, outwards
    a0 = edge[-1][1]
    pts += [_p(R_AP_OUT, a0 + (360.0 - 2 * a0) * k / 90.0)     # round the bottom
            for k in range(91)]
    pts += [_p(rr, 360.0 - a) for rr, a in reversed(edge)]      # west edge, inwards
    a1 = edge[0][1]
    pts += [_p(R_AP_IN, 360.0 - a1 - (360.0 - 2 * a1) * k / 90.0)
            for k in range(91)]                                # back round inside
    return _path(pts, close=True)


# ---------------------------------------------------------------------------
# Ornament.
# ---------------------------------------------------------------------------
def _milled_case() -> str:
    cuts = []
    for i in range(200):
        b = i * 1.8
        x0, y0 = _p(R_CASE_IN + 5.0, b)
        x1, y1 = _p(R_CASE_OUT - 5.0, b)
        cuts.append(f"M{_f(x0)} {_f(y0)}L{_f(x1)} {_f(y1)}")
    return (f"<circle cx='{CX}' cy='{CY}' r='{_f((R_CASE_IN + R_CASE_OUT) / 2)}' "
            f"fill='none' stroke='{INK}' stroke-width='{_f(R_CASE_OUT - R_CASE_IN)}'/>"
            f"<path d='{''.join(cuts)}' stroke='#3a4a5e' stroke-width='1.5' opacity='.7'/>"
            f"<circle cx='{CX}' cy='{CY}' r='{_f(R_CASE_IN + 1.5)}' fill='none' "
            f"stroke='{GOLD}' stroke-width='1.6'/>"
            f"<circle cx='{CX}' cy='{CY}' r='{_f(R_CASE_OUT - 1.5)}' fill='none' "
            f"stroke='{GOLD}' stroke-width='1.6'/>")


def _guilloche(r_out: float, r_in: float) -> str:
    """Engine-turning, the same rose-engine family the moon dial carries."""
    out = []
    for teeth, amp, weight in ((44, 9.0, 0.5), (28, 14.0, 0.35)):
        for k in range(5):
            radius = r_in + (r_out - r_in) * (k + 0.5) / 5.0
            pts = []
            for i in range(361):
                th = math.radians(i)
                rr = radius + amp * math.cos(teeth * th)
                pts.append((CX + rr * math.cos(th), CY + rr * math.sin(th)))
            out.append(f"<path d='{_path(pts, close=True)}' fill='none' "
                       f"stroke='{GUILLOCHE}' stroke-width='.5' opacity='{weight}'/>")
    return "".join(out)


def _belts() -> str:
    """Jupiter's cloud bands, engraved across the part of the plate that is Jupiter.

    Below the horizon there is nothing to draw but the planet you are standing on,
    so the plate carries its belts and zones, and the Red Spot itself sits at the
    bottom of the dial — under your feet, which is where it is.
    """
    out = []
    for k in range(9):
        rr = R_AP_IN + (R_AP_OUT - R_AP_IN) * (k + 0.5) / 9.0
        col = CLOUD_A if k % 2 else CLOUD_B
        w = (R_AP_OUT - R_AP_IN) / 9.0 * (0.85 if k % 2 else 0.7)
        out.append(f"<circle cx='{CX}' cy='{CY}' r='{_f(rr)}' fill='none' "
                   f"stroke='{col}' stroke-width='{_f(w)}' opacity='.55'/>")
    # the storm's own oval, drawn as the spiral it is
    spiral = []
    for i in range(260):
        t = i / 259.0
        a = math.radians(-t * 620.0)
        rx, ry = 74.0 * (1.0 - 0.72 * t), 46.0 * (1.0 - 0.72 * t)
        spiral.append((CX + rx * math.cos(a), CY + (R_AP_IN + R_AP_OUT) / 2 + ry * math.sin(a)))
    out.append(f"<ellipse cx='{CX}' cy='{_f(CY + (R_AP_IN + R_AP_OUT) / 2)}' rx='78' ry='49' "
               f"fill='{SPOT}' opacity='.55'/>")
    out.append(f"<path d='{_path(spiral)}' fill='none' stroke='#7c3324' "
               f"stroke-width='1.1' opacity='.5'/>")
    return "".join(out)


def _graduations() -> str:
    """The outer scale: the local day, in hours before and after the meridian.

    A Jovian day is 9h55m40s, so the marks are Earth-hours from local noon and the
    scale simply stops a shade before it meets itself at the bottom. Labelling it in
    hours anybody can read seemed better than inventing a Jovian hour.
    """
    out = [f"<circle cx='{CX}' cy='{CY}' r='{_f((R_SCALE_IN + R_SCALE_OUT) / 2)}' "
           f"fill='none' stroke='{INK}' stroke-width='{_f(R_SCALE_OUT - R_SCALE_IN)}' "
           f"opacity='.92'/>"]
    day_h = 360.0 / (rs.W2_RATE - rs.GRS_DRIFT) * 24.0   # hours in a Red Spot day
    for half_h in range(-int(day_h), int(day_h) + 1):
        h = half_h / 2.0
        if abs(h) > day_h / 2.0:
            continue
        ang = h / day_h * 360.0
        major = abs(h - round(h)) < 1e-6
        x0, y0 = _p(R_SCALE_IN + (1.0 if major else 7.0), ang)
        x1, y1 = _p(R_SCALE_OUT - 1.0, ang)
        out.append(f"<line x1='{_f(x0)}' y1='{_f(y0)}' x2='{_f(x1)}' y2='{_f(y1)}' "
                   f"stroke='{GOLD_LIGHT}' stroke-width='{1.6 if major else 0.8}' "
                   f"opacity='{0.95 if major else 0.6}'/>")
        if major and int(h) % 2 == 0 and h != 0:
            tx, ty = _p((R_SCALE_IN + R_SCALE_OUT) / 2, ang)
            out.append(f"<text x='{_f(tx)}' y='{_f(ty + 3.6)}' text-anchor='middle' "
                       f"font-size='10' fill='{GOLD_LIGHT}' font-family='Georgia,serif' "
                       f"opacity='.9'>{abs(int(h))}</text>")
    tx, ty = _p((R_SCALE_IN + R_SCALE_OUT) / 2, 0)
    out.append(f"<text x='{_f(tx)}' y='{_f(ty + 3.8)}' text-anchor='middle' font-size='10.5' "
               f"fill='{GOLD_LIGHT}' font-family='Georgia,serif' letter-spacing='1'>NOON</text>")
    return "".join(out)


def _cardinals() -> str:
    """The compass points, and which edge of the plate is which.

    Worth spelling out, because the sense of the dial catches people: from twenty-two
    degrees *south*, the moons cross the northern sky, so the top of the dial is
    north and the motion runs from east on the right to west on the left — the
    opposite way round from a northern observer's intuition.
    """
    out = []
    for label, ang in (("N", 0.0), ("E", 90.0), ("S", 180.0), ("W", 270.0)):
        x, y = _p(R_AP_OUT + 22.0, ang)
        out.append(f"<text x='{_f(x)}' y='{_f(y + 4)}' text-anchor='middle' font-size='13' "
                   f"fill='{GOLD}' font-family='Georgia,serif' letter-spacing='1'>{label}</text>")
    # Set just under the horizon rather than above it, where the moons are: the two
    # edges of the plate need naming, and nothing is ever drawn on the plate.
    for label, ang in (("rising", 99.0), ("setting", 261.0)):
        x, y = _p(308.0, ang)
        out.append(f"<text x='{_f(x)}' y='{_f(y)}' text-anchor='middle' font-size='11.5' "
                   f"fill='#8a7448' font-family='Georgia,serif' font-style='italic' "
                   f"letter-spacing='1.2' opacity='.85'>{label}</text>")
    return "".join(out)


def _tracks() -> str:
    """The four circles the moons are carried on, faintly, so the empty ones read."""
    out = []
    for i in range(4):
        fit = FITS[i]
        rr = R_A + R_K * fit["radius"]
        out.append(f"<circle cx='{CX}' cy='{CY}' r='{_f(rr)}' fill='none' "
                   f"stroke='{GOLD_LIGHT}' stroke-width='.8' opacity='.5' "
                   f"stroke-dasharray='2 5'/>")
        x, y = _p(rr, 0)
        out.append(f"<text x='{_f(x)}' y='{_f(y - 7)}' text-anchor='middle' font-size='10' "
                   f"fill='{GOLD_LIGHT}' opacity='.9' font-family='Georgia,serif' "
                   f"letter-spacing='.5'>{jove.ROMAN[i]}</text>")
    return "".join(out)


def _fits() -> list[dict]:
    """The four disc fits, cached — each one is 600 evaluations of the whole sky and
    they do not change unless the geometry does."""
    cache = HERE / "data" / "redspot_discs.json"
    if cache.exists():
        return json.loads(cache.read_text())
    out = [rs.fit_disc(i) for i in range(4)]
    cache.write_text(json.dumps(out, indent=1))
    return out


FITS = _fits()


def dial_svg() -> str:
    """The parts that do not move. Everything that does is drawn by the page."""
    sky_clip = (f"<clipPath id='ring'><path d='"
                f"M{_f(CX - R_AP_OUT)} {_f(CY)}"
                f"a{_f(R_AP_OUT)} {_f(R_AP_OUT)} 0 1 0 {_f(2 * R_AP_OUT)} 0"
                f"a{_f(R_AP_OUT)} {_f(R_AP_OUT)} 0 1 0 {_f(-2 * R_AP_OUT)} 0"
                f"M{_f(CX - R_AP_IN)} {_f(CY)}"
                f"a{_f(R_AP_IN)} {_f(R_AP_IN)} 0 1 0 {_f(2 * R_AP_IN)} 0"
                f"a{_f(R_AP_IN)} {_f(R_AP_IN)} 0 1 0 {_f(-2 * R_AP_IN)} 0"
                f"' clip-rule='evenodd'/></clipPath>")
    return f"""<svg id='dial' viewBox='0 0 900 900' xmlns='http://www.w3.org/2000/svg'>
<defs>{sky_clip}
<clipPath id='plate'><path d='{_plate_path()}'/></clipPath>
<radialGradient id='hubg' cx='50%' cy='38%'>
  <stop offset='0' stop-color='#f7f0df'/><stop offset='1' stop-color='#e0d3b6'/>
</radialGradient>
<radialGradient id='glow' cx='50%' cy='50%'>
  <stop offset='0' stop-color='#ffe9b0' stop-opacity='.95'/>
  <stop offset='1' stop-color='#ffe9b0' stop-opacity='0'/>
</radialGradient>
</defs>
<circle cx='{CX}' cy='{CY}' r='{_f(R_CASE_OUT)}' fill='{PLATE}'/>
{_guilloche(R_CASE_IN - 2, R_HUB + 4)}
{_milled_case()}
<g id='sky' clip-path='url(#ring)'><rect x='0' y='0' width='900' height='900' fill='{NIGHT}'/></g>
<g clip-path='url(#ring)'>{_tracks()}</g>
<g id='bodies'></g>
<path d='{_plate_path()}' fill='{PLATE}'/>
<g clip-path='url(#plate)' opacity='.92'>{_belts()}</g>
<path d='{_plate_path()}' fill='none' stroke='{INK}' stroke-width='1.4'/>
<circle cx='{CX}' cy='{CY}' r='{_f(R_AP_OUT)}' fill='none' stroke='{GOLD}' stroke-width='3'/>
<circle cx='{CX}' cy='{CY}' r='{_f(R_AP_IN)}' fill='none' stroke='{GOLD}' stroke-width='3'/>
{_graduations()}
{_cardinals()}
<g id='sunmark'></g>
<circle cx='{CX}' cy='{CY}' r='{_f(R_HUB)}' fill='url(#hubg)' stroke='{GOLD}' stroke-width='2.5'/>
<g id='hub'></g>
</svg>"""


# ---------------------------------------------------------------------------
# The theory, packed for the browser.
#
# The tables are shipped in the form ``jove`` has already parsed them into, not
# retyped as JavaScript source. There is therefore no second copy of Lieske's
# numbers anywhere in this project, and no way for the page and the reference
# implementation to disagree about them.
# ---------------------------------------------------------------------------
def _pack_table(table):
    out = []
    for amp, vec, const in table:
        out.append([amp, const, [[k, c] for k, c in enumerate(vec) if c]])
    return out


def payload() -> str:
    fit = jove.fit()
    data = {
        "sig": [_pack_table(t) for t in jove.SIGMAS],
        "tanb": [_pack_table(t) for t in jove.TANB],
        "rad": [_pack_table(t) for t in jove.RADIUS],
        "rmean": list(jove.R_MEAN),
        "jup": fit["jupiter"],
        "moonR": [r / jove.R_JUP_KM for r in rs.MOON_RADIUS_KM],
        "k": {
            "thetaNode": rs.THETA_NODE, "thetaNodeRate": rs.THETA_NODE_RATE,
            "w3": [rs.W3_0, rs.W3_RATE], "w2": [rs.W2_0, rs.W2_RATE],
            "grs": [rs.GRS_EPOCH_JD, rs.GRS_LON_II, rs.GRS_DRIFT, rs.GRS_LAT,
                    rs.GRS_HEIGHT_KM],
            "ecc2": rs.ECC2, "flat": rs.R_JUP_POLAR_KM / jove.R_JUP_KM,
            "rjup": jove.R_JUP_KM, "au": jove.AU_KM, "rsun": jove.R_SUN_KM,
            "ltPerR": jove.LT_PER_RJUP, "cAu": jove.C_AU_PER_DAY,
            "rjupAu": jove.R_JUP_AU,
            "dip": rs.HORIZON_DIP, "refr": rs.HORIZON_REFRACTION,
            "synodic": list(rs.SYNODIC_DAY),
            "RA": R_A, "RK": R_K, "CX": CX, "CY": CY,
            "apIn": R_AP_IN, "apOut": R_AP_OUT,
            "scale": (R_SCALE_IN + R_SCALE_OUT) / 2,
            "dayHours": 360.0 / (rs.W2_RATE - rs.GRS_DRIFT) * 24.0,
            "tints": list(MOON_TINT), "copper": COPPER, "moonlit": MOONLIT,
            "night": NIGHT, "day": DAY,
        },
        "names": list(jove.MOONS), "roman": list(jove.ROMAN),
        "fits": [{"radius": f["radius"], "offset": f["offset"],
                  "worst": f["worst_deg"], "worstMin": f["worst_min"]} for f in FITS],
    }
    return json.dumps(data, separators=(",", ":"))


JS = r"""
const D=Math.PI/180, K=DATA.k;
const A=[ "l1","l2","l3","l4","p1","p2","p3","p4","w1","w2","w3","w4","G","Gp","P","psi","Phi" ];

function ev(tbl,base){let s=0;for(const t of tbl){let a=t[1];for(const [k,c] of t[2])a+=c*base[k];s+=t[0]*Math.sin(a*D);}return s;}

/* Lieske's E5, term for term as jove.py evaluates it. */
function e5(jd){
  const t=jd-2443000.5;
  const l=[106.07719+203.488955790*t,175.73161+101.374724735*t,
           120.55883+50.317609207*t,84.44459+21.571071177*t];
  const p=[97.0881+0.16138586*t,154.8663+0.04726307*t,188.1840+0.00712734*t,335.2868+0.00184000*t];
  const w=[312.3346-0.13279386*t,100.4411-0.03263064*t,119.1942-0.00717703*t,322.6186-0.00175934*t];
  const gamma=0.33033*Math.sin((163.679+0.0010512*t)*D)+0.03439*Math.sin((34.486-0.0161731*t)*D);
  const phiLam=199.6766+0.17379190*t, psi=316.5182-0.00000208*t;
  const G=30.23756+0.0830925701*t+gamma, Gp=31.97853+0.0334597339*t, P=13.469942;
  const base=l.concat(p,w,[G,Gp,P,psi,phiLam]);
  const sigma=DATA.sig.map(tb=>ev(tb,base));
  const L=[0,1,2,3].map(i=>l[i]+sigma[i]);
  const ext=base.concat(L,sigma);
  const B=[0,1,2,3].map(i=>Math.atan(ev(DATA.tanb[i],ext)));
  const R=[0,1,2,3].map(i=>{
    let s=0;for(const tt of DATA.rad[i]){let a=tt[1];for(const [k,c] of tt[2])a+=c*base[k];s+=tt[0]*Math.cos(a*D);}
    return DATA.rmean[i]*(1+s);});
  const pr=1.3966626*((jd-2433282.423)/36525)+0.0003088*Math.pow((jd-2433282.423)/36525,2);
  const Ld=L.map(x=>x+pr), psid=psi+pr;
  const T=(jd-2451545.0)/36525;
  const I=3.120262+0.0006*((jd-2433282.5)/36525);
  const Om=100.464441+1.0209550*T+0.00040117*T*T+0.000000569*T*T*T;
  const inc=1.303270-0.0054966*T+0.00000465*T*T-0.000000004*T*T*T;
  const cI=Math.cos(I*D),sI=Math.sin(I*D),ph=(psid-Om)*D;
  const cF=Math.cos(ph),sF=Math.sin(ph),ci=Math.cos(inc*D),si=Math.sin(inc*D);
  const cO=Math.cos(Om*D),sO=Math.sin(Om*D);
  const toE=(x,y,z)=>{const b1=y*cI-z*sI,c1=y*sI+z*cI,a2=x*cF-b1*sF,b2=x*sF+b1*cF,
                       b3=b2*ci-c1*si,c3=b2*si+c1*ci;
                       return [a2*cO-b3*sO,a2*sO+b3*cO,c3];};
  const basis=[toE(1,0,0),toE(0,1,0),toE(0,0,1)];
  const sats=[0,1,2,3].map(i=>{const u=((Ld[i]-psid)%360)*D;
    return toE(R[i]*Math.cos(u)*Math.cos(B[i]),R[i]*Math.sin(u)*Math.cos(B[i]),R[i]*Math.sin(B[i]));});
  return {sats:sats,basis:basis};
}

function intoEq(basis,v){return [0,1,2].map(k=>basis[k][0]*v[0]+basis[k][1]*v[1]+basis[k][2]*v[2]);}
function dot(a,b){return a[0]*b[0]+a[1]*b[1]+a[2]*b[2];}
function norm(v){const m=Math.sqrt(dot(v,v));return [v[0]/m,v[1]/m,v[2]/m];}
function cross(a,b){return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];}

function series(block,d){let v=0,tau=d/36525;
  (block.poly||[]).forEach((c,k)=>v+=c*Math.pow(tau,k));
  for(const t of block.terms){const th=(t.phase+t.rate*d)*D;v+=t.sin*Math.sin(th)+t.cos*Math.cos(th);}
  return v;}
function helioVec(jd){const b=DATA.jup,d=jd-2451545.0;
  const lon=(b.L0+b.rate*d+series(b.lon,d))*D, lat=series(b.lat,d)*D, r=series(b.r,d);
  return [r*Math.cos(lat)*Math.cos(lon),r*Math.cos(lat)*Math.sin(lon),r*Math.sin(lat)];}
function jupFromSun(jd){let tau=0,v=null,dist=0;
  for(let i=0;i<3;i++){v=helioVec(jd-tau);dist=Math.sqrt(dot(v,v));tau=dist/K.cAu;}
  return {v:v,dist:dist};}

function theta3(jd){return K.w3[0]+K.thetaNode+(K.w3[1]+K.thetaNodeRate)*(jd-2451545.0);}
function theta2(jd){return K.w2[0]+K.thetaNode+(K.w2[1]+K.thetaNodeRate)*(jd-2451545.0);}
function grsLon(jd){return ((K.grs[1]+K.grs[2]*(jd-K.grs[0]))%360+360)%360;}

function siteBasis(jd){
  const a=(theta2(jd)-grsLon(jd))*D, phi=K.grs[3]*D;
  const ca=Math.cos(a),sa=Math.sin(a),cp=Math.cos(phi),sp=Math.sin(phi);
  const n=1/Math.sqrt(1-K.ecc2*sp*sp), h=K.grs[4]/K.rjup;
  const rxy=(n+h)*cp, z=(n*(1-K.ecc2)+h)*sp;
  return {pos:[rxy*ca,rxy*sa,z],zen:[cp*ca,cp*sa,sp],
          nth:[-sp*ca,-sp*sa,cp],est:[-sa,ca,0]};
}

function altaz(v,b){const u=norm(v);
  return [Math.asin(Math.max(-1,Math.min(1,dot(u,b.zen))))/D,
          (Math.atan2(dot(u,b.est),dot(u,b.nth))/D+360)%360];}

function refract(alt){if(alt<-2)return alt;
  const r=1/Math.tan((alt+7.31/(alt+4.4))*D);return alt+r/34*K.refr;}

function sky(jd){
  const st=e5(jd), b=siteBasis(jd);
  const js=jupFromSun(jd);
  const sunEq=intoEq(st.basis,js.v.map(c=>-c/K.rjupAu));
  const sunV=[0,1,2].map(k=>sunEq[k]-b.pos[k]);
  const sHat=norm(sunEq), sunHat=norm(sunV);
  const sa=altaz(sunV,b);
  const sunAng=Math.asin(K.rsun/(js.dist*K.au))/D;
  const sunHalf=K.rsun/(js.dist*K.au);
  const sun={name:"Sun",alt:refract(sa[0]),geo:sa[0],az:sa[1],ang:sunAng};
  sun.up=sun.alt>-K.dip;
  const moons=[];
  for(let i=0;i<4;i++){
    let s=intoEq(st.basis,st.sats[i]);
    let v=[0,1,2].map(k=>s[k]-b.pos[k]);
    const tau=Math.sqrt(dot(v,v))*K.ltPerR;
    const st2=e5(jd-tau);
    s=intoEq(st2.basis,st2.sats[i]);
    v=[0,1,2].map(k=>s[k]-b.pos[k]);
    const dist=Math.sqrt(dot(v,v)), aa=altaz(v,b);
    const ang=Math.asin(DATA.moonR[i]/dist)/D;
    const toSun=norm([0,1,2].map(k=>sunEq[k]-s[k])), toMe=norm(v.map(c=>-c));
    const cosa=Math.max(-1,Math.min(1,dot(toSun,toMe)));
    let illum=0.5*(1+cosa);
    const m=norm(v);
    const su=norm([0,1,2].map(k=>sunHat[k]-dot(sunHat,m)*m[k]));
    let up=[0,1,2].map(k=>b.zen[k]-dot(b.zen,m)*m[k]);
    up=(dot(up,up)>1e-12)?norm(up):b.nth;
    const rt=cross(m,up);
    const limb=(Math.atan2(dot(su,rt),dot(su,up))/D+360)%360;
    const depth=-dot(s,sHat);
    const perp=[0,1,2].map(k=>s[k]+depth*sHat[k]);
    const rho=Math.sqrt(perp[0]*perp[0]+perp[1]*perp[1]+Math.pow(perp[2]/K.flat,2));
    const umbra=depth>0?1-sunHalf*depth:0;
    const ecl=depth>0&&rho<umbra;
    if(ecl)illum=0;
    const app=refract(aa[0]);
    const sep=Math.acos(Math.max(-1,Math.min(1,dot(m,sunHat))))/D;
    moons.push({name:DATA.names[i],roman:DATA.roman[i],i:i,alt:app,geo:aa[0],az:aa[1],
      dist:dist,distKm:dist*K.rjup,ang:ang,illum:illum,limb:limb,eclipsed:ecl,
      up:app>-K.dip,
      solar:sep<ang-sunAng?"total":(sep<ang+sunAng?"partial":"")});
  }
  return {jd:jd,sun:sun,moons:moons,lonII:grsLon(jd),
          hourAngle:((theta2(jd)-grsLon(jd))-Math.atan2(sHat[1],sHat[0])/D)};
}

/* Sky to plate. Stereographic from the pole, which is the one projection in which
   a daily circle stays a circle and a uniform turn stays uniform. */
function project(alt,az){
  const a=az*D,z=alt*D,p=K.grs[3]*D;
  const e=Math.cos(z)*Math.sin(a),n=Math.cos(z)*Math.cos(a),u=Math.sin(z);
  const pz=n*Math.cos(p)+u*Math.sin(p), pn=-n*Math.sin(p)+u*Math.cos(p);
  const r=Math.tan(0.5*Math.acos(Math.max(-1,Math.min(1,pz))));
  return {r:r,ang:Math.atan2(e,pn)/D};
}
function place(r,angDeg){const t=angDeg*D;
  return [K.CX+r*Math.sin(t),K.CY-r*Math.cos(t)];}

/* A lit disc: the limb on the sunward side, then the terminator ellipse. Built from
   points rather than arc flags so it cannot flip at the quarters. */
function phasePath(cx,cy,R,illum,paDeg){
  /* Built in a frame whose +x points at the bright limb, then turned so that +x
     lies at position angle pa — reckoned from straight up, towards the right,
     which is how the sunward side of a moon is actually described. */
  const k=2*illum-1, pa=paDeg*D, ca=Math.cos(pa), sa=Math.sin(pa), pts=[];
  const put=(x,y)=>{pts.push([cx+x*sa+y*ca,cy-x*ca+y*sa]);};
  for(let j=0;j<=24;j++){const f=(-90+180*j/24)*D;put(R*Math.cos(f),R*Math.sin(f));}
  for(let j=24;j>=0;j--){const f=(-90+180*j/24)*D;put(-R*k*Math.cos(f),R*Math.sin(f));}
  return "M"+pts.map(p=>p[0].toFixed(2)+" "+p[1].toFixed(2)).join("L")+"Z";
}

function jdNow(){return offsetMs===null?Date.now()/86400000+2440587.5+69.184/86400
                                       :baseJd+offsetMs/86400000;}
let offsetMs=null, baseJd=0, playing=null;

/* When this moon next changes its mind about being up. Scanned in ten-minute steps
   and then bisected — safe, because nothing here rises twice in half a Jovian day
   and the quickest of them takes better than five hours to cross. Skipped during
   playback, where it would cost more than the animation. */
function nextCross(i,jd){
  const step=1/144;
  let was=sky(jd).moons[i].up;
  const n=Math.ceil(K.synodic[i]*144*1.05);
  for(let k=1;k<=n;k++){
    const t=jd+k*step, now=sky(t).moons[i].up;
    if(now!==was){
      let lo=t-step, hi=t;
      for(let b=0;b<10;b++){const mid=(lo+hi)/2;
        if(sky(mid).moons[i].up===now)hi=mid;else lo=mid;}
      return {rising:now,jd:(lo+hi)/2};
    }
  }
  return null;
}

function fmtHM(h){const s=h<0?"-":"";h=Math.abs(h);
  const hh=Math.floor(h),mm=Math.round((h-hh)*60);
  return s+hh+"h"+String(mm===60?0:mm).padStart(2,"0")+"m";}

function draw(){
  const jd=jdNow(), s=sky(jd);
  /* The sky's colour is the Sun's altitude: full day, the long Jovian twilight,
     then a night lit by whichever moons are up. */
  const a=s.sun.alt;
  const day=Math.max(0,Math.min(1,(a+9)/16));
  const mix=(c1,c2,t)=>{const p=x=>[parseInt(x.substr(1,2),16),parseInt(x.substr(3,2),16),parseInt(x.substr(5,2),16)];
    const A1=p(c1),B1=p(c2);return "rgb("+A1.map((v,i)=>Math.round(v+(B1[i]-v)*t)).join(",")+")";};
  document.getElementById("sky").innerHTML=
    "<rect x='0' y='0' width='900' height='900' fill='"+mix(K.night,K.day,day)+"'/>";

  let g="";
  /* The Sun on the outer scale, and the daylight that goes with it. */
  const sp=project(s.sun.geo,s.sun.az);
  const sxy=place(K.scale,sp.ang);
  g="<circle cx='"+sxy[0].toFixed(1)+"' cy='"+sxy[1].toFixed(1)+"' r='30' fill='url(#glow)'/>"+
    "<circle cx='"+sxy[0].toFixed(1)+"' cy='"+sxy[1].toFixed(1)+"' r='7' fill='#f6d477' stroke='#8a6a20'/>";
  document.getElementById("sunmark").innerHTML=g;

  /* The moons. Size is the true angular diameter, magnified alike for all four, so
     Io really is drawn twice Europa's width — and swells as it climbs, because it
     is nearer at the meridian than at the horizon. */
  let b="";
  for(const m of s.moons){
    const p=project(m.geo,m.az);
    const rr=K.RA+K.RK*p.r;
    if(rr<K.apIn-14||rr>K.apOut+14)continue;
    const xy=place(rr,p.ang);
    const R=Math.max(3.2,m.ang*62);
    const tint=m.eclipsed?K.copper:DATA.k.tints[m.i];
    b+="<g opacity='"+(m.up?1:0.999)+"'>";
    b+="<circle cx='"+xy[0].toFixed(1)+"' cy='"+xy[1].toFixed(1)+"' r='"+R.toFixed(1)+
       "' fill='#2a2f3a' opacity='"+(m.eclipsed?0.15:0.5)+"'/>";
    if(m.eclipsed){
      b+="<circle cx='"+xy[0].toFixed(1)+"' cy='"+xy[1].toFixed(1)+"' r='"+R.toFixed(1)+
         "' fill='"+K.copper+"' opacity='.75'/>";
    }else{
      b+="<path d='"+phasePath(xy[0],xy[1],R,m.illum,m.limb)+"' fill='"+tint+"'/>";
    }
    b+="<circle cx='"+xy[0].toFixed(1)+"' cy='"+xy[1].toFixed(1)+"' r='"+R.toFixed(1)+
       "' fill='none' stroke='#6c5a34' stroke-width='.6' opacity='.8'/>";
    b+="<text x='"+xy[0].toFixed(1)+"' y='"+(xy[1]-R-5).toFixed(1)+"' text-anchor='middle' "+
       "font-size='10' font-family='Georgia,serif' fill='#e8dcbd' opacity='.95'>"+m.roman+"</text>";
    b+="</g>";
  }
  document.getElementById("bodies").innerHTML=b;

  /* The hub: what is up, and what it is doing. Drawn as plain SVG text rather than
     borrowed HTML, so the dial stays one self-contained drawing if it is ever
     lifted out of the page. */
  const T=(x,y,t,o)=>{o=o||{};
    return "<text x='"+x+"' y='"+y+"' font-family='Georgia,serif' font-size='"+(o.size||13)+
      "' fill='"+(o.fill||"#2a3140")+"' text-anchor='"+(o.anchor||"start")+"'"+
      (o.style?" font-style='"+o.style+"'":"")+(o.ls?" letter-spacing='"+o.ls+"'":"")+
      ">"+t+"</text>";};
  const RULE=(y,w)=>"<line x1='"+(K.CX-w)+"' y1='"+y+"' x2='"+(K.CX+w)+"' y2='"+y+
    "' stroke='#c9b98f' stroke-width='.8'/>";
  let h=T(K.CX,352,"THE VIEW FROM THE",{size:11,fill:"#8d6f28",anchor:"middle",ls:1.7})+
        T(K.CX,368,"GREAT RED SPOT",{size:11,fill:"#8d6f28",anchor:"middle",ls:1.7})+
        RULE(384,120);
  s.moons.forEach((m,j)=>{
    const y=406+j*22;
    const dim=m.up?"#2a3140":"#98a0ab";
    const col=m.eclipsed?"#8a4a35":(m.up?"#2f6b45":"#98a0ab");
    h+=T(312,y,m.roman,{size:11,fill:"#8d6f28"})+
       T(334,y,m.name,{fill:dim})+
       T(470,y,m.up?m.alt.toFixed(0)+"°":"—",{anchor:"end",fill:dim})+
       T(514,y,m.up?m.az.toFixed(0)+"°":"",{anchor:"end",fill:dim})+
       T(520,y,m.eclipsed?"eclipsed":(m.up?"up":"set"),
         {size:11.5,style:"italic",fill:col});
    const c=playing?null:nextCross(m.i,jd);
    if(c)h+=T(624,y,(c.rising?"rises ":"sets ")+fmtHM((c.jd-jd)*24),
              {size:11,anchor:"end",fill:"#7b838f"});
  });
  /* Local time is just where the Sun stands: the same hour angle the outer scale
     is graduated in. */
  const solarHour=project(s.sun.geo,s.sun.az).ang/360*K.dayHours;
  const light=s.sun.up?"day":(s.sun.alt>-12?"twilight":"night");
  h+=RULE(506,120)+
     T(K.CX,526,light+" · sun "+s.sun.alt.toFixed(0)+"° · "+
       fmtHM(Math.abs(solarHour))+(solarHour<0?" past noon":" to noon"),
       {size:12,fill:"#5d6470",anchor:"middle"})+
     T(K.CX,544,"λ II  "+s.lonII.toFixed(1)+"°",
       {size:12,fill:"#5d6470",anchor:"middle"});
  const solar=s.moons.filter(m=>m.solar);
  if(solar.length)h+=T(K.CX,564,solar[0].name+" is crossing the Sun",
       {size:12,style:"italic",fill:"#8a4a35",anchor:"middle"});
  document.getElementById("hub").innerHTML=h;

  const dt=new Date((jd-2440587.5-69.184/86400)*86400000);
  document.getElementById("stamp").textContent=dt.toISOString().replace("T"," ").slice(0,16)+" UTC";
}

function step(ms){offsetMs=(offsetMs===null?(baseJd=jdNow(),0):offsetMs)+ms;draw();}
function live(){offsetMs=null;draw();}
function play(mult){
  if(playing){clearInterval(playing);playing=null;
    document.getElementById("play").textContent="▶ Run a Jovian day";return;}
  if(offsetMs===null){baseJd=jdNow();offsetMs=0;}
  document.getElementById("play").textContent="■ Stop";
  playing=setInterval(()=>{offsetMs+=mult;draw();},40);
}
setInterval(()=>{if(!playing&&offsetMs===null)draw();},20000);
"""


def page(body_extra: str = "") -> str:
    f = FITS
    tbl = "".join(
        f"<tr><td>{jove.MOONS[i]}</td><td>{rs.SYNODIC_DAY[i]*24:.3f} h</td>"
        f"<td>{f[i]['radius']:.4f}</td><td>{f[i]['offset']:.4f}</td>"
        f"<td>{f[i]['worst_deg']:.1f}&deg;</td><td>{f[i]['worst_min']:.0f} min</td></tr>"
        for i in range(4))
    return f"""<!doctype html><html lang='en'><head><meta charset='utf-8'>
<meta name='viewport' content='width=device-width,initial-scale=1'>
<title>The Red Spot dial &mdash; Jupiter's moons over a Jovian horizon</title>
<style>
:root{{--ink:#1a2431;--pale:#f6f2e8;--gold:#8d6f28;--rule:#d8cdb4;}}
*{{box-sizing:border-box}}
body{{margin:0;background:#eee8db;color:var(--ink);
  font:16.5px/1.62 Georgia,'Iowan Old Style',serif;}}
main{{max-width:840px;margin:0 auto;padding:36px 22px 90px}}
h1{{font-size:31px;line-height:1.16;margin:.1em 0 .1em;letter-spacing:-.2px}}
h2{{font-size:19px;margin:2.3em 0 .5em;letter-spacing:.3px}}
.sub{{color:#5d6470;font-style:italic;margin:0 0 1.6em}}
figure{{margin:0 0 10px}}
svg#dial{{width:100%;height:auto;display:block;
  filter:drop-shadow(0 10px 26px rgba(20,26,38,.22))}}
.controls{{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin:14px 0 6px}}
button{{font:14px Georgia,serif;padding:7px 13px;border:1px solid var(--rule);
  background:var(--pale);color:var(--ink);border-radius:3px;cursor:pointer}}
button:hover{{background:#fff}}
#stamp{{text-align:center;color:#6b7280;font-size:13.5px;letter-spacing:.4px}}
p{{margin:0 0 1.05em}}
table.spec{{border-collapse:collapse;width:100%;font-size:14.5px;margin:.6em 0 1.4em}}
table.spec th,table.spec td{{border-bottom:1px solid var(--rule);padding:6px 8px;text-align:right}}
table.spec th:first-child,table.spec td:first-child{{text-align:left}}
table.spec th{{font-weight:normal;font-style:italic;color:#5d6470}}
.note{{font-size:14.5px;color:#4d5560;border-left:2px solid var(--gold);padding:2px 0 2px 14px;
  margin:1.4em 0}}
.hubwrap{{font:12.5px/1.35 Georgia,serif;color:#2a3140;text-align:center;padding-top:2px}}
.hubtitle{{font-size:11px;letter-spacing:1.7px;color:#8d6f28;margin-bottom:7px}}
.hubtab{{border-collapse:collapse;margin:0 auto;font-size:12.5px}}
.hubtab td{{padding:1.5px 5px}}
.hubtab td.r{{color:#8d6f28;font-size:11px}}
.hubtab td.n{{text-align:right;font-variant-numeric:tabular-nums}}
.hubtab td.s{{font-style:italic;font-size:11.5px;text-align:left}}
.hubtab td.up{{color:#2f6b45}} .hubtab td.dn{{color:#98a0ab}} .hubtab td.ecl{{color:#8a4a35}}
.hubfoot{{margin-top:7px;color:#5d6470;font-size:11.5px}}
.eclipse{{margin-top:5px;color:#8a4a35;font-size:11.5px;font-style:italic}}
footer{{margin-top:3em;padding-top:1.2em;border-top:1px solid var(--rule);
  font-size:13.5px;color:#5d6470}}
</style></head><body><main>
<h1>The Red Spot dial</h1>
<p class='sub'>A moonphase complication rebuilt for somebody standing in the storm.</p>
<figure>{dial_svg()}</figure>
<div class='controls'>
<button onclick='live()'>Now</button>
<button onclick='step(-3600000)'>&minus;1 h</button>
<button onclick='step(3600000)'>+1 h</button>
<button onclick='step(-86400000)'>&minus;1 day</button>
<button onclick='step(86400000)'>+1 day</button>
<button id='play' onclick='play(600000)'>&#9654; Run a Jovian day</button>
</div>
<div id='stamp'></div>

<h2>What it is</h2>
<p>A moonphase dial is a disc carrying a moon behind a plate with a hole in it. The
plate hides most of the moon and the shape of its edge is the phase. That is the
entire machine, and it has been the entire machine since the sixteenth century.</p>
<p>This is the same machine with one substitution. The plate is no longer a pair of
stylised clouds — it is Jupiter, seen from inside its own weather. The observer
stands at the centre of the Great Red Spot, twenty-two degrees south of the equator,
carried round once every nine hours and fifty-six minutes, and the edge of the plate
is that observer's horizon. A moon slides behind the plate because it has set.</p>

<h2>Why the centre of the dial is a point underfoot</h2>
<p>Jupiter's north pole stands at the middle of this dial, and from twenty-two
degrees south the north pole is twenty-two degrees <em>below</em> the horizon, due
north. It is the centre anyway, because it is the axis. Project the sky
stereographically from the pole and two things happen at once: every daily track
becomes a circle about that point, and a steady rotation stays steady. Centre the
drawing anywhere else and the discs would have to speed up and slow down to keep
the moons in the right place. This is the astrolabe's oldest trick and it is
borrowed here intact.</p>
<p>So the four moons ride four circles about one arbor line, each turning once per
its own <em>synodic day</em> — the beat between Jupiter's rotation and the moon's
own orbital motion, which is what sets how often a moon comes round again:</p>
<table class='spec'>
<tr><th>moon</th><th>synodic day</th><th>track radius</th><th>arbor offset</th>
<th>worst error</th><th>in time</th></tr>
{tbl}</table>
<p>The <em>arbor offset</em> is the part worth staring at. A disc turning about the
dial's exact centre does not quite fit the sky; shifting its arbor a little does.
The offsets were fitted blind, four independent least squares, and they are not
free parameters that happened to help — every one of them comes out at half the
tangent of that moon's parallax, to within one per cent. (Half, because that is the
scale the stereographic projection happens to have where these tracks lie.) Which
is to say: the dial is off-centre because <em>the observer is</em>, and by exactly
as much. What is left over, the last few degrees, is second-order parallax, and no
rigid circle can carry it: at worst it puts Io eleven minutes early or late in a
thirteen-hour day, and Callisto three.</p>

<h2>How to read the rings</h2>
<p>The order of the rings is not the order of the orbits. It is the order of
parallax. Io is nearest, so standing on the planet throws Io furthest out of place,
and Io's ring is furthest in. In truth all four tracks lie within five per cent of
each other, because all four moons hug Jupiter's equator; the dial magnifies that
spread about forty-fold so they can be told apart, and the magnification is linear.
Watch Io over an hour or two and it visibly swings in and out along its ring — that
is not Io moving. That is you, being carried sideways underneath it.</p>
<p>Angles are not magnified. The top of the dial is the meridian, so a moon at the
top is at its highest, due north, about sixty-five degrees up. The right-hand edge
of the plate is where things rise and the left-hand edge is where they set. The
two edges lean, slightly, and by different amounts at different radii — that lean is
this dial's version of the moonphase plate's humps, and it is cut where each track
truly crosses the horizon rather than where a straight line would put it.</p>
<p>The moons are drawn at their true angular sizes relative to one another, and they
swell and shrink as they cross, being nearer overhead than at the horizon. Io
subtends about 34 arcminutes from the cloud tops — a shade larger than our own Moon
from the ground. They show phases, because of course they do. And when one enters
Jupiter's shadow it goes coppery rather than black: Jupiter's air bends a little red
sunlight into its own umbra, in the way ours does during a lunar eclipse. That last
is an inference from the physics, not something anyone has photographed.</p>
<p>The colour the window takes when the Sun is up is a drawing convention and
nothing more. It is set from the Sun's altitude so that the dial reads at a glance,
but nobody has stood on those cloud tops, and what little is known — a thin
hydrogen-and-helium sky under an ammonia haze, lit twenty-seven times more faintly
than noon on Earth — does not settle the question. Treat the tint as an index
finger, not as a photograph.</p>

<h2>What was checked, and against what</h2>
<p>Three things could be wrong independently, so three were tested separately.</p>
<p><strong>Which way Jupiter is facing.</strong> The satellite theory lands in a
frame whose x-axis is where Jupiter's equator crosses the ecliptic; the IAU's
rotation angle is measured from a different line entirely. The offset between them
was fitted to 758 sub-observer longitudes from JPL Horizons spanning 2016 to 2099,
and over that span the residual is worst-case 0.006&deg; — six-tenths of a second of
Jupiter's rotation.</p>
<p><strong>The sky from the cloud tops.</strong> Horizons will put an observer on
Jupiter, so it will state the altitude and azimuth of Io from a site at 22.4&deg;
south. Against 289 of those places over four days, this page's whole chain — theory,
frame, rotation, spheroid, local vertical — agrees to within about a minute and a
half of arc, which is a few seconds of time. The residue is not the chain: it is the
satellite theory's own error, which is about two thousand kilometres in a moon's
place, a twentieth of Jupiter's width, and invisible from Earth. Stand a thousand
times closer and the same error is suddenly big enough to see.</p>
<p><strong>Where the Red Spot is.</strong> This is the soft one, and it is soft
because of Jupiter rather than because of arithmetic. The spot drifts — currently
about sixteen degrees a year, westward, through the very longitude system that was
defined from its own rotation a century ago. Its longitude here was measured by
inverting 918 published transit times for 2026 back through this same rotation
model, which recovers it to 0.18&deg; — exactly the scatter you would expect from
times printed to the nearest minute, so the inversion adds nothing of its own. But
published sources disagree with each other by about ten degrees at any given
moment, and the spot is some twelve degrees of longitude wide, so "the centre of the
Red Spot" is only good to a few degrees in the first place.</p>
<div class='note'>That is this dial's real error bar: about a quarter of an hour,
and all of it in knowing where the storm is, none of it in knowing where the moons
are. Re-measure the longitude yearly — <code>validate_redspot.py</code> does it from
a published transit table in one pass.</div>

<h2>Two allowances</h2>
<p>Jupiter has no surface, so "horizon" means the top of the surrounding cloud deck.
The Red Spot stands about 8 km above that deck, which depresses its horizon by
0.86&deg;, and Jupiter's air bends light over the edge much as ours does — roughly
0.55&deg;, estimated from the refractivity of hydrogen and helium at the cloud tops
and a 25 km scale height, and good to about a factor of two. Together they let the
moons rise about four minutes early. Both are named constants with their workings
written out; neither is large enough to argue about, and both are included so that
leaving them out is not a decision made silently.</p>

<h2>What standing there would actually do to you</h2>

<p>Everything above is computed. This part is not the instrument's claim, it is
simply what is known, and it is worth writing down because the dial quietly asks you
to imagine a thing that cannot happen.</p>

<p>You would not burn. You would <em>freeze</em> — the cloud tops sit at about
&minus;145&nbsp;&deg;C. You would not breathe, because the air is nine parts hydrogen
to one part helium and no parts oxygen. You would weigh two and a half times what you
weigh now. The wind at the Spot&rsquo;s rim runs at something like 430&nbsp;km/h,
though the middle of it — where this dial stands — is comparatively calm, which is
the sort of comfort that stops being comforting when you think about it.</p>

<p>And there is nothing to stand <em>on</em>. Jupiter has no surface. You would sink,
and it would get warmer and heavier the whole way down, until somewhere in the dark
the pressure finished the argument. So: freeze, suffocate, crush — in that order,
with the burning saved for last and far too late to matter.</p>

<p class='note'>The <em>sky</em> in this dial is real. Point a telescope at Jupiter
and the moons are where it says they are; the arithmetic is checked against JPL
Horizons and the errors are printed above. The <em>observer</em> is a fiction. That
is the only thing on this page that has not been measured, and it seemed better to
say so plainly than to let a handsome dial imply otherwise.</p>

<footer>Computed in the page from Lieske's E5 theory — the same tables the reference
implementation uses, shipped as data rather than retyped, so the two cannot disagree
about a number. No network, no fonts, no images: this file works from a memory stick
with the wifi off.</footer>
{body_extra}
</main>
<script>const DATA={payload()};</script>
<script>{JS}
draw();</script>
</body></html>"""


def main() -> None:
    out = HERE / "out"
    out.mkdir(exist_ok=True)
    path = out / "redspot.html"
    path.write_text(page())
    print(f"wrote {path}  ({path.stat().st_size/1024:.0f} KB)")


if __name__ == "__main__":
    main()
