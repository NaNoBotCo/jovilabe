"""The instrument: an antique jovilabe drawn entirely as geometry.

Everything on the page is a path computed from the same constants the arithmetic
uses. No bitmaps, no webfonts, no network calls — the file works from a file://
URL with the wifi off, which is the promise the sibling moon complication makes
and the one an instrument this old-fashioned ought to keep.

The plan dial is drawn to TRUE SCALE. Callisto really does ride twenty-six
Jupiter radii out, and Jupiter really is a bead at that distance. Orreries have
always cheated this — swelling the globes so they can be painted — and the cheat
is precisely what stops people realising how much empty space is up there. The
telescopic panel below is where the magnification lives, and it says so.

Layers of the plan dial, from the back forwards, which is the order they are drawn:

    case -> wheelwork behind the piercings -> plate -> zodiac ring -> orbit rings
         -> shadow cone -> Jupiter -> the four moons -> indices
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import jove

HERE = Path(__file__).resolve().parent

# ---------------------------------------------------------------------------
# Layout. viewBox 1000 x 1000, centre (500, 500), y down.
# ---------------------------------------------------------------------------
CX = CY = 500.0
R_CASE_OUT = 494.0
R_CASE_IN = 460.0
R_ZODIAC_OUT = 456.0
R_ZODIAC_IN = 398.0
R_PLATE = 393.0        # the pierced plate the wheelwork shows through
R_ORBIT_MAX = 330.0    # Callisto's ring

# One Jupiter equatorial radius, in dial units. Everything inside the plate is
# true to this — the orbits, the globe, and the width of the shadow.
SCALE = R_ORBIT_MAX / jove.R_MEAN[3]

INK = "#20180d"
BRASS = "#96723a"
BRASS_DK = "#6d5027"
BRASS_LT = "#c8a765"
PLATE = "#efe4cc"
GUILLOCHE = "#dccfae"
STEEL = "#5a6472"
NIGHT = "#111d31"
SHADOW_FILL = "#141d2e"
JUP_BODY = "#d9c197"
JUP_BELT = "#9c7448"
JUP_SPOT = "#b4573c"
MOON_INK = ("#c8632f", "#cfa96a", "#8d8577", "#5d5346")  # Io, Europa, Ganymede, Callisto
MOON_NAMES = jove.MOONS
ROMAN = jove.ROMAN

ZODIAC = ("ARI", "TAU", "GEM", "CNC", "LEO", "VIR",
          "LIB", "SCO", "SGR", "CAP", "AQR", "PSC")


def _f(v: float) -> str:
    """Trim float noise out of emitted path data — the file is served, not read."""
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def _p(r: float, bearing_deg: float, cx=CX, cy=CY):
    """A point at radius r and a bearing measured clockwise from twelve o'clock."""
    t = math.radians(bearing_deg - 90.0)
    return (cx + r * math.cos(t), cy + r * math.sin(t))


def _path(points, close=False) -> str:
    d = "M" + " L".join(f"{_f(x)} {_f(y)}" for x, y in points)
    return d + ("Z" if close else "")


def _arc_ring(r_out: float, r_in: float, cx=CX, cy=CY) -> str:
    """An annulus as one even-odd path — two circles, outer then inner."""
    return (f"M{_f(cx - r_out)} {_f(cy)}a{_f(r_out)} {_f(r_out)} 0 1 0 {_f(2 * r_out)} 0"
            f"a{_f(r_out)} {_f(r_out)} 0 1 0 {_f(-2 * r_out)} 0Z"
            f"M{_f(cx - r_in)} {_f(cy)}a{_f(r_in)} {_f(r_in)} 0 1 0 {_f(2 * r_in)} 0"
            f"a{_f(r_in)} {_f(r_in)} 0 1 0 {_f(-2 * r_in)} 0Z")


# ---------------------------------------------------------------------------
# Ornament
# ---------------------------------------------------------------------------
def guilloche(r_out: float, r_in: float, cx=CX, cy=CY, rings: int = 5) -> str:
    """Engine-turning: nested hypotrochoids, the way a rose engine cuts them.

    Sampled in proportion to the radius. Cutting the same 481 points into a
    ninety-unit sub-dial as into a four-hundred-unit main plate cost a hundred
    kilobytes an inch and drew nothing the eye could see.
    """
    out = []
    steps = max(160, min(620, int(r_out * 1.55)))
    scale = r_out / 393.0
    for teeth, amp, weight in ((32, 11.0, 0.5), (46, 7.0, 0.34), (20, 16.0, 0.28)):
        for k in range(rings):
            radius = r_in + (r_out - r_in) * (k + 0.5) / rings
            pts = []
            for i in range(steps + 1):
                th = 2.0 * math.pi * i / steps
                rr = radius + amp * scale * math.cos(teeth * th)
                pts.append((cx + rr * math.cos(th), cy + rr * math.sin(th)))
            out.append(f"<path d='{_path(pts, True)}' fill='none' stroke='{GUILLOCHE}' "
                       f"stroke-width='.55' opacity='{weight}'/>")
    return "".join(out)


