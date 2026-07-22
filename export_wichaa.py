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
TARGET = HERE.parent / "manuscript-wiki" / "jovilabe.py"
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


def scope_selector(sel: str) -> str:
    parts = []
    for one in sel.split(","):
        one = one.strip()
        if not one:
            continue
        if one in (":root", "body"):
            # Custom properties and the page background belong to the wrapper now.
            parts.append(SCOPE)
        elif one.startswith("@"):
            parts.append(one)
        elif one.startswith(SCOPE):
            parts.append(one)
        else:
            parts.append(f"{SCOPE} {one}")
    return ",".join(parts)


def scope_css(css: str) -> str:
    out = []
    for prelude, body in split_rules(css):
        if prelude.startswith("@media"):
            inner = "".join(f"{scope_selector(p)}{{{b}}}" for p, b in split_rules(body))
            out.append(f"{prelude}{{{inner}}}")
        elif prelude.startswith("@"):
            out.append(f"{prelude}{{{body}}}")
        else:
            out.append(f"{scope_selector(prelude)}{{{body}}}")
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


def main():
    check = "--check" in sys.argv
    src = module_source(dial.og_card_svg())
    if check:
        if not TARGET.exists() or TARGET.read_text() != src:
            print(f"{TARGET} is out of date — run: python3 export_wichaa.py")
            sys.exit(1)
        print(f"{TARGET.name} is up to date")
        return
    TARGET.write_text(src)
    print(f"wrote {TARGET}  ({len(src)/1024:.0f} KB)")


if __name__ == "__main__":
    main()
