"""appraisal_advanced.py - advanced appraisal methods for risk_calc.py.

Standard library only. risk_calc.py imports this module and exposes each
function as a subcommand:

  blinding     Bang (2004) per-arm and James (1996) overall blinding indexes
  bayes        Bayesian reanalysis of a reported estimate and CI under
               skeptical, flat, enthusiastic, and custom priors; plus the
               Analysis of Credibility (Matthews) critical prior limits
  evalue       E-value for unmeasured confounding (VanderWeele & Ding 2017)
  retrodesign  power, Type S (sign) and Type M (magnitude) error for a
               plausible true effect (Gelman & Carlin 2014)
  meta         fixed-effect and random-effects meta-analysis (DerSimonian-
               Laird, Paule-Mandel, REML), Hartung-Knapp-Sidik-Jonkman CI,
               I-squared, Q test, prediction interval
  smd2nnt      convert a standardized mean difference to an NNT (Kraemer &
               Kupfer 2006; Furukawa & Leucht 2011)

Every function returns a dict of named values plus an "assumptions" entry
that states what the method assumes. The caller labels the result: the
arithmetic is exact, but the result is only as good as the inputs.

Distribution functions (normal, t, chi-square) are implemented here with
textbook algorithms (Acklam's inverse normal with Halley refinement; Lentz
continued fractions for the incomplete beta and gamma). They were checked
against SciPy; see the verification script in the workspace.
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional, Sequence, Tuple

# --------------------------------------------------------------------------
# Distribution functions
# --------------------------------------------------------------------------

def norm_cdf(x: float) -> float:
    return 0.5 * math.erfc(-x / math.sqrt(2.0))


def norm_pdf(x: float) -> float:
    return math.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)


def norm_ppf(p: float) -> float:
    """Inverse normal CDF: Acklam's rational approximation plus one Halley step."""
    if not 0.0 < p < 1.0:
        if p == 0.0:
            return -math.inf
        if p == 1.0:
            return math.inf
        raise ValueError("p must be in (0, 1)")
    a = [-3.969683028665376e01, 2.209460984245205e02, -2.759285104469687e02,
         1.383577518672690e02, -3.066479806614716e01, 2.506628277459239e00]
    b = [-5.447609879822406e01, 1.615858368580409e02, -1.556989798598866e02,
         6.680131188771972e01, -1.328068155288572e01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e00,
         -2.549732539343734e00, 4.374664141464968e00, 2.938163982698783e00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e00,
         3.754408661907416e00]
    plow, phigh = 0.02425, 1 - 0.02425
    if p < plow:
        q = math.sqrt(-2 * math.log(p))
        x = (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / \
            ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
    elif p <= phigh:
        q = p - 0.5
        r = q * q
        x = (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q / \
            (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1)
    else:
        q = math.sqrt(-2 * math.log(1 - p))
        x = -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / \
             ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
    # Halley refinement
    e = norm_cdf(x) - p
    u = e * math.sqrt(2 * math.pi) * math.exp(x * x / 2)
    return x - u / (1 + x * u / 2)


def _betacf(a: float, b: float, x: float) -> float:
    """Continued fraction for the incomplete beta (modified Lentz)."""
    tiny = 1e-300
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    d = 1.0 / (d if abs(d) > tiny else tiny)
    h = d
    for m in range(1, 1000):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > tiny else tiny)
        c = 1.0 + aa / c
        c = c if abs(c) > tiny else tiny
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > tiny else tiny)
        c = 1.0 + aa / c
        c = c if abs(c) > tiny else tiny
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 1e-15:
            break
    return h


def betainc_reg(a: float, b: float, x: float) -> float:
    """Regularized incomplete beta I_x(a, b)."""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    lbeta = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
    front = math.exp(lbeta + a * math.log(x) + b * math.log1p(-x))
    if x < (a + 1.0) / (a + b + 2.0):
        return front * _betacf(a, b, x) / a
    return 1.0 - front * _betacf(b, a, 1.0 - x) / b


