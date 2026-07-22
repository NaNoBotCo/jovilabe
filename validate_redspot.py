"""Check the view from the Red Spot against JPL, and say by how much it is out.

Three separate claims are tested here, because three separate things could be
wrong and they fail in different ways:

  1. **Which way Jupiter is facing.** Horizons is asked for the sub-observer
     longitude of Jupiter over 83 years; this file works out the same angle from
     ``jove``'s frame and reports the constant offset between them. That offset is
     ``redspot.THETA_NODE``, so this is both the calibration and its own check —
     what matters is that the residual around it is flat.

  2. **The sky from a place on the cloud tops.** Horizons will put an observer on
     Jupiter, so it will state the altitude and azimuth of Io from a site at 22.4
     south. That is the whole chain — satellite theory, frame, rotation, spheroid,
     local vertical — in one number, checked against somebody else's arithmetic.

  3. **Where the Red Spot is.** Inverted out of a year of published transit times.
     A transit is the moment the spot crosses the central meridian, so each printed
     time is a measurement of the spot's longitude, and 918 of them are a good one.

Network use is small and read-only, and every response is cached under
data/horizons/ so a second run is offline.
"""

from __future__ import annotations

import html
import math
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

import jove
import redspot as rs

HERE = Path(__file__).resolve().parent
CACHE = HERE / "data" / "horizons"
API = "https://ssd.jpl.nasa.gov/api/horizons.api"
GRS_TABLE = "https://www.projectpluto.com/jeve_grs.htm"


def _get(tag: str, url: str) -> str:
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / f"{tag}.txt"
    if path.exists():
        return path.read_text()
    with urllib.request.urlopen(url, timeout=180) as r:
        text = r.read().decode(errors="replace")
    path.write_text(text)
    return text


def horizons(tag: str, **over) -> list[list[float]]:
    q = {"format": "text", "OBJ_DATA": "NO", "MAKE_EPHEM": "YES",
         "EPHEM_TYPE": "OBSERVER", "ANG_FORMAT": "'DEG'", "CSV_FORMAT": "'YES'",
         "TIME_TYPE": "'TT'", "CAL_FORMAT": "'JD'", "EXTRA_PREC": "'YES'"}
    q.update({k: v for k, v in over.items()})
    url = API + "?" + "&".join(f"{k}={urllib.parse.quote(str(v))}" for k, v in q.items())
    text = _get(tag, url)
    if "$$SOE" not in text:
        raise SystemExit(f"Horizons refused {tag}:\n{text[:900]}")
    body = text.split("$$SOE")[1].split("$$EOE")[0].strip().splitlines()
    out = []
    for line in body:
        cells = [c.strip() for c in line.split(",")]
        nums = []
        for c in cells:
            try:
                nums.append(float(c))
            except ValueError:
                pass
        out.append(nums)
    return out


def check_facing() -> float:
    """Claim 1: the angle from the ecliptic node to Jupiter's prime meridian."""
    rows = horizons("obs599_2016-01-01_2099-01-01_40d", COMMAND="'599'",
                    CENTER="'500@399'", START_TIME="'2016-01-01'",
                    STOP_TIME="'2099-01-01'", STEP_SIZE="'40d'", QUANTITIES="'14'")
    worst = 0.0
    worst_lat = 0.0
    for jd, oblon, oblat in rows:
        v, _, _, _, _, jd_seen = jove.jupiter_from(jd, "earth")
        look = jove._norm((-v[0], -v[1], -v[2]))
        st = jove.e5(jd_seen)
        lj = jove.into_equator(st["basis"], look)
        east = math.degrees(math.atan2(lj[1], lj[0]))
        got = (east + oblon) % 360.0
        want = rs.theta3(jd_seen) % 360.0
        worst = max(worst, abs((got - want + 180.0) % 360.0 - 180.0))
        # Horizons reports the sub-observer point as the centre-line intercept, in
        # planetodetic latitude — so the direction's own latitude has to be taken
        # through the flattening before the two can be compared. That it then
        # agrees at all is a check on the pole, which nothing else here tests.
        latd = math.degrees(math.asin(lj[2]))
        graphic = math.degrees(math.atan(math.tan(math.radians(latd))
                                         / (1.0 - rs.ECC2)))
        worst_lat = max(worst_lat, abs(oblat - graphic))
    print(f"  facing:   {len(rows)} sub-observer longitudes, 2016-2099")
    print(f"            worst error {worst:.4f} deg "
          f"= {worst / rs.W3_RATE * 86400:.2f} s of Jupiter's rotation")
    print(f"            pole, from the sub-observer latitude: {worst_lat:.4f} deg")
    return worst


