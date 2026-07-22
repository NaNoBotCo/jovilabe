"""Hold the page's arithmetic against redspot.py, and say where they differ.

The dial ships Lieske's tables as data rather than as retyped JavaScript, so the
two implementations cannot disagree about a *number*. They can still disagree about
an *operation* — a sign, an order of rotations, a degrees-for-radians. This runs
the page's own script under node and compares, body by body, against the Python it
was ported from.

Nothing here touches the network. It needs node on the path; without it, it says so
and stops rather than pretending to have checked.
"""

from __future__ import annotations

import json
import math
import re
import shutil
import subprocess
import sys
from pathlib import Path

import redspot as rs

HERE = Path(__file__).resolve().parent
PAGE = HERE / "out" / "redspot.html"
SAMPLES = [2461243.5 + k * 0.137 for k in range(24)]


def run_node(jds: list[float]) -> list[dict]:
    html = PAGE.read_text()
    blocks = re.findall(r"<script>(.*?)</script>", html, re.S)
    if len(blocks) < 2:
        raise SystemExit("no scripts in the page — build it with redspot_dial.py first")
    # Drop only the trailing first-paint call, not the one inside the ticker.
    data, code = blocks[-2], re.sub(r"draw\(\);\s*$", "", blocks[-1])
    harness = f"""
{data}
const document={{getElementById:()=>({{innerHTML:"",textContent:""}})}};
const setInterval=()=>0;
{code}
const out=[];
for(const jd of {json.dumps(jds)}){{
  const s=sky(jd);
  out.push({{lon:s.lonII,sun:[s.sun.alt,s.sun.az],
    moons:s.moons.map(m=>[m.alt,m.az,m.dist,m.ang,m.illum,m.limb,m.eclipsed?1:0])}});
}}
console.log(JSON.stringify(out));
"""
    p = subprocess.run(["node", "--input-type=module", "-e", harness],
                       capture_output=True, text=True)
    if p.returncode:
        raise SystemExit("node refused the page's script:\n" + p.stderr[:2000])
    return json.loads(p.stdout)


def main() -> None:
    if not shutil.which("node"):
        print("node not on the path — the browser port was NOT checked.")
        sys.exit(1)
    got = run_node(SAMPLES)
    worst = {"sky": 0.0, "size": 0.0, "illum": 0.0, "limb": 0.0, "lon": 0.0}
    flags = 0
    for jd, g in zip(SAMPLES, got):
        s = rs.sky(jd)
        worst["lon"] = max(worst["lon"], abs(g["lon"] - s["lon_II"]))
        for i, m in enumerate(s["moons"]):
            a1, a2 = math.radians(m.alt), math.radians(g["moons"][i][0])
            sep = math.degrees(math.acos(max(-1.0, min(1.0,
                math.sin(a1) * math.sin(a2) + math.cos(a1) * math.cos(a2)
                * math.cos(math.radians(m.az - g["moons"][i][1]))))))
            worst["sky"] = max(worst["sky"], sep)
            worst["size"] = max(worst["size"], abs(g["moons"][i][3] - m.ang_radius))
            worst["illum"] = max(worst["illum"], abs(g["moons"][i][4] - m.illum))
            d = abs(g["moons"][i][5] - m.limb_pa) % 360.0
            worst["limb"] = max(worst["limb"], min(d, 360.0 - d))
            flags += int(bool(g["moons"][i][6]) != bool(m.eclipsed))
    print(f"the page against redspot.py, {len(SAMPLES)} instants x 4 moons:")
    print(f"  place in the sky   {worst['sky'] * 3600:8.4f} arcsec")
    print(f"  angular radius     {worst['size'] * 3600:8.4f} arcsec")
    print(f"  lit fraction       {worst['illum']:8.2e}")
    print(f"  bright limb angle  {worst['limb']:8.2e} deg")
    print(f"  spot longitude     {worst['lon']:8.2e} deg")
    print(f"  eclipse flags disagreeing: {flags}")
    if worst["sky"] > 1e-6 or flags:
        raise SystemExit("the page and the reference have drifted apart.")
    print("  the page and the reference agree.")


if __name__ == "__main__":
    main()