def t_cdf(t: float, df: float) -> float:
    x = df / (df + t * t)
    tail = 0.5 * betainc_reg(df / 2.0, 0.5, x)
    return 1.0 - tail if t > 0 else tail


def t_ppf(p: float, df: float) -> float:
    """Inverse t CDF by bracketing bisection (robust for any df > 0)."""
    if not 0.0 < p < 1.0:
        raise ValueError("p must be in (0, 1)")
    lo, hi = -1.0, 1.0
    while t_cdf(lo, df) > p:
        lo *= 2.0
    while t_cdf(hi, df) < p:
        hi *= 2.0
    for _ in range(200):
        mid = (lo + hi) / 2.0
        if t_cdf(mid, df) < p:
            lo = mid
        else:
            hi = mid
        if hi - lo < 1e-13:
            break
    return (lo + hi) / 2.0


def _gammainc_lower_reg(s: float, x: float) -> float:
    """Regularized lower incomplete gamma P(s, x)."""
    if x <= 0.0:
        return 0.0
    if x < s + 1.0:  # series
        term = 1.0 / s
        total = term
        ap = s
        for _ in range(10000):
            ap += 1.0
            term *= x / ap
            total += term
            if abs(term) < abs(total) * 1e-16:
                break
        return total * math.exp(-x + s * math.log(x) - math.lgamma(s))
    # continued fraction for Q, then P = 1 - Q
    tiny = 1e-300
    b = x + 1.0 - s
    c = 1.0 / tiny
    d = 1.0 / b
    h = d
    for i in range(1, 10000):
        an = -i * (i - s)
        b += 2.0
        d = an * d + b
        d = 1.0 / (d if abs(d) > tiny else tiny)
        c = b + an / c
        c = c if abs(c) > tiny else tiny
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 1e-16:
            break
    q = math.exp(-x + s * math.log(x) - math.lgamma(s)) * h
    return 1.0 - q


def chi2_sf(x: float, df: float) -> float:
    return 1.0 - _gammainc_lower_reg(df / 2.0, x / 2.0)


def _z2(level: float) -> float:
    return norm_ppf(1.0 - (1.0 - level) / 2.0)


# --------------------------------------------------------------------------
# 1. Blinding indexes
# --------------------------------------------------------------------------