def milled_case() -> str:
    """A knurled bezel: 200 radial cuts, the way a case edge is actually milled."""
    cuts = []
    for i in range(200):
        a = i * 1.8
        x1, y1 = _p(R_CASE_IN + 1.0, a)
        x2, y2 = _p(R_CASE_OUT - 1.0, a)
        cuts.append(f"M{_f(x1)} {_f(y1)}L{_f(x2)} {_f(y2)}")
    return (f"<circle cx='{CX}' cy='{CY}' r='{R_CASE_OUT}' fill='{BRASS}'/>"
            f"<circle cx='{CX}' cy='{CY}' r='{R_CASE_OUT - 1}' fill='none' "
            f"stroke='{BRASS_LT}' stroke-width='2'/>"
            f"<path d='{''.join(cuts)}' stroke='{BRASS_DK}' stroke-width='1.1' opacity='.55'/>"
            f"<circle cx='{CX}' cy='{CY}' r='{R_CASE_IN}' fill='{PLATE}' "
            f"stroke='{BRASS_DK}' stroke-width='2'/>")


def beaded(r: float, n: int = 120, rad: float = 2.0, cx=CX, cy=CY) -> str:
    """A ring of beads — the cheapest ornament a case-maker has, and the oldest."""
    d = []
    for i in range(n):
        x, y = _p(r, i * 360.0 / n, cx, cy)
        d.append(f"M{_f(x - rad)} {_f(y)}a{_f(rad)} {_f(rad)} 0 1 0 {_f(2 * rad)} 0"
                 f"a{_f(rad)} {_f(rad)} 0 1 0 {_f(-2 * rad)} 0Z")
    return f"<path d='{''.join(d)}' fill='{BRASS_LT}' opacity='.7'/>"


# ---------------------------------------------------------------------------
# Wheelwork
# ---------------------------------------------------------------------------
MODULE = 1.30  # dial units per tooth of pitch diameter — one module for every wheel


def pitch_r(teeth: int) -> float:
    return MODULE * teeth / 2.0


def gear_path(cx: float, cy: float, teeth: int, phase: float = 0.0) -> str:
    """A wheel of ``teeth`` teeth at the common module, as one closed path.

    The profile is a plain trapezoid rather than a true involute. At the sizes
    these are drawn the difference is under half a pixel, and a real involute
    flank would be a lie about precision the rest of the drawing does not claim.
    """
    r = pitch_r(teeth)
    tip, root = r + MODULE * 0.62, r - MODULE * 0.78
    w = 2.0 * math.pi / teeth
    pts = []
    for i in range(teeth):
        a = phase + i * w
        for frac, rr in ((0.00, root), (0.20, tip), (0.50, tip), (0.70, root)):
            th = a + frac * w
            pts.append((cx + rr * math.cos(th), cy + rr * math.sin(th)))
    return _path(pts, True)


def wheel_group(cx, cy, teeth, colour=BRASS, crossings=True, label=None) -> str:
    """A wheel with its crossings — the spokes a clockmaker cuts to save weight."""
    r = pitch_r(teeth)
    out = [f"<path d='{gear_path(cx, cy, teeth)}' fill='{colour}' stroke='{BRASS_DK}' "
           f"stroke-width='.5'/>"]
    if crossings and r > 16:
        n = 5 if r > 44 else 4
        rim, hub = r - MODULE * 2.6, max(4.0, r * 0.17)
        holes = []
        for i in range(n):
            a0 = i * 2 * math.pi / n + 0.36
            a1 = (i + 1) * 2 * math.pi / n - 0.36
            pts = [(cx + hub * 1.5 * math.cos(a0), cy + hub * 1.5 * math.sin(a0))]
            steps = 12
            for k in range(steps + 1):
                a = a0 + (a1 - a0) * k / steps
                pts.append((cx + rim * math.cos(a), cy + rim * math.sin(a)))
            pts.append((cx + hub * 1.5 * math.cos(a1), cy + hub * 1.5 * math.sin(a1)))
            holes.append(_path(pts, True))
        out.append(f"<path d='{''.join(holes)}' fill='{PLATE}' opacity='.85'/>")
        out.append(f"<circle cx='{_f(cx)}' cy='{_f(cy)}' r='{_f(hub)}' fill='{BRASS_DK}'/>")
    else:
        out.append(f"<circle cx='{_f(cx)}' cy='{_f(cy)}' r='{_f(max(2.0, r * 0.22))}' "
                   f"fill='{BRASS_DK}'/>")
    if label:
        out.append(f"<text class='teeth' x='{_f(cx)}' y='{_f(cy - r - 5)}'>{label}</text>")
    return "".join(out)


