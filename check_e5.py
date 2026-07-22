"""Compare the E5 satellite theory against Horizons in Jupiter's own frame.

This is the sharpest test available. Asking Horizons for Jupiter-centred vectors
takes the observer, the light-time, and the sky projection out of the comparison
altogether, so whatever is left is the theory. The residual is split three ways —
along the orbit, radially, and out of the orbital plane — because those three fail
for different reasons and the shape of the error says which.
"""

from __future__ import annotations

import math
import sys
import urllib.parse
import urllib.request
from pathlib import Path

import jove
from validate import CACHE, API, _isnum

HERE = Path(__file__).resolve().parent
SATS = {"Io": "501", "Europa": "502", "Ganymede": "503", "Callisto": "504"}


def fetch_vec(command: str, start: str, stop: str, step: str) -> str:
    CACHE.mkdir(parents=True, exist_ok=True)
    tag = f"vec{command}_{start}_{stop}_{step}".replace(" ", "").replace(":", "")
    path = CACHE / f"{tag}.txt"
    if path.exists():
        return path.read_text()
    q = {
        "format": "text", "COMMAND": f"'{command}'", "OBJ_DATA": "NO",
        "MAKE_EPHEM": "YES", "EPHEM_TYPE": "VECTORS",
        "CENTER": "'500@599'",           # Jupiter's centre, not the system barycentre
        "REF_PLANE": "'ECLIPTIC'", "REF_SYSTEM": "'ICRF'",
        "VEC_TABLE": "'1'", "OUT_UNITS": "'KM-S'", "VEC_CORR": "'NONE'",
        "START_TIME": f"'{start}'", "STOP_TIME": f"'{stop}'", "STEP_SIZE": f"'{step}'",
        "CSV_FORMAT": "'YES'", "CAL_FORMAT": "'JD'", "TIME_TYPE": "'TT'",
    }
    url = API + "?" + "&".join(f"{k}={urllib.parse.quote(v)}" for k, v in q.items())
    with urllib.request.urlopen(url, timeout=120) as r:
        text = r.read().decode()
    if "$$SOE" not in text:
        raise SystemExit(f"Horizons refused {command}:\n{text[:900]}")
    path.write_text(text)
    return text


def vec_rows(text: str):
    out, inside = [], False
    for line in text.splitlines():
        if line.startswith("$$SOE"):
            inside = True
            continue
        if line.startswith("$$EOE"):
            break
        if not inside:
            continue
        f = [c.strip() for c in line.split(",")]
        nums = [float(c) for c in f if c and _isnum(c)]
        if len(nums) >= 4:
            out.append((nums[0], nums[1], nums[2], nums[3]))  # jd, x, y, z (km)
    return out


def model_vec(jd, i):
    """Satellite vector relative to Jupiter, ecliptic J2000, in km."""
    x, y, z = jove.e5(jd)["sats"][i]
    p = -math.radians(jove.precession_lon(jd))
    return ((x * math.cos(p) - y * math.sin(p)) * jove.R_JUP_KM,
            (x * math.sin(p) + y * math.cos(p)) * jove.R_JUP_KM,
            z * jove.R_JUP_KM)


def main():
    start, stop, step = "2026-01-01", "2027-01-01", "1 d"
    if len(sys.argv) > 3:
        start, stop, step = sys.argv[1], sys.argv[2], sys.argv[3]
    print(f"E5 vs Horizons, Jupiter-centred, {start} .. {stop} every {step}\n")
    print(f"  {'moon':10s} {'along':>9s} {'radial':>9s} {'normal':>9s} {'total':>9s}"
          f" {'total':>9s}   (worst, R_Jup unless marked)")
    worst_all = 0.0
    for i, (name, cmd) in enumerate(SATS.items()):
        rows = vec_rows(fetch_vec(cmd, start, stop, step))
        wa = wr = wn = wt = 0.0
        for jd, hx, hy, hz in rows:
            mx, my, mz = model_vec(jd, i)
            dx, dy, dz = mx - hx, my - hy, mz - hz
            r = math.sqrt(hx * hx + hy * hy + hz * hz)
            # Along-track and radial in the orbit plane; normal is out of it.
            rad = (dx * hx + dy * hy + dz * hz) / r
            nx, ny, nz = -hy, hx, 0.0          # in-plane, perpendicular to radius
            nm = math.hypot(nx, ny)
            along = (dx * nx + dy * ny) / nm
            normal = dz - (rad * hz / r)
            wa = max(wa, abs(along)); wr = max(wr, abs(rad))
            wn = max(wn, abs(normal)); wt = max(wt, math.sqrt(dx * dx + dy * dy + dz * dz))
        rj = jove.R_JUP_KM
        print(f"  {name:10s} {wa/rj:9.4f} {wr/rj:9.4f} {wn/rj:9.4f} {wt/rj:9.4f} {wt:8.0f}km")
        worst_all = max(worst_all, wt / rj)
    print(f"\n  worst of all: {worst_all:.4f} R_Jup ({worst_all*jove.R_JUP_KM:.0f} km)")


if __name__ == "__main__":
    main()