def blinding(t_guess_t: int, t_guess_c: int, t_dk: int,
             c_guess_t: int, c_guess_c: int, c_dk: int,
             level: float = 0.95) -> Dict[str, object]:
    """Bang (2004) per-arm index and James (1996) overall index.

    Inputs are counts of guesses in each true arm:
      treatment arm: guessed treatment / guessed control / don't know
      control arm:   guessed treatment / guessed control / don't know
    """
    counts = [t_guess_t, t_guess_c, t_dk, c_guess_t, c_guess_c, c_dk]
    if any(v < 0 for v in counts):
        raise ValueError("counts must be non-negative")
    n_t = t_guess_t + t_guess_c + t_dk
    n_c = c_guess_t + c_guess_c + c_dk
    if n_t == 0 or n_c == 0:
        raise ValueError("each arm needs at least one respondent")
    z = _z2(level)

    def bang(correct: int, incorrect: int, n: int) -> Dict[str, object]:
        if correct + incorrect == 0:
            return {"index": float("nan"), "se": float("nan"), "ci": (float("nan"), float("nan"))}
        pc, pi = correct / n, incorrect / n
        est = pc - pi  # identical to (2*correct/(correct+incorrect) - 1) * (correct+incorrect)/n
        se = math.sqrt(max(pc + pi - (pc - pi) ** 2, 0.0) / n)
        return {"index": est, "se": se, "ci": (est - z * se, est + z * se)}

    bang_t = bang(t_guess_t, t_guess_c, n_t)
    bang_c = bang(c_guess_c, c_guess_t, n_c)

    # James index: rows = guess (treatment, control, DK); columns = true arm (treatment, control)
    x = [[t_guess_t, c_guess_t], [t_guess_c, c_guess_c], [t_dk, c_dk]]
    n = n_t + n_c
    if x[0][0] + x[0][1] + x[1][0] + x[1][1] == 0:
        james = {"index": 1.0, "se": 0.0, "ci": (1.0, 1.0),
                 "note": "all respondents answered don't know; James index fixed at 1 (James 1996, p. 1425)"}
    else:
        w = [[0.0, 0.5], [0.5, 0.0]]  # default weights: correct 0, incorrect 0.5 (DK weight 1 is implicit)
        P = [[x[i][j] / n for j in range(2)] for i in range(3)]
        row = [sum(P[i]) for i in range(3)]               # guess-category totals
        col_guessers = [P[0][j] + P[1][j] for j in range(2)]  # arm totals excluding DK
        pdk = row[2]
        pdo = sum(w[i][j] * P[i][j] for i in range(2) for j in range(2)) / (1 - pdk)
        denom = sum(w[i][j] * row[i] * col_guessers[j] for i in range(2) for j in range(2))
        pde = denom / (1 - pdk) ** 2
        if pde == 0:
            james = {"index": float("nan"), "se": float("nan"), "ci": (float("nan"), float("nan")),
                     "note": "James index undefined (expected disagreement is 0)"}
        else:
            kd = (pdo - pde) / pde
            est = (1 + pdk + (1 - pdk) * kd) / 2
            t1_den = 4 * denom ** 2
            t1_num = 0.0
            for i in range(2):
                for j in range(2):
                    extra = sum(w[r][j] * row[r] + w[i][r] * col_guessers[r] for r in range(2))
                    t1_num += P[i][j] * (1 - pdk) ** 2 * ((1 - pdk) * w[i][j] - (1 + kd) * extra) ** 2
            v1 = t1_num / t1_den
            v2 = pdk * (1 - pdk) - (1 - pdk) * (1 + kd) * (pdk + ((1 - pdk) * (1 + kd)) / 4)
            se = math.sqrt(max((v1 + v2) / n, 0.0))
            james = {"index": est, "se": se, "ci": (est - z * se, est + z * se)}

    def read_bang(b: Dict[str, object]) -> str:
        v = b["index"]
        if isinstance(v, float) and math.isnan(v):
            return "undefined (no one in this arm guessed)"
        lo, hi = b["ci"]
        if hi < -0.2 or lo > 0.2:
            return "outside -0.2 to 0.2 with the whole CI: evidence of unblinding (or opposite guessing if negative)"
        if -0.2 <= v <= 0.2:
            return "inside -0.2 to 0.2: consistent with blinding by the usual convention"
        return "point estimate outside -0.2 to 0.2, CI overlaps it: possible unblinding"

    james_read = "undefined"
    if not (isinstance(james["index"], float) and math.isnan(james["index"])):
        james_read = ("CI upper limit below 0.5: unblinding claimed (James convention)"
                      if james["ci"][1] < 0.5 else
                      "CI reaches 0.5 or above: no claim of unblinding by the James convention")

    return {
        "n_treatment": n_t, "n_control": n_c,
        "bang_treatment": bang_t, "bang_treatment_reading": read_bang(bang_t),
        "bang_control": bang_c, "bang_control_reading": read_bang(bang_c),
        "james_overall": james, "james_reading": james_read,
        "scales": ("Bang: -1 to 1; 0 = random guessing; 1 = everyone correct; -1 = everyone wrong. "
                   "James: 0 to 1; 0 = everyone correct; 0.5 = random guessing; 1 = everyone answered don't know."),
        "assumptions": ("Guess data come from the trial's blinding survey (state when it was asked). "
                        "Normal-approximation CIs; small arms make them unreliable. "
                        "The -0.2 to 0.2 Bang band and the James 0.5 threshold are conventions, not tests of efficacy."),
    }


