"""Where the four Medicean stars are — Lieske's E5 theory, and the geometry around it.

This is the arithmetic behind the jovilabe. It answers, for any instant:

  * where Io, Europa, Ganymede and Callisto stand relative to Jupiter, as seen
    from the Earth and as seen from the Sun;
  * which of them is in front of the disc, behind it, inside the shadow, or
    casting a shadow onto the cloud tops.

Those last four are the *phenomena* — the events an antique jovilabe existed to
predict, because a moment you can time from a ship's deck and from a European
observatory at the same instant is a longitude.

Two sources feed it, and both are measured rather than asserted:

  * the satellites themselves, from the E5 theory (Lieske 1977, in the form Meeus
    gives in *Astronomical Algorithms* ch. 44), checked here against JPL Horizons;
  * Jupiter's and the Earth's own places, from a compact series fitted to DE440 by
    ``fit_ephemeris.py``, whose residual is printed when it runs.

Everything is plain stdlib so this file can be the reference the browser port is
checked against, term for term.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent

DEG = math.pi / 180.0
AU_KM = 149597870.7
C_AU_PER_DAY = 173.1446326742
R_JUP_KM = 71492.0          # equatorial
R_JUP_POLAR_KM = 66854.0    # polar — Jupiter is visibly out of round, 1 part in 15
FLATTEN = R_JUP_POLAR_KM / R_JUP_KM
R_JUP_AU = R_JUP_KM / AU_KM
R_SUN_KM = 696000.0
# Light crawls one Jupiter radius in this fraction of a day. Small, but it is what
# separates a satellite's true place from its seen place, and it is the same effect
# Romer measured on a far larger baseline.
LT_PER_RJUP = R_JUP_KM / 299792.458 / 86400.0

MOONS = ("Io", "Europa", "Ganymede", "Callisto")
ROMAN = ("I", "II", "III", "IV")


# ---------------------------------------------------------------------------
# The E5 argument vocabulary.
#
# Every periodic term below is written the way the theory writes it — "l2-2l3+p3"
# — and parsed into a coefficient vector once, at import. Writing the tables as
# formulae rather than as numbers is deliberate: they can be read against the
# source, and the same strings are shipped to the browser, so the two
# implementations cannot drift apart by a typo in one of them.
# ---------------------------------------------------------------------------
ARGS = ("l1", "l2", "l3", "l4", "p1", "p2", "p3", "p4",
        "w1", "w2", "w3", "w4", "G", "Gp", "P", "psi", "Phi")
_IDX = {name: i for i, name in enumerate(ARGS)}


def parse_arg(expr: str):
    """'l2-2l3+p3' -> (coefficient vector, constant in degrees)."""
    vec = [0.0] * len(ARGS)
    const = 0.0
    tok, sign = "", 1
    expr = expr.replace(" ", "")
    i = 0
    while i <= len(expr):
        ch = expr[i] if i < len(expr) else "+"
        if ch in "+-" and tok:
            num, name = "", ""
            for c in tok:
                (num := num + c) if (c.isdigit() or c == ".") and not name else (name := name + c)
            mult = float(num) if num else 1.0
            if name:
                vec[_IDX[name]] += sign * mult
            else:
                const += sign * mult
            tok, sign = "", (1 if ch == "+" else -1)
        elif ch in "+-":
            sign = 1 if ch == "+" else -1
        else:
            tok += ch
        i += 1
    return vec, const


def _table(rows):
    """[(amplitude, 'formula'), ...] -> [(amplitude, vector, constant), ...]"""
    out = []
    for amp, expr in rows:
        vec, const = parse_arg(expr)
        out.append((amp, vec, const))
    return out


# --- Sigma_i: the corrections to the mean longitudes, in degrees ------------
SIGMA1 = _table([
    (+0.47259, "2l1-2l2"),
    (-0.03478, "p3-p4"),
    (+0.01081, "l2-2l3+p3"),
    (+0.00738, "Phi"),
    (+0.00713, "l2-2l3+p2"),
    (-0.00674, "p1+p3-2P-2G"),
    (+0.00666, "l2-2l3+p4"),
    (+0.00445, "l1-p3"),
    (-0.00354, "l1-l2"),
    (-0.00317, "2psi-2P"),
    (+0.00265, "l1-p4"),
    (-0.00186, "G"),
    (+0.00162, "p2-p3"),
    (+0.00158, "4l1-4l2"),
    (-0.00155, "l1-l3"),
    (-0.00138, "psi+w3-2P-2G"),
    (-0.00115, "2l1-4l2+2w2"),
    (+0.00089, "p2-p4"),
    (+0.00085, "l1+p3-2P-2G"),
    (+0.00083, "w2-w3"),
    (+0.00053, "psi-w2"),
])

SIGMA2 = _table([
    (+1.06476, "2l2-2l3"),
    (+0.04256, "l1-2l2+p3"),
    (+0.03581, "l2-p3"),
    (+0.02395, "l1-2l2+p4"),
    (+0.01984, "l2-p4"),
    (-0.01778, "Phi"),
    (+0.01654, "l2-p2"),
    (+0.01334, "l2-2l3+p2"),
    (+0.01294, "p3-p4"),
    (-0.01142, "l2-l3"),
    (-0.01057, "G"),
    (-0.00775, "2psi-2P"),
    (+0.00524, "2l1-2l2"),
    (-0.00460, "l1-l3"),
    (+0.00316, "psi-2G+w3-2P"),
    (-0.00203, "p1+p3-2P-2G"),
    (+0.00146, "psi-w3"),
    (-0.00145, "2G"),
    (+0.00125, "psi-w4"),
    (-0.00115, "l1-2l3+p3"),
    (-0.00094, "2l2-2w2"),
    (+0.00086, "2l1-4l2+2w2"),
    (-0.00086, "5Gp-2G+52.225"),
    (-0.00078, "l2-l4"),
    (-0.00064, "3l3-7l4+4p4"),
    (+0.00064, "p1-p4"),
    (-0.00063, "l1-2l3+p4"),
    (+0.00058, "w3-w4"),
    (+0.00056, "2psi-2P-2G"),
    (+0.00056, "2l2-2l4"),
    (+0.00055, "2l1-2l3"),
    (+0.00052, "3l3-7l4+p3+3p4"),
    (-0.00043, "l1-p3"),
    (+0.00041, "5l2-5l3"),
    (+0.00041, "p4-P"),
    (+0.00032, "w2-w3"),
    (+0.00032, "2l3-2G-2P"),
])

SIGMA3 = _table([
    (+0.16490, "l3-p3"),
    (+0.09081, "l3-p4"),
    (-0.06907, "l2-l3"),
    (+0.03784, "p3-p4"),
    (+0.01846, "2l3-2l4"),
    (-0.01340, "G"),
    (-0.01014, "2psi-2P"),
    (+0.00704, "l2-2l3+p3"),
    (-0.00620, "l2-2l3+p2"),
    (-0.00541, "l3-l4"),
    (+0.00381, "l2-2l3+p4"),
    (+0.00235, "psi-w3"),
    (+0.00198, "psi-w4"),
    (+0.00176, "Phi"),
    (+0.00130, "3l3-3l4"),
    (+0.00125, "l1-l3"),
    (-0.00119, "5Gp-2G+52.225"),
    (+0.00109, "l1-l2"),
    (-0.00100, "3l3-7l4+4p4"),
    (+0.00091, "w3-w4"),
    (+0.00080, "3l3-7l4+p3+3p4"),
    (-0.00075, "2l2-3l3+p3"),
    (+0.00072, "p1+p3-2P-2G"),
    (+0.00069, "p4-P"),
    (-0.00058, "2l3-3l4+p4"),
    (-0.00057, "l3-2l4+p4"),
    (+0.00056, "l3+p3-2P-2G"),
    (-0.00052, "l2-2l3+p1"),
    (-0.00050, "p2-p3"),
    (+0.00048, "l3-2l4+p3"),
    (-0.00045, "2l2-3l3+p4"),
    (-0.00041, "p2-p4"),
    (-0.00038, "2G"),
    (-0.00037, "p3-p4+w3-w4"),
    (-0.00032, "3l3-7l4+2p3+2p4"),
    (+0.00030, "4l3-4l4"),
    (+0.00029, "l3+p4-2P-2G"),
    (-0.00028, "w3+psi-2P-2G"),
    (+0.00026, "l3-P-G"),
    (+0.00024, "l2-3l3+2l4"),
    (+0.00021, "2l3-2P-2G"),
    (-0.00021, "l3-p2"),
    (+0.00017, "2l3-2p3"),
])

SIGMA4 = _table([
    (+0.84287, "l4-p4"),
    (+0.03431, "p4-p3"),
    (-0.03305, "2psi-2P"),
    (-0.03211, "G"),
    (-0.01862, "l4-p3"),
    (+0.01186, "psi-w4"),
    (+0.00623, "l4+p4-2G-2P"),
    (+0.00387, "2l4-2p4"),
    (-0.00284, "5Gp-2G+52.225"),
    (-0.00234, "2psi-2p4"),
    (-0.00223, "l3-l4"),
    (+0.00208, "l4-P"),
    (-0.00178, "psi+w4-2p4"),
    (+0.00134, "p4-P"),
    (+0.00125, "2l4-2G-2P"),
    (-0.00117, "2G"),
    (-0.00112, "2l3-2l4"),
    (+0.00107, "3l3-7l4+4p4"),
    (+0.00102, "l4-G-P"),
    (+0.00096, "2l4-psi-w4"),
    (+0.00087, "2psi-2w4"),
    (-0.00085, "3l3-7l4+p3+3p4"),
    (+0.00085, "l3-2l4+p4"),
    (-0.00081, "2l4-2psi"),
    (+0.00071, "l4+p4-2P-3G"),
    (+0.00061, "l1-l4"),
    (-0.00056, "psi-w3"),
    (-0.00054, "l3-2l4+p3"),
    (+0.00051, "l2-l4"),
    (+0.00042, "2psi-2G-2P"),
    (+0.00039, "2p4-2w4"),
    (+0.00036, "psi+P-p4-w4"),
    (+0.00035, "2Gp-G+188.37"),
    (-0.00035, "l4-p4+2P-2psi"),
    (-0.00032, "l4+p4-2P-G"),
    (+0.00030, "2Gp-2G+149.15"),
    (+0.00029, "3l3-7l4+2p3+2p4"),
    (+0.00028, "l4-p4+2psi-2P"),
    (-0.00028, "2l4-2w4"),
    (-0.00027, "p4-w4"),
    (-0.00026, "5Gp-3G+188.37"),
    (+0.00025, "w4-w3"),
    (-0.00025, "l2-3l3+2l4"),
    (-0.00023, "3l3-3l4"),
    (+0.00021, "2l4-2P-3G"),
    (-0.00021, "2l3-3l4+p4"),
    (+0.00019, "l4-p4-G"),
    (-0.00019, "2l4-p3-p4"),
    (-0.00018, "l4-p4+G"),
    (-0.00016, "l4+p3-2P-2G"),
])

SIGMAS = (SIGMA1, SIGMA2, SIGMA3, SIGMA4)

# --- tan B_i: the satellites' latitudes above Jupiter's equatorial plane ----
# "L1", "L2"... stand for the *true* longitudes l_i + Sigma_i, so these tables
# are evaluated after the Sigmas are known. A handful of terms also carry a
# multiple of Sigma itself; those are written out with an "S1".."S4" token.
LAT_ARGS = ARGS + ("L1", "L2", "L3", "L4", "S1", "S2", "S3", "S4")
_LIDX = {n: i for i, n in enumerate(LAT_ARGS)}


def _parse_lat(expr: str):
    vec = [0.0] * len(LAT_ARGS)
    const = 0.0
    tok, sign, i = "", 1, 0
    expr = expr.replace(" ", "")
    while i <= len(expr):
        ch = expr[i] if i < len(expr) else "+"
        if ch in "+-" and tok:
            num, name = "", ""
            for c in tok:
                (num := num + c) if (c.isdigit() or c == ".") and not name else (name := name + c)
            mult = float(num) if num else 1.0
            if name:
                vec[_LIDX[name]] += sign * mult
            else:
                const += sign * mult
            tok, sign = "", (1 if ch == "+" else -1)
        elif ch in "+-":
            sign = 1 if ch == "+" else -1
        else:
            tok += ch
        i += 1
    return vec, const


def _ltable(rows):
    return [(amp, *_parse_lat(expr)) for amp, expr in rows]


TANB = (
    _ltable([
        (+0.0006393, "L1-w1"),
        (+0.0001825, "L1-w2"),
        (+0.0000329, "L1-w3"),
        (-0.0000311, "L1-psi"),
        (+0.0000093, "L1-w4"),
        (+0.0000075, "3L1-4l2-1.9927S1+w2"),
        (+0.0000046, "L1+psi-2P-2G"),
    ]),
    _ltable([
        (+0.0081004, "L2-w2"),
        (+0.0004512, "L2-w3"),
        (-0.0003284, "L2-psi"),
        (+0.0001160, "L2-w4"),
        (+0.0000272, "l1-2l3+1.0146S2+w2"),
        (-0.0000144, "L2-w1"),
        (+0.0000143, "L2+psi-2P-2G"),
        (+0.0000035, "L2-psi+G"),
        (-0.0000028, "l1-2l3+1.0146S2+w3"),
    ]),
    _ltable([
        (+0.0032402, "L3-w3"),
        (-0.0016911, "L3-psi"),
        (+0.0006847, "L3-w4"),
        (-0.0002797, "L3-w2"),
        (+0.0000321, "L3+psi-2P-2G"),
        (+0.0000051, "L3-psi+G"),
        (-0.0000045, "L3-psi-G"),
        (-0.0000045, "L3+psi-2P"),
        (+0.0000037, "L3+psi-2P-3G"),
        (+0.0000030, "2l2-3L3+4.03S3+w2"),
        (-0.0000021, "2l2-3L3+4.03S3+w3"),
    ]),
    _ltable([
        (-0.0076579, "L4-psi"),
        (+0.0044134, "L4-w4"),
        (-0.0005112, "L4-w3"),
        (+0.0000773, "L4+psi-2P-2G"),
        (+0.0000104, "L4-psi+G"),
        (-0.0000102, "L4-psi-G"),
        (+0.0000088, "L4+psi-2P-3G"),
        (-0.0000038, "L4+psi-2P-G"),
    ]),
)

# --- R_i: the radius vectors, in Jupiter equatorial radii ------------------
R_MEAN = (5.90569, 9.39657, 14.98832, 26.36273)
RADIUS = (
    _table([
        (-0.0041339, "2l1-2l2"),
        (-0.0000387, "l1-p3"),
        (-0.0000214, "l1-p4"),
        (+0.0000170, "l1-l2"),
        (-0.0000131, "4l1-4l2"),
        (+0.0000106, "l1-l3"),
        (-0.0000066, "l1+p3-2P-2G"),
    ]),
    _table([
        (+0.0093848, "l1-l2"),
        (-0.0003116, "l2-p3"),
        (-0.0001744, "l2-p4"),
        (-0.0001442, "l2-p2"),
        (+0.0000553, "l2-l3"),
        (+0.0000523, "l1-l3"),
        (-0.0000290, "2l1-2l2"),
        (+0.0000164, "2l2-2w2"),
        (+0.0000107, "l1-2l3+p3"),
        (-0.0000102, "l2-p1"),
        (-0.0000091, "2l1-2l3"),
    ]),
    _table([
        (-0.0014388, "l3-p3"),
        (-0.0007919, "l3-p4"),
        (+0.0006342, "l2-l3"),
        (-0.0001761, "2l3-2l4"),
        (+0.0000294, "l3-l4"),
        (-0.0000156, "3l3-3l4"),
        (+0.0000156, "l1-l3"),
        (-0.0000153, "l1-l2"),
        (+0.0000070, "2l2-3l3+p3"),
        (-0.0000051, "l3+p3-2P-2G"),
    ]),
    _table([
        (-0.0073546, "l4-p4"),
        (+0.0001621, "l4-p3"),
        (+0.0000974, "l3-l4"),
        (-0.0000543, "l4+p4-2P-2G"),
        (-0.0000271, "2l4-2p4"),
        (+0.0000182, "l4-P"),
        (+0.0000177, "2l3-2l4"),
        (-0.0000167, "2l4-psi-w4"),
        (+0.0000167, "psi-w4"),
        (-0.0000155, "2l4-2P-2G"),
        (+0.0000142, "2l4-2psi"),
        (+0.0000105, "l1-l4"),
        (+0.0000092, "l2-l4"),
        (-0.0000089, "l4-P-G"),
        (-0.0000062, "l4+p4-2P-3G"),
        (+0.0000048, "2l4-2w4"),
    ]),
)

# The satellites' mean motions, degrees per day — the numbers the gear train has
# to hit, and the ones the light-time correction needs.
MEAN_MOTION = (203.488955790, 101.374724735, 50.317609207, 21.571071177)


# ---------------------------------------------------------------------------
# Jupiter and the Earth, from the series fitted to DE440.
# ---------------------------------------------------------------------------
_FIT = None


def fit():
    global _FIT
    if _FIT is None:
        _FIT = json.loads((HERE / "data" / "ephem_fit.json").read_text())
    return _FIT


def _series(block, d):
    v = 0.0
    tau = d / 36525.0
    for k, c in enumerate(block["poly"]):
        v += c * tau ** k
    for t in block["terms"]:
        th = (t["phase"] + t["rate"] * d) * DEG
        v += t["sin"] * math.sin(th) + t["cos"] * math.cos(th)
    return v


def helio(body: str, jd: float):
    """Geometric heliocentric (lon deg, lat deg, r AU), true ecliptic and equinox of DATE.

    Of date, not J2000 — that is the frame the series was fitted in, and it is also
    the frame the satellite theory lands in once Meeus's precession term is added,
    so the two can be used together without any further rotation. Precessing this
    a second time is not a small mistake: it swings Jupiter's direction by a third
    of a degree, which is nothing on the sky and a fifth of a Jupiter radius in the
    projected place of Callisto.
    """
    b = fit()[body]
    d = jd - 2451545.0
    lon = b["L0"] + b["rate"] * d + _series(b["lon"], d)
    return lon % 360.0, _series(b["lat"], d), _series(b["r"], d)


def _rect(lon_deg, lat_deg, r):
    la, be = lon_deg * DEG, lat_deg * DEG
    return (r * math.cos(be) * math.cos(la), r * math.cos(be) * math.sin(la), r * math.sin(be))


def helio_vec(body: str, jd: float):
    return _rect(*helio(body, jd))


def precession_lon(jd: float) -> float:
    """General precession in ecliptic longitude, J2000 to date, in degrees.

    Nothing inside the instrument needs this — the dial works entirely in the
    ecliptic of date. It exists so the validation scripts can carry a result back
    to J2000 and hold it against Horizons. Only the longitude drift is modelled;
    the 47"/century tilt of the ecliptic plane itself moves a satellite by well
    under a hundredth of a Jupiter radius over the instrument's span.
    """
    t = (jd - 2451545.0) / 36525.0
    return (5029.0966 * t + 1.11113 * t * t) / 3600.0


# ---------------------------------------------------------------------------
# The satellites themselves.
# ---------------------------------------------------------------------------
def e5(jd_tdb: float):
    """Ecliptic-of-date rectangular coordinates of the four moons, in Jupiter radii.

    Returns a list of (x, y, z) relative to Jupiter's centre, plus the unit vector
    of Jupiter's north pole in the same frame — which is what tells the dial which
    way is "north" and how far open the satellites' orbits are tilted towards us.
    """
    t = jd_tdb - 2443000.5

    l = [106.07719 + 203.488955790 * t,
         175.73161 + 101.374724735 * t,
         120.55883 + 50.317609207 * t,
         84.44459 + 21.571071177 * t]
    p = [97.0881 + 0.16138586 * t,
         154.8663 + 0.04726307 * t,
         188.1840 + 0.00712734 * t,
         335.2868 + 0.00184000 * t]
    w = [312.3346 - 0.13279386 * t,
         100.4411 - 0.03263064 * t,
         119.1942 - 0.00717703 * t,
         322.6186 - 0.00175934 * t]
    # The "principal inequality in Jupiter" — the 900-year swing the Jupiter-Saturn
    # commensurability puts into Jupiter's own longitude, which the satellites feel.
    gamma = (0.33033 * math.sin((163.679 + 0.0010512 * t) * DEG)
             + 0.03439 * math.sin((34.486 - 0.0161731 * t) * DEG))
    phi_lam = 199.6766 + 0.17379190 * t   # phase of the free libration
    psi = 316.5182 - 0.00000208 * t       # node of Jupiter's equator on the ecliptic
    G = 30.23756 + 0.0830925701 * t + gamma
    Gp = 31.97853 + 0.0334597339 * t
    P = 13.469942

    base = l + p + w + [G, Gp, P, psi, phi_lam]

    def evaluate(table):
        s = 0.0
        for amp, vec, const in table:
            a = const
            for i, c in enumerate(vec):
                if c:
                    a += c * base[i]
            s += amp * math.sin(a * DEG)
        return s

    sigma = [evaluate(tbl) for tbl in SIGMAS]
    L = [l[i] + sigma[i] for i in range(4)]
    ext = base + L + sigma

    # Latitudes. Their tables reference the true longitudes and, in a few terms,
    # the Sigmas themselves, so they can only be evaluated once the above is known.
    B = []
    for i in range(4):
        s = 0.0
        for amp, vec, const in TANB[i]:
            a = const
            for k, c in enumerate(vec):
                if c:
                    a += c * ext[k]
            s += amp * math.sin(a * DEG)
        B.append(math.atan(s))

    # Radius vectors.
    R = []
    for i in range(4):
        s = 0.0
        for amp, vec, const in RADIUS[i]:
            a = const
            for k, c in enumerate(vec):
                if c:
                    a += c * base[k]
            s += amp * math.cos(a * DEG)
        R.append(R_MEAN[i] * (1.0 + s))

    # Carry the B1950 frame of the theory forward to the equinox of date.
    prec = 1.3966626 * ((jd_tdb - 2433282.423) / 36525.0) \
        + 0.0003088 * ((jd_tdb - 2433282.423) / 36525.0) ** 2
    L = [x + prec for x in L]
    psi_d = psi + prec

    # Jupiter's equator on its orbit, and its orbit on the ecliptic.
    T = (jd_tdb - 2451545.0) / 36525.0
    I = 3.120262 + 0.0006 * ((jd_tdb - 2433282.5) / 36525.0)
    Om = 100.464441 + 1.0209550 * T + 0.00040117 * T * T + 0.000000569 * T ** 3
    inc = 1.303270 - 0.0054966 * T + 0.00000465 * T * T - 0.000000004 * T ** 3

    cI, sI = math.cos(I * DEG), math.sin(I * DEG)
    phi = (psi_d - Om) * DEG
    cF, sF = math.cos(phi), math.sin(phi)
    ci, si = math.cos(inc * DEG), math.sin(inc * DEG)
    cO, sO = math.cos(Om * DEG), math.sin(Om * DEG)

    def to_ecliptic(x, y, z):
        # Jupiter's equator -> its orbit -> the ecliptic of date. Four rotations,
        # in the order the planes actually nest.
        b1 = y * cI - z * sI
        c1 = y * sI + z * cI
        a2 = x * cF - b1 * sF
        b2 = x * sF + b1 * cF
        b3 = b2 * ci - c1 * si
        c3 = b2 * si + c1 * ci
        return (a2 * cO - b3 * sO, a2 * sO + b3 * cO, c3)

    # The same rotation as a matrix, so the dial can also go the other way: the
    # Sun's and the Earth's directions have to be brought *into* Jupiter's
    # equatorial plane to draw the shadow and to know which way we are looking.
    basis = [to_ecliptic(*e) for e in ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))]

    us = [(L[i] - psi_d) % 360.0 for i in range(4)]
    sats = []
    for i in range(4):
        u = us[i] * DEG
        sats.append(to_ecliptic(R[i] * math.cos(u) * math.cos(B[i]),
                                R[i] * math.sin(u) * math.cos(B[i]),
                                R[i] * math.sin(B[i])))
    return {
        "sats": sats,
        # A fictitious fifth satellite standing on Jupiter's pole gives the pole's
        # direction in the same frame, for free and by exactly the same rotations.
        "pole": basis[2],
        "basis": basis, "L": L, "R": R, "B": B, "u": us, "psi": psi_d,
        # Where each moon stands in its own orbit, which is what the rings show:
        # the angle round from the node of Jupiter's equator, and the distance out.
        # The projection onto Jupiter's equatorial plane, which is what a view from
        # above the pole shows — so the in-plane component R*cos(B), not R itself.
        # The difference is a dozen kilometres and invisible on the dial, but the
        # ring position and the rectangular vector should mean the same thing.
        "plan": [(R[i] * math.cos(us[i] * DEG) * math.cos(B[i]),
                  R[i] * math.sin(us[i] * DEG) * math.cos(B[i])) for i in range(4)],
    }


def into_equator(basis, v):
    """Bring an ecliptic direction into Jupiter's equatorial frame.

    The basis is orthonormal, so its inverse is its transpose — three dot products.
    """
    return tuple(sum(basis[k][j] * v[j] for j in range(3)) for k in range(3))


def _norm(v):
    m = math.sqrt(sum(c * c for c in v))
    return (v[0] / m, v[1] / m, v[2] / m)


def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def jupiter_from(jd: float, observer: str):
    """Astrometric vector from an observer to Jupiter, and the light-time.

    ``observer`` is 'earth' or 'sun'. The returned vector is referred to the
    ecliptic of date — the same frame ``e5`` lands in — so the two can be combined
    without any rotation between them.
    """
    obs = (0.0, 0.0, 0.0) if observer == "sun" else helio_vec("earth", jd)
    # Iterate the light-time: where was Jupiter when the light we see now left it?
    tau = 0.0
    for _ in range(3):
        j = helio_vec("jupiter", jd - tau)
        v = (j[0] - obs[0], j[1] - obs[1], j[2] - obs[2])
        dist = math.sqrt(_dot(v, v))
        tau = dist / C_AU_PER_DAY
    lon = math.degrees(math.atan2(v[1], v[0])) % 360.0
    lat = math.degrees(math.asin(v[2] / dist))
    return v, lon, lat, dist, tau, jd - tau


class View:
    """The four moons as one observer sees them.

    ``x`` runs along the projection of Jupiter's equator — the line the moons
    string themselves out along in a telescope — positive in the direction of
    increasing position angle, which is eastward when Jupiter's pole happens to
    point at the celestial one. ``y`` runs towards Jupiter's north pole. ``z`` is
    depth: positive means in front of Jupiter, towards the observer. All three are
    in Jupiter equatorial radii.
    """


def observe(jd: float, observer: str = "earth") -> View:
    v_obs_to_jup, lon, lat, dist, tau, jd_seen = jupiter_from(jd, observer)
    look = _norm((-v_obs_to_jup[0], -v_obs_to_jup[1], -v_obs_to_jup[2]))  # Jupiter -> observer

    st = e5(jd_seen)
    sats, pole = st["sats"], st["pole"]
    # Each moon is seen at its own instant: light from one in front of Jupiter left
    # it later than light from one behind it. A few seconds — and the same asymmetry
    # Romer noticed, on a baseline a thousand times shorter.
    fixed = []
    for i, s in enumerate(sats):
        fixed.append(e5(jd_seen + _dot(s, look) * LT_PER_RJUP)["sats"][i])

    yhat = _norm(tuple(pole[k] - _dot(pole, look) * look[k] for k in range(3)))
    xhat = _cross(look, yhat)

    out = View()
    out.x = [_dot(s, xhat) for s in fixed]
    out.y = [_dot(s, yhat) for s in fixed]
    out.z = [_dot(s, look) for s in fixed]
    out.r_sky = [math.hypot(a, b) for a, b in zip(out.x, out.y)]
    out.tilt = math.degrees(math.asin(max(-1.0, min(1.0, _dot(pole, look)))))
    out.dist = dist
    out.jd_seen = jd_seen
    out.jup_vec = v_obs_to_jup
    out.pole = pole
    out.look = look
    out.vecs = fixed
    out.state = st
    return out


def disc_semi_minor(tilt_deg: float) -> float:
    """Jupiter's apparent polar semi-diameter, in equatorial radii.

    Edge-on it is the true flattening, 0.935; seen over the pole it would be a
    circle. Nothing else on this instrument would notice the difference, but a
    transit that began an hour early would.
    """
    s = math.sin(tilt_deg * DEG)
    return math.sqrt(s * s + FLATTEN * FLATTEN * (1.0 - s * s))


def phenomena(jd: float):
    """Which moons are transiting, occulted, eclipsed, or casting a shadow.

    Four states, and the instrument's whole purpose. A moon can be in more than one
    at once — near opposition it is routinely eclipsed and occulted together — so
    each is reported separately rather than collapsed into a single label.
    """
    e = observe(jd, "earth")
    s = observe(jd, "sun")
    r_helio = math.sqrt(_dot(s.jup_vec, s.jup_vec))
    # Half-angle of the Sun as seen from Jupiter: the rate at which the umbra closes.
    # The Sun is not a point, so the shadow is a narrowing cone, and by Callisto's
    # orbit it has lost a fortieth of its width.
    sun_ang = R_SUN_KM / (r_helio * AU_KM)
    b_e = disc_semi_minor(e.tilt)
    b_s = disc_semi_minor(s.tilt)

    out = []
    for i in range(4):
        # In front of / behind the disc, as seen from the Earth.
        on_disc_e = (e.x[i] ** 2 + (e.y[i] / b_e) ** 2) < 1.0
        # Inside the shadow, as seen from the Sun.
        depth = -s.z[i]  # positive = behind Jupiter, down the shadow
        umbra = 1.0 - sun_ang * depth if depth > 0 else 0.0
        penumbra = 1.0 + sun_ang * depth if depth > 0 else 0.0
        rho = math.hypot(s.x[i], s.y[i] / b_s)
        out.append({
            "moon": MOONS[i], "roman": ROMAN[i],
            "transit": on_disc_e and e.z[i] > 0,
            "occulted": on_disc_e and e.z[i] < 0,
            "eclipsed": depth > 0 and rho < umbra,
            "penumbral": depth > 0 and umbra <= rho < penumbra,
            # The moon's shadow lands on Jupiter when the moon stands in front of
            # the disc as seen from the Sun.
            "shadow": (s.x[i] ** 2 + (s.y[i] / b_s) ** 2) < 1.0 and s.z[i] > 0,
            "x": e.x[i], "y": e.y[i], "z": e.z[i],
            "sx": s.x[i], "sy": s.y[i], "sz": s.z[i],
        })
    # The plan view: where each moon stands in its own orbit, seen from above
    # Jupiter's north pole, and which way the Sun and the Earth lie from there.
    st = e.state
    sun_dir = into_equator(st["basis"], _norm(s.look))
    earth_dir = into_equator(st["basis"], e.look)
    return {"moons": out, "tilt": e.tilt, "dist": e.dist, "r_helio": r_helio,
            "semi_minor": b_e, "jd_seen": e.jd_seen,
            "light_minutes": (jd - e.jd_seen) * 1440.0,
            "plan": st["plan"], "u": st["u"], "R": st["R"],
            "sun_az": math.degrees(math.atan2(sun_dir[1], sun_dir[0])) % 360.0,
            "earth_az": math.degrees(math.atan2(earth_dir[1], earth_dir[0])) % 360.0,
            "ang_radius_arcsec": math.degrees(math.asin(R_JUP_AU / e.dist)) * 3600.0}


# ---------------------------------------------------------------------------
# The phenomena, as events with beginnings and ends.
# ---------------------------------------------------------------------------
KINDS = ("eclipsed", "occulted", "transit", "shadow")
KIND_NAMES = {
    "eclipsed": "eclipse", "occulted": "occultation",
    "transit": "transit", "shadow": "shadow transit",
}


def events(jd0: float, days: float = 7.0, coarse_min: float = 6.0):
    """Every phenomenon beginning or ending in a window, to the minute.

    Scanned coarsely and then bisected. The coarse step has to be shorter than the
    briefest event worth catching: Io crosses the disc in about two hours and its
    ingress takes minutes, so six minutes is comfortable and 1 in 8 of a day's
    computation. Anything shorter than the coarse step can be missed entirely,
    which is a real limit and is stated on the page rather than papered over.
    """
    step = coarse_min / 1440.0
    n = int(days / step)
    prev = phenomena(jd0)["moons"]
    out = []
    for k in range(1, n + 1):
        jd = jd0 + k * step
        cur = phenomena(jd)["moons"]
        for i in range(4):
            for kind in KINDS:
                if cur[i][kind] == prev[i][kind]:
                    continue
                lo, hi = jd - step, jd
                want = cur[i][kind]
                for _ in range(14):  # 6 min / 2^14 is well under a second
                    mid = 0.5 * (lo + hi)
                    if phenomena(mid)["moons"][i][kind] == want:
                        hi = mid
                    else:
                        lo = mid
                out.append({
                    "jd": 0.5 * (lo + hi), "moon": MOONS[i], "index": i,
                    "kind": kind, "name": KIND_NAMES[kind],
                    "begins": want,
                })
        prev = cur
    out.sort(key=lambda e: e["jd"])
    return out