def train_layout(train):
    """Arbor positions for a train, meshing properly at the common module.

    Each stage is a pinion on one arbor driving a wheel on the next, so the centre
    distance between them is the sum of their pitch radii. Nothing here is fudged:
    if two circles touch in the drawing, those two wheels really would mesh.
    """
    arbors = [{"x": 0.0, "pinion": train[0][1], "wheel": None}]
    x = 0.0
    for k, (w, p) in enumerate(train):
        x += pitch_r(p) + pitch_r(w)
        nxt = train[k + 1][1] if k + 1 < len(train) else None
        arbors.append({"x": x, "wheel": w, "pinion": nxt})
    return arbors


def train_svg(train, y, x0, name, rate_days, idx) -> str:
    """One train drawn along a horizontal line, with its wheels turning."""
    arbors = train_layout(train)
    out = [f"<g class='train' data-train='{idx}'>"]
    # The line of arbors, drawn first so the wheels sit on it.
    out.append(f"<line x1='{_f(x0 - 12)}' y1='{_f(y)}' x2='{_f(x0 + arbors[-1]['x'] + 12)}' "
               f"y2='{_f(y)}' stroke='{STEEL}' stroke-width='1' opacity='.35'/>")
    # Ratio so far, so each arbor knows how fast it turns: the drawing animates at
    # the true relative rates, which is the only way the picture stays a mechanism.
    ratio = 1.0
    for k, a in enumerate(arbors):
        x = x0 + a["x"]
        if a["wheel"]:
            ratio *= a["wheel"] / train[k - 1][1]
            out.append(f"<g class='rot' data-turns='{1.0/ratio:.9f}' "
                       f"style='transform-origin:{_f(x)}px {_f(y)}px'>"
                       + wheel_group(x, y, a["wheel"], BRASS, True,
                                     str(a["wheel"])) + "</g>")
        if a["pinion"]:
            out.append(f"<g class='rot' data-turns='{1.0/ratio:.9f}' "
                       f"style='transform-origin:{_f(x)}px {_f(y)}px'>"
                       + wheel_group(x, y, a["pinion"], BRASS_LT, False,
                                     None if a["wheel"] else str(a["pinion"])) + "</g>")
    out.append(f"<text class='trainname' x='{_f(x0 - 18)}' y='{_f(y + 5)}' "
               f"text-anchor='end'>{name}</text>")
    out.append("</g>")
    return "".join(out)


def differential_svg(cx, cy) -> str:
    """The bevel differential that makes Ganymede exact.

    Two inputs, one carrier, and the carrier turns at the mean of them. Feed it
    Europa geared up three times and Io running backwards and it produces
    (3n2 - n1)/2, which the Laplace resonance says *is* Ganymede's rate. Not an
    approximation that drifts slowly — an identity.
    """
    R = 46.0
    out = [f"<circle cx='{_f(cx)}' cy='{_f(cy)}' r='{_f(R + 16)}' fill='none' "
           f"stroke='{STEEL}' stroke-width='1.2' stroke-dasharray='5 4' opacity='.6'/>"]
    # carrier
    out.append(f"<g class='rot' data-turns='0.13977160' style='transform-origin:{_f(cx)}px {_f(cy)}px'>"
               f"<circle cx='{_f(cx)}' cy='{_f(cy)}' r='{_f(R)}' fill='none' "
               f"stroke='{BRASS}' stroke-width='7' opacity='.9'/>"
               f"<circle cx='{_f(cx)}' cy='{_f(cy - R)}' r='9' fill='{BRASS_LT}' "
               f"stroke='{BRASS_DK}'/>"
               f"<circle cx='{_f(cx)}' cy='{_f(cy + R)}' r='9' fill='{BRASS_LT}' "
               f"stroke='{BRASS_DK}'/></g>")
    # the two inputs, turning opposite ways
    out.append(f"<g class='rot' data-turns='-0.56524564' "
               f"style='transform-origin:{_f(cx - R - 26)}px {_f(cy)}px'>"
               + wheel_group(cx - R - 26, cy, 22, BRASS_LT, False) + "</g>")
    out.append(f"<g class='rot' data-turns='0.84479276' "
               f"style='transform-origin:{_f(cx + R + 26)}px {_f(cy)}px'>"
               + wheel_group(cx + R + 26, cy, 22, BRASS_LT, False) + "</g>")
    out.append(f"<text class='teeth' x='{_f(cx - R - 26)}' y='{_f(cy + 34)}'>Io, reversed</text>")
    out.append(f"<text class='teeth' x='{_f(cx + R + 26)}' y='{_f(cy + 34)}'>Europa &#215;3</text>")
    out.append(f"<text class='trainname' x='{_f(cx)}' y='{_f(cy + R + 40)}' "
               f"text-anchor='middle'>Ganymede &#8212; the mean of the two</text>")
    return "".join(out)


