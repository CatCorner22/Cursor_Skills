#!/usr/bin/env python3
"""Citation and study-quality appraisal helpers (standard library only).

Subcommands
  worksheet  Parse citations (one per line, or a CSV with a "citation" column and
             optional "claim" column), extract DOI / PMID / PMCID / NCT / arXiv IDs,
             flag preprint servers, and print a worksheet with lookup URLs to fetch.
  rob2       Overall RoB 2 judgement from the five domain judgements.
  robins-i   Overall ROBINS-I (2016) judgement from the seven domain judgements.
  amstar2    AMSTAR 2 overall confidence from critical flaws and other weaknesses.
  grade      GRADE certainty for a body of evidence from start level and ratings.

The judgement rules follow the published tools:
  RoB 2: Sterne et al., BMJ 2019;366:l4898 (overall: low only if all domains low;
         high if any domain high, or several "some concerns" that substantially
         lower confidence; otherwise some concerns).
  ROBINS-I: Sterne et al., BMJ 2016;355:i4919, Table 2 (version 2 was released in
         2025 with revised algorithms; check which version a review used).
  AMSTAR 2: Shea et al., BMJ 2017;358:j4008 (critical items 2, 4, 7, 9, 11, 13, 15).
  GRADE: Guyatt et al., BMJ 2008;336:924-926 and the GRADE guideline series.
The tools are aids to judgement. Each prints the rule it applied so a reader can
check it; none replaces reading the study.
"""
import argparse
import csv
import io
import json
import re
import sys
import urllib.parse

# ---------------------------------------------------------------- identifiers
DOI_RE = re.compile(r"\b(10\.\d{4,9}/[^\s\"<>]+)", re.I)
PMID_RE = re.compile(r"\bPMID:?\s*(\d{1,9})\b", re.I)
PMCID_RE = re.compile(r"\b(PMC\d{4,9})\b", re.I)
NCT_RE = re.compile(r"\b(NCT\d{8})\b", re.I)
REF_HEADING_RE = re.compile(r"^#{0,6}\s*\**\s*(references|bibliography|works cited|sources)\b", re.I)
REF_NUMBER_RE = re.compile(r"^(\[\d+\]|\d+[.)])\s*")
ARXIV_RE = re.compile(r"\barXiv:\s*(\d{4}\.\d{4,5}(?:v\d+)?)\b", re.I)

# DOI prefixes registered by preprint servers. A preprint has not been peer reviewed;
# look for a later published version before relying on it.
PREPRINT_PREFIXES = {
    "10.1101": "bioRxiv or medRxiv (check the DOI suffix and the server page)",
    "10.31234": "PsyArXiv (OSF)",
    "10.31219": "OSF Preprints",
    "10.2139": "SSRN",
    "10.21203": "Research Square",
    "10.20944": "Preprints.org",
    "10.48550": "arXiv",
    "10.22541": "Authorea",
    "10.36227": "TechRxiv",
}


def _clean_doi(doi):
    """Strip trailing punctuation that regexes pick up from prose.

    A closing parenthesis is kept when the DOI itself opened one, as in
    10.1016/S2215-0366(25)00187-4 or a DOI that ends in ")".
    """
    doi = doi.strip()
    while doi and doi[-1] in ".,;]}'\"" or (doi.endswith(")") and doi.count(")") > doi.count("(")):
        doi = doi[:-1]
    return doi


def parse_identifiers(text):
    """Return a dict of identifiers found in one citation string."""
    ids = {}
    m = DOI_RE.search(text)
    if m:
        ids["doi"] = _clean_doi(m.group(1))
    m = PMID_RE.search(text)
    if m:
        ids["pmid"] = m.group(1)
    m = PMCID_RE.search(text)
    if m:
        ids["pmcid"] = m.group(1).upper()
    m = NCT_RE.search(text)
    if m:
        ids["nct"] = m.group(1).upper()
    m = ARXIV_RE.search(text)
    if m:
        ids["arxiv"] = m.group(1)
    return ids


def lookup_urls(ids):
    """URLs to fetch (with the WebFetch tool, not the shell) for each identifier."""
    urls = {}
    if "doi" in ids:
        q = urllib.parse.quote(ids["doi"], safe="/():;")
        urls["crossref"] = f"https://api.crossref.org/works/{q}"
        urls["doi_landing"] = f"https://doi.org/{q}"
    if "pmid" in ids:
        urls["pubmed"] = f"https://pubmed.ncbi.nlm.nih.gov/{ids['pmid']}/"
    if "pmcid" in ids:
        urls["pmc"] = f"https://pmc.ncbi.nlm.nih.gov/articles/{ids['pmcid']}/"
    if "nct" in ids:
        urls["registry"] = f"https://clinicaltrials.gov/study/{ids['nct']}"
    if "arxiv" in ids:
        urls["arxiv"] = f"https://arxiv.org/abs/{ids['arxiv']}"
    return urls


