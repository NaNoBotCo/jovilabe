"""Assemble the whole instrument into one self-contained HTML file.

    python3 build.py            -> out/jovilabe.html

Nothing is fetched at build time except from files already on disk, and the page
itself fetches nothing at all. The gear search takes half a minute, so its result
is cached in data/gears.json and only recomputed when that file is missing or the
--gears flag is given.
"""

from __future__ import annotations

import html
import json
import subprocess
import sys
from pathlib import Path

import dial
import emit
import jove
import page

HERE = Path(__file__).resolve().parent
OUT = HERE / "out" / "jovilabe.html"
GEARS_CACHE = HERE / "data" / "gears.json"
VALIDATION = HERE / "data" / "validation.json"

# Where the Great Red Spot is put in System II at J2000. The spot's longitude is
# NOT predictable — it drifts by tens of degrees a year and has to be re-set from
# observation, exactly as it would on a real instrument. This is a starting mark,
# and the caption says as much.
GRS_LON_J2000 = 105.0


def gear_data(force=False):
    if GEARS_CACHE.exists() and not force:
        return json.loads(GEARS_CACHE.read_text())
    import gears
    data = gears.design()
    data.append({"name": "Ganymede", "laplace": gears.laplace_check()})
    GEARS_CACHE.write_text(json.dumps(data, indent=1))
    return data


def dial_constants() -> str:
    """Layout numbers handed to the script from the drawing, so they cannot drift."""
    return json.dumps({
        "CX": dial.CX, "CY": dial.CY, "SCALE": dial.SCALE,
        "SCOPE_CX": dial.SCOPE_CX, "SCOPE_CY": dial.SCOPE_CY, "SCOPE_R": dial.SCOPE_R,
        "DISC_R": dial.DISC_R, "MOON_INK": list(dial.MOON_INK),
        "GRS0": GRS_LON_J2000,
    }, separators=(",", ":"))


def gear_table(gd) -> str:
    rows = []
    label = {"Jupiter round the zodiac": "Jupiter&#8217;s year round the zodiac",
             "Jupiter rotation (System II)": "Jupiter&#8217;s own turn (System II)",
             "Earth-Jupiter synodic": "Earth&#8211;Jupiter synodic"}
    for g in gd:
        if "train" not in g:
            continue
        train = " ".join(f"{w}/{p}" for w, p in g["train"])
        if g.get("step_up"):
            train += " <i>(step-up)</i>"
        yrs = g["years_to_one_turn_out"]
        out = "never" if yrs > 1e7 else f"{yrs:,.0f} years"
        rows.append(
            f"<tr><td>{label.get(g['name'], g['name'])}</td>"
            f"<td class=num>{g['period_days']:.6f}</td>"
            f"<td class=mono>{train}</td>"
            f"<td class=num>{g['degrees_per_century']:.2f}&deg;</td>"
            f"<td class=num>{out}</td></tr>")
    lap = next(g["laplace"] for g in gd if "laplace" in g)
    rows.append(
        "<tr><td><b>Ganymede</b> &#8212; not geared but <b>derived</b></td>"
        f"<td class=num>{360.0/jove.MEAN_MOTION[2]:.6f}</td>"
        "<td class=mono>bevel differential</td>"
        "<td class=num>0.00&deg;</td>"
        f"<td class=num>1&deg; in {lap['years_to_one_degree']:,.0f} years</td></tr>")
    return "".join(rows)


def validation_table() -> str:
    v = json.loads(VALIDATION.read_text())
    rows = []
    for key in sorted(v["windows"]):
        w = v["windows"][key]
        rows.append(f"<tr><td>{w['start']} to {w['stop']}</td>"
                    f"<td class=num>{w['epochs']}</td>"
                    f"<td class=num>{w['worst_rjup']:.4f}</td>"
                    f"<td class=num>{w['worst_km']:,.0f} km</td></tr>")
    return "".join(rows), v


def build(force_gears=False):
    gd = gear_data(force_gears)
    vrows, vjson = validation_table()
    body = page.body(gd, gear_table(gd), vrows, vjson)
    script = (f"var THEORY={emit.theory_json()};\n"
              f"var EPHEM={emit.ephem_json()};\n"
              f"var CONST={emit.constants_json()};\n"
              f"var DIAL={dial_constants()};\n"
              + page.JS + page.JS_RENDER)
    doc = (
        "<!doctype html><html lang=en><head><meta charset=utf-8>"
        "<meta name=viewport content='width=device-width,initial-scale=1'>"
        "<title>The Jovilabe &#8212; Jupiter&#8217;s four moons, geared</title>"
        "<meta name=description content='A working antique-style jovilabe: the four "
        "Galilean moons in their orbits, their eclipses and transits, and the wheelwork "
        "that would drive them.'>"
        f"<style>{page.CSS}</style></head><body><div class=wrap>"
        + body +
        f"<script>{script}</script></div></body></html>")
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(doc, encoding="utf-8")
    print(f"wrote {OUT}  ({len(doc)/1024:.0f} KB)")
    return OUT


if __name__ == "__main__":
    build("--gears" in sys.argv)