def movement_svg(gear_data) -> str:
    """The whole movement: four geared trains and one differential.

    Drawn at a single module, so every mesh in the picture is a mesh that would
    work. The wheels turn at their true relative rates when the dial runs.
    """
    by_name = {g["name"]: g for g in gear_data if "train" in g}
    labels = {"Jupiter round the zodiac": "Jupiter&#8217;s year"}
    # Two columns. The three satellite trains are small enough to stack on the
    # left; Jupiter's year needs three wheels of well over a hundred teeth and
    # takes the right on its own, with the differential beneath it.
    columns = (["Io", "Europa", "Callisto"], ["Jupiter round the zodiac"])
    x0s = (150.0, 640.0)

    def height_of(g):
        arbors = train_layout(g["train"])
        return max(pitch_r(a["wheel"] or 6) for a in arbors) * 2 + 42

    placed, col_bottom = [], []
    for col, names in enumerate(columns):
        y = 0.0
        for name in names:
            g = by_name[name]
            h = height_of(g)
            y += h / 2 + 20
            placed.append((g, x0s[col], y, col))
            y += h / 2
        col_bottom.append(y)

    diff_cy = col_bottom[1] + 150.0
    width = 1120.0
    height = max(col_bottom[0], diff_cy + 130.0) + 30.0
    body = [f"<rect x='0' y='0' width='{_f(width)}' height='{_f(height)}' rx='14' "
            f"fill='{PLATE}' stroke='{BRASS_DK}' stroke-width='2'/>",
            f"<line x1='{_f(width*0.5)}' y1='24' x2='{_f(width*0.5)}' y2='{_f(height-24)}' "
            f"stroke='{BRASS_DK}' stroke-width='1' opacity='.25'/>"]
    for i, (g, x0, yy, _col) in enumerate(placed):
        name = labels.get(g["name"], g["name"])
        body.append(train_svg(g["train"], yy, x0, name, g["period_days"], i))
    body.append(differential_svg(width * 0.74, diff_cy))
    return (f"<svg class='movement' viewBox='0 0 {_f(width)} {_f(height)}' "
            f"xmlns='http://www.w3.org/2000/svg' role='img' "
            f"aria-label='The wheelwork: four geared trains and a differential'>"
            + "".join(body) + "</svg>")


# ---------------------------------------------------------------------------
# The plan dial
# ---------------------------------------------------------------------------
def _annular_sector(r1, r2, a0, a1, cx=CX, cy=CY, steps=26) -> str:
    pts = [_p(r1, a0 + (a1 - a0) * k / steps, cx, cy) for k in range(steps + 1)]
    pts += [_p(r2, a1 - (a1 - a0) * k / steps, cx, cy) for k in range(steps + 1)]
    return _path(pts, True)


WINDOWS = [(b - 26.0, b + 26.0) for b in (45.0, 135.0, 225.0, 315.0)]
WIN_IN, WIN_OUT = 340.0, 386.0


def _window_wheels() -> str:
    """Wheel teeth showing through the piercings.

    These are not the movement — the movement has its own drawing. They are the
    edges of it, caught in the apertures the way you catch a glimpse of the train
    through the pierced plate of a skeleton clock.
    """
    out = []
    for i, (a0, a1) in enumerate(WINDOWS):
        mid = (a0 + a1) / 2.0
        for j, (rr, teeth, turns) in enumerate(((362.0, 96, 12.0), (322.0, 64, -5.0))):
            cx, cy = _p(rr, mid + (8.0 if j else -8.0))
            out.append(f"<g class='rot' data-turns='{turns * (i + 1):.4f}' "
                       f"style='transform-origin:{_f(cx)}px {_f(cy)}px'>"
                       + wheel_group(cx, cy, teeth, BRASS_DK if j else BRASS, True)
                       + "</g>")
    return "".join(out)


def _zodiac_ring() -> str:
    out = [f"<path d='{_arc_ring(R_ZODIAC_OUT, R_ZODIAC_IN)}' fill='{PLATE}' "
           f"fill-rule='evenodd' stroke='{BRASS_DK}' stroke-width='1.6'/>"]
    ticks = []
    for d in range(0, 360, 5):
        # Longitude runs anticlockwise on the sky; the dial follows it, so a
        # bearing here is minus the ecliptic longitude.
        long_tick = (d % 30 == 0)
        r0 = R_ZODIAC_IN + (0 if long_tick else (10 if d % 10 else 6))
        x1, y1 = _p(r0, -d)
        x2, y2 = _p(R_ZODIAC_OUT, -d)
        ticks.append(f"M{_f(x1)} {_f(y1)}L{_f(x2)} {_f(y2)}")
    out.append(f"<path d='{''.join(ticks)}' stroke='{INK}' stroke-width='.9' opacity='.75'/>")
    for i, name in enumerate(ZODIAC):
        x, y = _p((R_ZODIAC_IN + R_ZODIAC_OUT) / 2.0, -(i * 30.0 + 15.0))
        out.append(f"<text class='zsign' x='{_f(x)}' y='{_f(y + 6)}'>{name}</text>")
    return "".join(out)


