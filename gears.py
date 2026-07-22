"""Designing the wheelwork: what tooth counts would actually drive this thing.

A jovilabe is not a screen. If the four moons are to be carried round by gears
from a single daily arbor, somebody has to choose integers — and integers cannot
express 1.769137786 days. This module does the choosing, and prints how wrong each
choice is in a unit a clockmaker would recognise: how long the train runs before it
is a whole revolution out.

One piece of the design is not an approximation at all. The Laplace resonance

    n(Io) - 3 n(Europa) + 2 n(Ganymede) = 0

holds to a part in 10^11 in the mean motions, which means Ganymede's rate is
*determined* by the other two. A bevel differential whose carrier turns at the mean
of its two inputs will produce it exactly, from Europa geared up three times and Io
running backwards. No error term, no drift, ever. Laplace published the relation in
1805 and it is the one place in this instrument where the physics does the
engineering's work for it.
"""

from __future__ import annotations

import math
from fractions import Fraction

# Mean motions in degrees per day, straight from the E5 theory. These are the
# numbers the wheelwork has to hit.
from jove import MEAN_MOTION, MOONS

DAY = 1.0

# Periods in days: one turn of a moon's ring.
PERIODS = {m: 360.0 / n for m, n in zip(MOONS, MEAN_MOTION)}

# The other hands on the instrument.
OTHER = {
    # Jupiter's cloud tops do not turn as a body. System II is the rate of the
    # equatorial belts, and it is the one the Great Red Spot is quoted against.
    "Jupiter rotation (System II)": 9.0 / 24 + 55.0 / 1440 + 40.632 / 86400,
    "Jupiter round the zodiac": 4332.589,
    "Earth-Jupiter synodic": 398.88405,
}

PINIONS = range(6, 21)     # below six leaves a pinion runs badly
WHEELS = range(10, 181)    # above ~180 teeth the wheel is too big to cut cleanly


_PAIRS = None


def _wheel_pairs():
    """Every product of two wheels, sorted, so a third stage can be found by search.

    Looping over both wheels inside a loop over three pinions is thirty million
    combinations and takes minutes. Computing the products once and bisecting takes
    a second, and finds exactly the same best train.
    """
    global _PAIRS
    if _PAIRS is None:
        _PAIRS = sorted((a * b, a, b) for a in WHEELS for b in WHEELS)
    return _PAIRS


def best_trains(ratio: float, stages: int = 2, keep: int = 4):
    """Tooth counts whose ratio best approximates ``ratio`` (driver turns per output turn).

    ``ratio`` must be at least 1 — a train that steps *up* is the same train read
    from the other end, and ``plan`` handles the flip. Returns (relative error,
    [(wheel, pinion), ...]) sorted best first.
    """
    import bisect

    found = []
    if stages == 2:
        for p1 in PINIONS:
            for p2 in PINIONS:
                target = ratio * p1 * p2
                for w1 in WHEELS:
                    w2 = round(target / w1)
                    if w2 not in WHEELS:
                        continue
                    got = (w1 * w2) / (p1 * p2)
                    found.append((abs(got - ratio) / ratio, [(w1, p1), (w2, p2)]))
    else:
        pairs = _wheel_pairs()
        prods = [p[0] for p in pairs]
        for p1 in PINIONS:
            for p2 in PINIONS:
                for p3 in PINIONS:
                    target = ratio * p1 * p2 * p3
                    for w1 in WHEELS:
                        want = target / w1
                        if want < prods[0] or want > prods[-1]:
                            continue
                        k = bisect.bisect_left(prods, want)
                        for j in (k - 1, k, k + 1):
                            if not 0 <= j < len(pairs):
                                continue
                            _, w2, w3 = pairs[j]
                            got = (w1 * w2 * w3) / (p1 * p2 * p3)
                            found.append((abs(got - ratio) / ratio,
                                          [(w1, p1), (w2, p2), (w3, p3)]))
    found.sort(key=lambda t: t[0])
    # Strip trains that are the same set of wheels in a different order.
    seen, out = set(), []
    for err, train in found:
        key = tuple(sorted(train))
        if key in seen:
            continue
        seen.add(key)
        out.append((err, train))
        if len(out) >= keep:
            break
    return out


