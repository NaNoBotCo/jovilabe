"""The sky as it stands over the Great Red Spot: where the four moons are, and
whether they are up.

The jovilabe proper answers *where the moons are from here*. This answers the
opposite question — where they are from **there**, for an observer standing at the
centre of the Red Spot, 22 degrees south of Jupiter's equator, turning with the
storm once every 9h55m40s.

It is the same arithmetic seen from the other end, and it needs three things the
Earth-facing instrument never needed:

  1. **Which way Jupiter is facing.** ``jove.e5`` lands in a frame whose x-axis is
     the ascending node of Jupiter's equator on the ecliptic of date. The rotation
     from that node to Jupiter's prime meridian is calibrated here against JPL
     Horizons' own sub-observer longitude — see ``THETA_0`` — rather than derived,
     because the two frames' nodes are defined against different reference planes
     and the offset between them is exactly the kind of thing to get backwards.

  2. **Where the Red Spot is.** The spot is not a fixed feature. It drifts in
     System II, which is embarrassing for System II, since System II was defined
     from the spot's own rotation in the first place. Its longitude is therefore an
     *observed* quantity with a shelf life, measured here by inverting a year of
     published transit times (``validate_redspot.py``) and stated with its date.

  3. **A horizon.** Jupiter has no surface, so "horizon" means the top of the
     surrounding cloud deck. The Red Spot stands about 8 km above that deck, which
     buys a little extra view, and the air bends light over the edge much as ours
     does. Both allowances are named constants below with their derivations, and
     both are small: together they let the moons rise about four minutes early.

Everything is stdlib, and everything that could have been asserted is measured.
"""

from __future__ import annotations

import math

import jove
from jove import AU_KM, DEG, MOONS, R_JUP_KM, R_SUN_KM, ROMAN, _cross, _dot, _norm

# ---------------------------------------------------------------------------
# Jupiter's rotation, in the frame the satellite theory lands in.
#
# THETA_0 and THETA_RATE give the angle, measured eastward from the ascending node
# of Jupiter's equator on the ecliptic of date, to the System III prime meridian.
# The IAU gives that angle from a different node — the one on the ICRF equator —
# so the two differ by a constant, which is what THETA_NODE is. It was not
# derived; it was fitted to 758 sub-observer longitudes from JPL Horizons spanning
# 2016 to 2099, and over that span the fit is worst-case 0.006 deg out, which is
# six-tenths of a second of Jupiter's rotation. Re-run validate_redspot.py to
# check it. The tiny rate correction is the ecliptic node's own precession away
# from the ICRF one, 0.07 deg per century.
# ---------------------------------------------------------------------------
THETA_NODE = 41.058083          # ecliptic node -> ICRF node, degrees, at J2000
THETA_NODE_RATE = 1.908e-6      # ...and its drift, degrees per day

# The IAU rotation elements themselves (Archinal et al., WGCCRE). System III is the
# magnetic field's frame and is what "Jupiter's rotation" means; System II is the
# older, slower one fitted long ago to the temperate belts, and it is the frame the
# Red Spot's longitude is always quoted in.
W3_0, W3_RATE = 284.95, 870.5360000
W2_0, W2_RATE = 43.3, 870.270

# ---------------------------------------------------------------------------
# The Great Red Spot as a place to stand.
#
# Longitude: measured in validate_redspot.py by inverting 918 published transit
# times for 2026 back through this same rotation model. That recovers the
# longitude the tables were built on to +/-0.18 deg, which is exactly the scatter
# you would expect from times printed to the nearest minute — so the inversion
# adds no error of its own.
#
# The drift is the honest part. The spot has been sliding westward at roughly 16
# deg a year of late, and published sources disagree with each other by about ten
# degrees at any given moment, which is a quarter-hour of Jovian rotation. That,
# and not the arithmetic, is this dial's error bar. The spot is also some 12 deg of
# longitude wide, so "the centre of the Red Spot" is itself only good to a few
# degrees. Re-measure yearly.
# ---------------------------------------------------------------------------
GRS_EPOCH_JD = 2461000.0        # 2025 Nov 21
GRS_LON_II = 80.2               # System II west longitude at that epoch, degrees
GRS_DRIFT = 16.0 / 365.25       # degrees per day, westward
GRS_LAT = -22.4                 # planetographic, degrees; the spot's centre
GRS_HEIGHT_KM = 8.0             # cloud tops above the surrounding deck