# --------------------------------------------------------------------------
# 2. Bayesian reanalysis and Analysis of Credibility
# --------------------------------------------------------------------------

def _posterior(m: float, s: float, prior_mean: Optional[float], prior_sd: Optional[float]) -> Tuple[float, float]:
    if prior_sd is None:  # flat prior: posterior = likelihood
        return m, s
    wp, wd = 1 / prior_sd ** 2, 1 / s ** 2
    return (wp * prior_mean + wd * m) / (wp + wd), math.sqrt(1 / (wp + wd))


def bayes(estimate: float, lo: float, hi: float, level: float = 0.95, scale: str = "diff",
          mcid: Optional[float] = None, better: str = "lower",
          prior_mean: Optional[float] = None, prior_sd: Optional[float] = None,
          cred_level: float = 0.95) -> Dict[str, object]:
    """Normal-normal Bayesian reanalysis of a reported estimate and CI.

    scale: "diff" (mean or risk difference) or "ratio" (RR, OR, HR; analysed on the log scale).
    better: "lower" if lower values favour the treatment (e.g., MADRS change, RR < 1), else "higher".
    mcid: smallest clinically meaningful effect on the reported scale (e.g., -2 MADRS points, RR 0.8).
    """
    if not lo < hi:
        raise ValueError("lo must be below hi")
    if scale not in ("diff", "ratio"):
        raise ValueError("scale must be diff or ratio")
    if better not in ("lower", "higher"):
        raise ValueError("better must be lower or higher")
    if scale == "ratio":
        if min(estimate, lo, hi) <= 0:
            raise ValueError("ratio inputs must be positive")
        m, l, u = math.log(estimate), math.log(lo), math.log(hi)
        null = 0.0
        delta = math.log(mcid) if mcid is not None else None
        back = math.exp
    else:
        m, l, u = estimate, lo, hi
        null = 0.0
        delta = mcid
        back = (lambda v: v)
    z = _z2(level)
    s = (u - l) / (2 * z)
    sign = -1.0 if better == "lower" else 1.0  # benefit direction
    zc = _z2(cred_level)

    if delta is not None and sign * delta <= 0:
        raise ValueError("mcid must lie on the benefit side of the null (check --better)")

    priors: List[Tuple[str, Optional[float], Optional[float], str]] = [
        ("flat", None, None, "no prior information; posterior equals the likelihood"),
    ]
    if delta is not None:
        sd_skept = abs(delta) / 1.6448536269514722
        priors.append(("skeptical", null, sd_skept,
                       "centred on no effect; 5% prior probability the effect is at least the MCID"))
        priors.append(("enthusiastic", delta, sd_skept,
                       "centred on the MCID; 5% prior probability of no benefit or harm"))
    if prior_sd is not None:
        lp = math.log(prior_mean) if (scale == "ratio" and prior_mean is not None) else prior_mean
        ls = prior_sd  # sd is always on the working (log for ratios) scale
        priors.append(("custom", lp if lp is not None else 0.0, ls, "user-specified prior (sd on the working scale)"))

    results = {}
    for name, pm, ps, desc in priors:
        mu, sd = _posterior(m, s, pm, ps)
        p_benefit = norm_cdf(sign * (mu - null) / sd)
        p_mcid = norm_cdf(sign * (mu - delta) / sd) if delta is not None else None
        entry = {
            "prior": desc,
            "prior_mean": back(pm) if pm is not None else None,
            "posterior_median": back(mu),
            "credible_interval": (back(mu - zc * sd), back(mu + zc * sd)),
            "P(any benefit)": p_benefit,
            "P(harm)": 1 - p_benefit,
        }
        if p_mcid is not None:
            entry["P(benefit >= MCID)"] = p_mcid
        results[name] = entry

    credibility = _credibility(l, u, null, back, z)

    return {
        "working_scale": "log" if scale == "ratio" else "difference",
        "se_from_ci": s,
        "priors": results,
        "credibility": credibility,
        "assumptions": ("Normal likelihood rebuilt from the reported estimate and CI (symmetric on the working scale). "
                        "Priors are normal. Results depend on the prior; report all of them. "
                        "The inputs are what the paper or release reported; label the output accordingly."),
    }


