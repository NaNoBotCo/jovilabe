"""Run the browser's arithmetic and the Python's over the same grid, and diff them.

The page carries its own copy of the theory because it has to work offline. Two
copies of anything drift, so this compares them directly rather than hoping. The
JavaScript is pulled out of the built page and run under node; if node is not
installed the check reports that and exits, rather than passing quietly.

    python3 check_port.py
"""

from __future__ import annotations

import json
import math
import shutil
import subprocess
import sys
from pathlib import Path

import build
import dial
import emit
import jove
import page

HERE = Path(__file__).resolve().parent

# The harness: the theory half of the page's script, plus a loop that prints what
# the Python will be asked for. The rendering half needs a DOM and is not included.
HARNESS = r"""
var OUT=[];
for (var k=0;k<N;k++){
  var jd = JD0 + k*STEP;
  var ph = phenomena(jd);
  var row = {jd:jd, dist:ph.dist, tilt:ph.tilt, light:ph.lightMin,
             sunAz:ph.sunAz, earthAz:ph.earthAz, ang:ph.angRadius, x:[],y:[],z:[],
             R:[], u:[], flags:[]};
  for (var i=0;i<4;i++){
    row.x.push(ph.moons[i].x); row.y.push(ph.moons[i].y); row.z.push(ph.moons[i].z);
    row.R.push(ph.R[i]); row.u.push(ph.u[i]);
    row.flags.push([ph.moons[i].transit?1:0, ph.moons[i].occulted?1:0,
                    ph.moons[i].eclipsed?1:0, ph.moons[i].shadow?1:0].join(''));
  }
  OUT.push(row);
}
console.log(JSON.stringify(OUT));
"""


def run_js(jd0: float, step: float, n: int):
    node = shutil.which("node")
    if not node:
        print("node is not installed — cannot run the port. "
              "This check did NOT pass; it did not run.")
        sys.exit(2)
    src = (f"var THEORY={emit.theory_json()};\n"
           f"var EPHEM={emit.ephem_json()};\n"
           f"var CONST={emit.constants_json()};\n"
           f"var JD0={jd0!r}, STEP={step!r}, N={n};\n"
           # The page wraps everything in an IIFE that ends in the render half;
           # here the theory half is used on its own, so close it by hand.
           + page.JS + HARNESS + "\n})();\n")
    tmp = HERE / "out" / "_port_check.js"
    tmp.parent.mkdir(exist_ok=True)
    tmp.write_text(src)
    r = subprocess.run([node, str(tmp)], capture_output=True, text=True)
    if r.returncode:
        print(r.stderr[:3000])
        sys.exit(1)
    tmp.unlink()
    return json.loads(r.stdout)


def main():
    jd0, step, n = 2461000.5, 0.37, 220   # an awkward step, to avoid landing on a pattern
    js = run_js(jd0, step, n)
    worst = {"x": 0.0, "y": 0.0, "z": 0.0, "R": 0.0, "u": 0.0,
             "dist": 0.0, "tilt": 0.0, "light": 0.0, "sunAz": 0.0, "ang": 0.0}
    flag_mismatch = 0
    for row in js:
        py = jove.phenomena(row["jd"])
        worst["dist"] = max(worst["dist"], abs(py["dist"] - row["dist"]))
        worst["tilt"] = max(worst["tilt"], abs(py["tilt"] - row["tilt"]))
        worst["light"] = max(worst["light"], abs(py["light_minutes"] - row["light"]))
        worst["ang"] = max(worst["ang"], abs(py["ang_radius_arcsec"] - row["ang"]))
        d = abs(py["sun_az"] - row["sunAz"])
        worst["sunAz"] = max(worst["sunAz"], min(d, 360.0 - d))
        for i in range(4):
            m = py["moons"][i]
            worst["x"] = max(worst["x"], abs(m["x"] - row["x"][i]))
            worst["y"] = max(worst["y"], abs(m["y"] - row["y"][i]))
            worst["z"] = max(worst["z"], abs(m["z"] - row["z"][i]))
            worst["R"] = max(worst["R"], abs(py["R"][i] - row["R"][i]))
            du = abs(py["u"][i] - row["u"][i])
            worst["u"] = max(worst["u"], min(du, 360.0 - du))
            flags = "".join("1" if m[k] else "0"
                            for k in ("transit", "occulted", "eclipsed", "shadow"))
            if flags != row["flags"][i]:
                flag_mismatch += 1
                if flag_mismatch < 6:
                    print(f"  flags differ at JD {row['jd']:.4f} {jove.MOONS[i]}: "
                          f"python {flags} vs js {row['flags'][i]}")

    print(f"JavaScript port vs Python reference, {len(js)} epochs "
          f"({jd0} + {step}d steps)\n")
    units = {"x": "R_Jup", "y": "R_Jup", "z": "R_Jup", "R": "R_Jup", "u": "deg",
             "dist": "AU", "tilt": "deg", "light": "min", "sunAz": "deg", "ang": "arcsec"}
    for k in worst:
        print(f"  {k:7s} worst difference {worst[k]:.3e} {units[k]}")
    print(f"\n  phenomenon flags: {flag_mismatch} mismatches out of {len(js)*4}")

    bad = worst["x"] > 1e-9 or worst["u"] > 1e-9 or flag_mismatch
    print("\n" + ("MISMATCH — the port has drifted from the reference."
                  if bad else
                  "The two implementations agree to floating-point noise."))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