def _orbit_rings() -> str:
    out = []
    for i in range(4):
        r = SCALE * jove.R_MEAN[i]
        out.append(f"<circle cx='{CX}' cy='{CY}' r='{_f(r)}' fill='none' "
                   f"stroke='{BRASS}' stroke-width='1.1' opacity='.85'/>")
        # A graduation every ten degrees of orbital angle, so the ring reads as a
        # scale and not just a decorative circle.
        ticks = []
        for d in range(0, 360, 10):
            big = (d % 90 == 0)
            x1, y1 = _p(r - (5 if big else 3), -d)
            x2, y2 = _p(r + (5 if big else 3), -d)
            ticks.append(f"M{_f(x1)} {_f(y1)}L{_f(x2)} {_f(y2)}")
        out.append(f"<path d='{''.join(ticks)}' stroke='{BRASS_DK}' "
                   f"stroke-width='.7' opacity='.5'/>")
        out.append(f"<text class='ringlab' x='{CX}' y='{_f(CY - r - 9)}'>{ROMAN[i]}</text>")
    return "".join(out)


def _shadow_cone() -> str:
    """Jupiter's shadow, drawn as the narrowing cone it really is.

    The Sun is half a degree wide from here, so the umbra closes at about 0.0009
    radians per Jupiter radius and has lost a fortieth of its width by the time it
    reaches Callisto. Invisible on the page; the difference between an eclipse
    predicted and an eclipse missed at the edges.
    """
    far = 27.6
    sun_ang = jove.R_SUN_KM / (5.2 * jove.AU_KM)
    umb = [(SCALE * d, SCALE * (1.0 - sun_ang * d)) for d in (1.0, far)]
    pen = [(SCALE * d, SCALE * (1.0 + sun_ang * d)) for d in (1.0, far)]
    def band(pts, fill, op):
        p = [(x, -w) for x, w in pts] + [(x, w) for x, w in reversed(pts)]
        return (f"<path d='{_path([(CX + a, CY + b) for a, b in p], True)}' "
                f"fill='{fill}' opacity='{op}'/>")
    return ("<g id='shadow'>" + band(pen, SHADOW_FILL, .18) + band(umb, SHADOW_FILL, .5)
            + "</g>")


def _jupiter_plan() -> str:
    """Jupiter from above its own pole: half in sunlight, half not.

    Drawn at true size, which at this scale is a bead twelve units across. That is
    the honest proportion and the whole reason the shadow reaches so far.
    """
    r = SCALE
    return (f"<g id='jupplan'>"
            f"<circle cx='{CX}' cy='{CY}' r='{_f(r)}' fill='{SHADOW_FILL}'/>"
            f"<path d='M{_f(CX)} {_f(CY - r)}a{_f(r)} {_f(r)} 0 0 1 0 {_f(2 * r)}Z' "
            f"fill='{JUP_BODY}' id='juplit'/>"
            f"<circle cx='{CX}' cy='{CY}' r='{_f(r)}' fill='none' stroke='{BRASS_DK}' "
            f"stroke-width='.8'/></g>")


def _moon_beads() -> str:
    out = []
    for i in range(4):
        out.append(
            f"<g class='bead' id='bead{i}'>"
            f"<circle r='9' fill='{MOON_INK[i]}' stroke='{INK}' stroke-width='1'/>"
            f"<text class='beadlab' y='-14'>{ROMAN[i]}</text></g>")
    return "".join(out)