def _credibility(l: float, u: float, null: float, back, z: float) -> Dict[str, object]:
    """Matthews' Analysis of Credibility, solved numerically from its definitions.

    Significant result (CI excludes the null): the critical skeptical limit SL is the
    95% bound of a null-centred prior N(0, (SL/z)^2) that makes the posterior interval
    just touch the null. Non-significant result: the critical advocacy limit AL defines
    a prior centred at AL/2 with 95% interval (0, AL) that makes the posterior just exclude the null.
    """
    m = (l + u) / 2
    s = (u - l) / (2 * z)
    significant = (l > null) or (u < null)
    sgn = 1.0 if m > null else -1.0

    def post_bound(pm: float, ps: float) -> float:
        mu, sd = _posterior(m, s, pm, ps)
        return mu - sgn * z * sd  # the bound nearest the null

    if significant:
        # find tau such that post_bound(0, tau) == 0; bound moves away from null as tau grows
        lo_t, hi_t = 1e-9, 1e-9
        while sgn * post_bound(null, hi_t) <= 0:
            hi_t *= 2
            if hi_t > 1e12:
                break
        for _ in range(300):
            mid = (lo_t + hi_t) / 2
            if sgn * post_bound(null, mid) > 0:
                hi_t = mid
            else:
                lo_t = mid
        sl = z * hi_t
        closed = (u - l) ** 2 / (4 * math.sqrt(abs(u * l)))
        return {
            "result_is": "statistically significant",
            "critical_skeptical_limit": back(null + sgn * sl),
            "closed_form_check": back(null + sgn * closed),
            "reading": ("The finding stays credible only if prior evidence makes effects at least this large "
                        "plausible. If prior knowledge says effects that large are implausible, a skeptic "
                        "can reasonably doubt the result."),
        }
    # non-significant: find AL with prior N(AL/2, (AL/(2z))^2) making the posterior exclude the null
    direction = sgn if m != null else 1.0

    def bound_for(al: float) -> float:
        mu, sd = _posterior(m, s, al / 2, abs(al) / (2 * z))
        return mu - direction * z * sd

    # Small advocacy priors (tight intervals from 0 to AL) always force significance, because the
    # prior interval itself excludes the null. The critical limit is the LARGEST AL that still makes
    # the posterior significant: expand until significance is lost, then bisect for the crossing.
    lo_a = 1e-6 * direction
    if direction * bound_for(lo_a) <= 0:
        return {"result_is": "not statistically significant", "critical_advocacy_limit": None,
                "reading": "could not bracket the advocacy limit"}
    hi_a = lo_a
    while direction * bound_for(hi_a) > 0:
        lo_a = hi_a
        hi_a *= 2
        if abs(hi_a) > 1e12:
            return {"result_is": "not statistically significant", "critical_advocacy_limit": None,
                    "reading": "no finite advocacy limit found"}
    for _ in range(300):
        mid = (lo_a + hi_a) / 2
        if direction * bound_for(mid) > 0:
            lo_a = mid
        else:
            hi_a = mid
    al = (lo_a + hi_a) / 2
    closed = -(u + l) * (u - l) ** 2 / (2 * u * l)
    return {
        "result_is": "not statistically significant",
        "critical_advocacy_limit": back(null + al),
        "closed_form_check": back(null + closed),
        "reading": ("The non-significant result counts as evidence of an effect only for someone whose prior "
                    "belief, before this study, already put the effect between no effect and this limit with 95% "
                    "confidence. That belief must come from other evidence; this study cannot supply it."),
    }


# --------------------------------------------------------------------------
# 3. E-value and retrodesign
# --------------------------------------------------------------------------