def preprint_flag(ids):
    if "arxiv" in ids:
        return "arXiv preprint"
    doi = ids.get("doi", "")
    for prefix, name in PREPRINT_PREFIXES.items():
        if doi.lower().startswith(prefix + "/"):
            return name
    return ""


def read_rows(path):
    """Read citations from a CSV (with a 'citation' column) or plain text."""
    text = sys.stdin.read() if path == "-" else open(path, encoding="utf-8").read()
    first = text.lstrip().splitlines()[0] if text.strip() else ""
    if "citation" in first.lower() and "," in first:
        reader = csv.DictReader(io.StringIO(text))
        rows = []
        for r in reader:
            low = {k.strip().lower(): (v or "").strip() for k, v in r.items() if k}
            if low.get("citation"):
                rows.append({"claim": low.get("claim", ""), "citation": low["citation"]})
        return rows
    lines = text.splitlines()
    # A whole document: keep only the reference list after a References heading.
    for i, ln in enumerate(lines):
        if REF_HEADING_RE.match(ln.strip()):
            lines = lines[i + 1:]
            break
    rows = []
    for ln in lines:
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        ln = REF_NUMBER_RE.sub("", ln)
        rows.append({"claim": "", "citation": ln})
    return rows


def cmd_worksheet(a):
    rows = read_rows(a.file)
    out = []
    for i, r in enumerate(rows, 1):
        ids = parse_identifiers(r["citation"])
        out.append({
            "n": i,
            "claim": r["claim"],
            "citation": r["citation"],
            "identifiers": ids,
            "lookup_urls": lookup_urls(ids),
            "preprint": preprint_flag(ids),
            "no_identifier": not ids,
        })
    if a.json:
        print(json.dumps(out, indent=2))
        return 0
    print("# Citation worksheet")
    print()
    print("Fetch each lookup URL with WebFetch (the shell cannot reach these sites).")
    print("From Crossref, record the title, authors, journal, year, and any 'updated-by'")
    print("entries (type retraction, correction, or expression_of_concern; source may be")
    print("'publisher' or 'retraction-watch'). Then fill the blank columns.")
    print()
    print("| # | Claim | Citation | IDs | Preprint? | Exists and matches? | Status | Supports claim? | Design | Tool and rating | Certainty |")
    print("|---|---|---|---|---|---|---|---|---|---|---|")
    for o in out:
        ids = "; ".join(f"{k}:{v}" for k, v in o["identifiers"].items()) or "NONE: search by title"
        pre = o["preprint"] or "no"
        cit = o["citation"].replace("|", "/")
        claim = o["claim"].replace("|", "/")
        print(f"| {o['n']} | {claim} | {cit} | {ids} | {pre} |  |  |  |  |  |  |")
    print()
    for o in out:
        if o["lookup_urls"]:
            print(f"{o['n']}. " + "  ".join(f"{k}: {u}" for k, u in o["lookup_urls"].items()))
        else:
            print(f"{o['n']}. no identifier: search Crossref with "
                  "https://api.crossref.org/works?query.bibliographic=<title words>&rows=5")
    flagged = [o["n"] for o in out if o["preprint"]]
    missing = [o["n"] for o in out if o["no_identifier"]]
    print()
    print(f"summary: {len(out)} citations; preprints: {flagged or 'none'}; "
          f"without an identifier: {missing or 'none'}")
    return 0


# ---------------------------------------------------------------- RoB 2
ROB2_LEVELS = ("low", "some", "high")


def rob2_overall(domains, several_some_lower_confidence=False):
    """domains: list of five values from ROB2_LEVELS."""
    if len(domains) != 5 or any(d not in ROB2_LEVELS for d in domains):
        raise ValueError("RoB 2 needs five domain judgements: low, some, or high")
    n_some = domains.count("some")
    if "high" in domains:
        return "high", "at least one domain is high risk"
    if n_some == 0:
        return "low", "all five domains are low risk"
    if n_some >= 2 and several_some_lower_confidence:
        return "high", (f"{n_some} domains raise some concerns and the assessor judged that "
                        "together they substantially lower confidence in the result")
    note = "at least one domain raises some concerns and none is high"
    if n_some >= 2:
        note += (f"; {n_some} domains raise some concerns: RoB 2 allows 'high' if together they "
                 "substantially lower confidence (re-run with --several-some-lower-confidence "
                 "if you judge so, and say why)")
    return "some concerns", note