def dial_svg() -> str:
    clip = ("<clipPath id='plateclip'><path fill-rule='evenodd' d='"
            + f"M{_f(CX - R_PLATE)} {_f(CY)}a{_f(R_PLATE)} {_f(R_PLATE)} 0 1 0 "
              f"{_f(2 * R_PLATE)} 0a{_f(R_PLATE)} {_f(R_PLATE)} 0 1 0 {_f(-2 * R_PLATE)} 0Z"
            + "".join(_annular_sector(WIN_IN, WIN_OUT, a0, a1) for a0, a1 in WINDOWS)
            + "'/></clipPath>")
    plate = ("<path fill-rule='evenodd' fill='" + PLATE + "' d='"
             + f"M{_f(CX - R_PLATE)} {_f(CY)}a{_f(R_PLATE)} {_f(R_PLATE)} 0 1 0 "
               f"{_f(2 * R_PLATE)} 0a{_f(R_PLATE)} {_f(R_PLATE)} 0 1 0 {_f(-2 * R_PLATE)} 0Z"
             + "".join(_annular_sector(WIN_IN, WIN_OUT, a0, a1) for a0, a1 in WINDOWS)
             + "'/>")
    rims = "".join(
        f"<path d='{_annular_sector(WIN_IN, WIN_OUT, a0, a1)}' fill='none' "
        f"stroke='{BRASS_DK}' stroke-width='1.6'/>" for a0, a1 in WINDOWS)
    return f"""
<svg class='dial' viewBox='0 0 1000 1000' xmlns='http://www.w3.org/2000/svg' role='img'
     aria-label='A jovilabe: the four Galilean moons in their orbits about Jupiter,
                 with Jupiter&#8217;s shadow and a zodiac ring'>
  <defs>{clip}</defs>
  <!-- 1. the case -->
  {milled_case()}
  <!-- 2. the wheelwork, which the plate will cover except at the piercings -->
  {_window_wheels()}
  <!-- 3. the plate, pierced -->
  {plate}
  <g clip-path='url(#plateclip)'>{guilloche(R_PLATE - 6, 200.0)}</g>
  {rims}
  <!-- 4. the zodiac, in ecliptic longitude -->
  {_zodiac_ring()}
  {beaded(R_ZODIAC_IN - 7, 96, 1.9)}
  <g id='zodhands'>
    <g id='jhand'>
      <path d='M{_f(CX)} {_f(CY - R_ZODIAC_OUT + 6)}L{_f(CX - 11)} {_f(CY - 352)}
         L{_f(CX)} {_f(CY - 336)}L{_f(CX + 11)} {_f(CY - 352)}Z'
         fill='{BRASS_DK}' stroke='{PLATE}' stroke-width='1.2'/>
      <circle cx='{CX}' cy='{_f(CY - 366)}' r='7' fill='{BRASS_DK}'
         stroke='{PLATE}' stroke-width='1.4'/></g>
    <g id='ehand'><circle cx='{CX}' cy='{_f(CY - R_ZODIAC_IN + 20)}' r='7'
       fill='{STEEL}' stroke='{PLATE}' stroke-width='1.8'/></g>
  </g>
  <!-- 5. the orbits, true to scale -->
  {_orbit_rings()}
  <!-- 6. the shadow, then the globe, then the moons -->
  {_shadow_cone()}
  {_jupiter_plan()}
  {_moon_beads()}
  <!-- 7. the cartouche -->
  <text class='sig' x='{CX}' y='{_f(CY + 372)}'>IOVILABIVM &#183; MEDICEORVM SIDERVM</text>
</svg>"""


# ---------------------------------------------------------------------------
# The telescopic view — what an eyepiece actually shows
# ---------------------------------------------------------------------------
SCOPE_W, SCOPE_H = 1200.0, 210.0
SCOPE_CX, SCOPE_CY = SCOPE_W / 2.0, SCOPE_H / 2.0
SCOPE_R = 20.6          # dial units per Jupiter radius: Callisto just fits


def scope_svg() -> str:
    """The strip: Jupiter and four points of light, to true scale.

    This is the picture Galileo drew night after night in the winter of 1610, and
    the reason he drew it so often is that it is the only picture in the sky that
    visibly changes in an hour. East is to the left, north up, the way it is on a
    star chart and not the way it is in most telescopes.
    """
    out = [f"<rect x='0' y='0' width='{_f(SCOPE_W)}' height='{_f(SCOPE_H)}' rx='10' "
           f"fill='{NIGHT}'/>"]
    # The line of the orbits, for reference.
    out.append(f"<line x1='24' y1='{_f(SCOPE_CY)}' x2='{_f(SCOPE_W - 24)}' "
               f"y2='{_f(SCOPE_CY)}' stroke='{BRASS}' stroke-width='.6' opacity='.28'/>")
    for i in range(4):
        r = SCOPE_R * jove.R_MEAN[i]
        out.append(f"<circle cx='{_f(SCOPE_CX)}' cy='{_f(SCOPE_CY)}' r='{_f(r)}' fill='none' "
                   f"stroke='{BRASS}' stroke-width='.5' opacity='.16'/>")
    out.append(f"<g id='scopejup'>"
               f"<ellipse cx='{_f(SCOPE_CX)}' cy='{_f(SCOPE_CY)}' rx='{_f(SCOPE_R)}' "
               f"ry='{_f(SCOPE_R * jove.FLATTEN)}' fill='{JUP_BODY}'/>"
               f"<rect x='{_f(SCOPE_CX - SCOPE_R)}' y='{_f(SCOPE_CY - SCOPE_R * .42)}' "
               f"width='{_f(2 * SCOPE_R)}' height='{_f(SCOPE_R * .2)}' fill='{JUP_BELT}' "
               f"opacity='.75'/>"
               f"<rect x='{_f(SCOPE_CX - SCOPE_R)}' y='{_f(SCOPE_CY + SCOPE_R * .2)}' "
               f"width='{_f(2 * SCOPE_R)}' height='{_f(SCOPE_R * .2)}' fill='{JUP_BELT}' "
               f"opacity='.75'/></g>")
    for i in range(4):
        out.append(f"<g class='smoon' id='sm{i}'>"
                   f"<circle r='5' fill='{MOON_INK[i]}' stroke='#f2e6cc' stroke-width='.8'/>"
                   f"<text class='smlab' y='-11'>{ROMAN[i]}</text></g>")
    out.append(f"<text class='compass' x='30' y='{_f(SCOPE_H - 14)}'>east</text>"
               f"<text class='compass' x='{_f(SCOPE_W - 30)}' y='{_f(SCOPE_H - 14)}' "
               f"text-anchor='end'>west</text>")
    return (f"<svg class='scope' viewBox='0 0 {_f(SCOPE_W)} {_f(SCOPE_H)}' "
            f"xmlns='http://www.w3.org/2000/svg' role='img' "
            f"aria-label='Jupiter and its four moons through a telescope, to scale'>"
            + "".join(out) + "</svg>")