def _evalue_rr(rr: float) -> float:
    if rr < 1:
        rr = 1 / rr
    return rr + math.sqrt(rr * (rr - 1))


def evalue(measure: str, estimate: float, lo: Optional[float] = None, hi: Optional[float] = None,
           common: bool = False, se: Optional[float] = None) -> Dict[str, object]:
    """E-value (VanderWeele & Ding 2017).

    measure: rr, or, hr, smd. For or/hr, common=True when the outcome is common (>15%).
    For smd, pass se (standard error of d) to get the CI E-value.
    """
    measure = measure.lower()
    notes = []
    if measure == "rr":
        conv = lambda v: v
    elif measure == "or":
        if common:
            conv = lambda v: math.sqrt(v)
            notes.append("common outcome: RR approximated by sqrt(OR)")
        else:
            conv = lambda v: v
            notes.append("rare outcome: OR approximates RR")
    elif measure == "hr":
        if common:
            conv = lambda v: (1 - 0.5 ** math.sqrt(v)) / (1 - 0.5 ** math.sqrt(1 / v))
            notes.append("common outcome: RR approximated by (1 - 0.5^sqrt(HR)) / (1 - 0.5^sqrt(1/HR))")
        else:
            conv = lambda v: v
            notes.append("rare outcome: HR approximates RR")
    elif measure == "smd":
        conv = None
        notes.append("SMD converted with RR ~ exp(0.91 d)")
    else:
        raise ValueError("measure must be rr, or, hr, or smd")

    if measure == "smd":
        rr = math.exp(0.91 * estimate)
        ci = None
        if se is not None:
            ci = (math.exp(0.91 * estimate - 1.78 * se), math.exp(0.91 * estimate + 1.78 * se))
    else:
        if estimate <= 0:
            raise ValueError("ratio must be positive")
        rr = conv(estimate)
        ci = (conv(lo), conv(hi)) if (lo is not None and hi is not None) else None

    e_point = _evalue_rr(rr)
    e_ci = None
    if ci is not None:
        if ci[0] <= 1 <= ci[1]:
            e_ci = 1.0
            notes.append("CI includes the null: CI E-value is 1")
        else:
            near = ci[0] if rr > 1 else ci[1]
            e_ci = _evalue_rr(near)
    return {
        "rr_used": rr,
        "e_value_point": e_point,
        "e_value_ci_limit": e_ci,
        "reading": (f"An unmeasured confounder would need to be associated with both the exposure and the outcome "
                    f"by a risk ratio of at least {e_point:.2f} each, beyond the measured confounders, to explain "
                    "away the point estimate" + (f"; at least {e_ci:.2f} to move the CI to include the null." if e_ci else ".")),
        "notes": notes,
        "assumptions": ("Applies to a comparison between groups in observational data. It does not apply to a "
                        "single-arm before/after change (no comparison group to confound). A large E-value is not "
                        "proof of causation; it says how strong confounding would have to be."),
    }


def retrodesign(true_effect: float, se: float, alpha: float = 0.05) -> Dict[str, object]:
    """Power, Type S and Type M (exaggeration) error (Gelman & Carlin 2014), closed form."""
    if se <= 0:
        raise ValueError("se must be positive")
    if true_effect == 0:
        raise ValueError("true_effect must be non-zero")
    a = abs(true_effect)
    z = norm_ppf(1 - alpha / 2)
    lam = a / se
    p_hi = 1 - norm_cdf(z - lam)   # significant, right sign
    p_lo = norm_cdf(-z - lam)      # significant, wrong sign
    power = p_hi + p_lo
    type_s = p_lo / power
    # E|X| over the rejection region, X ~ N(a, se^2), region |X| > z*se
    c = z * se
    e_hi = a * (1 - norm_cdf((c - a) / se)) + se * norm_pdf((c - a) / se)
    e_lo = -a * norm_cdf((-c - a) / se) + se * norm_pdf((-c - a) / se)
    exaggeration = (e_hi + e_lo) / power / a
    return {
        "true_effect_assumed": true_effect, "se": se, "alpha": alpha,
        "power": power,
        "type_s_error": type_s,
        "exaggeration_ratio_type_m": exaggeration,
        "reading": (f"If the true effect is {true_effect}, a study with SE {se} has {power:.0%} power; a significant "
                    f"result would overstate the effect about {exaggeration:.1f}-fold on average and have the wrong "
                    f"sign {type_s:.1%} of the time."),
        "assumptions": ("The true effect is an external, plausible value (from prior trials or a meta-analysis), "
                        "not the study's own estimate. Normal sampling distribution."),
    }


