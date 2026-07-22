"""Check the satellite theory against JPL Horizons, and say by how much it is out.

The instrument's claim is that it agrees with the sky. This is where that claim
is tested rather than asserted. Horizons is asked for the true geocentric places
of Jupiter and of its four large moons over a long span; ``jove.py`` is asked for
the same instants; and the difference is reported in Jupiter radii — the unit the
dial is actually drawn in, so the number means something to a reader.

Network use is small and read-only: a handful of text queries to
ssd.jpl.nasa.gov, cached under data/horizons/ so a re-run is offline.
"""

from __future__ import annotations

import json
import math
import sys
import urllib.parse
import urllib.request
from pathlib import Path

import jove

HERE = Path(__file__).resolve().parent
CACHE = HERE / "data" / "horizons"
API = "https://ssd.jpl.nasa.gov/api/horizons.api"
RECORD = HERE / "data" / "validation.json"

# 599 is Jupiter itself, not the system barycentre — the moons' offsets are
# measured from the planet's centre, so the reference has to be too.
BODIES = {"jupiter": "599", "Io": "501", "Europa": "502", "Ganymede": "503", "Callisto": "504"}


def fetch(command: str, start: str, stop: str, step: str) -> str:
    CACHE.mkdir(parents=True, exist_ok=True)
    tag = f"{command}_{start}_{stop}_{step}".replace(" ", "").replace(":", "")
    path = CACHE / f"{tag}.txt"
    if path.exists():
        return path.read_text()
    q = {
        "format": "text", "COMMAND": f"'{command}'", "OBJ_DATA": "NO",
        "MAKE_EPHEM": "YES", "EPHEM_TYPE": "OBSERVER", "CENTER": "'500@399'",
        "START_TIME": f"'{start}'", "STOP_TIME": f"'{stop}'", "STEP_SIZE": f"'{step}'",
        # 1 = astrometric RA/Dec; the airless, light-time-corrected place, which is
        # what a theory computes. Apparent place would fold in refraction and the
        # observer's own motion and muddy the comparison.
        "QUANTITIES": "'1'", "ANG_FORMAT": "'DEG'", "CSV_FORMAT": "'YES'",
        "TIME_TYPE": "'TT'", "CAL_FORMAT": "'JD'", "EXTRA_PREC": "'YES'",
    }
    url = API + "?" + "&".join(f"{k}={urllib.parse.quote(v)}" for k, v in q.items())
    with urllib.request.urlopen(url, timeout=120) as r:
        text = r.read().decode()
    if "$$SOE" not in text:
        raise SystemExit(f"Horizons refused {command}:\n{text[:900]}")
    path.write_text(text)
    return text


def rows(text: str):
    """(jd_tt, ra_deg, dec_deg) from a CSV Horizons table."""
    out = []
    inside = False
    for line in text.splitlines():
        if line.startswith("$$SOE"):
            inside = True
            continue
        if line.startswith("$$EOE"):
            break
        if not inside:
            continue
        f = [c.strip() for c in line.split(",")]
        # JD, (blank flags), RA, Dec — the flag columns move about, so take the
        # last two numbers on the line rather than trusting a fixed index.
        nums = [c for c in f if c and _isnum(c)]
        out.append((float(nums[0]), float(nums[-2]), float(nums[-1])))
    return out