R_JUP_POLAR_KM = jove.R_JUP_POLAR_KM
ECC2 = 1.0 - (R_JUP_POLAR_KM / R_JUP_KM) ** 2

# Radii of the four moons, km (IAU mean radii) — they are drawn to scale, and Io
# turns out to subtend very nearly what our own Moon does from the ground.
MOON_RADIUS_KM = (1821.6, 1560.8, 2631.2, 2410.3)

# ---------------------------------------------------------------------------
# Two small allowances for standing inside an atmosphere rather than above one.
#
# DIP: from 8 km up on a 71,492 km ball the horizon is depressed by
# arccos(R/(R+h)) = 0.86 deg, so the moons rise a little early and set a little
# late. This is the Red Spot's own altitude above the deck around it.
#
# REFRACTION: an estimate, not a measurement. Jupiter's air at the cloud tops is
# 86% H2 and 14% He at about 0.7 bar and 165 K, giving a refractivity of about
# 1.4e-4, and a scale height kT/(mu*m_u*g) of about 25 km. The usual horizontal
# refraction approximation (n-1)*sqrt(2R/H) then gives 0.62 deg, and that formula
# runs about 14% high on Earth, where it gives 0.65 deg against a measured 0.57 —
# so call it 0.55 deg and treat the figure as good to a factor of two. It moves a
# rise time by about a minute and a half. It is included because leaving it out
# would be a decision too, and this way the decision is visible.
# ---------------------------------------------------------------------------
HORIZON_DIP = math.degrees(math.acos(R_JUP_KM / (R_JUP_KM + GRS_HEIGHT_KM)))
HORIZON_REFRACTION = 0.55


def theta3(jd: float) -> float:
    """Eastward angle from the ecliptic node of Jupiter's equator to System III's
    prime meridian, in degrees. This is the number that says which way Jupiter is
    facing, and everything below hangs off it."""
    d = jd - 2451545.0
    return W3_0 + THETA_NODE + (W3_RATE + THETA_NODE_RATE) * d


def theta2(jd: float) -> float:
    """The same, for System II — the frame the Red Spot's longitude is quoted in."""
    d = jd - 2451545.0
    return W2_0 + THETA_NODE + (W2_RATE + THETA_NODE_RATE) * d


def grs_lon_II(jd: float) -> float:
    """The spot's System II west longitude at ``jd``, extrapolated from its epoch."""
    return (GRS_LON_II + GRS_DRIFT * (jd - GRS_EPOCH_JD)) % 360.0


def grs_lon_III(jd: float) -> float:
    """...and in System III, which is the frame JPL and SPICE want it in."""
    return (grs_lon_II(jd) + theta3(jd) - theta2(jd)) % 360.0


