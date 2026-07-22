"""Generate the wichaa.net page module from this project.

    python3 export_wichaa.py            # writes ../manuscript-wiki/jovilabe.py
    python3 export_wichaa.py --check    # non-zero if that file is out of date

The site is a separate repository and must build without reaching into this one,
so the instrument is *generated* into it rather than imported from it. Generated,
not copied: there is one source, and `--check` fails the build if the copy has
gone stale. That is the same guarantee the E5 tables get by being emitted to
JavaScript instead of retyped.

The one real adaptation is the stylesheet. Standing alone, this page owns `body`,
`h1`, `table` and so on; inside wichaa it owns none of them. Every rule is
therefore rewritten under a single `.jov` scope, so the instrument cannot fight
the site's own styles and the site cannot leak into the instrument.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import build
import dial
import emit
import page

HERE = Path(__file__).resolve().parent
WIKI = HERE.parent / "manuscript-wiki"
TARGET = WIKI / "jovilabe.py"
RS_TARGET = WIKI / "redspot.py"
SCOPE = ".jov"


def split_rules(css: str):
    """Top-level (prelude, body) pairs. The CSS here has no nesting beyond @media."""
    out, i, n = [], 0, len(css)
    while i < n:
        j = css.find("{", i)
        if j < 0:
            break
        prelude = css[i:j].strip()
        depth, k = 1, j + 1
        while k < n and depth:
            if css[k] == "{":
                depth += 1
            elif css[k] == "}":
                depth -= 1
            k += 1
        out.append((prelude, css[j + 1:k - 1]))
        i = k
    return out


def scope_selector(sel: str, scope: str = SCOPE) -> str:
    parts = []
    for one in sel.split(","):
        one = one.strip()
        if not one:
            continue
        if one in (":root", "body"):
            # Custom properties and the page background belong to the wrapper now.
            parts.append(scope)
        elif one.startswith("@"):
            parts.append(one)
        elif one.startswith(scope):
            parts.append(one)
        else:
            parts.append(f"{scope} {one}")
    return ",".join(parts)


def scope_css(css: str, scope: str = SCOPE) -> str:
    out = []
    for prelude, body in split_rules(css):
        if prelude.startswith("@media"):
            inner = "".join(f"{scope_selector(p, scope)}{{{b}}}" for p, b in split_rules(body))
            out.append(f"{prelude}{{{inner}}}")
        elif prelude.startswith("@"):
            out.append(f"{prelude}{{{body}}}")
        else:
            out.append(f"{scope_selector(prelude, scope)}{{{body}}}")
    return "".join(out)


EXTRA = """
/* The instrument brings its own card; the site brings the page. This wrapper is
   only here to carry the custom properties down and to set the serif the essay is
   written in — giving it a background and a border too would put a box inside a
   box. The site's --ink and the instrument's stay separate because they are
   declared at different levels, which is the whole point of the scope. */
.jov{display:block;color:var(--ink);margin:0 0 8px;
  font:17px/1.62 Georgia,'Iowan Old Style','Times New Roman',serif}
.jov .wrap{max-width:none;padding:0}
.jov p{max-width:70ch}
.jov h2{margin-top:1.7em}
"""


def module_source(card: str) -> str:
    gd = build.gear_data()
    vrows, vjson = build.validation_table()
    body = page.body(gd, build.gear_table(gd), vrows, vjson)
    # The standalone page's <header> is the document's; here the site supplies one,
    # so the instrument's own title block is dropped and NAV is spliced in instead.
    body = re.sub(r"^\s*<header class=top>.*?</header>", "", body, flags=re.S)

    css = scope_css(page.CSS) + EXTRA
    script = (f"var THEORY={emit.theory_json()};\n"
              f"var EPHEM={emit.ephem_json()};\n"
              f"var CONST={emit.constants_json()};\n"
              f"var DIAL={build.dial_constants()};\n"
              + page.JS + page.JS_RENDER)

    return f'''"""The jovilabe — GENERATED. Do not edit; edit the jovilabe project instead.

Written by ``jovilabe/export_wichaa.py`` from that project's own source, so the
instrument on this site and the one in that repository cannot disagree. To change
anything here, change it there and re-run the exporter; ``--check`` will tell you
if this file has gone stale.

What it is: a working antique-style jovilabe for the four Galilean moons —
their orbits to true scale, their eclipses and transits, Romer's light equation,
the Laplace resonance, and the wheelwork that would drive the whole thing.
Checked against JPL Horizons to {vjson["worst_overall_rjup"]:.4f} Jupiter radii
across 2015-2100.

Everything is geometry and arithmetic computed in the page: no images, no fonts,
no network. It works from a file:// URL with the wifi off.
"""

DIAL_CSS = {css!r}

_BODY = {body!r}

_SCRIPT = {script!r}


def jovilabe_body(nav: str) -> str:
    """The page: the site's header, then the instrument and its essay."""
    return (
        "<header><div><h1>The Jovilabe</h1>"
        "<p class=sub>Iovilabium &#183; Mediceorum Siderum &#8212; Jupiter&#8217;s four "
        "great moons, where they stand tonight and where their shadows fall</p></div>"
        + nav + "</header>"
        "<main id=main><div class=jov><div class=wrap>" + _BODY + "</div></div>"
        "<script>" + _SCRIPT + "</script></main>"
    )


def card_svg() -> str:
    """The 1200x630 share card: the dial itself, not a second drawing of it."""
    return _CARD


