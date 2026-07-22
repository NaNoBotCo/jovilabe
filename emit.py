"""Ship the theory to the browser without letting it drift from the Python.

The E5 tables are written once, in ``jove.py``, as formulae like ``l2-2l3+p3``.
This module turns those same parsed structures into compact JSON. Nothing is
retyped, so there is no second copy to fall out of step — and ``check_port.py``
then runs both implementations over the same grid and insists they agree.
"""

from __future__ import annotations

import json
from pathlib import Path

import jove

HERE = Path(__file__).resolve().parent


def _sparse(vec):
    """Keep only the non-zero coefficients: [[index, coefficient], ...]."""
    return [[i, c] for i, c in enumerate(vec) if c]


def _table(tbl):
    return [[amp, _sparse(vec), const] for amp, vec, const in tbl]


def theory_json() -> str:
    doc = {
        "sigma": [_table(t) for t in jove.SIGMAS],
        "tanb": [_table(t) for t in jove.TANB],
        "radius": [_table(t) for t in jove.RADIUS],
        "rmean": list(jove.R_MEAN),
        "n": list(jove.MEAN_MOTION),
    }
    return json.dumps(doc, separators=(",", ":"))


def ephem_json() -> str:
    """The fitted planetary series, re-encoded as arrays rather than objects.

    Same numbers, a third of the bytes: [rate, phase, sin, cos] beats four keys
    repeated two hundred times.
    """
    fit = jove.fit()
    out = {"span": fit["span"]}
    for body in ("jupiter", "earth"):
        b = fit[body]
        out[body] = {
            "L0": b["L0"], "rate": b["rate"],
            "lon": {"poly": b["lon"]["poly"],
                    "t": [[t["rate"], t["phase"], t["sin"], t["cos"]] for t in b["lon"]["terms"]]},
            "lat": {"poly": b["lat"]["poly"],
                    "t": [[t["rate"], t["phase"], t["sin"], t["cos"]] for t in b["lat"]["terms"]]},
            "r": {"poly": b["r"]["poly"],
                  "t": [[t["rate"], t["phase"], t["sin"], t["cos"]] for t in b["r"]["terms"]]},
        }
    return json.dumps(out, separators=(",", ":"))


def constants_json() -> str:
    return json.dumps({
        "RJUP_KM": jove.R_JUP_KM, "RJUP_AU": jove.R_JUP_AU, "AU_KM": jove.AU_KM,
        "FLATTEN": jove.FLATTEN, "RSUN_KM": jove.R_SUN_KM,
        "C": jove.C_AU_PER_DAY, "LT_PER_RJUP": jove.LT_PER_RJUP,
        "MOONS": list(jove.MOONS), "ROMAN": list(jove.ROMAN),
    }, separators=(",", ":"))


if __name__ == "__main__":
    for name, fn in (("theory", theory_json), ("ephem", ephem_json), ("constants", constants_json)):
        print(f"{name:10s} {len(fn()):8,d} bytes")