def _isnum(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def sky_offset(ra1, dec1, ra0, dec0):
    """Offset of (ra1,dec1) from (ra0,dec0), in arcsec, as (east, north)."""
    d0 = math.radians(dec0)
    de = (ra1 - ra0)
    de = (de + 180.0) % 360.0 - 180.0
    return de * 3600.0 * math.cos(d0), (dec1 - dec0) * 3600.0


def main():
    start, stop, step = "2026-01-01", "2029-01-01", "3 d"
    if len(sys.argv) > 3:
        start, stop, step = sys.argv[1], sys.argv[2], sys.argv[3]
    print(f"Horizons {start} .. {stop} every {step}")

    data = {}
    for name, cmd in BODIES.items():
        data[name] = rows(fetch(cmd, start, stop, step))
        print(f"  {name:9s} {len(data[name])} rows")

    n = min(len(v) for v in data.values())
    worst = {m: 0.0 for m in jove.MOONS}
    total = {m: 0.0 for m in jove.MOONS}
    worst_when = {m: 0.0 for m in jove.MOONS}
    count = 0

    for k in range(n):
        jd_tt = data["jupiter"][k][0]
        # Horizons TT and the TDB the theory wants differ by under 2 ms. Ignorable
        # here, and saying so is cheaper than pretending it was handled.
        jra, jdec = data["jupiter"][k][1], data["jupiter"][k][2]
        v = jove.observe(jd_tt, "earth")
        ang = math.degrees(jove.R_JUP_AU / v.dist) * 3600.0
        for i, moon in enumerate(jove.MOONS):
            east, north = model_offset(v, i, jd_tt)
            hra, hdec = data[moon][k][1], data[moon][k][2]
            he, hn = sky_offset(hra, hdec, jra, jdec)
            err = math.hypot(east - he, north - hn) / ang  # in Jupiter radii
            total[moon] += err
            if err > worst[moon]:
                worst[moon], worst_when[moon] = err, jd_tt
        count += 1

    print(f"\n{count} epochs compared. Error in Jupiter equatorial radii:\n")
    print(f"  {'moon':10s} {'mean':>9s} {'worst':>9s}   worst at (JD)")
    for m in jove.MOONS:
        print(f"  {m:10s} {total[m]/count:9.4f} {worst[m]:9.4f}   {worst_when[m]:.1f}")
    biggest = max(worst.values())
    print(f"\n  worst of all: {biggest:.4f} R_Jup"
          f"  ({biggest*jove.R_JUP_KM:.0f} km)")

    # Record it, so the page quotes a number that was actually measured rather
    # than one somebody remembered.
    rec = json.loads(RECORD.read_text()) if RECORD.exists() else {"windows": {}}
    rec["windows"][f"{start}..{stop}"] = {
        "start": start, "stop": stop, "step": step, "epochs": count,
        "worst_rjup": biggest, "worst_km": biggest * jove.R_JUP_KM,
        "per_moon": {m: {"mean": total[m] / count, "worst": worst[m]} for m in jove.MOONS},
    }
    rec["worst_overall_rjup"] = max(w["worst_rjup"] for w in rec["windows"].values())
    RECORD.write_text(json.dumps(rec, indent=1))
    print(f"  recorded in {RECORD.name}")


EPS0 = math.radians(23.4392911)  # obliquity of the ecliptic at J2000


def model_offset(v, i, jd):
    """The model's satellite-minus-Jupiter offset in arcsec, as (east, north).

    Built from the satellite's rectangular vector rather than from a position
    angle, so nothing has to be borrowed from Horizons but the epoch. The route is:
    undo the precession that carried the theory to the equinox of date, turn the
    ecliptic frame into the equatorial one, add the offset onto Jupiter's own
    geocentric vector, and take the difference of the two directions.
    """
    p = -math.radians(jove.precession_lon(jd))

    def deprecess(a, b, c, scale=1.0):
        return ((a * math.cos(p) - b * math.sin(p)) * scale,
                (a * math.sin(p) + b * math.cos(p)) * scale, c * scale)

    # ecliptic J2000 -> equatorial J2000
    def eq(a, b, c):
        return (a, b * math.cos(EPS0) - c * math.sin(EPS0), b * math.sin(EPS0) + c * math.cos(EPS0))

    jx, jy, jz = eq(*deprecess(*v.jup_vec))
    sx, sy, sz = eq(*deprecess(*v.vecs[i], scale=jove.R_JUP_AU))
    tx, ty, tz = jx + sx, jy + sy, jz + sz

    def radec(a, b, c):
        return math.degrees(math.atan2(b, a)) % 360.0, math.degrees(math.asin(c / math.sqrt(a * a + b * b + c * c)))

    ra1, dec1 = radec(tx, ty, tz)
    ra0, dec0 = radec(jx, jy, jz)
    return sky_offset(ra1, dec1, ra0, dec0)


if __name__ == "__main__":
    main()
