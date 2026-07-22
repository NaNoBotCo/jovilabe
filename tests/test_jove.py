"""Checks that do not need the network — physics that must hold whatever the code does.

The real accuracy checks live in validate.py and check_e5.py, which talk to JPL
Horizons. These are the ones that can run on a train: identities, symmetries, and
sanity limits that a wrong implementation would break even without a reference.

    python3 tests/test_jove.py
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import jove  # noqa: E402

FAIL = []


def check(name, cond, detail=""):
    print(f"  {'ok  ' if cond else 'FAIL'}  {name}" + (f"   {detail}" if detail else ""))
    if not cond:
        FAIL.append(name)


def main():
    print("Galilean satellite model — offline checks\n")

    # --- the resonance, which everything mechanical leans on -----------------
    n1, n2, n3, _ = jove.MEAN_MOTION
    resid = n1 - 3 * n2 + 2 * n3
    check("Laplace relation holds in the mean motions", abs(resid) < 1e-7,
          f"residual {resid:.2e} deg/day")

    jd = 2461243.0

    # --- orbital radii stay near their means --------------------------------
    st = jove.e5(jd)
    for i in range(4):
        r, mean = st["R"][i], jove.R_MEAN[i]
        check(f"{jove.MOONS[i]} radius within 2% of mean",
              abs(r - mean) / mean < 0.02, f"{r:.3f} vs {mean:.3f} R_Jup")

    # --- latitudes are small: these orbits are nearly in Jupiter's equator ---
    for i in range(4):
        check(f"{jove.MOONS[i]} latitude under 1 degree",
              abs(math.degrees(st["B"][i])) < 1.0,
              f"{math.degrees(st['B'][i]):+.3f} deg")

    # --- the rotation chain must be orthonormal ------------------------------
    b = st["basis"]
    worst = 0.0
    for i in range(3):
        for j in range(3):
            want = 1.0 if i == j else 0.0
            worst = max(worst, abs(jove._dot(b[i], b[j]) - want))
    check("frame basis is orthonormal", worst < 1e-12, f"worst {worst:.1e}")

    # --- the plan view and the 3-D vectors must be the same thing ------------
    worst = 0.0
    for i in range(4):
        px, py = st["plan"][i]
        worst = max(worst, abs(math.hypot(px, py) - st["R"][i] * math.cos(st["B"][i])))
    check("plan positions agree with the radius vectors", worst < 1e-9,
          f"worst {worst:.1e} R_Jup")

    # --- light-time is the distance over c ----------------------------------
    ph = jove.phenomena(jd)
    want = ph["dist"] / jove.C_AU_PER_DAY * 1440.0
    check("light-time matches distance over c", abs(ph["light_minutes"] - want) < 1e-6,
          f"{ph['light_minutes']:.4f} vs {want:.4f} min")

    # --- Jupiter's distance never leaves its real range ----------------------
    lo = hi = None
    for k in range(0, 4400, 7):
        d = jove.phenomena(2457023.5 + k)["dist"]
        lo = d if lo is None else min(lo, d)
        hi = d if hi is None else max(hi, d)
    check("Earth-Jupiter distance stays in 3.9-6.5 AU", 3.9 < lo and hi < 6.5,
          f"{lo:.3f} .. {hi:.3f} AU")

    # --- an eclipse must happen behind the planet, never in front -----------
    bad = 0
    for k in range(0, 600):
        p = jove.phenomena(2461243.0 + k * 0.11)
        for m in p["moons"]:
            if m["eclipsed"] and m["sz"] >= 0:
                bad += 1
            if m["shadow"] and m["sz"] <= 0:
                bad += 1
    check("eclipses fall behind Jupiter and shadows in front", bad == 0,
          f"{bad} contradictions in 600 samples")

    # --- every event found must actually be a change of state ---------------
    evs = jove.events(2461243.0, days=2.0)
    wrong = 0
    for e in evs:
        before = jove.phenomena(e["jd"] - 2e-4)["moons"][e["index"]][e["kind"]]
        after = jove.phenomena(e["jd"] + 2e-4)["moons"][e["index"]][e["kind"]]
        if before == after or after != e["begins"]:
            wrong += 1
    check("every event brackets a real state change", wrong == 0,
          f"{len(evs)} events, {wrong} wrong")

    # --- Io's transits last about as long as they really do -----------------
    starts = [e for e in evs if e["kind"] == "transit" and e["index"] == 0 and e["begins"]]
    ends = [e for e in evs if e["kind"] == "transit" and e["index"] == 0 and not e["begins"]]
    if starts and ends:
        dur = (ends[0]["jd"] - starts[0]["jd"]) * 24.0
        check("an Io transit lasts about 2 to 2.5 hours", 1.9 < dur < 2.6,
              f"{dur:.2f} hours")

    print()
    if FAIL:
        print(f"{len(FAIL)} FAILED: {', '.join(FAIL)}")
        sys.exit(1)
    print("all checks passed")


if __name__ == "__main__":
    main()