def check_sky(days: float = 4.0) -> float:
    """Claim 2: altitude and azimuth of each moon from a site on the cloud tops.

    The site is nailed to System III rather than to the Red Spot, deliberately —
    this tests the geometry alone, with none of the spot's own observational
    uncertainty folded in.
    """
    lat, west = rs.GRS_LAT, 90.0
    site = rs.Site(lat, west, system=3, height_km=0.0, name="test site")
    start, stop, step = "2026-07-01", "2026-07-05", "20m"
    worst = 0.0
    for i, code in enumerate(("501", "502", "503", "504")):
        rows = horizons(f"site{code}_{start}_{stop}_{step}", COMMAND=f"'{code}'",
                        CENTER="'coord@599'", COORD_TYPE="'GEODETIC'",
                        # Horizons wants the site as an east longitude, and for a
                        # west-positive body that means a negative one.
                        SITE_COORD=f"'{west - 360.0},{lat},0'", START_TIME=f"'{start}'",
                        STOP_TIME=f"'{stop}'", STEP_SIZE=f"'{step}'",
                        QUANTITIES="'4'", APPARENT="'AIRLESS'")
        bad = 0.0
        for row in rows:
            jd, az, alt = row[0], row[1], row[2]
            m = rs.sky(jd, site=site, refraction=False)["moons"][i]
            a1, a2 = math.radians(alt), math.radians(m.geometric_alt)
            sep = math.degrees(math.acos(max(-1.0, min(1.0,
                math.sin(a1) * math.sin(a2) + math.cos(a1) * math.cos(a2)
                * math.cos(math.radians(az - m.az))))))
            bad = max(bad, sep)
        worst = max(worst, bad)
        print(f"  sky:      {jove.MOONS[i]:<9s} {len(rows):4d} places over {days:g} days,"
              f" worst {bad * 3600:6.1f} arcsec")
    return worst


def check_spot() -> tuple[float, float]:
    """Claim 3: the Red Spot's longitude, out of a year of transit times.

    Each printed transit is the moment the spot lay on the central meridian, so
    running the rotation model backwards through it returns the longitude whoever
    computed the table was using. The scatter of the answers is the test: times
    printed to the nearest minute cannot do better than 0.17 deg rms, so anything
    near that means the model and theirs agree as closely as the printing allows.
    """
    text = _get("projectpluto_grs_2026", GRS_TABLE)
    text = html.unescape(re.sub(r"<[^>]+>", "", text))
    months = {m: i + 1 for i, m in enumerate(
        "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split())}
    stamps = re.findall(r"(20\d\d) (\w\w\w) (\d\d) (\d\d):(\d\d)", text)
    dt = 69.184 / 86400.0  # TT - UTC: 32.184 s plus 37 leap seconds

    def jd_of(y, mo, d, h, mi):
        a = (14 - mo) // 12
        yy, mm = y + 4800 - a, mo + 12 * a - 3
        jdn = (d + (153 * mm + 2) // 5 + 365 * yy + yy // 4 - yy // 100
               + yy // 400 - 32045)
        return jdn - 0.5 + (h + mi / 60.0) / 24.0 + dt

    xs, ys = [], []
    for y, mo, d, h, mi in stamps:
        jd = jd_of(int(y), months[mo], int(d), int(h), int(mi))
        v, _, _, _, _, jd_seen = jove.jupiter_from(jd, "earth")
        look = jove._norm((-v[0], -v[1], -v[2]))
        lj = jove.into_equator(jove.e5(jd_seen)["basis"], look)
        east = math.degrees(math.atan2(lj[1], lj[0]))
        xs.append(jd_seen - rs.GRS_EPOCH_JD)
        ys.append((rs.theta2(jd_seen) - east) % 360.0)
    # Unwrap, then a straight line: the intercept is the longitude at the epoch and
    # the slope is whatever drift the table's author built in.
    un, prev = [], ys[0]
    for v in ys:
        while v - prev > 180.0:
            v -= 360.0
        while v - prev < -180.0:
            v += 360.0
        un.append(v)
        prev = v
    n = len(xs)
    sx, sy = sum(xs), sum(un)
    sxx = sum(x * x for x in xs)
    sxy = sum(x * y for x, y in zip(xs, un))
    slope = (n * sxy - sx * sy) / (n * sxx - sx * sx)
    icept = (sy - slope * sx) / n
    resid = [y - (icept + slope * x) for x, y in zip(xs, un)]
    rms = (sum(r * r for r in resid) / n) ** 0.5
    print(f"  spot:     {n} transits, {min(xs):.0f} to {max(xs):.0f} d from epoch")
    print(f"            lambda_II = {icept % 360.0:.2f} deg at JD {rs.GRS_EPOCH_JD:.1f},"
          f" drift {slope * 365.25:+.1f} deg/yr")
    print(f"            residual {rms:.3f} deg rms "
          f"(minute-rounding alone gives 0.17)")
    return icept % 360.0, slope


def check_mechanism() -> None:
    """What the four discs can do: the fitted arbor, and what it costs.

    Each disc is a rigid circle turning at a rate a gear train can hold. The
    residual is second-order parallax — the part of "you are standing on the
    planet, not at its centre" that no single circle can carry.
    """
    print("  discs:    arbor    radius   worst error")
    for i in range(4):
        fit = rs.fit_disc(i)
        print(f"            {jove.MOONS[i]:<9s} {fit['offset']:.4f}  {fit['radius']:.4f}"
              f"   {fit['worst_deg']:.2f} deg = {fit['worst_min']:.1f} min")


def main() -> None:
    print("The view from the Great Red Spot, against JPL Horizons and the tables:")
    check_facing()
    check_sky()
    check_spot()
    check_mechanism()


if __name__ == "__main__":
    main()