DISC_R = 132.0


def disc_svg() -> str:
    """Jupiter's disc, magnified, where transits and shadow transits are legible.

    The globe here is drawn about six times larger relative to the moons' orbits
    than it truly is. It has to be: a shadow crossing the cloud tops is the finest
    thing this instrument predicts and at true scale it would be two pixels wide.
    """
    cx = cy = 160.0
    belts = []
    for y0, h, op in ((-0.62, .10, .35), (-0.40, .17, .8), (0.16, .19, .8),
                      (0.50, .11, .4), (-0.05, .07, .2)):
        belts.append(f"<rect x='{_f(cx - DISC_R)}' y='{_f(cy + DISC_R * y0)}' "
                     f"width='{_f(2 * DISC_R)}' height='{_f(DISC_R * h)}' "
                     f"fill='{JUP_BELT}' opacity='{op}'/>")
    return f"""
<svg class='disc' viewBox='0 0 320 320' xmlns='http://www.w3.org/2000/svg' role='img'
     aria-label='Jupiter&#8217;s disc with the Great Red Spot, transits and shadows'>
  <defs><clipPath id='discclip'><ellipse cx='{_f(cx)}' cy='{_f(cy)}'
      rx='{_f(DISC_R)}' ry='{_f(DISC_R * jove.FLATTEN)}'/></clipPath></defs>
  <rect x='0' y='0' width='320' height='320' rx='10' fill='{NIGHT}'/>
  <ellipse cx='{_f(cx)}' cy='{_f(cy)}' rx='{_f(DISC_R)}'
     ry='{_f(DISC_R * jove.FLATTEN)}' fill='{JUP_BODY}'/>
  <g clip-path='url(#discclip)'>
    {''.join(belts)}
    <ellipse id='grs' cx='{_f(cx)}' cy='{_f(cy + DISC_R * 0.25)}' rx='{_f(DISC_R * .17)}'
       ry='{_f(DISC_R * .085)}' fill='{JUP_SPOT}' opacity='.85'/>
    <g id='discmarks'></g>
    <!-- the night side: Jupiter is never more than a few degrees off full from here,
         but the sliver is real and it is which limb the shadows fall past -->
    <rect id='termin' x='0' y='0' width='0' height='320' fill='{SHADOW_FILL}' opacity='.55'/>
  </g>
  <ellipse cx='{_f(cx)}' cy='{_f(cy)}' rx='{_f(DISC_R)}' ry='{_f(DISC_R * jove.FLATTEN)}'
     fill='none' stroke='{BRASS_DK}' stroke-width='1.2' opacity='.7'/>
  <text class='compass' x='160' y='306' text-anchor='middle'>the disc, magnified</text>
</svg>"""


