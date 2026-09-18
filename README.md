# The Jovilabe

A working antique-style instrument for the four Galilean moons of Jupiter — where
they stand, when they are eclipsed, when they cross the disc, and what wheelwork
would be needed to carry them round. One self-contained HTML file, no network, no
fonts, no images: everything is geometry computed from the same constants the
arithmetic uses.

Built as a companion to the moon complication at
[wichaa.net/moon](https://wichaa.net/moon/) — same idea, same honesty about error,
a much larger mechanism.

    python3 build.py          # -> out/jovilabe.html
    open out/jovilabe.html

Or use the launcher on the Desktop: **`Jovilabe.command`**.

## What it shows

* **The plan dial** — the system from above Jupiter's north pole, orbits drawn to
  **true scale**, with the planet's shadow as the narrowing cone it really is. A
  moon crossing that cone is being eclipsed and you can watch it happen.
* **The telescopic strip** — the same instant through an eyepiece, also true scale,
  east to the left. The picture Galileo drew night after night in 1610.
* **The magnified disc** — transits and shadow transits, which at true scale would
  be two pixels wide.
* **The light equation** — Rømer's sub-dial: how long ago the arrangement you are
  looking at actually happened, 33 to 53 minutes.
* **The Laplace resonance** — two needles for `λ₁ − 3λ₂ + 2λ₃`. From the mean
  longitudes it never stirs; from the true ones it breathes ±4°.
* **The movement** — four geared trains and a differential, at one common module,
  turning at their true relative rates.
* **The next seven days** of every eclipse, occultation, transit and shadow transit.

## How accurate it is, and how that was established

| what | source | measured against |
|---|---|---|
| the four moons | Lieske's E5 theory (Meeus ch. 44) | JPL Horizons |
| Jupiter and the Earth | series fitted here to JPL DE440 | DE440 residual, printed by the fit |
| the browser's copy | emitted from the Python tables | the Python, epoch by epoch |

Worst error against Horizons, in Jupiter radii — the unit the dial is drawn in:

| window | worst |
|---|---|
| 2016 | 0.0275 (1,968 km) |
| 2026 | 0.0280 (2,005 km) |
| 2040 | 0.0303 (2,167 km) |
| 2070 | 0.0454 (3,249 km) |
| 2099 | 0.0556 (3,975 km) |

That is about a twentieth of the planet's width at worst — smaller than the beads
the page draws the moons with. The limit is the satellite theory itself, not
anything built around it: with the planetary series taken out of the comparison the
figure is the same.

## The files

| file | what it does |
|---|---|
| `jove.py` | the E5 theory, the geometry, the phenomena, the event finder |
| `fit_ephemeris.py` | fits Jupiter's and the Earth's places against DE440 |
| `gears.py` | searches for tooth counts, and checks the Laplace differential |
| `dial.py` | every path on the instrument |
| `page.py` | the stylesheet, the browser port of the theory, the essay |
| `emit.py` | ships the theory tables to the browser without retyping them |
| `build.py` | assembles `out/jovilabe.html` |
| `validate.py` | the model vs Horizons, in the sky |
| `check_e5.py` | the theory alone vs Horizons, in Jupiter's own frame |
| `check_port.py` | the JavaScript vs the Python, over the same grid |
| `tests/test_jove.py` | offline checks: identities, symmetries, sanity limits |

### Rebuilding

`build.py` needs only the standard library. The two things that do not are optional
and cached:

* `fit_ephemeris.py` needs numpy + Skyfield + DE440. It uses the coucal-clock
  virtualenv: `"$HOME/Developer/claude code projects/coucal-clock/.venv/bin/python"`.
  Its output, `data/ephem_fit.json`, is committed, so you only rerun it to change
  the span or the tolerances.
* `validate.py` and `check_e5.py` fetch from JPL Horizons over the network and
  cache under `data/horizons/`. Small, read-only text queries.

`gears.py` takes about thirty seconds; `build.py` caches it in `data/gears.json`
and only reruns it with `--gears`.

## Two mistakes worth not repeating

**Frames.** Skyfield's `ecliptic_frame` is the ecliptic **of date**, not J2000.
The fitted planetary series was therefore already in the frame the satellite theory
lands in, and precessing it a second time swung Jupiter's direction by a third of a
degree — invisible on the sky, a fifth of a Jupiter radius in Callisto's projected
place. It looked exactly like a plausible limitation of the theory. It was found by
measuring against Horizons and noticing the residual tracked the precession angle to
four figures.

**Resolution.** The first fit of the planetary series was garbage. An 85-year span
cannot separate two frequencies closer than about 0.012°/day, and the candidate list
was full of unresolvable near-duplicates that crowded out the real terms and left the
design matrix rank-deficient. Deduplicating candidates by resolvable frequency took
the worst residual from 0.3 AU to 2×10⁻⁶ AU.

Both were caught by measurement, not by reading the code. That is the whole argument
for `validate.py` existing.


## Licence

Records, prose and pages: CC BY-SA 4.0. Code: AGPL-3.0-or-later. Anything
carried in from elsewhere keeps its own terms — see [LICENSE](LICENSE).

**Commercial licence.** If share-alike doesn't fit your use — a corpus, a
product, a model — a commercial licence is available.
[Open an issue](https://github.com/NaNoBotCo/jovilabe/issues) and say what you need.

---

Contact: Nan · nan@motdang.net · Sponsor: [Ko-fi](https://ko-fi.com/defiantchiangmai) · [Patreon](https://www.patreon.com/nanobotco)