# --------------------------------------------------------------------------
# 4. Meta-analysis
# --------------------------------------------------------------------------

def _tau2_dl(y: Sequence[float], v: Sequence[float]) -> float:
    w = [1 / vi for vi in v]
    sw = sum(w)
    mu = sum(wi * yi for wi, yi in zip(w, y)) / sw
    q = sum(wi * (yi - mu) ** 2 for wi, yi in zip(w, y))
    c = sw - sum(wi * wi for wi in w) / sw
    return max(0.0, (q - (len(y) - 1)) / c)


def _q_at(y, v, t2):
    w = [1 / (vi + t2) for vi in v]
    mu = sum(wi * yi for wi, yi in zip(w, y)) / sum(w)
    return sum(wi * (yi - mu) ** 2 for wi, yi in zip(w, y))


def _tau2_pm(y, v) -> float:
    k = len(y)
    if _q_at(y, v, 0.0) <= k - 1:
        return 0.0
    lo, hi = 0.0, 1.0
    while _q_at(y, v, hi) > k - 1:
        hi *= 2
    for _ in range(300):
        mid = (lo + hi) / 2
        if _q_at(y, v, mid) > k - 1:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def _tau2_reml(y, v) -> float:
    t2 = _tau2_dl(y, v)
    for _ in range(1000):
        w = [1 / (vi + t2) for vi in v]
        sw = sum(w)
        mu = sum(wi * yi for wi, yi in zip(w, y)) / sw
        num = sum(wi * wi * ((yi - mu) ** 2 - vi) for wi, yi, vi in zip(w, y, v)) + sum(wi * wi for wi in w) / sw
        new = max(0.0, num / sum(wi * wi for wi in w))
        if abs(new - t2) < 1e-12:
            t2 = new
            break
        t2 = new
    return t2


