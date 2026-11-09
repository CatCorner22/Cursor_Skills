#!/usr/bin/env python3
"""risk_calc.py - exact, reproducible effect-measure arithmetic for appraising medical studies.

Why this script exists
----------------------
Claude must never compute ARR, NNT, odds ratios, confidence intervals, or a
fragility index in its head. Mental arithmetic on rounded percentages is the
most common way a critical appraisal goes wrong. This script does the
arithmetic, shows every intermediate value, and states its assumptions.

Standard library only (math, argparse, json), so it runs in any session.

Numeric note: statistics need logarithms and square roots, so this script uses
IEEE-754 floats (about 15-16 significant digits). It rounds only for display.
That differs from the integer-cent / Decimal rule used for money work; money
rules do not apply to probabilities.

Sign convention (used everywhere in the skill)
----------------------------------------------
- "Group 1" = intervention/exposed arm. "Group 0" = control/comparator arm.
- risk1 = events1 / n1 ; risk0 = events0 / n0.
- Risk difference RD = risk1 - risk0.
- If the event is BAD (death, relapse, adverse event) and RD < 0, the
  intervention reduces risk: ARR = -RD and NNT (benefit) = 1 / ARR.
- If the event is GOOD (response, remission) and RD > 0, the intervention
  increases the good outcome: absolute benefit increase ABI = RD and
  NNT (benefit) = 1 / ABI.
- When the RD favours control instead, the script reports NNH (number needed
  to harm).
- The script asks which kind of event it is (--event good|bad) so that it can
  label benefit vs harm correctly. It never guesses.

Subcommands
-----------
  binary      2x2 table -> risks, RD/ARR, RR/RRR, OR, NNT/NNH, CIs, Fisher p,
              fragility index
  orrr        convert an odds ratio to a risk ratio at a stated baseline risk
  diagnostic  sensitivity, specificity, prevalence -> PPV, NPV, LRs, and
              natural frequencies per 1,000
  smd         standardised mean difference (Cohen's d, Hedges' g) with CI
  frequencies restate a relative effect as natural frequencies per N people
  pctcheck    test whether a reported percentage is possible with the stated n
  ci2smd      derive SD and an approximate SMD from a mean difference and its CI
  blinding    Bang (per arm) and James (overall) blinding indexes from guess data
  bayes       Bayesian reanalysis of an estimate + CI under skeptical, flat,
              enthusiastic, and custom priors; Analysis of Credibility limits
  evalue      E-value for unmeasured confounding (observational comparisons)
  retrodesign power, Type S and Type M (exaggeration) error for a plausible effect
  meta        fixed/random-effects meta-analysis (DL, PM, REML), HKSJ CI,
              I-squared, Q, prediction interval
  smd2nnt     standardized mean difference -> NNT (Kraemer; Furukawa)

Advanced methods live in appraisal_advanced.py (same folder).

Every subcommand accepts --json for machine-readable output.

Run `python3 risk_calc.py <subcommand> -h` for the arguments.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
import appraisal_advanced as adv  # noqa: E402

Z_95 = 1.959963984540054  # two-sided 95% normal quantile


# --------------------------------------------------------------------------
# Small helpers
# --------------------------------------------------------------------------

def _z_for(level: float) -> float:
    """Normal quantile for a two-sided confidence level, via inverse error function."""
    if abs(level - 0.95) < 1e-12:
        return Z_95
    # Acklam-free approach: bisection on the normal CDF (adequate and dependency-free).
    target = 1 - (1 - level) / 2
    lo, hi = 0.0, 10.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if 0.5 * (1 + math.erf(mid / math.sqrt(2))) < target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def wilson(x: int, n: int, z: float) -> Tuple[float, float]:
    """Wilson score interval for a single proportion."""
    if n == 0:
        return (float("nan"), float("nan"))
    p = x / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = (z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def newcombe_rd_ci(x1: int, n1: int, x0: int, n0: int, z: float) -> Tuple[float, float]:
    """Newcombe (1998) method 10 hybrid score CI for p1 - p0.

    Chosen over the simple Wald interval because Wald misbehaves with small
    samples and proportions near 0 or 1 - exactly the situation in many
    psychedelic trials (n < 100 per arm, low remission rates in placebo arms).
    """
    p1, p0 = x1 / n1, x0 / n0
    l1, u1 = wilson(x1, n1, z)
    l0, u0 = wilson(x0, n0, z)
    d = p1 - p0
    lower = d - math.sqrt((p1 - l1) ** 2 + (u0 - p0) ** 2)
    upper = d + math.sqrt((u1 - p1) ** 2 + (p0 - l0) ** 2)
    return (lower, upper)


def _log_choose(n: int, k: int) -> float:
    return math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)


def fisher_exact_two_sided(a: int, b: int, c: int, d: int) -> float:
    """Two-sided Fisher exact p-value for the 2x2 table [[a, b], [c, d]].

    Uses the standard 'sum of probabilities <= observed probability' rule
    (the same rule as R's fisher.test and scipy.stats.fisher_exact).
    """
    row1 = a + b
    col1 = a + c
    n = a + b + c + d
    kmin = max(0, row1 + col1 - n)
    kmax = min(row1, col1)

    def logp(k: int) -> float:
        return _log_choose(col1, k) + _log_choose(n - col1, row1 - k) - _log_choose(n, row1)

    lp_obs = logp(a)
    total = 0.0
    eps = 1e-7  # relative tolerance, matches common implementations
    for k in range(kmin, kmax + 1):
        lp = logp(k)
        if lp <= lp_obs + math.log1p(eps):
            total += math.exp(lp)
    return min(1.0, total)


def fragility_index(x1: int, n1: int, x0: int, n0: int, alpha: float = 0.05) -> Dict[str, object]:
    """Fragility index (Walsh et al., J Clin Epidemiol 2014).

    Definition: the minimum number of patients in the arm with FEWER events
    whose status would have to change from non-event to event for the
    two-sided Fisher exact p-value to reach or exceed alpha.

    Only defined when the original result is statistically significant
    (Fisher p < alpha). For a non-significant result the script reports the
    "reverse fragility index" (number of changes needed to MAKE it
    significant), labelled as such, because users often ask for it.
    """
    p0 = fisher_exact_two_sided(x1, n1 - x1, x0, n0 - x0)
    result: Dict[str, object] = {"fisher_p_original": p0, "alpha": alpha}
    if p0 < alpha:
        # change non-events to events in the arm with fewer events
        if x1 <= x0:
            arm = "group1"
            ex, nx, ey, ny = x1, n1, x0, n0
        else:
            arm = "group0"
            ex, nx, ey, ny = x0, n0, x1, n1
        steps = 0
        p = p0
        while p < alpha and ex < nx:
            ex += 1
            steps += 1
            if arm == "group1":
                p = fisher_exact_two_sided(ex, nx - ex, ey, ny - ey)
            else:
                p = fisher_exact_two_sided(ey, ny - ey, ex, nx - ex)
        result.update({
            "kind": "fragility_index",
            "value": steps,
            "arm_modified": arm,
            "fisher_p_after": p,
            "interpretation": (
                f"Changing {steps} patient(s) in {arm} from non-event to event "
                f"moves Fisher p from {p0:.4g} to {p:.4g} (>= {alpha})."
            ),
        })
    else:
        # reverse fragility: move events toward significance in the arm with fewer events
        if x1 <= x0:
            arm = "group1"
            ex, nx, ey, ny = x1, n1, x0, n0
            direction = -1  # fewer events in group1 -> decrease further to widen the gap
        else:
            arm = "group0"
            ex, nx, ey, ny = x0, n0, x1, n1
            direction = -1
        steps = 0
        p = p0
        while p >= alpha and 0 < ex:
            ex += direction
            steps += 1
            if arm == "group1":
                p = fisher_exact_two_sided(ex, nx - ex, ey, ny - ey)
            else:
                p = fisher_exact_two_sided(ey, ny - ey, ex, nx - ex)
        result.update({
            "kind": "reverse_fragility_index",
            "value": steps if p < alpha else None,
            "arm_modified": arm,
            "fisher_p_after": p,
            "interpretation": (
                "Original result is not significant by Fisher exact test; "
                f"{steps} event-to-non-event change(s) in {arm} would make p = {p:.4g}."
                if p < alpha else
                "Original result is not significant and cannot be made significant "
                "by changing events in the arm with fewer events."
            ),
        })
    return result


# --------------------------------------------------------------------------
# Binary outcomes
# --------------------------------------------------------------------------

def binary(x1: int, n1: int, x0: int, n0: int, event: str, level: float = 0.95,
           alpha: float = 0.05) -> Dict[str, object]:
    if event not in ("good", "bad"):
        raise ValueError("--event must be 'good' or 'bad'")
    for name, x, n in (("group1", x1, n1), ("group0", x0, n0)):
        if n <= 0 or x < 0 or x > n:
            raise ValueError(f"{name}: need 0 <= events <= n and n > 0 (got {x}/{n})")
    z = _z_for(level)
    r1, r0 = x1 / n1, x0 / n0
    rd = r1 - r0
    rd_lo, rd_hi = newcombe_rd_ci(x1, n1, x0, n0, z)

    out: Dict[str, object] = {
        "inputs": {"events1": x1, "n1": n1, "events0": x0, "n0": n0,
                   "event_type": event, "confidence_level": level},
        "risk1": r1, "risk1_ci_wilson": wilson(x1, n1, z),
        "risk0": r0, "risk0_ci_wilson": wilson(x0, n0, z),
        "risk_difference_RD": rd, "RD_ci_newcombe": (rd_lo, rd_hi),
        "notes": [],
    }

    # Relative risk with Katz log CI; Haldane 0.5 correction only if a zero cell
    a, b, c, d = x1, n1 - x1, x0, n0 - x0
    corrected = any(v == 0 for v in (a, b, c, d))
    if corrected:
        a_, b_, c_, d_ = a + 0.5, b + 0.5, c + 0.5, d + 0.5
        out["notes"].append("Zero cell present: 0.5 added to every cell for RR/OR and their CIs "
                            "(Haldane-Anscombe). Point RD and risks use raw counts.")
    else:
        a_, b_, c_, d_ = float(a), float(b), float(c), float(d)
    n1_, n0_ = a_ + b_, c_ + d_
    rr = (a_ / n1_) / (c_ / n0_)
    se_log_rr = math.sqrt(1 / a_ - 1 / n1_ + 1 / c_ - 1 / n0_)
    rr_ci = (math.exp(math.log(rr) - z * se_log_rr), math.exp(math.log(rr) + z * se_log_rr))
    orr = (a_ * d_) / (b_ * c_)
    se_log_or = math.sqrt(1 / a_ + 1 / b_ + 1 / c_ + 1 / d_)
    or_ci = (math.exp(math.log(orr) - z * se_log_or), math.exp(math.log(orr) + z * se_log_or))
    out.update({
        "risk_ratio_RR": rr, "RR_ci_katz_log": rr_ci,
        "relative_risk_change_RR_minus_1": rr - 1,
        "odds_ratio_OR": orr, "OR_ci_woolf_log": or_ci,
    })

    # Benefit / harm framing
    beneficial_direction = (rd < 0) if event == "bad" else (rd > 0)
    if rd == 0:
        out["absolute_effect"] = "No difference in risk; NNT is infinite."
    else:
        mag = abs(rd)
        nn = 1 / mag
        if beneficial_direction:
            if event == "bad":
                out["ARR_absolute_risk_reduction"] = mag
                out["RRR_relative_risk_reduction"] = 1 - rr
            else:
                out["ABI_absolute_benefit_increase"] = mag
                out["RBI_relative_benefit_increase"] = rr - 1
            out["NNT_benefit"] = nn
            out["NNT_benefit_rounded_up"] = math.ceil(nn - 1e-12)
        else:
            if event == "bad":
                out["ARI_absolute_risk_increase"] = mag
                out["RRI_relative_risk_increase"] = rr - 1
            else:
                out["ABR_absolute_benefit_reduction"] = mag
            out["NNH_harm"] = nn
            out["NNH_harm_rounded_up"] = math.ceil(nn - 1e-12)
        # NNT CI by inverting RD CI (Altman, BMJ 1998)
        out["NNT_ci_altman"] = _nnt_ci(rd_lo, rd_hi, event)

    # Odds ratio vs risk ratio divergence warning
    if max(r0, r1) > 0.10:
        out["notes"].append(
            "At least one risk exceeds 10%: the odds ratio will overstate the risk ratio. "
            "Do not read the OR as 'times as likely'.")
    out["fisher_exact_p_two_sided"] = fisher_exact_two_sided(a, b, c, d)
    out["fragility"] = fragility_index(x1, n1, x0, n0, alpha)
    if min(n1, n0) < 30:
        out["notes"].append("An arm has fewer than 30 participants: intervals are wide and "
                            "normal approximations are rough; rely on the Fisher p and Wilson/"
                            "Newcombe intervals reported here.")
    out["framing_table"] = _framing(r1, r0, rd_lo, rd_hi, rr, rr_ci, event, out.get("NNT_ci_altman"))
    return out


def _framing(r1: float, r0: float, rd_lo: float, rd_hi: float, rr: float,
             rr_ci: Tuple[float, float], event: str, nnt_ci: Optional[Dict[str, object]]) -> Dict[str, object]:
    """The required absolute-vs-relative framing: the same result stated every way a reader meets it."""
    per = 1000
    rel = rr - 1
    word = "fewer" if (r1 < r0) else "more"
    kind = "events" if event == "bad" else "responders"
    rows = [
        ("Baseline (control) risk", f"{r0:.1%}"),
        ("Intervention risk", f"{r1:.1%}"),
        ("Absolute difference", f"{(r1 - r0) * 100:+.1f} percentage points (CI {rd_lo * 100:+.1f} to {rd_hi * 100:+.1f})"),
        ("Relative difference", f"{rel:+.0%} (RR {rr:.2f}, CI {rr_ci[0]:.2f} to {rr_ci[1]:.2f})"),
        (f"Per {per:,} people", f"{round(r0 * per)} vs {round(r1 * per)} {kind}: {abs(round(r1 * per) - round(r0 * per))} {word}"),
    ]
    if r1 != r0:
        nn = 1 / abs(r1 - r0)
        good = (r1 < r0) if event == "bad" else (r1 > r0)
        label = "NNT (benefit)" if good else "NNH (harm)"
        if nnt_ci and nnt_ci.get("crosses_zero"):
            ci_txt = nnt_ci["statement"]
        elif nnt_ci and "range" in nnt_ci:
            ci_txt = f"CI {nnt_ci['range'][0]:.1f} to {nnt_ci['range'][1]:.1f}"
        else:
            ci_txt = "CI not available"
        rows.append((label, f"{nn:.1f}, so {math.ceil(nn - 1e-12)} when rounded up ({ci_txt})"))
    warnings = []
    if r0 < 0.05 and abs(rel) >= 0.25:
        warnings.append("Low baseline risk: a large relative change is a small absolute change. Lead with the absolute figure.")
    if rd_lo < 0 < rd_hi:
        warnings.append("The absolute-difference CI includes zero: the data are compatible with no difference.")
    return {"rows": rows, "warnings": warnings,
            "rule": "State the absolute and the relative figure together, with the time frame and the baseline risk."}


def _nnt_ci(rd_lo: float, rd_hi: float, event: str) -> Dict[str, object]:
    """Express the RD CI as NNT bounds. Handles a CI that crosses zero."""
    def label(rd: float) -> str:
        good_side = (rd < 0) if event == "bad" else (rd > 0)
        return "NNTB" if good_side else "NNTH"
    if rd_lo < 0 < rd_hi:
        return {
            "crosses_zero": True,
            "statement": (f"95% CI runs from {label(rd_lo)} {1/abs(rd_lo):.1f} through infinity to "
                          f"{label(rd_hi)} {1/abs(rd_hi):.1f}. The data are compatible with benefit, "
                          "no effect, and harm."),
        }
    lo_n, hi_n = sorted((1 / abs(rd_lo) if rd_lo else math.inf, 1 / abs(rd_hi) if rd_hi else math.inf))
    return {"crosses_zero": False, "label": label((rd_lo + rd_hi) / 2), "range": (lo_n, hi_n)}


# --------------------------------------------------------------------------
# Odds ratio -> risk ratio
# --------------------------------------------------------------------------

def or_to_rr(odds_ratio: float, baseline_risk: float) -> Dict[str, object]:
    """Zhang & Yu (JAMA 1998): RR = OR / (1 - p0 + p0 * OR).

    Exact for a single 2x2 table; only an approximation for adjusted ORs
    from logistic regression (it can bias the CI). Say so in any write-up.
    """
    if not (0 < baseline_risk < 1):
        raise ValueError("baseline risk must be strictly between 0 and 1")
    rr = odds_ratio / (1 - baseline_risk + baseline_risk * odds_ratio)
    r1 = rr * baseline_risk
    return {
        "odds_ratio": odds_ratio, "baseline_risk_p0": baseline_risk,
        "risk_ratio_RR": rr, "implied_risk1": r1, "implied_RD": r1 - baseline_risk,
        "implied_NNT_or_NNH": (1 / abs(r1 - baseline_risk)) if r1 != baseline_risk else math.inf,
        "caveat": "Zhang-Yu conversion: exact for crude 2x2 ORs; approximate for adjusted ORs.",
    }


# --------------------------------------------------------------------------
# Diagnostic / screening tests
# --------------------------------------------------------------------------

def diagnostic(sens: float, spec: float, prevalence: float, per: int = 1000) -> Dict[str, object]:
    for name, v in (("sensitivity", sens), ("specificity", spec), ("prevalence", prevalence)):
        if not (0 <= v <= 1):
            raise ValueError(f"{name} must be between 0 and 1")
    tp = sens * prevalence * per
    fn = (1 - sens) * prevalence * per
    tn = spec * (1 - prevalence) * per
    fp = (1 - spec) * (1 - prevalence) * per
    ppv = tp / (tp + fp) if (tp + fp) else float("nan")
    npv = tn / (tn + fn) if (tn + fn) else float("nan")
    lr_pos = sens / (1 - spec) if spec < 1 else math.inf
    lr_neg = (1 - sens) / spec if spec > 0 else math.inf
    return {
        "per": per, "true_positives": tp, "false_positives": fp,
        "true_negatives": tn, "false_negatives": fn,
        "PPV": ppv, "NPV": npv, "LR_positive": lr_pos, "LR_negative": lr_neg,
        "plain_language": (f"Of {per} people tested, about {tp + fp:.0f} test positive; "
                           f"{tp:.0f} of them truly have the condition and {fp:.0f} do not."),
    }


# --------------------------------------------------------------------------
# Continuous outcomes
# --------------------------------------------------------------------------

def smd(mean1: float, sd1: float, n1: int, mean0: float, sd0: float, n0: int,
        level: float = 0.95) -> Dict[str, object]:
    """Cohen's d (pooled SD) and Hedges' g (small-sample corrected) with approximate CI."""
    z = _z_for(level)
    sp = math.sqrt(((n1 - 1) * sd1 ** 2 + (n0 - 1) * sd0 ** 2) / (n1 + n0 - 2))
    d = (mean1 - mean0) / sp
    j = 1 - 3 / (4 * (n1 + n0) - 9)
    g = j * d
    se_g = math.sqrt((n1 + n0) / (n1 * n0) + g ** 2 / (2 * (n1 + n0)))
    return {
        "mean_difference": mean1 - mean0, "pooled_sd": sp,
        "cohens_d": d, "hedges_g": g, "g_ci": (g - z * se_g, g + z * se_g),
        "caveat": ("Sign follows mean1 - mean0. For symptom scales where lower is better, "
                   "a negative value favours group 1. Benchmarks (0.2/0.5/0.8) are Cohen's "
                   "generic conventions, not clinical importance thresholds."),
    }


def frequencies(baseline_risk: float, relative_change: float, per: int = 1000) -> Dict[str, object]:
    """Restate 'X% relative reduction' at a stated baseline risk as counts per N people."""
    r1 = baseline_risk * (1 + relative_change)
    return {
        "per": per, "baseline_events": baseline_risk * per, "intervention_events": r1 * per,
        "difference_events": (r1 - baseline_risk) * per,
        "statement": (f"At a baseline risk of {baseline_risk:.1%}, a relative change of "
                      f"{relative_change:+.0%} moves events from {baseline_risk*per:.1f} to "
                      f"{r1*per:.1f} per {per} people - a difference of "
                      f"{(r1-baseline_risk)*per:+.1f} per {per}."),
    }


def pctcheck(percent: float, max_n: int, decimals: int = 0,
             count: Optional[int] = None) -> Dict[str, object]:
    """Which (k, n) pairs with n <= max_n round to the reported percentage?

    Use it to test whether a reported percentage is consistent with the stated
    denominator (a GRIM-style check). Example: "64% of 60 patients" is
    impossible, because 38/60 = 63.3% and 39/60 = 65.0%. So the analysis
    population was not the 60 randomized patients. Rounding is round-half-up
    at the stated number of decimals; percentages reported with other
    rounding rules can produce off-by-one edge cases, so say so.
    """
    from decimal import Decimal, ROUND_HALF_UP
    target = Decimal(str(percent)).quantize(Decimal(1).scaleb(-decimals))
    q = Decimal(1).scaleb(-decimals)
    hits: List[Tuple[int, int]] = []
    for n in range(1, max_n + 1):
        for k in range(0, n + 1):
            v = (Decimal(k) * 100 / Decimal(n)).quantize(q, rounding=ROUND_HALF_UP)
            if v == target:
                hits.append((k, n))
    ns = sorted({n for _, n in hits})
    if count is not None:
        # Which denominators make count/n round to the reported percentage?
        count_ns = sorted({n for k, n in hits if k == count})
        return {
            "reported_percent": float(target), "count": count, "max_n_checked": max_n,
            "denominators_consistent_with_count": count_ns,
            "statement": (f"{count} events and {float(target)}% fit denominator(s) "
                          f"{count_ns if count_ns else 'none'} (n <= {max_n})."),
        }
    return {
        "reported_percent": float(target), "max_n_checked": max_n,
        "consistent_n_values": ns,
        "max_consistent_n": ns[-1] if ns else None,
        "max_n_consistent": (max_n in ns),
        "pairs_near_max_n": [p for p in hits if p[1] >= max_n - 3],
        "statement": (f"{float(target)}% is {'consistent' if max_n in ns else 'NOT consistent'} "
                      f"with a denominator of {max_n}."),
    }


def ci2smd(md: float, lo: float, hi: float, n1: int, n0: int, level: float = 0.95) -> Dict[str, object]:
    """Back-calculate SE, pooled SD and an approximate SMD from a reported mean
    difference and its confidence interval (no SDs reported).

    SE = (hi - lo) / (2 z); pooled SD ≈ SE / sqrt(1/n1 + 1/n0).
    Assumes a symmetric, normal-theory CI from a two-group comparison. For
    model-adjusted (LS-mean/MMRM) differences this is an approximation; label
    results "derived from the reported CI".
    """
    z = _z_for(level)
    se = (hi - lo) / (2 * z)
    sd = se / math.sqrt(1 / n1 + 1 / n0)
    d = md / sd
    j = 1 - 3 / (4 * (n1 + n0) - 9)
    return {
        "mean_difference": md, "ci": (lo, hi), "se_derived": se,
        "pooled_sd_derived": sd, "cohens_d_approx": d, "hedges_g_approx": j * d,
        "asymmetry_warning": (abs((hi - md) - (md - lo)) > 0.05 * abs(hi - lo)),
        "caveat": "Derived from the reported CI; approximate for adjusted (LS-mean/MMRM) estimates.",
    }


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def _fmt(v: object) -> str:
    if isinstance(v, float):
        if math.isinf(v):
            return "inf"
        if v != 0 and abs(v) < 0.001:
            return f"{v:.3g}"  # keep small p-values visible instead of printing 0.0000
        return f"{v:.4f}"
    if isinstance(v, tuple):
        return "(" + ", ".join(_fmt(x) for x in v) + ")"
    if isinstance(v, dict):
        return "{" + "; ".join(f"{k}: {_fmt(x)}" for k, x in v.items()) + "}"
    if isinstance(v, list):
        return " | ".join(_fmt(x) for x in v)
    return str(v)


def _print(result: Dict[str, object], as_json: bool) -> None:
    if as_json:
        def conv(o):
            if isinstance(o, float) and math.isinf(o):
                return "inf"
            if isinstance(o, tuple):
                return [conv(x) for x in o]
            if isinstance(o, dict):
                return {k: conv(x) for k, x in o.items()}
            if isinstance(o, list):
                return [conv(x) for x in o]
            return o
        print(json.dumps(conv(result), indent=2))
    else:
        for k, v in result.items():
            print(f"{k}: {_fmt(v)}")


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("binary", help="2x2 table effect measures")
    b.add_argument("--events1", type=int, required=True, help="events in intervention arm")
    b.add_argument("--n1", type=int, required=True, help="participants in intervention arm")
    b.add_argument("--events0", type=int, required=True, help="events in control arm")
    b.add_argument("--n0", type=int, required=True, help="participants in control arm")
    b.add_argument("--event", choices=["good", "bad"], required=True,
                   help="good = response/remission; bad = death/relapse/adverse event")
    b.add_argument("--level", type=float, default=0.95)
    b.add_argument("--alpha", type=float, default=0.05)
    b.add_argument("--json", action="store_true")

    o = sub.add_parser("orrr", help="odds ratio -> risk ratio at a baseline risk")
    o.add_argument("--or", dest="odds_ratio", type=float, required=True)
    o.add_argument("--baseline", type=float, required=True, help="control-group risk, 0-1")
    o.add_argument("--json", action="store_true")

    dg = sub.add_parser("diagnostic", help="PPV/NPV/LRs from sensitivity, specificity, prevalence")
    dg.add_argument("--sens", type=float, required=True)
    dg.add_argument("--spec", type=float, required=True)
    dg.add_argument("--prev", type=float, required=True)
    dg.add_argument("--per", type=int, default=1000)
    dg.add_argument("--json", action="store_true")

    s = sub.add_parser("smd", help="Cohen's d / Hedges' g")
    for arm in ("1", "0"):
        s.add_argument(f"--mean{arm}", type=float, required=True)
        s.add_argument(f"--sd{arm}", type=float, required=True)
        s.add_argument(f"--n{arm}", type=int, required=True)
    s.add_argument("--level", type=float, default=0.95)
    s.add_argument("--json", action="store_true")

    f = sub.add_parser("frequencies", help="relative change -> counts per N")
    f.add_argument("--baseline", type=float, required=True)
    f.add_argument("--relative-change", type=float, required=True,
                   help="e.g. -0.25 for a 25%% relative reduction")
    f.add_argument("--per", type=int, default=1000)
    f.add_argument("--json", action="store_true")

    pc = sub.add_parser("pctcheck", help="is a reported percentage possible with the stated n?")
    pc.add_argument("--percent", type=str, required=True)
    pc.add_argument("--n", type=int, required=True, help="stated denominator (checks all n up to this)")
    pc.add_argument("--decimals", type=int, default=None,
                    help="decimal places in the reported figure (default: inferred from --percent as typed)")
    pc.add_argument("--count", type=int, default=None,
                    help="stated number of events: report which denominators fit count and percent")
    pc.add_argument("--json", action="store_true")

    cs = sub.add_parser("ci2smd", help="SD and SMD derived from a mean difference and its CI")
    cs.add_argument("--md", type=float, required=True)
    cs.add_argument("--lo", type=float, required=True)
    cs.add_argument("--hi", type=float, required=True)
    cs.add_argument("--n1", type=int, required=True)
    cs.add_argument("--n0", type=int, required=True)
    cs.add_argument("--level", type=float, default=0.95)
    cs.add_argument("--json", action="store_true")

    bl = sub.add_parser("blinding", help="Bang and James blinding indexes from end-of-trial guesses")
    bl.add_argument("--t-guess-t", type=int, required=True, help="treatment arm: guessed treatment")
    bl.add_argument("--t-guess-c", type=int, required=True, help="treatment arm: guessed control")
    bl.add_argument("--t-dk", type=int, default=0, help="treatment arm: don't know")
    bl.add_argument("--c-guess-t", type=int, required=True, help="control arm: guessed treatment")
    bl.add_argument("--c-guess-c", type=int, required=True, help="control arm: guessed control")
    bl.add_argument("--c-dk", type=int, default=0, help="control arm: don't know")
    bl.add_argument("--level", type=float, default=0.95)
    bl.add_argument("--json", action="store_true")

    by = sub.add_parser("bayes", help="Bayesian reanalysis of a reported estimate and CI")
    by.add_argument("--est", type=float, required=True)
    by.add_argument("--lo", type=float, required=True)
    by.add_argument("--hi", type=float, required=True)
    by.add_argument("--level", type=float, default=0.95, help="confidence level of the reported CI")
    by.add_argument("--scale", choices=["diff", "ratio"], default="diff")
    by.add_argument("--mcid", type=float, default=None, help="smallest meaningful effect, on the reported scale")
    by.add_argument("--better", choices=["lower", "higher"], required=True,
                    help="lower = lower values favour treatment (MADRS change, RR < 1)")
    by.add_argument("--prior-mean", type=float, default=None, help="custom prior mean (reported scale)")
    by.add_argument("--prior-sd", type=float, default=None, help="custom prior SD (working scale: log for ratios)")
    by.add_argument("--json", action="store_true")

    ev = sub.add_parser("evalue", help="E-value for unmeasured confounding")
    ev.add_argument("--measure", choices=["rr", "or", "hr", "smd"], required=True)
    ev.add_argument("--est", type=float, required=True)
    ev.add_argument("--lo", type=float, default=None)
    ev.add_argument("--hi", type=float, default=None)
    ev.add_argument("--common", action="store_true", help="outcome prevalence above about 15%% (OR and HR)")
    ev.add_argument("--se", type=float, default=None, help="SE of d (SMD only)")
    ev.add_argument("--json", action="store_true")

    rd = sub.add_parser("retrodesign", help="power, Type S and Type M error for a plausible true effect")
    rd.add_argument("--true-effect", type=float, required=True)
    rd.add_argument("--se", type=float, required=True)
    rd.add_argument("--alpha", type=float, default=0.05)
    rd.add_argument("--json", action="store_true")

    ma = sub.add_parser("meta", help="fixed or random-effects meta-analysis")
    ma.add_argument("--est", type=float, nargs="+", required=True, help="study estimates (ratios if --scale ratio)")
    ma.add_argument("--se", type=float, nargs="+", default=None, help="SEs (of the log ratio if --scale ratio)")
    ma.add_argument("--lo", type=float, nargs="+", default=None, help="lower CI limits (instead of --se)")
    ma.add_argument("--hi", type=float, nargs="+", default=None, help="upper CI limits (instead of --se)")
    ma.add_argument("--labels", nargs="+", default=None)
    ma.add_argument("--method", choices=["fixed", "dl", "pm", "reml"], default="reml")
    ma.add_argument("--no-hksj", action="store_true")
    ma.add_argument("--scale", choices=["diff", "ratio"], default="diff")
    ma.add_argument("--level", type=float, default=0.95)
    ma.add_argument("--json", action="store_true")

    sn = sub.add_parser("smd2nnt", help="standardized mean difference -> NNT")
    sn.add_argument("--d", type=float, required=True, help="positive = treatment better")
    sn.add_argument("--cer", type=float, default=None, help="control-group responder rate, 0-1")
    sn.add_argument("--json", action="store_true")

    a = p.parse_args(argv)
    try:
        if a.cmd == "binary":
            res = binary(a.events1, a.n1, a.events0, a.n0, a.event, a.level, a.alpha)
        elif a.cmd == "orrr":
            res = or_to_rr(a.odds_ratio, a.baseline)
        elif a.cmd == "diagnostic":
            res = diagnostic(a.sens, a.spec, a.prev, a.per)
        elif a.cmd == "smd":
            res = smd(a.mean1, a.sd1, a.n1, a.mean0, a.sd0, a.n0, a.level)
        elif a.cmd == "pctcheck":
            dec = a.decimals if a.decimals is not None else (
                len(a.percent.split(".")[1]) if "." in a.percent else 0)
            res = pctcheck(float(a.percent), a.n, dec, a.count)
        elif a.cmd == "ci2smd":
            res = ci2smd(a.md, a.lo, a.hi, a.n1, a.n0, a.level)
        elif a.cmd == "blinding":
            res = adv.blinding(a.t_guess_t, a.t_guess_c, a.t_dk, a.c_guess_t, a.c_guess_c, a.c_dk, a.level)
        elif a.cmd == "bayes":
            res = adv.bayes(a.est, a.lo, a.hi, a.level, a.scale, a.mcid, a.better, a.prior_mean, a.prior_sd)
        elif a.cmd == "evalue":
            res = adv.evalue(a.measure, a.est, a.lo, a.hi, a.common, a.se)
        elif a.cmd == "retrodesign":
            res = adv.retrodesign(a.true_effect, a.se, a.alpha)
        elif a.cmd == "meta":
            if a.se is None:
                if a.lo is None or a.hi is None:
                    raise ValueError("give --se, or both --lo and --hi")
                zz = adv._z2(a.level)
                if a.scale == "ratio":
                    ses = [(math.log(h) - math.log(l)) / (2 * zz) for l, h in zip(a.lo, a.hi)]
                else:
                    ses = [(h - l) / (2 * zz) for l, h in zip(a.lo, a.hi)]
            else:
                ses = a.se
            res = adv.meta(a.est, ses, a.method, not a.no_hksj, a.level, a.scale, a.labels)
        elif a.cmd == "smd2nnt":
            res = adv.smd2nnt(a.d, a.cer)
        else:
            res = frequencies(a.baseline, a.relative_change, a.per)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    _print(res, a.json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
