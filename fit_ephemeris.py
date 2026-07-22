"""Fit a compact heliocentric series for Jupiter and the Earth against JPL DE440.

Why fit rather than copy VSOP87? Because a fitted series can be *measured*. The
whole instrument stands on the claim that the dial agrees with the sky, and a
table of coefficients transcribed from a book is a claim you cannot check without
the book. Here the residual against DE440 is computed, printed, and carried onto
the page. If a coefficient is wrong the residual says so.

Run with the coucal-clock virtualenv, which already carries Skyfield + DE440:

    "$HOME/Developer/claude code projects/coucal-clock/.venv/bin/python" fit_ephemeris.py

Output: data/ephem_fit.json — mean elements plus a pruned list of periodic terms
for Jupiter's and the Earth's heliocentric ecliptic longitude, latitude and radius
vector, referred to the mean equinox and ecliptic of J2000.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from skyfield.api import load_file
from skyfield.framelib import ecliptic_frame
from skyfield.api import load

HERE = Path(__file__).resolve().parent
DE440 = Path.home() / "Developer/claude code projects/coucal-clock/data/ephemeris/de440.bsp"

# The span the instrument claims. Wide enough that the page is useful for a
# lifetime either side of now, narrow enough that a short series can hold it.
JD0, JD1 = 2457023.5, 2488070.5  # 2015-01-01 .. 2100-01-01
STEP = 2.0  # days between samples

# Mean motions in degrees per day, J2000. Only used to *name* candidate
# frequencies for the fit; the amplitudes and phases are all solved for.
N = {
    "J": 0.0830853001,   # Jupiter
    "S": 0.0334442282,   # Saturn
    "U": 0.0117257800,   # Uranus
    "N": 0.0059800000,   # Neptune
    "E": 0.9856076686,   # Earth
    "V": 1.6021302244,   # Venus
    "M": 0.5240207766,   # Mars
    "D": 12.1907491914,  # Moon's mean elongation (Earth's wobble about the EMB)
}
L0 = {  # mean longitudes at J2000, degrees
    "J": 34.351519, "S": 50.077444, "U": 314.055005, "N": 304.348665,
    "E": 100.466457, "V": 181.979801, "M": 355.433000, "D": 297.850195,
}


def sample():
    """Heliocentric ecliptic J2000 (lon, lat, r) for Jupiter and the Earth.

    Geometric, not astrometric: no light-time, no aberration. Those belong to the
    observer and the page applies them itself, so baking them in here would apply
    them twice.
    """
    eph = load_file(str(DE440))
    ts = load.timescale()
    jd = np.arange(JD0, JD1 + STEP, STEP)
    t = ts.tdb_jd(jd)
    sun = eph["sun"]
    out = {}
    for key, target in (("jupiter", eph["jupiter barycenter"]), ("earth", eph["earth"])):
        lat, lon, dist = (target - sun).at(t).frame_latlon(ecliptic_frame)
        out[key] = (lon.degrees, lat.degrees, dist.au)
    return jd, out


POLY = 4  # constant + linear + quadratic + cubic in centuries


def unwrap_linear(jd, lon_deg, n_per_day, l0):
    """Subtract the mean longitude, leaving a small bounded function to fit."""
    mean = l0 + n_per_day * (jd - 2451545.0)
    return (lon_deg - mean + 180.0) % 360.0 - 180.0


# Rayleigh resolution of the sample span: two sinusoids closer in rate than this
# are the same sinusoid as far as an 85-year fit can tell.
RAYLEIGH = 360.0 / (JD1 - JD0)


def candidates(spec):
    """Integer combinations of the named mean motions, as (rate, phase, label).

    Combinations whose rates fall within half a Rayleigh width of one another are
    indistinguishable over the span, so only the one with the smallest integers
    survives. Skipping this step was what broke the first attempt: with Uranus and
    Neptune in the basis, thousands of unresolvable near-duplicates crowded out the
    real terms and left the design matrix rank-deficient.
    """
    keys = list(spec)
    ranges = [range(-spec[k], spec[k] + 1) for k in keys]
    seen, out = set(), []

    def rec(i, combo):
        if i == len(keys):
            if not any(combo):
                return
            rate = sum(c * N[k] for c, k in zip(combo, keys))
            if abs(rate) < RAYLEIGH:  # slower than one cycle per span: a drift, not a term
                return
            if rate < 0:  # the sin/cos pair spans both signs; keep one representative
                combo = tuple(-c for c in combo)
                rate = -rate
            if combo in seen:
                return
            seen.add(combo)
            phase = sum(c * L0[k] for c, k in zip(combo, keys))
            label = " ".join(f"{c:+d}{k}" for c, k in zip(combo, keys) if c)
            out.append((rate, phase, label, sum(abs(c) for c in combo)))
            return
        for c in ranges[i]:
            rec(i + 1, combo + (c,))

    rec(0, ())
    # One representative per resolvable frequency cell, and let it be the one with
    # the smallest integers — that is the term an astronomer would actually name.
    cell = {}
    for rate, phase, label, order in out:
        k = round(rate / (RAYLEIGH / 2.0))
        if k not in cell or order < cell[k][3]:
            cell[k] = (rate, phase, label, order)
    return [(r, p, l) for r, p, l, _ in sorted(cell.values())]


def _design(d, chosen):
    """[sin(arg) ... cos(arg) ... 1, tau, tau^2, tau^3] as columns.

    The polynomial tail is not decoration. Jupiter's largest perturbation, the
    great inequality with Saturn, has a period of some 900 years; across an
    85-year window it is a slow bend, not a cycle, and no sinusoid the span can
    resolve will absorb it. The cubic does.
    """
    tau = d / 36525.0
    poly = np.stack([tau ** k for k in range(POLY)], axis=0)
    if not chosen:
        return poly.T
    th = np.radians(
        np.array([c[1] for c in chosen])[:, None] + np.array([c[0] for c in chosen])[:, None] * d
    )
    return np.concatenate([np.sin(th), np.cos(th), poly], axis=0).T


def _scores(d, resid, cands, chunk=400):
    """Periodogram power of every candidate argument against the residual.

    Sinusoids at distinct frequencies are near-orthogonal over an 85-year span, so
    one pass of this ranks the terms worth adding. Chunked because the full
    candidate matrix would be a gigabyte.
    """
    rates = np.array([c[0] for c in cands])
    phases = np.array([c[1] for c in cands])
    out = np.empty(len(cands))
    n = len(d)
    for i in range(0, len(cands), chunk):
        th = np.radians(phases[i:i + chunk, None] + rates[i:i + chunk, None] * d[None, :])
        s, c = np.sin(th), np.cos(th)
        out[i:i + chunk] = (s @ resid) ** 2 / (n / 2) + (c @ resid) ** 2 / (n / 2)
    return out


def fit_series(jd, y, cands, max_terms, tol, batch=8):
    """Pick arguments by periodogram a few at a time, solve jointly, prune, repeat.

    A single least-squares solve over every candidate would be both enormous and
    ill-conditioned. Ranking against what is *left* keeps the design matrix small
    and every surviving term physically nameable. Terms are added in small batches
    because after each solve the residual — and therefore the ranking — changes.
    """
    d = jd - 2451545.0
    chosen = []
    cols = _design(d, chosen)
    coef, *_ = np.linalg.lstsq(cols, y, rcond=None)
    resid = y - cols @ coef
    while len(chosen) < max_terms and np.abs(resid).max() > tol:
        sc = _scores(d, resid, cands)
        added = 0
        for i in np.argsort(-sc):
            if added >= batch or len(chosen) >= max_terms:
                break
            rate = cands[i][0]
            # An argument the span cannot separate from one already in hand adds
            # nothing but a near-duplicate column.
            if any(abs(rate - c[0]) < RAYLEIGH / 2.0 for c in chosen):
                continue
            chosen.append(cands[i])
            added += 1
        if not added:
            break
        cols = _design(d, chosen)
        coef, *_ = np.linalg.lstsq(cols, y, rcond=None)
        resid = y - cols @ coef
    # Drop terms carrying less than the tolerance, then re-solve so the survivors
    # absorb what the dropped ones held.
    n = len(chosen)
    if n:
        keep = np.hypot(coef[:n], coef[n:2 * n]) > tol / 10.0
        if 0 < keep.sum() < n:
            chosen = [c for c, k in zip(chosen, keep) if k]
            cols = _design(d, chosen)
            coef, *_ = np.linalg.lstsq(cols, y, rcond=None)
            resid = y - cols @ coef
    n = len(chosen)
    terms = [
        {"rate": chosen[i][0], "phase": chosen[i][1],
         "sin": float(coef[i]), "cos": float(coef[n + i]), "arg": chosen[i][2]}
        for i in range(n)
    ]
    terms.sort(key=lambda t: -math.hypot(t["sin"], t["cos"]))
    poly = [float(v) for v in coef[2 * n:]]
    return terms, poly, float(np.abs(resid).max()), float(np.sqrt((resid ** 2).mean()))


def fit_body(jd, lon, lat, r, spec, budgets, tols):
    key = spec["_n"]
    resid_lon = unwrap_linear(jd, lon, N[key], L0[key])
    basis = candidates({k: v for k, v in spec.items() if not k.startswith("_")})
    print(f"    {len(basis)} resolvable candidate arguments")
    out = {"L0": L0[key], "rate": N[key]}
    for name, y, budget, tol in (
        ("lon", resid_lon, budgets[0], tols[0]),
        ("lat", lat, budgets[1], tols[1]),
        ("r", r, budgets[2], tols[2]),
    ):
        terms, poly, worst, rms = fit_series(jd, np.asarray(y, float), basis, budget, tol)
        unit = "AU" if name == "r" else "deg"
        print(f"    {name:4s}  {len(terms):3d} terms   worst {worst:.3e} {unit}   rms {rms:.3e} {unit}")
        out[name] = {"terms": terms, "poly": poly, "worst": worst, "rms": rms}
    return out


def main():
    print("sampling DE440 ...")
    jd, s = sample()
    print(f"  {len(jd)} samples, JD {jd[0]:.1f} .. {jd[-1]:.1f}")

    print("  fitting Jupiter ...")
    jup = fit_body(
        jd, *s["jupiter"],
        # Jupiter is pushed about mainly by Saturn (the great inequality 2L_J-5L_S),
        # then Uranus and Neptune. The Earth's pull on it is far below our tolerance.
        {"_n": "J", "J": 8, "S": 6, "U": 3, "N": 2},
        budgets=(60, 30, 40),
        tols=(5e-4, 5e-4, 1e-5),
    )
    print("  fitting the Earth ...")
    ear = fit_body(
        jd, *s["earth"],
        # The Earth's own orbit, plus the monthly wobble about the Earth-Moon
        # barycentre (D) and the tugs of Venus, Mars and Jupiter.
        {"_n": "E", "E": 6, "V": 4, "M": 3, "J": 3, "D": 2, "S": 2},
        budgets=(60, 30, 40),
        tols=(5e-4, 5e-4, 1e-5),
    )

    doc = {
        "span_jd": [JD0, JD1],
        "span": ["2015-01-01", "2100-01-01"],
        "step_days": STEP,
        "source": "JPL DE440, heliocentric ecliptic and equinox of J2000",
        "jupiter": jup,
        "earth": ear,
    }
    p = HERE / "data" / "ephem_fit.json"
    p.write_text(json.dumps(doc, indent=1))
    print(f"wrote {p}  ({p.stat().st_size/1024:.1f} KB)")


if __name__ == "__main__":
    main()