class Site:
    """A place to stand on Jupiter, fixed in one of the two longitude systems.

    ``lon`` is west longitude in degrees, the convention every Jovian map uses.
    A site in System II drifts slowly through System III and vice versa, so which
    system it is nailed to is part of the site, not an afterthought.
    """

    def __init__(self, lat: float, lon, system: int = 3, height_km: float = 0.0,
                 name: str = "site"):
        self.lat, self.lon, self.system = lat, lon, system
        self.height_km, self.name = height_km, name

    def west_lon(self, jd: float) -> float:
        lon = self.lon(jd) if callable(self.lon) else self.lon
        return lon % 360.0

    def meridian(self, jd: float) -> float:
        """Eastward angle from the frame's x-axis to the site's meridian."""
        th = theta2(jd) if self.system == 2 else theta3(jd)
        return th - self.west_lon(jd)

    def basis(self, jd: float):
        """(position, zenith, north, east) in Jupiter's equatorial frame, in
        equatorial radii. The position is a real vector on the spheroid, not a
        direction — from five Jupiter radii away, Io cares about the difference."""
        a = math.radians(self.meridian(jd))
        phi = math.radians(self.lat)
        ca, sa, cp, sp = math.cos(a), math.sin(a), math.cos(phi), math.sin(phi)
        # Planetographic latitude is the latitude of the local vertical, so the
        # normal is trivial and the position vector is the part that needs the
        # spheroid: N is the prime vertical radius of curvature.
        n = 1.0 / math.sqrt(1.0 - ECC2 * sp * sp)
        h = self.height_km / R_JUP_KM
        rxy, z = (n + h) * cp, (n * (1.0 - ECC2) + h) * sp
        return ((rxy * ca, rxy * sa, z),
                (cp * ca, cp * sa, sp),
                (-sp * ca, -sp * sa, cp),
                (-sa, ca, 0.0))


GRS = Site(GRS_LAT, grs_lon_II, system=2, height_km=GRS_HEIGHT_KM, name="Great Red Spot")


class Seen:
    """One body in the sky over the site."""

    def __init__(self, **kw):
        self.__dict__.update(kw)

    def __repr__(self):
        return (f"<{self.name} alt {self.alt:+6.2f} az {self.az:6.2f} "
                f"{'up' if self.up else '  '}>")


def _altaz(v, zen, nth, est):
    """Altitude and azimuth (from north, through east) of a vector in the local frame."""
    u = _norm(v)
    return (math.degrees(math.asin(max(-1.0, min(1.0, _dot(u, zen))))),
            math.degrees(math.atan2(_dot(u, est), _dot(u, nth))) % 360.0)


def _refract(alt: float) -> float:
    """Apparent altitude from geometric altitude.

    Bennett's formula, scaled so that at the horizon it gives HORIZON_REFRACTION
    instead of Earth's 34 arcminutes. The *shape* of the curve is a property of an
    exponential atmosphere and carries over; only the size of it is Jupiter's.
    """
    if alt < -2.0:
        return alt
    r = 1.0 / math.tan(math.radians(alt + 7.31 / (alt + 4.4)))  # arcmin, Earth
    return alt + r / 34.0 * HORIZON_REFRACTION