# ---------------------------------------------------------------------------
# Two sub-dials
# ---------------------------------------------------------------------------
def light_dial_svg() -> str:
    """Romer's light equation: how long ago the thing you are looking at happened.

    The scale is minutes of light-time. Romer's whole discovery lives in the swing
    of this hand: the eclipses ran late when it read high and early when it read
    low, by just the amount the hand had moved.
    """
    cx = cy = 130.0
    R = 96.0
    lo, hi = 30.0, 56.0
    ticks, labels = [], []
    for m in range(30, 57, 2):
        a = -120.0 + 240.0 * (m - lo) / (hi - lo)
        big = (m % 5 == 0)
        x1, y1 = _p(R - (13 if big else 7), a, cx, cy)
        x2, y2 = _p(R, a, cx, cy)
        ticks.append(f"M{_f(x1)} {_f(y1)}L{_f(x2)} {_f(y2)}")
        if big:
            lx, ly = _p(R - 27, a, cx, cy)
            labels.append(f"<text class='subnum' x='{_f(lx)}' y='{_f(ly + 5)}'>{m}</text>")
    return f"""
<svg class='sub' viewBox='0 0 260 260' xmlns='http://www.w3.org/2000/svg' role='img'
     aria-label='Sub-dial: the light equation, in minutes'>
  <circle cx='{_f(cx)}' cy='{_f(cy)}' r='{_f(R + 26)}' fill='{BRASS}'/>
  <circle cx='{_f(cx)}' cy='{_f(cy)}' r='{_f(R + 16)}' fill='{PLATE}'
     stroke='{BRASS_DK}' stroke-width='1.6'/>
  {guilloche(R + 8, 30.0, cx, cy, 3)}
  <path d='{''.join(ticks)}' stroke='{INK}' stroke-width='1.4'/>
  {''.join(labels)}
  <text class='sublab' x='{_f(cx)}' y='{_f(cy - 34)}'>LIGHT EQVATION</text>
  <text class='sublab2' x='{_f(cx)}' y='{_f(cy + 52)}'>minutes</text>
  <g id='lighthand'><path d='M{_f(cx)} {_f(cy + 14)}L{_f(cx - 4)} {_f(cy - R + 20)}
     L{_f(cx)} {_f(cy - R + 8)}L{_f(cx + 4)} {_f(cy - R + 20)}Z' fill='{STEEL}'/></g>
  <circle cx='{_f(cx)}' cy='{_f(cy)}' r='6' fill='{BRASS_DK}'/>
  <text class='subread' id='lightread' x='{_f(cx)}' y='{_f(cy + 82)}'>&#8212;</text>
</svg>"""


def resonance_dial_svg() -> str:
    """The Laplace resonance, shown by a needle that does not move.

    Three hands run round at the three mean longitudes. The fourth needle carries
    the combination L1 - 3 L2 + 2 L3, and it sits at half a turn and stays there —
    for as long as anybody has been able to measure. That stillness is the reason
    the differential in the movement can be exact.
    """
    cx = cy = 130.0
    R = 96.0
    ticks = []
    for d in range(0, 360, 15):
        big = (d % 90 == 0)
        x1, y1 = _p(R - (12 if big else 6), d, cx, cy)
        x2, y2 = _p(R, d, cx, cy)
        ticks.append(f"M{_f(x1)} {_f(y1)}L{_f(x2)} {_f(y2)}")
    hands = []
    for i, col in enumerate(MOON_INK[:3]):
        hands.append(f"<g class='reshand' id='rh{i}'><line x1='{_f(cx)}' y1='{_f(cy)}' "
                     f"x2='{_f(cx)}' y2='{_f(cy - R + 22 + i * 13)}' stroke='{col}' "
                     f"stroke-width='3' stroke-linecap='round'/></g>")
    return f"""
<svg class='sub' viewBox='0 0 260 260' xmlns='http://www.w3.org/2000/svg' role='img'
     aria-label='Sub-dial: the Laplace resonance argument, pinned at half a turn'>
  <circle cx='{_f(cx)}' cy='{_f(cy)}' r='{_f(R + 26)}' fill='{BRASS}'/>
  <circle cx='{_f(cx)}' cy='{_f(cy)}' r='{_f(R + 16)}' fill='{PLATE}'
     stroke='{BRASS_DK}' stroke-width='1.6'/>
  {guilloche(R + 8, 26.0, cx, cy, 3)}
  <path d='{''.join(ticks)}' stroke='{INK}' stroke-width='1.2' opacity='.8'/>
  <text class='sublab' x='{_f(cx)}' y='{_f(cy - 40)}'>RESONANTIA</text>
  {''.join(hands)}
  <g id='resarg'><path d='M{_f(cx)} {_f(cy + 20)}L{_f(cx - 6)} {_f(cy - R + 6)}
     L{_f(cx)} {_f(cy - R - 4)}L{_f(cx + 6)} {_f(cy - R + 6)}Z' fill='{INK}'/></g>
  <g id='restrue'><line x1='{_f(cx)}' y1='{_f(cy + 16)}' x2='{_f(cx)}' y2='{_f(cy - R - 8)}'
     stroke='#b4573c' stroke-width='1.6'/></g>
  <circle cx='{_f(cx)}' cy='{_f(cy)}' r='7' fill='{BRASS_DK}'/>
  <text class='subread' id='resread' x='{_f(cx)}' y='{_f(cy + 82)}'>&#8212;</text>
</svg>"""