def cmd_rob2(a):
    doms = [a.d1, a.d2, a.d3, a.d4, a.d5]
    overall, rule = rob2_overall(doms, a.several_some_lower_confidence)
    names = ["D1 randomization process", "D2 deviations from intended interventions",
             "D3 missing outcome data", "D4 measurement of the outcome",
             "D5 selection of the reported result"]
    for n, d in zip(names, doms):
        print(f"{n}: {d}")
    print(f"overall: {overall}")
    print(f"rule_applied: {rule}")
    print("note: RoB 2 rates one result (outcome and time point), not the whole trial.")
    return 0


# ---------------------------------------------------------------- ROBINS-I (2016)
ROBINS_LEVELS = ("low", "moderate", "serious", "critical", "ni")


def robins_overall(domains, ni_in_key_domain=None):
    """ROBINS-I 2016 Table 2. domains: seven values from ROBINS_LEVELS."""
    if len(domains) != 7 or any(d not in ROBINS_LEVELS for d in domains):
        raise ValueError("ROBINS-I needs seven domain judgements: low, moderate, serious, critical, ni")
    if "critical" in domains:
        return "critical", "critical risk of bias in at least one domain"
    if "serious" in domains:
        return "serious", "serious risk in at least one domain and critical in none"
    if "ni" in domains:
        key = ni_in_key_domain if ni_in_key_domain is not None else True
        if key:
            return "no information", ("no clear indication of serious or critical risk, but no "
                                      "information in one or more key domains (a judgement is required)")
        rest = [d for d in domains if d != "ni"]
        lvl = "low" if all(d == "low" for d in rest) else "moderate"
        return lvl, ("no information only in domains the assessor judged not key; rated on the "
                     "remaining domains (state this judgement)")
    if all(d == "low" for d in domains):
        return "low", "low risk in all domains (comparable to a well-performed randomized trial)"
    return "moderate", "low or moderate risk in all domains"


def cmd_robins(a):
    doms = [a.d1, a.d2, a.d3, a.d4, a.d5, a.d6, a.d7]
    key = None if a.ni_key is None else (a.ni_key == "yes")
    overall, rule = robins_overall(doms, key)
    names = ["D1 confounding", "D2 selection of participants", "D3 classification of interventions",
             "D4 deviations from intended interventions", "D5 missing data",
             "D6 measurement of outcomes", "D7 selection of the reported result"]
    for n, d in zip(names, doms):
        print(f"{n}: {d}")
    print(f"overall: {overall}")
    print(f"rule_applied: {rule}")
    print("note: these are the 2016 rules. ROBINS-I version 2 (2025) adds algorithms and "
          "immortal-time bias; say which version you applied.")
    return 0


# ---------------------------------------------------------------- AMSTAR 2
AMSTAR_CRITICAL = (2, 4, 7, 9, 11, 13, 15)


def amstar_overall(critical_flaws, noncritical_weaknesses):
    if critical_flaws < 0 or noncritical_weaknesses < 0:
        raise ValueError("counts cannot be negative")
    if critical_flaws > 1:
        return "critically low", "more than one critical flaw"
    if critical_flaws == 1:
        return "low", "one critical flaw, with or without non-critical weaknesses"
    if noncritical_weaknesses > 1:
        return "moderate", ("no critical flaw and more than one non-critical weakness (AMSTAR 2 notes "
                            "that many non-critical weaknesses may justify moving down to low)")
    return "high", "no critical flaw and at most one non-critical weakness"


def cmd_amstar(a):
    crit = nonc = 0
    detail = []
    if a.failed_items:
        items = sorted({int(x) for x in a.failed_items})
        bad = [i for i in items if not 1 <= i <= 16]
        if bad:
            print(f"error: AMSTAR 2 items run 1-16; got {bad}", file=sys.stderr)
            return 2
        crit = sum(1 for i in items if i in AMSTAR_CRITICAL)
        nonc = len(items) - crit
        detail = [f"item {i} ({'critical' if i in AMSTAR_CRITICAL else 'non-critical'})" for i in items]
    else:
        crit, nonc = a.critical_flaws, a.noncritical_weaknesses
    overall, rule = amstar_overall(crit, nonc)
    if detail:
        print("failed_items: " + ", ".join(detail))
    print(f"critical_flaws: {crit}")
    print(f"noncritical_weaknesses: {nonc}")
    print(f"overall_confidence: {overall}")
    print(f"rule_applied: {rule}")
    print("critical_items: 2 protocol registered before the review; 4 comprehensive search; "
          "7 list and justify excluded studies; 9 risk-of-bias assessment of included studies; "
          "11 appropriate meta-analysis methods; 13 risk of bias considered when interpreting "
          "results; 15 publication bias investigated (Shea et al. 2017; users may justify a "
          "different critical set)")
    return 0