def plan(period: float, keep: int = 3):
    """Best train for a hand of the given period, choosing the stage count itself.

    Two stages reach a ratio of nine hundred; Jupiter's own year is four thousand
    days and needs three. A period under a day is a step-up, which is the same
    wheelwork driven from the far end.
    """
    step_up = period < 1.0
    ratio = (1.0 / period) if step_up else period
    best = None
    for stages in (2, 3):
        got = best_trains(ratio, stages, keep=keep)
        if not got:
            continue
        if best is None or got[0][0] < best[0][0][0]:
            best = (got, stages)
        # Accept as soon as a stage count holds the ratio to a part in ten million;
        # more wheels past that only add backlash and things to go wrong.
        if got[0][0] < 1e-7:
            break
    if best is None:
        return [], 0, step_up
    return best[0], best[1], step_up


def describe(name: str, period: float, err: float, train, step_up=False) -> dict:
    """Turn a relative error into the numbers a maker would want quoted."""
    got = math.prod(w for w, _ in train) / math.prod(p for _, p in train)
    return {
        "name": name,
        "period_days": period,
        "train": train,
        "step_up": step_up,
        "ratio_true": (1.0 / period) if step_up else period,
        "ratio_got": got,
        "rel_error": err,
        "seconds_per_turn": err * period * 86400.0,
        # Days until the hand is a whole revolution out, in years.
        "years_to_one_turn_out": (period / err / 365.25) if err else float("inf"),
        "degrees_per_century": 360.0 * err * 36525.0 / period,
    }


def design():
    out = []
    for name, period in (list((m, PERIODS[m]) for m in ("Io", "Europa", "Callisto"))
                         + list(OTHER.items())):
        got, stages, step_up = plan(period)
        err, train = got[0]
        d = describe(name, period, err, train, step_up)
        d["stages"] = stages
        out.append(d)
    return out


def laplace_check() -> dict:
    """How exactly the resonance holds, and therefore how good the differential is."""
    n1, n2, n3, _ = MEAN_MOTION
    resid = n1 - 3.0 * n2 + 2.0 * n3
    derived = (3.0 * n2 - n1) / 2.0
    return {
        "residual_deg_per_day": resid,
        "derived_n3": derived,
        "true_n3": n3,
        "rel_error": abs(derived - n3) / n3,
        # How long before a differential-driven Ganymede is a degree out.
        "years_to_one_degree": (1.0 / abs(derived - n3) / 365.25) if derived != n3 else float("inf"),
    }


def main():
    print("Wheelwork for a jovilabe driven from an arbor turning once per day.")
    print("A train is written wheel/pinion, in order from the day arbor outwards.\n")
    rows = design()
    print(f"  {'hand':30s} {'period (d)':>12s}  {'train':30s} {'1 turn out in':>16s} {'deg/century':>12s}")
    for r in rows:
        train = " ".join(f"{w}/{p}" for w, p in r["train"])
        if r["step_up"]:
            train += "  (step-up)"
        yrs = r["years_to_one_turn_out"]
        yr = "never" if yrs > 1e7 else f"{yrs:,.0f} yr"
        print(f"  {r['name']:30s} {r['period_days']:12.6f}  {train:30s} {yr:>16s} "
              f"{r['degrees_per_century']:12.4f}")

    lap = laplace_check()
    print("\nGanymede is not geared. It is derived, by a bevel differential whose")
    print("carrier turns at the mean of its two inputs:")
    print("    Europa geared up three times, Io reversed  ->  (3 n2 - n1) / 2")
    print(f"    Laplace residual  n1 - 3n2 + 2n3 = {lap['residual_deg_per_day']:.3e} deg/day")
    print(f"    derived rate {lap['derived_n3']:.9f} vs true {lap['true_n3']:.9f} deg/day")
    print(f"    that is one degree of error in {lap['years_to_one_degree']:,.0f} years")

    print("\nRunners-up, for the moons, in case a wheel proves awkward to cut:")
    for moon in ("Io", "Europa", "Callisto"):
        got, _stages, _up = plan(PERIODS[moon], keep=3)
        for err, train in got[1:]:
            t = " ".join(f"{w}/{p}" for w, p in train)
            r = describe(moon, PERIODS[moon], err, train)
            print(f"  {moon:10s} {t:32s} 1 turn out in {r['years_to_one_turn_out']:>12,.0f} yr")


if __name__ == "__main__":
    main()