def sky(jd: float, site: Site = GRS, refraction: bool = True) -> dict:
    """Everything overhead at ``jd`` (TT): the four moons, the Sun, and the horizon.

    Altitudes are apparent — refracted, and reckoned from the depressed horizon of
    a site 8 km above the deck — so that ``alt > 0`` means the same thing an
    observer would mean by it.
    """
    st = jove.e5(jd)
    basis = st["basis"]
    pos, zen, nth, est = site.basis(jd)

    # The Sun. Jupiter is 5.2 au out, so the site's own offset from Jupiter's
    # centre moves the Sun by 0.01 deg — included anyway, since it costs nothing.
    vj, _, _, r_helio, _, _ = jove.jupiter_from(jd, "sun")
    sun_eq = jove.into_equator(basis, tuple(-c / jove.R_JUP_AU for c in vj))
    sun_v = tuple(sun_eq[k] - pos[k] for k in range(3))
    sun_dist = math.sqrt(_dot(sun_v, sun_v))
    alt, az = _altaz(sun_v, zen, nth, est)
    sun_ang = math.degrees(math.asin(R_SUN_KM / (r_helio * AU_KM)))
    sun = Seen(name="Sun", alt=(_refract(alt) if refraction else alt), az=az,
               geometric_alt=alt, dist=sun_dist, ang_radius=sun_ang,
               up=None, illum=1.0, limb_pa=0.0, eclipsed=False, roman="")
    sun.up = sun.alt > -HORIZON_DIP
    sun_hat = _norm(sun_v)

    # Jupiter's shadow, for the eclipses: a cone that closes at the rate the Sun
    # subtends from here, and whose cross-section is Jupiter's oblate silhouette.
    s_hat = _norm(sun_eq)
    sun_halfangle = R_SUN_KM / (r_helio * AU_KM)
    flat = R_JUP_POLAR_KM / R_JUP_KM

    moons = []
    for i in range(4):
        # Light-time from the moon to the site, iterated once: Io is a second and a
        # bit away, which moves it three thousandths of a degree. Small, but this is
        # the one instrument where the finite speed of light is the point.
        s = jove.into_equator(basis, st["sats"][i])
        v = tuple(s[k] - pos[k] for k in range(3))
        tau = math.sqrt(_dot(v, v)) * jove.LT_PER_RJUP
        s = jove.into_equator(jove.e5(jd - tau)["basis"], jove.e5(jd - tau)["sats"][i])
        v = tuple(s[k] - pos[k] for k in range(3))

        dist = math.sqrt(_dot(v, v))
        alt, az = _altaz(v, zen, nth, est)
        ang = math.degrees(math.asin(MOON_RADIUS_KM[i] / R_JUP_KM / dist))

        # Phase: the angle at the moon between the Sun and here. From the cloud tops
        # the moons wax and wane exactly as ours does, and near local noon they are
        # nearly full, because the Sun is behind the observer's head.
        to_sun = tuple(sun_eq[k] - s[k] for k in range(3))
        to_me = tuple(-v[k] for k in range(3))
        cosa = _dot(_norm(to_sun), _norm(to_me))
        phase = math.degrees(math.acos(max(-1.0, min(1.0, cosa))))
        illum = 0.5 * (1.0 + cosa)
        # Which way the lit limb faces, as an angle round from "up" towards the
        # right, so the crescent can be drawn the way it actually leans.
        m = _norm(v)
        su = _norm(tuple(sun_hat[k] - _dot(sun_hat, m) * m[k] for k in range(3)))
        up_v = tuple(zen[k] - _dot(zen, m) * m[k] for k in range(3))
        up_v = _norm(up_v) if _dot(up_v, up_v) > 1e-12 else nth
        rt = _cross(m, up_v)
        limb_pa = math.degrees(math.atan2(_dot(su, rt), _dot(su, up_v))) % 360.0

        # Eclipse: is the moon down the shadow, and how far off its axis?
        depth = -_dot(s, s_hat)
        perp = tuple(s[k] + depth * s_hat[k] for k in range(3))
        # The silhouette is an ellipse; squash the component along the pole.
        rho = math.sqrt(perp[0] ** 2 + perp[1] ** 2 + (perp[2] / flat) ** 2)
        umbra = 1.0 - sun_halfangle * depth if depth > 0 else 0.0
        penumbra = 1.0 + sun_halfangle * depth if depth > 0 else 0.0
        eclipsed = depth > 0 and rho < umbra
        if eclipsed:
            illum = 0.0

        app = _refract(alt) if refraction else alt
        moons.append(Seen(
            name=MOONS[i], roman=ROMAN[i], index=i,
            alt=app, geometric_alt=alt, az=az, dist=dist, dist_km=dist * R_JUP_KM,
            ang_radius=ang, illum=illum, phase=phase, limb_pa=limb_pa,
            eclipsed=eclipsed, penumbral=depth > 0 and umbra <= rho < penumbra,
            up=app > -HORIZON_DIP,
            # Standing here, is this moon in front of the Sun? Every shadow
            # transit seen from Earth is a total eclipse of the Sun for somebody
            # on the cloud tops, and Io's disc is six times the Sun's.
            sun_sep=math.degrees(math.acos(max(-1.0, min(1.0, _dot(_norm(v), sun_hat))))),
        ))
        m = moons[-1]
        m.solar_eclipse = ("total" if m.sun_sep < m.ang_radius - sun_ang else
                           "partial" if m.sun_sep < m.ang_radius + sun_ang else "")

    return {"jd": jd, "sun": sun, "moons": moons, "site": site,
            "lon_II": grs_lon_II(jd), "lon_III": site.west_lon(jd) if site.system == 3
            else grs_lon_III(jd),
            "sub_solar_lon": (theta3(jd) - math.degrees(math.atan2(s_hat[1], s_hat[0]))) % 360.0,
            "r_helio": r_helio}