_CARD = {card!r}
'''




# ---------------------------------------------------------------------------
# The Red Spot dial — the same treatment, a different page.
# ---------------------------------------------------------------------------
RS_SCOPE = ".rsp"

RS_EXTRA = """
/* Same bargain as the jovilabe's wrapper: carry the custom properties down, set
   the serif, and otherwise let the site own the page. */
.rsp{display:block;color:var(--ink);margin:0 0 8px;
  font:16.5px/1.62 Georgia,'Iowan Old Style',serif}
/* A full-width column reads badly. Give the dial room and the prose a measure. */
.rsp .rspmain{max-width:980px;margin:0 auto;padding:0}
.rsp p,.rsp h2,.rsp .note,.rsp table.spec,.rsp footer{max-width:72ch}
.rsp p{max-width:70ch}
"""


def redspot_source(card: str) -> str:
    """Split the standalone Red Spot document into a stylesheet and a body.

    Its `page()` builds a whole HTML file, which is the right shape standing alone
    and the wrong one inside a site. The <main> is renamed on the way through
    because wichaa already has one and a page may only have a single main element.
    """
    import redspot_dial

    doc = redspot_dial.page()
    css = doc[doc.index("<style>") + 7:doc.index("</style>")]
    body = doc[doc.index("<body>") + 6:doc.rindex("</body>")]

    css = css.replace("main{", ".rspmain{", 1)
    body = body.replace("<main>", "<div class='rspmain'>").replace("</main>", "</div>")

    # The page's own title block is the document's when it stands alone; here the
    # site header carries it, so strip it rather than hiding it — a second <h1>
    # left in the DOM is still a second <h1> to anything reading the page aloud.
    body = re.sub(r"<h1>.*?</h1>\s*", "", body, count=1, flags=re.S)
    body = re.sub(r"<p class='sub'>.*?</p>\s*", "", body, count=1, flags=re.S)

    # And scope it, or its body{} rule repaints the whole site.
    css = scope_css(css, RS_SCOPE) + RS_EXTRA

    return f'''"""The Red Spot dial — GENERATED. Do not edit; edit the jovilabe project instead.

Written by ``jovilabe/export_wichaa.py`` from ``redspot_dial.py``. The sky over
Jupiter's Great Red Spot: where the four Galilean moons are from *there*, whether
they are up, and how long the wait is between one rising and the next.

The companion piece to ``jovilabe.py`` — the same E5 tables, pointed the other way.
"""

DIAL_CSS = {css!r}

_BODY = {body!r}


def redspot_body(nav: str) -> str:
    """The page: the site's header, then the dial and its essay."""
    return (
        "<header><div><h1>The Red Spot dial</h1>"
        "<p class=sub>A moonphase complication rebuilt for somebody standing in the "
        "storm &#8212; Jupiter&#8217;s four moons, from a Jovian horizon</p></div>"
        + nav + "</header>"
        "<main id=main><div class=rsp>" + _BODY + "</div></main>"
    )


def card_svg() -> str:
    return _CARD


_CARD = {card!r}
'''


def redspot_card_svg() -> str:
    """The 1200x630 card, built from the still the page's own script drew.

    ``redspot_still.py`` runs the page in headless Chrome and keeps the drawing, so
    the card shows the instrument as the instrument actually renders it. If the
    still is missing the export says so rather than inventing a picture.
    """
    still = HERE / "out" / "redspot_still.svg"
    if not still.exists():
        raise SystemExit("out/redspot_still.svg is missing — run: python3 redspot_still.py")
    inner = still.read_text()
    inner = inner[inner.index(">") + 1:inner.rindex("</svg>")]
    return f"""<svg xmlns='http://www.w3.org/2000/svg' width='1200' height='630'
     viewBox='0 0 1200 630'>
  <rect width='1200' height='630' fill='#eee8db'/>
  <rect x='0' y='0' width='1200' height='14' fill='#8d6f28'/>
  <g transform='translate(18 -18) scale(0.74)'>{inner}</g>
  <g transform='translate(700 0)'>
    <text x='0' y='176' style='font:700 64px Georgia,serif' fill='#1a2431'>The Red Spot</text>
    <text x='0' y='240' style='font:700 64px Georgia,serif' fill='#1a2431'>dial</text>
    <text x='0' y='300' style='font:italic 26px Georgia,serif' fill='#5d6470'>
      a moonphase complication for</text>
    <text x='0' y='336' style='font:italic 26px Georgia,serif' fill='#5d6470'>
      somebody standing in the storm</text>
    <text x='0' y='406' style='font:23px Georgia,serif' fill='#1a2431'>
      Jupiter&#8217;s four moons, from a Jovian</text>
    <text x='0' y='440' style='font:23px Georgia,serif' fill='#1a2431'>
      horizon &#8212; risings, settings, eclipses.</text>
    <text x='0' y='500' style='font:22px Georgia,serif' fill='#5d6470'>
      A whole lunation every thirteen hours.</text>
    <text x='0' y='578' style='font:21px Georgia,serif;letter-spacing:.09em'
       fill='#8d6f28'>wichaa.net/redspot</text>
  </g>
</svg>"""


def main():
    check = "--check" in sys.argv
    rs = redspot_source(redspot_card_svg())
    pieces = ((TARGET, module_source(dial.og_card_svg())), (RS_TARGET, rs))

    stale = []
    for target, src in pieces:
        if check:
            if not target.exists() or target.read_text() != src:
                stale.append(target.name)
            continue
        target.write_text(src)
        print(f"wrote {target}  ({len(src)/1024:.0f} KB)")
    if check:
        if stale:
            print("out of date: " + ", ".join(stale) + " — run: python3 export_wichaa.py")
            sys.exit(1)
        print("both generated modules are up to date")


if __name__ == "__main__":
    main()