def meta(estimates: Sequence[float], ses: Sequence[float], method: str = "reml", hksj: bool = True,
         level: float = 0.95, scale: str = "diff", labels: Optional[Sequence[str]] = None) -> Dict[str, object]:
    """Inverse-variance meta-analysis.

    estimates/ses on the working scale (pass log ratios for ratio measures, or use scale='ratio'
    with ratio estimates and SEs of the log ratio).
    method: fixed, dl, pm, reml.
    """
    k = len(estimates)
    if k != len(ses) or k < 2:
        raise ValueError("need at least 2 studies with matching estimates and SEs")
    if any(s <= 0 for s in ses):
        raise ValueError("SEs must be positive")
    y = [math.log(e) for e in estimates] if scale == "ratio" else list(estimates)
    back = math.exp if scale == "ratio" else (lambda val: val)
    v = [s * s for s in ses]
    z = _z2(level)

    # heterogeneity statistics (always from fixed-effect weights)
    w0 = [1 / vi for vi in v]
    mu0 = sum(wi * yi for wi, yi in zip(w0, y)) / sum(w0)
    q = sum(wi * (yi - mu0) ** 2 for wi, yi in zip(w0, y))
    df = k - 1
    p_q = chi2_sf(q, df)
    i2 = max(0.0, (q - df) / q) if q > 0 else 0.0

    method = method.lower()
    if method == "fixed":
        t2 = 0.0
    elif method == "dl":
        t2 = _tau2_dl(y, v)
    elif method == "pm":
        t2 = _tau2_pm(y, v)
    elif method == "reml":
        t2 = _tau2_reml(y, v)
    else:
        raise ValueError("method must be fixed, dl, pm, or reml")

    w = [1 / (vi + t2) for vi in v]
    sw = sum(w)
    mu = sum(wi * yi for wi, yi in zip(w, y)) / sw
    se_mu = math.sqrt(1 / sw)
    ci = (mu - z * se_mu, mu + z * se_mu)
    out = {
        "k": k, "method": method,
        "pooled": back(mu),
        "ci_wald": (back(ci[0]), back(ci[1])),
        "tau2": t2, "tau": math.sqrt(t2),
        "Q": q, "df": df, "p_Q": p_q, "I2": i2,
    }
    if hksj and method != "fixed":
        qstar = sum(wi * (yi - mu) ** 2 for wi, yi in zip(w, y)) / df
        se_hk = math.sqrt(qstar / sw)
        se_hk_used = max(se_hk, se_mu)  # the "modified" HKSJ: never narrower than the Wald CI
        tq = t_ppf(1 - (1 - level) / 2, df)
        out["ci_hksj"] = (back(mu - tq * se_hk_used), back(mu + tq * se_hk_used))
        out["hksj_note"] = ("Hartung-Knapp-Sidik-Jonkman CI with t(k-1); the SE is not allowed to fall below the "
                            "Wald SE (modified HKSJ), which avoids the known over-narrowing when studies agree closely.")
    if k >= 3 and method != "fixed":
        tp = t_ppf(1 - (1 - level) / 2, k - 2)
        half = tp * math.sqrt(t2 + se_mu ** 2)
        out["prediction_interval"] = (back(mu - half), back(mu + half))
        out["prediction_note"] = "Where the true effect in a new, similar setting is expected to fall (Higgins 2009; t with k-2 df)."
    if labels:
        out["weights_percent"] = {lab: 100 * wi / sw for lab, wi in zip(labels, w)}
    out["assumptions"] = ("Inverse-variance weights from each study's SE. Random-effects models assume the true effects "
                          "vary normally across studies. With fewer than about 5 studies tau2 is poorly estimated; "
                          "prefer HKSJ and report the prediction interval. Pooling does not fix biased trials "
                          "(for psychedelics: functional unblinding).")
    return out


# --------------------------------------------------------------------------
# 5. SMD to NNT
# --------------------------------------------------------------------------

def smd2nnt(d: float, cer: Optional[float] = None) -> Dict[str, object]:
    """Convert a standardized mean difference to an NNT.

    Kraemer & Kupfer (2006): NNT = 1 / (2*Phi(d/sqrt(2)) - 1)  (no control rate needed; the
      probability that a random treated patient does better than a random control patient).
    Furukawa & Leucht (2011): with control-group responder rate CER,
      EER = Phi(d + Phi^-1(CER)); NNT = 1 / (EER - CER).
    d > 0 must mean the treatment is better.
    """
    if d == 0:
        raise ValueError("d must be non-zero")
    auc = norm_cdf(d / math.sqrt(2))
    out = {
        "d": d,
        "probability_of_superiority": auc,
        "nnt_kraemer": 1 / (2 * auc - 1),
    }
    if cer is not None:
        if not 0 < cer < 1:
            raise ValueError("cer must be between 0 and 1")
        eer = norm_cdf(d + norm_ppf(cer))
        out["control_response_rate"] = cer
        out["implied_treatment_response_rate"] = eer
        out["nnt_furukawa"] = 1 / (eer - cer)
    out["assumptions"] = ("Normally distributed outcomes with equal variances. The Furukawa NNT depends heavily on the "
                          "control response rate; use the rate from the trial or a relevant population. "
                          "Positive d must mean benefit; flip the sign of a MADRS reduction first.")
    return out