# ---------------------------------------------------------------------------
# The mechanism: what a disc can and cannot do.
#
# In the frame that turns with a moon's orbit, the moon stands still and the
# observer swings round Jupiter's axis once a synodic day. So the moon's track
# across the sky closes, and it closes at a uniform rate — which is exactly what a
# disc on an arbor does. Projected stereographically from Jupiter's south pole,
# every circle about the axis becomes a circle about the dial's centre, and a
# uniform turn becomes a uniform turn. That is the astrolabe's old trick and it is
# why this dial can be a stack of four coaxial discs rather than a computer.
#
# What a disc cannot do is parallax. The observer is only one Jupiter radius from
# the axis and Io is under six, so as the site swings round, Io's direction swings
# with it by up to nine degrees, and the true track is not quite a circle. The
# radius fitted below is the best single circle through it; ``track_error`` says
# what that costs, in degrees of sky and in minutes of rise time.
# ---------------------------------------------------------------------------
SYNODIC_RATE = tuple(W2_RATE - GRS_DRIFT - r for r in
                     (203.488955790, 101.374724735, 50.317609207, 21.571071177))
SYNODIC_DAY = tuple(360.0 / r for r in SYNODIC_RATE)


def project(alt: float, az: float, lat: float = GRS_LAT) -> tuple[float, float]:
    """Sky to plate: stereographic from the pole opposite Jupiter's north.

    The dial's centre is Jupiter's north pole, which from 22 deg south stands 22
    deg *below* the horizon — so the centre of this dial is a point underfoot, and
    the horizon is the off-centre circle drawn around it. Returns (x, y) in units
    where the celestial equator is 1, x east, y towards the pole's azimuth.
    """
    # Direction in the local frame, then into a pole-centred polar coordinate.
    a, z = math.radians(az), math.radians(alt)
    e, n, u = math.cos(z) * math.sin(a), math.cos(z) * math.cos(a), math.sin(z)
    p = math.radians(lat)  # the pole is at altitude = lat (negative here)
    # Rotate so the pole is the +Z axis: the pole lies due north at altitude lat.
    pz = n * math.cos(p) + u * math.sin(p)
    pn = -n * math.sin(p) + u * math.cos(p)
    r = math.tan(0.5 * math.acos(max(-1.0, min(1.0, pz))))
    ang = math.atan2(e, pn)
    return r * math.sin(ang), r * math.cos(ang)


def ring(seen, lat: float = GRS_LAT) -> tuple[float, float]:
    """Where a body sits on the dial: (radius, angle from the meridian, degrees).

    The angle runs positive to the east — that is, positive means the body has not
    reached the meridian yet — and it is the angle a disc would have turned
    through. The radius is its distance from the projected pole, which is where the
    four moons separate: Io swings nearest the pole, Callisto furthest.
    """
    x, y = project(seen.geometric_alt, seen.az, lat)
    return math.hypot(x, y), math.degrees(math.atan2(x, y))


def _solve(m, v):
    n = len(v)
    a = [row[:] + [v[i]] for i, row in enumerate(m)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(a[r][c]))
        a[c], a[p] = a[p], a[c]
        for r in range(n):
            if r != c:
                f = a[r][c] / a[c][c]
                for k in range(c, n + 1):
                    a[r][k] -= f * a[c][k]
    return [a[i][n] / a[i][i] for i in range(n)]