# ---------------------------------------------------------------- GRADE
GRADE_LEVELS = ["very low", "low", "moderate", "high"]


def grade_certainty(start, down, up):
    """start: 'high' (randomized) or 'low' (non-randomized). down/up: dicts of levels."""
    level = 3 if start == "high" else 1
    total_down = sum(down.values())
    total_up = sum(up.values())
    notes = []
    if total_up and start == "high":
        notes.append("rating up is normally used for non-randomized evidence; for randomized "
                     "evidence it is rarely appropriate: justify it")
    if total_up and total_down:
        notes.append("rating up is normally considered only when no domain has been rated down; "
                     "justify combining both")
    final = max(0, min(3, level - total_down + total_up))
    return GRADE_LEVELS[final], total_down, total_up, notes


def cmd_grade(a):
    down = {"risk_of_bias": a.risk_of_bias, "inconsistency": a.inconsistency,
            "indirectness": a.indirectness, "imprecision": a.imprecision,
            "publication_bias": a.publication_bias}
    up = {"large_effect": a.large_effect, "dose_response": a.dose_response,
          "opposing_confounding": a.opposing_confounding}
    for k, v in {**down, **up}.items():
        lim = 2 if k in down or k == "large_effect" else 1
        if not 0 <= v <= lim:
            print(f"error: {k} must be between 0 and {lim}", file=sys.stderr)
            return 2
    level, d, u, notes = grade_certainty(a.start, down, up)
    print(f"start: {a.start} ({'randomized trials' if a.start == 'high' else 'non-randomized studies'})")
    print("rated_down: " + ", ".join(f"{k} -{v}" for k, v in down.items() if v) if d else "rated_down: none")
    print("rated_up: " + ", ".join(f"{k} +{v}" for k, v in up.items() if v) if u else "rated_up: none")
    print(f"certainty: {level}")
    for n in notes:
        print(f"note: {n}")
    print("meaning: high = further research very unlikely to change confidence in the estimate; "
          "moderate = likely to have an important impact; low = very likely to; very low = any "
          "estimate is very uncertain")
    return 0


# ---------------------------------------------------------------- CLI
def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    s = p.add_subparsers(dest="cmd", required=True)

    w = s.add_parser("worksheet", help="build a citation worksheet with lookup URLs")
    w.add_argument("file", help="text file (one citation per line), CSV with a 'citation' column, or - for stdin")
    w.add_argument("--json", action="store_true")
    w.set_defaults(fn=cmd_worksheet)

    r = s.add_parser("rob2", help="overall RoB 2 judgement")
    for i in range(1, 6):
        r.add_argument(f"--d{i}", required=True, choices=ROB2_LEVELS)
    r.add_argument("--several-some-lower-confidence", action="store_true",
                   help="assessor judges that several 'some concerns' substantially lower confidence")
    r.set_defaults(fn=cmd_rob2)

    ri = s.add_parser("robins-i", help="overall ROBINS-I (2016) judgement")
    for i in range(1, 8):
        ri.add_argument(f"--d{i}", required=True, choices=ROBINS_LEVELS)
    ri.add_argument("--ni-key", choices=("yes", "no"),
                    help="is a domain with no information a key domain? (default: yes)")
    ri.set_defaults(fn=cmd_robins)

    am = s.add_parser("amstar2", help="AMSTAR 2 overall confidence")
    am.add_argument("--failed-items", nargs="+", help="item numbers (1-16) answered 'no'")
    am.add_argument("--critical-flaws", type=int, default=0)
    am.add_argument("--noncritical-weaknesses", type=int, default=0)
    am.set_defaults(fn=cmd_amstar)

    g = s.add_parser("grade", help="GRADE certainty for a body of evidence")
    g.add_argument("--start", required=True, choices=("high", "low"),
                   help="high for randomized trials, low for non-randomized studies")
    for name in ("risk-of-bias", "inconsistency", "indirectness", "imprecision", "publication-bias"):
        g.add_argument(f"--{name}", type=int, default=0, help="levels rated down (0-2)")
    g.add_argument("--large-effect", type=int, default=0, help="levels rated up (0-2)")
    g.add_argument("--dose-response", type=int, default=0, help="levels rated up (0-1)")
    g.add_argument("--opposing-confounding", type=int, default=0,
                   help="rate up 1 if all plausible confounding would reduce the effect (0-1)")
    g.set_defaults(fn=cmd_grade)

    a = p.parse_args(argv)
    try:
        return a.fn(a)
    except (ValueError, OSError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