def fit_disc(index: int, jd0: float = 2461000.0, span: float = 30.0, n: int = 600) -> dict:
    """The best rigid disc for one moon: where its arbor stands and how big it is.

    The model is a pin at a fixed radius on a disc turning at the moon's synodic
    rate about an arbor that need not be the dial's centre. Written out, the pin's
    place is linear in (arbor x, arbor y, and the two quadrature amplitudes), so the
    best one is a four-by-four least squares and not a search.

    The arbor offset that comes back is not a fudge. It lands, for all four moons,
    at the observer's distance from the axis divided by the moon's — which is the
    parallax exactly. The dial is off-centre because the observer is.
    """
    w = -360.0 / SYNODIC_DAY[index]
    s = [[0.0] * 4 for _ in range(4)]
    t = [0.0] * 4
    pts = []
    for k in range(n):
        jd = jd0 + span * k / n
        b = sky(jd, refraction=False)["moons"][index]
        x, y = project(b.geometric_alt, b.az)
        th = math.radians(w * (jd - jd0))
        for row, val in (([1, 0, math.sin(th), math.cos(th)], x),
                         ([0, 1, math.cos(th), -math.sin(th)], y)):
            for p in range(4):
                t[p] += row[p] * val
                for q in range(4):
                    s[p][q] += row[p] * row[q]
        pts.append((x, y, th))
    cx, cy, a, b_ = _solve(s, t)
    worst = 0.0
    for x, y, th in pts:
        mx = cx + a * math.sin(th) + b_ * math.cos(th)
        my = cy + a * math.cos(th) - b_ * math.sin(th)
        p1, p2 = unproject(x, y), unproject(mx, my)
        d = math.degrees(math.acos(max(-1.0, min(1.0,
            math.sin(math.radians(p1[0])) * math.sin(math.radians(p2[0]))
            + math.cos(math.radians(p1[0])) * math.cos(math.radians(p2[0]))
            * math.cos(math.radians(p1[1] - p2[1]))))))
        worst = max(worst, d)
    return {"offset": math.hypot(cx, cy), "radius": math.hypot(a, b_),
            "cx": cx, "cy": cy, "worst_deg": worst,
            "worst_min": worst / abs(w) * 1440.0,
            "parallax": math.degrees(math.asin(math.cos(math.radians(GRS_LAT))
                                               / jove.R_MEAN[index]))}


def crossings(index: int, jd: float, site: Site = GRS) -> dict:
    """When this moon next rises and next sets, in days from ``jd``.

    Scanned in twelve-minute steps and then bisected. Twelve minutes is safe here
    in a way it would not be for an eclipse: nothing rises and sets again inside
    half a Jovian day, and the fastest of them takes better than five hours to
    cross.
    """
    step = 12.0 / 1440.0
    out = {}
    was = sky(jd, site)["moons"][index].up
    k = 0
    while len(out) < 2 and k < int(SYNODIC_DAY[index] * 1.2 / step):
        k += 1
        now = sky(jd + k * step, site)["moons"][index].up
        if now != was:
            lo, hi = jd + (k - 1) * step, jd + k * step
            for _ in range(12):
                mid = 0.5 * (lo + hi)
                if sky(mid, site)["moons"][index].up == now:
                    hi = mid
                else:
                    lo = mid
            out.setdefault("rise" if now else "set", 0.5 * (lo + hi))
            was = now
    return out


def unproject(x: float, y: float, lat: float = GRS_LAT) -> tuple[float, float]:
    """Plate to sky — the inverse of ``project``, for drawing the horizon."""
    r = math.hypot(x, y)
    co = math.cos(2.0 * math.atan(r))
    s = math.sqrt(max(0.0, 1.0 - co * co))
    ang = math.atan2(x, y)
    pz, pn, e = co, s * math.cos(ang), s * math.sin(ang)
    p = math.radians(lat)
    n = pz * math.cos(p) - pn * math.sin(p)
    u = pz * math.sin(p) + pn * math.cos(p)
    return math.degrees(math.asin(max(-1.0, min(1.0, u)))), math.degrees(math.atan2(e, n)) % 360.0
