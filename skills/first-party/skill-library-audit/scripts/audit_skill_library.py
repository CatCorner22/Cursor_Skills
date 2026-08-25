#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
audit_skill_library.py — a static analyzer for Cursor/Claude-style skill libraries.

WHY THIS IS NOT A LINTER
========================
A skill library is two things at once:

  1. A ROUTING TABLE.   Every `chainTo` / `upgradeToSkill` / `targetSkill` edge is a
     forwarding rule. Rules can shadow each other, loop, dangle, or point at self.
  2. A RETRIEVAL INDEX. Every `description` / `promptSignals` block is a document in
     an inverted index that a model queries with the user's prompt.

So the right tooling borrows from four disciplines rather than from style checking:

  (a) INFORMATION RETRIEVAL. A description term's value as a trigger is inversely
      proportional to how many skills use it — that is exactly IDF. "test", "build",
      "agent", "api", "deploy" in 20/89 descriptions carry near-zero discriminative
      power; "@cursor/sdk" or "ZeroGPU" in 1/89 carry maximal power. This turns
      "that description is too greedy" from a vibe into a computable score.

  (b) STATIC ANALYSIS / COMPILERS. Dead-guard detection is unreachable-code analysis.
      Rule shadowing is overlapping case-label analysis: if match-set(A) contains
      match-set(B), A shadows B. A self-route is a no-op. chainTo cycles are call-graph
      cycles. Dangling targets are unresolved symbols. Key-placement outliers are type
      errors against an inferred schema.

  (c) NETWORK ROUTING (BGP / longest-prefix match). A well-formed routing table prefers
      the MOST SPECIFIC match. Skill libraries have no such tie-break, so a generic and
      a specific rule both "win" and the winner is whichever the model happened to read.
      We therefore report specificity inversions and ambiguous overlaps explicitly.

  (d) DIAGNOSTIC TEST THEORY / BAYES. A trigger is a diagnostic test for "is this skill
      the right one for this prompt?". With N skills the prior that any given skill is
      correct is ~1/N. At N=89 that is ~1.1%. A trigger with 90% sensitivity and 95%
      specificity yields a posterior of only ~17% — five of six firings are wrong. That
      is the quantitative reason greedy descriptions are catastrophic *specifically at
      scale*, and it is why we score greediness against library size rather than against
      a fixed word count. The report prints this computation for the actual N.

DETECTOR INVENTORY — EXACT vs HEURISTIC
=======================================
EXACT — decidable from the files alone; a finding is a fact, and a false positive is a
bug in this program rather than a judgement call:

  SK001  invalid or missing YAML frontmatter (also a broken overlay.yaml)
  SK002  duplicate skill `name:` values
  SK004  SKILL.md <-> overlay.yaml drift: conflicting values, differing rule counts, or
         a routing block present in one copy and absent from the other
  SK005  dangling chainTo/targetSkill/upgradeToSkill reference (closed-world: assumes
         this root is the whole library)
  SK006  self-referencing route (no-op edge)
  SK007  chainTo cycle (graph cycle detection)
  SK013  unreachable rule: a PURE-LITERAL skipIfFileContains alternative sits inside a
         literal that every branch of the rule's own pattern requires, so the guard
         fires on 100% of matches. Restricted to pure literals precisely so the claim
         stays a proof — see detect_dead_guards for why the set-subset version was not.

HEURISTIC — inference from an inferred schema, literal-substring reasoning, or a curated
lexicon. Each is a strong prior that a human must confirm, and each finding carries the
evidence that produced it:

  SK003  schema-outlier key placement (majority-vote schema inference; the report gives
         the majority/minority counts so the reader can judge the strength)
  SK008  greedy description: universal-quantifier clauses with no distinguishing anchor,
         scored by IDF over identifier-shaped terms and by collision set size
  SK009  cross-pack territory claim (pack ownership inferred from directory/skill names)
  SK010  overlapping / shadowing rules (regex literal-core containment; the broad side
         must be non-lossy or the containment argument is unsound)
  SK011  guard alternative naming a package or skill the library never mentions outside
         a guard. HIGH only on a wrong-scope near-miss (the typo signal); otherwise
         MEDIUM and explicitly labelled unverifiable — there is no registry access here
  SK012  vendor steering: a rule matching another vendor's package whose message pitches
         a product the pattern does not name. The novel class; always flagged for review
  SK014  dangling prose reference to a skill that does not exist
  SK015  unscoped skill (short description, no scoping metadata at all)
  SK016  priority inversion across a chainTo edge

PRECISION: WHAT A RED-TEAM PASS CHANGED
=======================================
An auditor that cries wolf is worse than none, because it teaches its readers to skip the
report. A false-positive pass over a real 89-skill, 9-pack library cut 152 findings to 20
(87% of the output was noise) while every ground-truth defect class still fires when
re-injected. The suppressions are recorded at each detector; the pattern behind them is
worth stating once:

  * DISTINGUISH A HOUSE IDIOM FROM A BUG BY PREVALENCE, NOT BY SHAPE. 56 self-routes in
    9 skills is a convention with no other spelling available; one self-route in a library
    that never does it is a slip. Same syntax, opposite verdict. (SK006)
  * A DETECTOR THAT FLAGS EITHER HALF OF THE GRAPH MEASURES NOTHING. SK016 fired on 19
    chainTo edges; inverting its comparison fired on 18. Neither was a defect — `chainTo`
    is unconditional, so priority never suppresses it. It was rebuilt around the shape the
    library's own review recorded.
  * ABSENCE OF METADATA IS NOT EVIDENCE WHEN 73% OF THE LIBRARY OMITS IT. SK015 now needs
    a demonstrated cross-pack rival, which is what made the recorded case a defect.
  * COLLISION MEANS A RIVAL FOR THE WHOLE CLAIM, NOT A SHARED WORD. Requiring the full
    anchor conjunction — and subtracting nested children, shared-prefix sub-families, and
    skills already named in a hand-written scope boundary — is what separates "hijacks
    every Python task" from "six SageMaker skills all say SageMaker". (SK008, SK015)
  * ROUTERS, UMBRELLAS AND CATALOGUE RULES ARE SUPPOSED TO BE BROAD. A dispatch rule
    enumerating every database package subsumes each storage specialist by design. (SK010)
  * RANK BY WHAT THE LIBRARY ITSELF COMMITTED TO. Vendor steering is a live defect when a
    pack exists for the product being steered away from, a contradiction when the rule's
    own destination supports it, and ordinary first-party promotion otherwise. (SK012)
  * A NEAR-MISS NEEDS A SHARED TAIL, NOT A SHARED PREFIX. `@vercel/auth` -> `@vercel/kv`
    is edit distance over an npm scope and proves nothing; `@vercel/ai-gateway` against
    the `@ai-sdk/gateway` this library uses is the same name in the wrong scope. (SK011)

KNOWN LIMITS (stated because a detector that hides its blind spots is worse than none):
  * SK012 depends on PRODUCT_ALIASES and STEERING_CUES, two hand-written tables. A vendor
    absent from the first, or a pitch phrased outside the second, is invisible to it.
    "Is X a competitor of Y" is world knowledge, not file structure. MAINTENANCE RULE:
    vendoring a pack means adding its product to PRODUCT_ALIASES in the same change —
    otherwise the rules that steer against the pack you just adopted stay unreadable to
    this detector, which is exactly how the ai-sdk -> LangChain steer survived review.
  * SK011 cannot tell a typo from a package this library simply never discusses.
  * SK010's literal extraction ignores anchors, lookarounds and character classes, so a
    flagged pair can still be disjoint in practice.
  * SK008 reads prose with a bag-of-anchors model; a long precise description can score
    badly for stylistic reasons. It is triage, not a gate.
  * SK003 assumes the majority placement is the correct one. In a library where the
    majority is wrong, it will confidently accuse the one correct skill.
  * The anchor index carries only identifier-shaped tokens, so an ordinary domain noun
    that genuinely discriminates ("trace", "commits") is invisible to it. That is why IDF
    now only SCORES an over-claim and no longer generates one: the failure mode of the
    missing vocabulary must be a missed finding, never an accusation.
  * SK006's idiom test needs a library big enough to have conventions. In a 3-skill
    library two self-routes read as a slip; that is the intended reading, but it means the
    same file can be judged differently depending on what it ships alongside.

Stdlib + PyYAML only. No network. Exit 0 iff no findings at/above --min-severity.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
from collections import Counter, defaultdict

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.stderr.write("audit_skill_library.py requires PyYAML (pip install pyyaml)\n")
    sys.exit(2)


# --------------------------------------------------------------------------------------
# Severity
# --------------------------------------------------------------------------------------

SEVERITY_ORDER = {"low": 0, "medium": 1, "high": 2}
SEV_LABEL = {"high": "HIGH", "medium": "MEDIUM", "low": "LOW"}


# --------------------------------------------------------------------------------------
# Lexicons
#
# These are the only hand-curated inputs in the analyzer. Everything else is derived from
# the library itself. They exist because "is Clerk a competitor of Supabase?" is not
# derivable from file structure — it is world knowledge. Findings that depend on this
# table are marked heuristic and flagged for human review.
# --------------------------------------------------------------------------------------

# product token -> literal substrings that name it (all lowercase)
PRODUCT_ALIASES = {
    "supabase": ["supabase", "@supabase/"],
    "firebase": ["firebase"],
    "clerk": ["clerk", "@clerk/"],
    "auth0": ["auth0", "@auth0/"],
    "descope": ["descope", "@descope/"],
    "workos": ["workos"],
    "stytch": ["stytch"],
    "kinde": ["kinde"],
    "better-auth": ["better-auth"],
    "nextauth": ["next-auth", "nextauth"],
    "lucia": ["lucia-auth"],
    "neon": ["neon", "@neondatabase/"],
    "upstash": ["upstash", "@upstash/"],
    "planetscale": ["planetscale"],
    "mongodb": ["mongodb", "mongoose"],
    "convex": ["convex"],
    "turso": ["turso", "@libsql/"],
    "prisma": ["prisma", "@prisma/"],
    "drizzle": ["drizzle", "drizzle-orm"],
    "vercel": ["vercel", "@vercel/"],
    "netlify": ["netlify"],
    "cloudflare": ["cloudflare", "wrangler"],
    "railway": ["railway"],
    "render": ["render.com"],
    "fly": ["fly.io"],
    "heroku": ["heroku"],
    "aws": ["aws", "sagemaker", "boto3"],
    "gcp": ["google cloud", "gcp"],
    "azure": ["azure"],
    "openai": ["openai", "@ai-sdk/openai"],
    "anthropic": ["anthropic", "@anthropic-ai/"],
    "google-ai": ["gemini", "@ai-sdk/google"],
    "huggingface": ["huggingface", "hugging face", "@huggingface/"],
    "replicate": ["replicate"],
    "modal": ["modal.com"],
    "langchain": ["langchain", "@langchain/", "langgraph", "deepagents"],
    "llamaindex": ["llamaindex", "llama-index"],
    "pinecone": ["pinecone"],
    "weaviate": ["weaviate"],
    "qdrant": ["qdrant"],
    "chroma": ["chromadb"],
    "playwright": ["playwright"],
    "cypress": ["cypress"],
    "adobe": ["adobe", "app builder", "appbuilder"],
    "cursor": ["cursor"],
    "stripe": ["stripe"],
    "sentry": ["sentry"],
    "datadog": ["datadog"],
}

# Cue words that turn "the message mentions product X" into "the message PITCHES X".
STEERING_CUES = [
    "instead",
    # Capability-parity pitches. A migration argument does not have to say "migrate":
    # "X provides equivalent capabilities … smaller bundle" is the same steer in
    # comparative clothing. Added after the ai-sdk -> LangChain rule evaded every cue
    # above while being the textbook instance of the class.
    "equivalent",
    "drop-in",
    "replacement",
    "smaller bundle",
    "alternative",
    "alternatives",
    "recommended",
    "recommend",
    "prefer",
    "preferred",
    "migrate",
    "migration",
    "switch to",
    "rather than",
    "marketplace-native",
    "one-click",
    "unified billing",
    "use the",
    "should use",
]

# Universal-quantifier claims: a description clause that claims an unbounded activation
# domain. These are the textual half of the greediness signal; the IDF half is computed.
QUANTIFIER_PATTERNS = [
    (r"\b(any|all|every)\s+(kind\s+of\s+|sort\s+of\s+)?(task|work|thing|code|project|file|request|question|operation)s?\b", 3.0),
    (r"\bANY\b", 2.5),  # literal shouty ANY, e.g. "ANY task involving Supabase"
    (r"\balways\s+(use|load|apply|invoke)\b", 2.0),
    (r"\bwhenever\b", 1.0),
    (r"\bevery\s+time\b", 1.5),
    (r"\bany\s+time\b", 1.5),
    (r"\bin\s+all\s+cases\b", 1.5),
    (r"\bproactively\b", 0.5),
]

STOPWORDS = set("""
a an and are as at be been but by can could do does doing for from had has have he her his
how i if in into is it its me more most no nor not of on once only or other our out over own
same she should so some such than that the their them then there these they this those to too
under until up use used uses using very was we were what when where which while who whom why
will with would you your yours skill skills claude cursor
""".split())


# --------------------------------------------------------------------------------------
# Frontmatter loading with line tracking
# --------------------------------------------------------------------------------------

FRONTMATTER_RE = re.compile(r"^---[ \t]*\r?\n(.*?)\r?\n---[ \t]*\r?\n", re.S)


def build_line_map(node, path, out, offset):
    """Walk a composed YAML node tree recording 1-based source lines per key path.

    `offset` is the number of file lines that precede the first line of the YAML
    document (1 for a SKILL.md whose line 1 is the opening `---`, 0 for overlay.yaml).
    """
    if isinstance(node, yaml.MappingNode):
        for key_node, value_node in node.value:
            key = key_node.value
            p = path + (key,)
            out[p] = key_node.start_mark.line + 1 + offset
            build_line_map(value_node, p, out, offset)
    elif isinstance(node, yaml.SequenceNode):
        for i, item in enumerate(node.value):
            p = path + (i,)
            out[p] = item.start_mark.line + 1 + offset
            build_line_map(item, p, out, offset)


class YamlDoc:
    """A parsed YAML document plus a key-path -> line map. Never raises on bad YAML."""

    def __init__(self, path, text, yaml_text, offset):
        self.path = path
        self.text = text
        self.yaml_text = yaml_text
        self.offset = offset
        self.data = None
        self.error = None
        self.error_line = None
        self.lines = {}
        if yaml_text is None:
            return
        try:
            self.data = yaml.safe_load(yaml_text)
        except yaml.YAMLError as exc:
            self.error = _yaml_error_message(exc)
            self.error_line = _yaml_error_line(exc, offset)
            return
        except Exception as exc:  # defensive: never crash the audit on one bad file
            self.error = "%s: %s" % (type(exc).__name__, exc)
            return
        try:
            node = yaml.compose(yaml_text)
            if node is not None:
                build_line_map(node, (), self.lines, offset)
        except Exception:
            pass  # line map is best-effort; findings degrade to file-level

    def line_for(self, path):
        """Line for the longest known prefix of `path`, else None.

        List indices are stored as ints by the composer but arrive as strings from the
        flattened diff paths, so digit-like elements are coerced before lookup.
        """
        p = tuple(int(e) if isinstance(e, str) and e.isdigit() else e for e in path)
        while p:
            if p in self.lines:
                return self.lines[p]
            p = p[:-1]
        return self.lines.get((), None)


def _yaml_error_message(exc):
    problem = getattr(exc, "problem", None) or str(exc).splitlines()[0]
    context = getattr(exc, "context", None)
    return ("%s %s" % (context, problem)).strip() if context else str(problem).strip()


def _yaml_error_line(exc, offset):
    mark = getattr(exc, "problem_mark", None) or getattr(exc, "context_mark", None)
    return mark.line + 1 + offset if mark is not None else None


def load_skill_md(path):
    try:
        text = open(path, encoding="utf-8", errors="replace").read()
    except OSError as exc:
        doc = YamlDoc(path, "", None, 0)
        doc.error = "unreadable file: %s" % exc
        return doc, ""
    match = FRONTMATTER_RE.match(text)
    if not match:
        doc = YamlDoc(path, text, None, 0)
        if text.lstrip().startswith("---"):
            doc.error = "frontmatter opened with '---' but never terminated"
        else:
            doc.error = "no YAML frontmatter block at top of file"
        return doc, text
    body = text[match.end():]
    return YamlDoc(path, text, match.group(1), 1), body


def load_overlay(path):
    try:
        text = open(path, encoding="utf-8", errors="replace").read()
    except OSError as exc:
        doc = YamlDoc(path, "", None, 0)
        doc.error = "unreadable file: %s" % exc
        return doc
    return YamlDoc(path, text, text, 0)


# --------------------------------------------------------------------------------------
# Regex literal-core extraction
#
# Compilers reason about case-label overlap by comparing constant sets. We approximate
# that for regexes: for each top-level alternation branch we extract the literal runs
# that ANY matching text must contain. This is sound for the shapes that actually appear
# in skill routing rules (`from ['"]@scope/pkg['"]`, bare substrings, simple groups) and
# deliberately conservative elsewhere — when in doubt we extract nothing, which makes the
# detectors miss rather than false-alarm.
# --------------------------------------------------------------------------------------

ESCAPE_LITERALS = {
    "n": "\n", "t": "\t", "r": "\r",
    ".": ".", "*": "*", "+": "+", "?": "?", "(": "(", ")": ")",
    "[": "[", "]": "]", "{": "{", "}": "}", "|": "|", "\\": "\\",
    "^": "^", "$": "$", "/": "/", "-": "-", "@": "@", "'": "'", '"': '"',
}


def _split_top_level_alternation(pattern):
    """Split on `|` that is not inside a group or character class."""
    parts, depth, in_class, buf, i = [], 0, False, [], 0
    while i < len(pattern):
        ch = pattern[i]
        if ch == "\\" and i + 1 < len(pattern):
            buf.append(pattern[i:i + 2])
            i += 2
            continue
        if in_class:
            if ch == "]":
                in_class = False
            buf.append(ch)
        elif ch == "[":
            in_class = True
            buf.append(ch)
        elif ch == "(":
            depth += 1
            buf.append(ch)
        elif ch == ")":
            depth -= 1
            buf.append(ch)
        elif ch == "|" and depth == 0:
            parts.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
        i += 1
    parts.append("".join(buf))
    return [p for p in parts if p.strip()]


def _find_group_end(pattern, start):
    depth, in_class, i = 0, False, start
    while i < len(pattern):
        ch = pattern[i]
        if ch == "\\":
            i += 2
            continue
        if in_class:
            if ch == "]":
                in_class = False
        elif ch == "[":
            in_class = True
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return -1


def _common_prefix(strings):
    if not strings:
        return ""
    prefix = strings[0]
    for s in strings[1:]:
        while not s.startswith(prefix):
            prefix = prefix[:-1]
            if not prefix:
                return ""
    return prefix


def _skip_quantifier(branch, i):
    """Advance past a quantifier (`?`, `*`, `+`, `{m,n}`) and a lazy `?` marker."""
    n = len(branch)
    if i < n and branch[i] in "?*+":
        i += 1
    elif i < n and branch[i] == "{":
        close = branch.find("}", i)
        i = (close + 1) if close != -1 else n
    if i < n and branch[i] == "?":
        i += 1
    return i


def _literal_runs(branch):
    """Maximal literal substrings that any text matching this branch must contain."""
    runs, buf, i = [], [], 0
    n = len(branch)

    def flush():
        if buf:
            runs.append("".join(buf))
            del buf[:]

    while i < n:
        ch = branch[i]
        nxt = branch[i + 1] if i + 1 < n else ""
        if ch == "\\":
            esc = nxt
            if esc in ESCAPE_LITERALS:
                # a literal escaped char, unless a quantifier makes it optional
                after = branch[i + 2] if i + 2 < n else ""
                if after and after in "?*":
                    flush()
                    i = _skip_quantifier(branch, i + 2)
                    continue
                buf.append(ESCAPE_LITERALS[esc])
                i += 2
                continue
            flush()  # \s \b \d \w etc. — a class, not a literal
            i = _skip_quantifier(branch, i + 2)
            continue
        if ch == "[":
            flush()
            end = branch.find("]", i + 1)
            if end == i + 1:  # a leading `]` inside the class is literal
                end = branch.find("]", i + 2)
            i = (end + 1) if end != -1 else n
            i = _skip_quantifier(branch, i)
            continue
        if ch == "(":
            end = _find_group_end(branch, i)
            if end == -1:
                flush()
                break
            inner = branch[i + 1:end]
            inner = re.sub(r"^\?(:|=|!|<=|<!|P<[^>]*>)", "", inner)
            quant = branch[end + 1] if end + 1 < n else ""
            alts = _split_top_level_alternation(inner)
            if quant in "?*":
                flush()  # whole group optional
            elif len(alts) > 1:
                # only the shared prefix of the alternatives is guaranteed
                prefixes = [_literal_runs(a) for a in alts]
                heads = [p[0] if p else "" for p in prefixes]
                cp = _common_prefix(heads)
                if cp:
                    buf.append(cp)
                flush()
            else:
                sub = _literal_runs(inner)
                if len(sub) == 1:
                    buf.append(sub[0])
                else:
                    flush()
                    runs.extend(sub)
            i = _skip_quantifier(branch, end + 1)
            continue
        if ch in "^$":
            i += 1
            continue
        if ch == ".":
            flush()
            i = _skip_quantifier(branch, i + 1)
            continue
        if nxt and nxt in "?*":
            # this literal char is optional — it ends the run and is not required
            flush()
            i = _skip_quantifier(branch, i + 1)
            continue
        if nxt == "{":
            close = branch.find("}", i + 1)
            spec = branch[i + 1:close] if close != -1 else ""
            if spec.startswith("0"):
                flush()
            else:
                buf.append(ch)
                flush()
            i = (close + 1) if close != -1 else n
            continue
        if nxt == "+":
            buf.append(ch)
            flush()
            i = _skip_quantifier(branch, i + 1)
            continue
        buf.append(ch)
        i += 1
    flush()
    return [r for r in runs if r.strip()]


def branch_cores(pattern):
    """For each alternation branch, its longest required literal (lowercased).

    Returns [] when nothing useful is extractable — detectors then skip the rule.
    """
    if not isinstance(pattern, str) or not pattern.strip():
        return []
    cores = []
    for branch in _split_top_level_alternation(pattern):
        runs = _literal_runs(branch)
        runs = [r for r in runs if len(r.strip()) >= 3]
        if runs:
            cores.append(max(runs, key=len).strip().lower())
    return cores


LOSSY_RE = re.compile(r"\((?:\?[:=!][^)]*)?[^)]*\|")  # a group containing alternation
WILDCARD_RE = re.compile(r"\\[wdWDS]|(?<!\\)\.")


def branch_is_lossy(branch):
    """True when literal extraction necessarily discarded a real constraint.

    An alternation group or a `.`/`\\w`/`\\d` wildcard means the extracted literals are a
    strict UNDER-approximation of what the branch requires. Detectors that need an
    over-approximation of the match set (SK013's "this guard always fires") must refuse
    to fire on a lossy branch, or they invent findings — e.g. reading
    `export\\s+default\\s+function\\s+\\w*(?:Page|Layout)` as merely requiring
    "export default function", which is strictly weaker than the truth.
    """
    return bool(LOSSY_RE.search(branch) or WILDCARD_RE.search(branch))


PURE_META_RE = re.compile(r"(?<!\\)[\[\]().*+?{}^$|]")
PURE_CLASS_RE = re.compile(r"\\[sdwbSDWBAZzGn t r]")


def pure_literal(branch):
    """The literal string this branch matches, or None if it is not a pure literal.

    "Pure" means the branch contains no regex operators whatsoever once backslash
    escapes of literal characters are resolved — `@vercel/kv` and `embed\\(` qualify,
    `from\\s+['\"]ai['\"]` does not. A pure literal guard is the only kind whose firing
    condition can be reasoned about exactly, which is what SK013 requires.
    """
    if not branch or PURE_META_RE.search(branch) or PURE_CLASS_RE.search(branch):
        return None
    runs = _literal_runs(branch)
    if len(runs) != 1:
        return None
    lit = runs[0].strip().lower()
    return lit if len(lit) >= 3 else None



# --------------------------------------------------------------------------------------
# Model objects
# --------------------------------------------------------------------------------------

class Rule:
    """One chainTo or validate entry."""

    def __init__(self, skill, kind, index, data):
        self.skill = skill
        self.kind = kind  # "chainTo" | "validate"
        self.index = index
        self.data = data if isinstance(data, dict) else {}
        self.pattern = self.data.get("pattern")
        self.message = self.data.get("message") or ""
        self.guard = self.data.get("skipIfFileContains")
        self.target = (
            self.data.get("targetSkill")
            or self.data.get("upgradeToSkill")
            or self.data.get("toSkill")
            or self.data.get("target")
        )
        self.target_key = next(
            (k for k in ("targetSkill", "upgradeToSkill", "toSkill", "target") if k in self.data),
            None,
        )

    @property
    def path(self):
        return (self.kind, self.index)

    def line(self, key=None):
        p = (self.kind, self.index) + ((key,) if key else ())
        return self.skill.doc.line_for(p)

    def label(self):
        return "%s[%d]" % (self.kind, self.index)


class Skill:
    def __init__(self, root, skill_path):
        self.path = skill_path
        self.dir = os.path.dirname(skill_path)
        self.rel = os.path.relpath(skill_path, root)
        parts = self.rel.split(os.sep)
        self.pack = parts[0] if len(parts) > 1 else "<root>"
        self.dirname = os.path.basename(self.dir)
        self.doc, self.body = load_skill_md(skill_path)
        self.fm = self.doc.data if isinstance(self.doc.data, dict) else {}
        self.name = self.fm.get("name") if isinstance(self.fm.get("name"), str) else None
        self.description = self.fm.get("description") if isinstance(self.fm.get("description"), str) else ""
        self.metadata = self.fm.get("metadata") if isinstance(self.fm.get("metadata"), dict) else {}
        self.overlay = None  # YamlDoc
        self.rules = []
        for kind in ("chainTo", "validate"):
            entries = self.fm.get(kind)
            if isinstance(entries, list):
                for i, entry in enumerate(entries):
                    self.rules.append(Rule(self, kind, i, entry))

    @property
    def key(self):
        return self.name or self.dirname

    def acquisition_patterns(self):
        """(field, key_path, value) for the three fields that CLAIM territory.

        pathPatterns / bashPatterns / importPatterns are how a skill says "these files
        and commands are mine". chainTo patterns are deliberately excluded: matching a
        competitor's import in order to hand off is legitimate routing, not a claim.

        The fields normally live under `metadata:` but are read at top level too, so a
        schema outlier is still checked for territory rather than silently skipped.
        """
        out, seen = [], set()
        for field in ("pathPatterns", "bashPatterns", "importPatterns"):
            for base in (("metadata",), ()):
                container = self.metadata if base else self.fm
                values = container.get(field)
                if not isinstance(values, list):
                    continue
                for i, value in enumerate(values):
                    if not isinstance(value, str) or (field, value) in seen:
                        continue
                    seen.add((field, value))
                    out.append((field, base + (field, i), value))
        return out

    def priority(self):
        p = self.metadata.get("priority")
        return p if isinstance(p, (int, float)) else None

    # -- FALSE-POSITIVE CONTROLS --------------------------------------------------------
    #
    # Everything below exists because a red-team pass over a real 89-skill library found
    # that each of these shapes looks like a defect to a naive detector and is in fact a
    # deliberate design. They are properties of the skill, computed from the skill, so
    # that every detector suppresses on the same evidence rather than each growing its
    # own ad-hoc exception list.

    def is_session_start(self):
        """Injected at session start, therefore never trigger-matched.

        A sessionStart skill is loaded unconditionally. Its description is documentation,
        not a trigger, and empty pathPatterns/bashPatterns are the POINT (they add zero
        trigger surface). Scoring it for greediness or for missing scope metadata asks
        the wrong question of it entirely.
        """
        return bool(self.metadata.get("sessionStart"))

    def has_scoping_metadata(self):
        return any(
            isinstance(self.metadata.get(k), (list, dict)) and self.metadata.get(k)
            for k in ("promptSignals", "pathPatterns", "importPatterns", "bashPatterns"))

    def boundary_skills(self):
        """Other skills this description explicitly cedes territory to.

        A description that says "for Adobe ExC E2E use `appbuilder-e2e-testing`; this
        skill owns everything else" has ALREADY been deconflicted, by hand, on purpose.
        That is the opposite of a greedy description and must not be scored as one — the
        real `playwright-cli` in the reviewed library carries exactly this text as the
        applied fix for the greedy version the ground truth recorded.
        """
        return {m.group(1) for m in re.finditer(
            r"`([a-z][a-z0-9]*(?:-[a-z0-9]+){1,4})`", self.description or "")}

    def declares_scope_boundary(self):
        low = (self.description or "").lower()
        if not any(cue in low for cue in (
                "scope boundary", "do not claim", "owns local and", "owns everything else",
                "instead of this skill", "not this skill", "use `", "→ `", "-> `",
                "handled by", "are managed by", "belongs to", "hand off", "handoff",
                "hands off", "defer to")):
            return False
        return bool(self.boundary_skills())

    def declares_coordinator(self):
        """Self-declared router / umbrella / entry point.

        `vercel/marketplace` and `vercel/build-agents` chain to many specialists on
        purpose; `hf-cloud-sagemaker-deployment-planner` says in so many words that it
        "is the entry-point skill ... and coordinates the other deployment skills";
        `adobe/appbuilder-workfront` is an umbrella over three nested sub-skills. Broad
        vocabulary is the job description of all four, so overlap with the specialists
        they dispatch to is design, not collision.
        """
        low = (self.description or "").lower()
        return any(cue in low for cue in (
            "entry-point skill", "entry point skill", "coordinates the other",
            "coordinating", "routes between", "router", "umbrella", "sub-skill",
            "sub-skills", "dispatch", "picks a deployment pathway", "start here"))


class Finding:
    def __init__(self, code, severity, title, detail, file, line=None, key_path=None,
                 skill=None, confidence="heuristic", defect_class=None, evidence=None):
        self.code = code
        self.severity = severity
        self.title = title
        self.detail = detail
        self.file = file
        self.line = line
        self.key_path = key_path
        self.skill = skill
        self.confidence = confidence  # "exact" | "heuristic"
        self.defect_class = defect_class
        self.evidence = evidence or {}

    def location(self):
        if self.line:
            return "%s:%d" % (self.file, self.line)
        if self.key_path:
            return "%s  (key: %s)" % (self.file, self.key_path)
        return self.file

    def to_dict(self):
        return {
            "code": self.code,
            "severity": self.severity,
            "confidence": self.confidence,
            "defect_class": self.defect_class,
            "skill": self.skill,
            "file": self.file,
            "line": self.line,
            "key_path": self.key_path,
            "title": self.title,
            "detail": self.detail,
            "evidence": self.evidence,
        }


# --------------------------------------------------------------------------------------
# Library
# --------------------------------------------------------------------------------------

class Library:
    def __init__(self, root):
        self.root = os.path.abspath(root)
        self.skills = []
        self.overlays = {}  # abs path -> YamlDoc
        self._load()
        self.by_name = defaultdict(list)
        for s in self.skills:
            if s.name:
                self.by_name[s.name].append(s)
        self.names = set(self.by_name)
        self.packs = defaultdict(list)
        for s in self.skills:
            self.packs[s.pack].append(s)
        self.pack_aliases = self._derive_pack_aliases()
        self.df, self.doc_terms = self._build_idf()
        self.package_universe = self._build_package_universe()

    def _load(self):
        for dirpath, dirnames, filenames in os.walk(self.root):
            dirnames[:] = [d for d in dirnames if d not in (".git", "node_modules", "__pycache__")]
            if "SKILL.md" in filenames:
                skill = Skill(self.root, os.path.join(dirpath, "SKILL.md"))
                overlay_path = os.path.join(dirpath, "overlay.yaml")
                if os.path.isfile(overlay_path):
                    doc = load_overlay(overlay_path)
                    skill.overlay = doc
                    self.overlays[overlay_path] = doc
                self.skills.append(skill)
        self.skills.sort(key=lambda s: s.rel)

    # -- pack ownership -----------------------------------------------------------------

    def _derive_pack_aliases(self):
        """pack -> set of normalized tokens that pack owns, derived from names only.

        A pack owns (a) its directory name, (b) every full skill name inside it, and
        (c) any hyphen-segment of a skill name that EQUALS the pack name (so the
        `supabase` pack owns `supabase` via `supabase-postgres-best-practices`).

        Deliberately narrow. An earlier version also claimed every non-generic segment,
        which made the `adobe` pack "own" the word `actions` (from `workfront-actions`)
        and then flagged every `app/actions/**` path in the library. Ownership claims
        must be conservative: a token owned by zero or several packs yields no finding
        rather than a guess.
        """
        aliases = defaultdict(set)
        for pack, skills in self.packs.items():
            pack_norm = normalize_token(pack)
            tokens = {pack_norm}
            for s in skills:
                for nm in filter(None, (s.name, s.dirname)):
                    tokens.add(normalize_token(nm))
                    for seg in re.split(r"[-_/]", nm):
                        if normalize_token(seg) == pack_norm:
                            tokens.add(pack_norm)
            aliases[pack] = {t for t in tokens if t}
        return aliases

    def owner_pack(self, token):
        """Pack that uniquely owns a namespace token, or None if 0 or >1 packs claim it."""
        norm = normalize_token(token)
        if not norm or len(norm) < 4:
            return None
        owners = [pack for pack, toks in self.pack_aliases.items() if norm in toks]
        return owners[0] if len(owners) == 1 else None

    # -- FALSE-POSITIVE CONTROLS --------------------------------------------------------

    def nested_children(self, skill):
        """Skills whose SKILL.md lives UNDER another skill's directory.

        `adobe/appbuilder-workfront/{workfront-actions,workfront-ui-extension,
        workfront-local-testing}` is an umbrella plus its three sub-skills. A parent
        sharing vocabulary with its own children is the directory layout speaking, not a
        trigger collision, so children are subtracted from the parent's collision set
        (and vice versa).
        """
        prefix = skill.dir + os.sep
        return {s.rel for s in self.skills if s is not skill and s.path.startswith(prefix)}

    def family_siblings(self, skill):
        """Same-pack skills that share the skill's own longest name prefix.

        The six `hf-cloud-*` SageMaker skills are a deliberate pipeline: context
        discovery -> IAM preflight -> deployment planner -> serving image -> production
        defaults. They MUST share the words "sagemaker" and "aws"; that is their subject.
        Counting each sibling as a competing claimant turns a coherent sub-family into
        five phantom defects, so a shared-prefix family is excluded from collision
        counts. Cross-pack collisions — the `playwright-cli` / `appbuilder-e2e-testing`
        shape that the ground truth actually recorded — are unaffected.
        """
        name = skill.name or skill.dirname
        segs = re.split(r"[-_]", name)
        if len(segs) < 2:
            return set()
        # Union over prefix widths, widest family first. Taking only the LONGEST shared
        # prefix under-clusters: `hf-cloud-sagemaker-deployment-planner` would find its
        # two `hf-cloud-sagemaker-*` siblings at width 3 and stop, leaving the other four
        # `hf-cloud-*` skills counted as rivals when they are the same pipeline.
        out = set()
        for width in (2, 3):
            if len(segs) < width:
                continue
            prefix = "-".join(segs[:width]) + "-"
            for s in self.packs.get(skill.pack, ()):
                if s is skill:
                    continue
                other = s.name or s.dirname
                other_segs = re.split(r"[-_]", other)
                if len(other_segs) < width:
                    continue
                if other.startswith(prefix) or name.startswith(
                        "-".join(other_segs[:width]) + "-"):
                    out.add(s.rel)
        return out

    def excluded_claimants(self, skill):
        """Everything that must not be counted as a rival claimant for `skill`."""
        out = self.nested_children(skill) | self.family_siblings(skill)
        # a skill that names another skill as a boundary has already ceded to it
        named = skill.boundary_skills()
        if named:
            out |= {s.rel for s in self.skills if (s.name or s.dirname) in named}
        # ...and so has any skill that names THIS one
        for s in self.skills:
            if s is not skill and (skill.name or skill.dirname) in s.boundary_skills():
                out.add(s.rel)
        return out

    def median_priority(self):
        vals = sorted(p for p in (s.priority() for s in self.skills) if p is not None)
        if not vals:
            return None
        mid = len(vals) // 2
        return vals[mid] if len(vals) % 2 else (vals[mid - 1] + vals[mid]) / 2.0

    # -- IDF ----------------------------------------------------------------------------

    def _build_idf(self):
        """Document frequency over ANCHOR terms, not over all words.

        Plain bag-of-words IDF is the wrong index for this job. Run over raw prose it
        rewards rare ENGLISH words ("executed", "orienting") rather than rare DOMAIN
        anchors, and in an 89-skill library essentially every description then contains
        some df==1 token, so every skill scores as maximally specific and the metric
        says nothing. What actually carries a trigger is the identifier-shaped
        vocabulary: `@ai-sdk/gateway`, `ZeroGPU`, `SageMaker`, `cacheTag`, `RLS`. Those
        are what we index.
        """
        doc_terms = {}
        df = Counter()
        for s in self.skills:
            terms = anchor_terms(s.description)
            doc_terms[s.rel] = terms
            for t in set(terms):
                df[t] += 1
        return df, doc_terms

    def idf(self, term):
        n = max(1, len(self.skills))
        return math.log(n / max(1, self.df.get(term, 0)))


    def anchor_index(self):
        """anchor term -> set of skill rel-paths whose description uses it."""
        index = defaultdict(set)
        for s in self.skills:
            for t in set(self.doc_terms.get(s.rel, [])):
                index[t].add(s.rel)
        return index


    def _build_package_universe(self):
        """Split the library's text into guard text and everything else.

        The question SK011 needs answered is not "does this package exist in the world"
        (undecidable here, no network) but "does this library believe it exists". So we
        build the corpus of everything the library says EXCEPT the contents of
        skipIfFileContains values, and the set of package identifiers named in it.

        Excluding guards is the whole point: a typo'd guard token must not be allowed to
        vouch for itself. If a skill nags you to move to `@vercel/ai-gateway` and the
        string `@vercel/ai-gateway` appears nowhere in the entire library except inside
        that guard — not in the rule's own message, not in the skill's prose, not in any
        code sample — then the library does not actually believe in that package, and a
        guard built on it can never fire.

        An earlier version built this from import/require/install sites only. That was
        too strict: `@ai-sdk/openai` is named in a dozen messages and prose lines in this
        library but never in a demonstrated import, and it was wrongly flagged.
        """
        nonguard_lines, guard_lines = [], []
        guard_re = re.compile(r"^\s*(-\s+)?skipIfFileContains\s*:", re.I)
        for s in self.skills:
            texts = [s.doc.text]
            if s.overlay is not None:
                texts.append(s.overlay.text)
            for text in texts:
                for line in text.splitlines():
                    (guard_lines if guard_re.match(line) else nonguard_lines).append(line)
        self.nonguard_corpus = "\n".join(nonguard_lines).lower()
        scoped_re = re.compile(r"@[a-z0-9][a-z0-9\-.]*/[a-z0-9][a-z0-9\-./]*")
        return set(scoped_re.findall(self.nonguard_corpus))

    def mentioned_outside_guards(self, literal):
        """Does this token appear anywhere in the library other than inside a guard?"""
        lit = literal.strip().lower()
        return bool(lit) and lit in self.nonguard_corpus

    def nearest_package(self, literal):
        import difflib
        matches = difflib.get_close_matches(
            literal.lower(), sorted(self.package_universe), n=1, cutoff=0.60)
        return matches[0] if matches else None


def normalize_token(token):
    return re.sub(r"[^a-z0-9]", "", (token or "").lower())


TOKEN_RE = re.compile(r"[A-Za-z0-9@][A-Za-z0-9@/_.\-]*")
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.;!?])\s+|\s+—\s+|\s+--\s+")

# Words that get a capital letter only because they open a sentence or are ordinary
# English used in title case. Being capitalized is evidence of an anchor ONLY for tokens
# that are not in this set.
COMMON_CAPITALIZED = set("""
use uses used using when whenever where while what which who why how also always never
never never for from with without within into onto about after before during under over
this that these those the a an and or but nor so yes no not all any every each both few
more most other some such only own same than too very can will just should now then here
there reach skip trigger triggers scope separate covers cover handles handle prevents
prevent guides guide helps help make makes create creates build builds run runs set sets
""".split())



def anchor_terms(text, with_positions=False):
    """Identifier-shaped tokens: the vocabulary that actually anchors a trigger.

    A token is an anchor when it looks like a name rather than a word — it carries a
    package/path separator, a digit, internal capitalisation, an all-caps acronym, a
    hyphenated compound, or is a mid-sentence proper noun. Sentence-initial capitals do
    not count on their own, or every description would "anchor" on its first word.

    PRODUCT_ALIASES membership counts only for a token WRITTEN as a name. Several keys in
    that table are also ordinary English words — `render`, `fly`, `modal`, `convex`,
    `next` — and promoting them on spelling alone inverts the detector. A lowercase
    "render" in running prose is a df==1 term, so it registers as a rare, highly
    discriminating anchor, and SK008's `if clause_rare and not hard: continue` then
    EXCUSES the surrounding universal claim. Two descriptions making the identical greedy
    claim get opposite verdicts because one of them happens to contain the word "render"
    (proven on fixture pair env-bootstrap / env-bootstrap-variant). Real product mentions
    are capitalised or carry a scope/hyphen/dot, so requiring name-shape keeps `Supabase`,
    `@supabase/ssr` and `fly.io` while dropping "on the fly".
    """
    if not isinstance(text, str):
        return [] if not with_positions else []
    found = []
    for sentence in SENTENCE_SPLIT_RE.split(text):
        first = True
        for match in TOKEN_RE.finditer(sentence):
            tok = match.group(0).strip("-._/,")
            was_first, first = first, False
            if len(tok) < 3:
                continue
            low = tok.lower()
            if low in STOPWORDS or low in COMMON_CAPITALIZED:
                continue
            structural = (
                any(ch in tok for ch in "@/_.")
                or any(ch.isdigit() for ch in tok)
                or (tok[1:] != tok[1:].lower())          # camelCase / interior capital
                or (tok.isupper() and len(tok) >= 2)      # PPR, RLS, IAM, ANY-caps acronym
                or ("-" in tok and len(tok) >= 6)
                or (low in PRODUCT_ALIASES
                    and (tok[0].isupper() or any(ch in tok for ch in "@/-.")))
            )
            proper_noun = tok[0].isupper() and not was_first
            if structural or proper_noun:
                found.append((low, match.start()) if with_positions else low)
    return found


def find_products(text):
    """Products named in a string, via the curated lexicon."""
    if not isinstance(text, str):
        return set()
    low = text.lower()
    hits = set()
    for product, aliases in PRODUCT_ALIASES.items():
        for alias in aliases:
            if alias.startswith("@"):
                if alias in low:
                    hits.add(product)
                    break
            else:
                if re.search(r"(?<![a-z0-9])" + re.escape(alias) + r"(?![a-z0-9])", low):
                    hits.add(product)
                    break
    return hits


# --------------------------------------------------------------------------------------
# Detectors
# --------------------------------------------------------------------------------------

def detect_frontmatter(lib):
    """SK001 — EXACT. Unparseable or absent frontmatter. Defect class 10.

    This is the most dangerous failure mode because it is silent and total: a skill whose
    frontmatter does not parse has no name, no description, no routing rules. It is
    invisible to the retriever while still occupying a directory that looks healthy.
    """
    out = []
    for s in lib.skills:
        if s.doc.error:
            out.append(Finding(
                "SK001", "high",
                "Frontmatter does not parse — skill is silently inert",
                "PyYAML rejected this file's frontmatter: %s. A skill whose frontmatter "
                "fails to parse contributes no name, description, or routing rules; it is "
                "invisible to retrieval while appearing installed." % s.doc.error,
                s.path, s.doc.error_line, "<frontmatter>", s.key, "exact", 10,
                {"parser_error": s.doc.error},
            ))
            continue
        if not isinstance(s.doc.data, dict):
            out.append(Finding(
                "SK001", "high",
                "Frontmatter is not a mapping",
                "Frontmatter parsed to %s, not a key/value mapping." % type(s.doc.data).__name__,
                s.path, 1, "<frontmatter>", s.key, "exact", 10,
            ))
            continue
        for field in ("name", "description"):
            if not isinstance(s.fm.get(field), str) or not s.fm.get(field, "").strip():
                out.append(Finding(
                    "SK001", "high",
                    "Missing required frontmatter field `%s`" % field,
                    "Every skill needs `%s`; without it the skill cannot be addressed "
                    "(name) or retrieved (description)." % field,
                    s.path, s.doc.line_for((field,)) or 1, field, s.key, "exact", 10,
                ))
    for path, doc in sorted(lib.overlays.items()):
        if doc.error:
            out.append(Finding(
                "SK001", "high",
                "overlay.yaml does not parse",
                "PyYAML rejected this overlay: %s. The machine-readable routing config is "
                "the file the router actually reads; if it does not parse, none of this "
                "skill's routing config is in force." % doc.error,
                path, doc.error_line, "<document>", None, "exact", 10,
                {"parser_error": doc.error},
            ))
    return out


def detect_duplicate_names(lib):
    """SK002 — EXACT. Two skills claiming the same `name:`.

    In a routing table this is an ambiguous forwarding entry: every chainTo edge naming
    it resolves nondeterministically.
    """
    out = []
    for name, skills in sorted(lib.by_name.items()):
        if len(skills) > 1:
            for s in skills:
                out.append(Finding(
                    "SK002", "high",
                    "Duplicate skill name `%s` (%d skills claim it)" % (name, len(skills)),
                    "Also declared by: %s. Every chainTo/upgradeToSkill edge naming `%s` "
                    "resolves ambiguously." % (
                        ", ".join(o.rel for o in skills if o is not s), name),
                    s.path, s.doc.line_for(("name",)), "name", s.key, "exact", None,
                    {"duplicates": [o.rel for o in skills]},
                ))
    return out


def detect_schema_outliers(lib):
    """SK003 — HEURISTIC (majority-vote schema inference). Defect class 3.

    There is no published schema for these files, so we infer one: for each key name we
    look at where the library MOSTLY puts it. A skill that puts `validate:` under
    `metadata:` while 13 siblings put it at top level is almost certainly disabling its
    own rules — the loader looks for the majority location and finds nothing.

    Heuristic because a minority placement could in principle be a deliberate,
    correctly-supported variant. Confidence rises with the majority/minority ratio,
    which is reported as evidence.
    """
    out = []
    ROUTING_CRITICAL = {"validate", "chainTo", "promptSignals", "description", "name",
                        "retrieval", "pathPatterns", "importPatterns", "bashPatterns",
                        "priority", "minScore"}

    placements = defaultdict(Counter)   # key name -> Counter(parent path str)
    per_skill = defaultdict(list)       # (key name, parent) -> [(skill, full path)]

    def walk(node, path, skill, depth):
        if depth > 2 or not isinstance(node, dict):
            return
        parent = ".".join(path) if path else "<root>"
        for k, v in node.items():
            if not isinstance(k, str):
                continue
            placements[k][parent] += 1
            per_skill[(k, parent)].append((skill, path + (k,)))
            if isinstance(v, dict):
                walk(v, path + (k,), skill, depth + 1)

    for s in lib.skills:
        if isinstance(s.doc.data, dict):
            walk(s.doc.data, (), s, 0)

    for key, parents in sorted(placements.items()):
        if len(parents) < 2:
            continue
        total = sum(parents.values())
        if total < 5:
            continue  # too little signal to infer a schema
        (majority_parent, majority_count), = parents.most_common(1)
        for parent, count in parents.items():
            if parent == majority_parent:
                continue
            if count > max(1, 0.2 * majority_count):
                continue  # a real variant, not an outlier
            severity = "high" if key in ROUTING_CRITICAL else "medium"
            for skill, full_path in per_skill[(key, parent)]:
                out.append(Finding(
                    "SK003", severity,
                    "Schema outlier: `%s` is nested under `%s` but %d/%d skills put it at `%s`"
                    % (key, parent, majority_count, total, majority_parent),
                    "Inferred library schema puts `%s` at `%s` (%d occurrences). This skill "
                    "is 1 of only %d placing it at `%s`. If the loader reads the majority "
                    "location, everything under this key is silently ignored — the classic "
                    "way a set of validate rules gets disabled without any error."
                    % (key, majority_parent, majority_count, count, parent),
                    skill.path, skill.doc.line_for(full_path), ".".join(full_path),
                    skill.key, "heuristic", 3,
                    {"key": key, "this_parent": parent, "majority_parent": majority_parent,
                     "majority_count": majority_count, "minority_count": count},
                ))
    return out


def _flatten(node, path=()):
    if isinstance(node, dict):
        for k, v in node.items():
            for item in _flatten(v, path + (str(k),)):
                yield item
    elif isinstance(node, list):
        for i, v in enumerate(node):
            for item in _flatten(v, path + (str(i),)):
                yield item
    else:
        yield path, node


def detect_overlay_drift(lib):
    """SK004 — EXACT. Defect class 2.

    Where a skill ships BOTH SKILL.md frontmatter and overlay.yaml, the overlay is the
    machine-readable copy the router consumes. A fix applied to only one of the two is
    a fix that was never actually put in force. This is a pure field-level diff of the
    keys present in both documents — a value conflict is a fact, not an inference.

    We do NOT report keys present in one file and absent in the other: an overlay is
    allowed to be a subset. Only conflicting values and differing rule-list lengths.
    """
    out = []
    ROUTING_CRITICAL_PREFIXES = ("description", "name", "chainTo", "validate")
    ROUTING_CRITICAL_LEAVES = ("priority", "minScore", "targetSkill", "upgradeToSkill",
                               "pattern", "skipIfFileContains", "severity")

    for s in lib.skills:
        if s.overlay is None or s.overlay.error or not isinstance(s.overlay.data, dict):
            continue
        if not isinstance(s.doc.data, dict):
            continue
        skill_flat = dict(_flatten(s.doc.data))
        overlay_flat = dict(_flatten(s.overlay.data))

        # Structural drift: a routing-critical block present in one copy and absent from
        # the other. This is how a schema-outlier fix shows up across the pair — move
        # `validate:` under `metadata:` in SKILL.md and the overlay still carries it at
        # top level, so the two files no longer describe the same skill at all.
        for kind in ("chainTo", "validate", "retrieval"):
            in_skill = isinstance(s.doc.data.get(kind), list) or \
                isinstance(s.doc.data.get(kind), dict)
            in_overlay = isinstance(s.overlay.data.get(kind), list) or \
                isinstance(s.overlay.data.get(kind), dict)
            if in_skill == in_overlay:
                continue
            present, absent = ("SKILL.md", "overlay.yaml") if in_skill else \
                ("overlay.yaml", "SKILL.md")
            out.append(Finding(
                "SK004", "high",
                "Config drift: `%s` block exists in %s but not in %s" % (kind, present, absent),
                "One config copy declares a top-level `%s` block and the other does not. "
                "Whichever file the router reads, one copy of this skill has routing rules "
                "the other lacks — and if the block was merely re-indented under another "
                "key, it is silently disabled there." % kind,
                s.overlay.path, s.overlay.line_for((kind,)), kind, s.key, "exact", 2,
                {"field": kind, "present_in": present, "absent_from": absent,
                 "skill_md_path": s.path, "skill_md_line": s.doc.line_for((kind,))},
            ))

        # rule-list length differences — the loudest value-level signal
        for kind in ("chainTo", "validate"):
            a = s.doc.data.get(kind)
            b = s.overlay.data.get(kind)
            if isinstance(a, list) and isinstance(b, list) and len(a) != len(b):
                out.append(Finding(
                    "SK004", "high",
                    "Config drift: SKILL.md has %d `%s` rules, overlay.yaml has %d"
                    % (len(a), kind, len(b)),
                    "The two config copies disagree on how many %s rules exist. Whichever "
                    "file the router reads, one set of rules is not in force." % kind,
                    s.overlay.path, s.overlay.line_for((kind,)), kind, s.key, "exact", 2,
                    {"skill_md_count": len(a), "overlay_count": len(b), "field": kind,
                     "skill_md_path": s.path},
                ))

        # SCALAR LISTS ARE SETS, NOT TUPLES.
        #
        # `retrieval.entities` is an unordered bag of index terms. Comparing it slot by
        # slot reports "SKILL.md says ToolLoopAgent, overlay says generateObject" — which
        # is an artifact of one file having dropped two earlier members, not two separate
        # conflicts. The real fact is a membership difference, so report it once, as one.
        list_paths = set()

        def _scalar_lists(node, path=()):
            if isinstance(node, dict):
                for k, v in node.items():
                    for item in _scalar_lists(v, path + (str(k),)):
                        yield item
            elif isinstance(node, list) and node and all(
                    isinstance(v, (str, int, float, bool)) for v in node):
                yield path, node
            elif isinstance(node, list):
                for i, v in enumerate(node):
                    for item in _scalar_lists(v, path + (str(i),)):
                        yield item

        skill_lists = dict(_scalar_lists(s.doc.data))
        overlay_lists = dict(_scalar_lists(s.overlay.data))
        for path, a in sorted(skill_lists.items()):
            b = overlay_lists.get(path)
            if b is None:
                continue
            list_paths.add(path)
            only_skill = [v for v in a if v not in b]
            only_overlay = [v for v in b if v not in a]
            if not only_skill and not only_overlay:
                continue
            out.append(Finding(
                "SK004", "medium",
                "Config drift at `%s`: the two copies list different members"
                % ".".join(path),
                "SKILL.md and overlay.yaml disagree on the membership of this list. "
                "Only in SKILL.md: %s. Only in overlay.yaml: %s. The overlay is the "
                "machine-readable copy — entries it still carries are still in force, "
                "and entries only SKILL.md has were never put in force."
                % (", ".join(map(str, only_skill)) or "(none)",
                   ", ".join(map(str, only_overlay)) or "(none)"),
                s.overlay.path, s.overlay.line_for(path), ".".join(path), s.key, "exact", 2,
                {"key_path": ".".join(path), "only_in_skill_md": only_skill,
                 "only_in_overlay": only_overlay, "skill_md_path": s.path,
                 "skill_md_line": s.doc.line_for(path)},
            ))

        reported = 0
        for path, skill_val in sorted(skill_flat.items()):
            if path not in overlay_flat:
                continue
            if tuple(path[:-1]) in list_paths:
                continue  # already reported once, as a membership difference
            overlay_val = overlay_flat[path]
            if skill_val == overlay_val:
                continue
            leaf = path[-1]
            critical = path[0] in ROUTING_CRITICAL_PREFIXES or leaf in ROUTING_CRITICAL_LEAVES
            severity = "high" if critical else "medium"
            reported += 1
            if reported > 12:
                out.append(Finding(
                    "SK004", "medium",
                    "Config drift: further differences truncated",
                    "More than 12 field-level differences between SKILL.md and overlay.yaml; "
                    "the two files have diverged broadly. Diff them directly.",
                    s.overlay.path, None, "<document>", s.key, "exact", 2,
                    {"skill_md_path": s.path},
                ))
                break
            out.append(Finding(
                "SK004", severity,
                "Config drift at `%s`: SKILL.md and overlay.yaml disagree" % ".".join(path),
                "SKILL.md says %s; overlay.yaml says %s. The overlay is the machine-readable "
                "copy — if the fix landed only in SKILL.md it was never actually in force."
                % (_short(skill_val), _short(overlay_val)),
                s.overlay.path, s.overlay.line_for(path), ".".join(path), s.key, "exact", 2,
                {"key_path": ".".join(path), "skill_md_value": _short(skill_val, 300),
                 "overlay_value": _short(overlay_val, 300), "skill_md_path": s.path,
                 "skill_md_line": s.doc.line_for(path)},
            ))
    return out


def _short(value, limit=140):
    text = value if isinstance(value, str) else json.dumps(value, default=str)
    text = " ".join(text.split())
    return text if len(text) <= limit else text[:limit - 1] + "…"


def detect_dangling_routes(lib):
    """SK005 — EXACT (closed-world). Defect class 9.

    A chainTo/upgradeToSkill naming a skill that is not in the library is an unresolved
    symbol. Exact under the closed-world assumption that this root IS the library; if
    skills can be resolved from elsewhere, these become warnings.
    """
    out = []
    for s in lib.skills:
        for rule in s.rules:
            if not rule.target or not isinstance(rule.target, str):
                continue
            if rule.target in lib.names:
                continue
            suggestion = _closest(rule.target, lib.names)
            out.append(Finding(
                "SK005", "high",
                "Dangling route: `%s` -> `%s` (no such skill)" % (s.key, rule.target),
                "%s.%s names a skill that does not exist in this library.%s Every firing of "
                "this rule is a routing dead end." % (
                    rule.label(), rule.target_key,
                    (" Closest existing name: `%s`." % suggestion) if suggestion else ""),
                s.path, rule.line(rule.target_key), "%s.%s" % (rule.label(), rule.target_key),
                s.key, "exact", 9,
                {"target": rule.target, "rule": rule.label(), "suggestion": suggestion},
            ))
    return out


def _closest(name, candidates):
    import difflib
    matches = difflib.get_close_matches(name, list(candidates), n=1, cutoff=0.7)
    return matches[0] if matches else None


def _shared_name_tail(a, b, min_segments=2):
    """Do two kebab names end in the same >=2-segment tail?

    `next-best-practices` / `react-best-practices` share `best-practices`; that is a
    substituted first segment, i.e. a naming mistake. Two names that merely score well on
    edit distance share no such tail and are not evidence of anything.
    """
    sa, sb = a.lower().split("-"), b.lower().split("-")
    n = 0
    while n < min(len(sa), len(sb)) and sa[-1 - n] == sb[-1 - n]:
        n += 1
    return n >= min_segments and (len(sa) > n or len(sb) > n)


def detect_self_routes(lib):
    """SK006 — EXACT detection, HOUSE-IDIOM aware. Defect class 8.

    A route whose target is the enclosing skill draws no edge in the routing graph. That
    much is a fact. Whether it is a DEFECT depends on something this detector must read
    off the library rather than assume.

    WHY THE NAIVE VERSION IS WRONG, AND HOW THE RED TEAM ESTABLISHED IT
    -------------------------------------------------------------------
    Run unconditionally, this detector produced 56 findings on the reviewed library —
    37% of the entire report. Every one of them was a false positive, and three
    independent pieces of evidence say so:

      1. 100% of `chainTo` entries in that library carry a `targetSkill`. The key is
         effectively mandatory, so "match this pattern and emit this advice while staying
         where you are" has no other spelling. A self target IS the spelling.
      2. The library's own review document prescribes self-targeting as the FIX for
         mis-targeted rules — "`@vercel/postgres` chainTo nextjs (should stay here)",
         "chainTo `generateObject` -> ai-gateway (should stay ai-sdk)". The applied
         commits deleted the cross-targeting rule and KEPT the self-targeting one.
      3. The messages read as reload instructions, not handoffs: "Run Skill(ai-sdk) for
         v6 migration guidance", "Reloading Vercel Sandbox guidance".

    The genuine instance the ground truth recorded (an Express rule in `vercel-functions`
    pointing at `vercel-functions`) was fixed by DELETING the key — so in the post-fix
    library the surviving self-routes are the intended ones.

    THE RULE. Prevalence decides. A self-route in a library that otherwise never uses the
    shape is a one-off slip and is reported per rule. A self-route in a library where the
    shape is pervasive — several skills, a large share of all edges — is a convention, and
    is reported ONCE as an aggregate observation naming every site, so a reviewer can
    still see it without 56 line items claiming to be bugs.
    """
    hits = []
    for s in lib.skills:
        for rule in s.rules:
            if isinstance(rule.target, str) and s.name and rule.target == s.name:
                hits.append((s, rule))
    if not hits:
        return []

    total_routed = sum(1 for s in lib.skills for r in s.rules if isinstance(r.target, str))
    skills_using = {s.key for s, _ in hits}
    share = len(hits) / max(1, total_routed)
    idiomatic = len(skills_using) >= 3 and share >= 0.15

    if idiomatic:
        sites = sorted({"%s %s" % (s.key, r.label()) for s, r in hits})
        first_skill, first_rule = hits[0]
        return [Finding(
            "SK006", "low",
            "Self-routing is a house idiom here (%d rules in %d skills), not %d defects"
            % (len(hits), len(skills_using), len(hits)),
            "%d of the %d routed rules in this library (%.0f%%), spread across %d skills "
            "(%s), set their target to the enclosing skill. At that prevalence this is a "
            "convention meaning \"emit this advice and reload my own guidance\", not %d "
            "independent mistakes — especially since every chainTo entry here carries a "
            "targetSkill, leaving no other way to spell \"stay here\". Reported once. If "
            "your router treats a self target as a real forwarding edge rather than a "
            "no-op, revisit all %d sites: %s."
            % (len(hits), total_routed, 100 * share, len(skills_using),
               ", ".join(sorted(skills_using)[:8]), len(hits), len(hits),
               ", ".join(sites[:12]) + ("…" if len(sites) > 12 else "")),
            first_skill.path, first_rule.line(first_rule.target_key), "<library>",
            None, "exact", 8,
            {"self_route_count": len(hits), "routed_rule_count": total_routed,
             "share": round(share, 3), "skills": sorted(skills_using), "sites": sites,
             "verdict": "house idiom — suppressed as individual findings"},
        )]

    out = []
    for s, rule in hits:
        sev = "medium" if rule.kind == "chainTo" else "low"
        out.append(Finding(
            "SK006", sev,
            "No-op self route: `%s` %s routes to itself" % (s.key, rule.label()),
            "%s.%s == the enclosing skill's own name, so the rule draws no edge: it "
            "fires, the router loads the skill that is already loaded, and nothing "
            "changes. Only %d rule(s) in %d skill(s) in this library do this, so it is a "
            "slip rather than a convention — either drop the key or point it at the skill "
            "that actually owns the advice."
            % (rule.label(), rule.target_key, len(hits), len(skills_using)),
            s.path, rule.line(rule.target_key), "%s.%s" % (rule.label(), rule.target_key),
            s.key, "exact", 8,
            {"rule": rule.label(), "kind": rule.kind, "pattern": _short(rule.pattern),
             "library_prevalence": len(hits), "skills_using": sorted(skills_using)},
        ))
    return out


def detect_cycles(lib):
    """SK007 — EXACT. chainTo cycles = call-graph cycles.

    Borrowed straight from BGP: a forwarding graph with a loop and no path history will
    ping-pong. Self-loops are excluded (reported by SK006).
    """
    out = []
    graph = defaultdict(set)
    edge_rule = {}
    edge_cores = defaultdict(set)
    for s in lib.skills:
        if not s.name:
            continue
        for rule in s.rules:
            if rule.kind != "chainTo":
                continue
            if isinstance(rule.target, str) and rule.target in lib.names and rule.target != s.name:
                graph[s.name].add(rule.target)
                edge_rule.setdefault((s.name, rule.target), (s, rule))
                edge_cores[(s.name, rule.target)] |= {
                    c for c in (branch_cores(rule.pattern) or []) if len(c) >= 4}

    cycles, seen = [], set()

    def dfs(node, stack, on_stack):
        if len(stack) > 8:
            return
        for nxt in sorted(graph.get(node, ())):
            if nxt in on_stack:
                idx = stack.index(nxt)
                cycle = stack[idx:]
                rot = min(range(len(cycle)), key=lambda i: cycle[i])
                canon = tuple(cycle[rot:] + cycle[:rot])
                if canon not in seen:
                    seen.add(canon)
                    cycles.append(canon)
                continue
            if nxt in visited_global:
                continue
            stack.append(nxt)
            on_stack.add(nxt)
            dfs(nxt, stack, on_stack)
            stack.pop()
            on_stack.discard(nxt)

    visited_global = set()
    for start in sorted(graph):
        dfs(start, [start], {start})
        visited_global.add(start)

    # SEVERITY BY LIVENESS, NOT BY TOPOLOGY.
    #
    # The graph edge is unconditional but the RULE is not: every chainTo fires only on its
    # own pattern. So a cycle in the edge graph is a real ping-pong only if one piece of
    # text can satisfy every pattern around the loop. Treating all cycles alike over-
    # reports: on the reviewed library it turned 4 live 2-cycles into 11 findings, seven
    # of which required four unrelated patterns to co-occur in a single file.
    #
    # Liveness is approximated by literal-core overlap between the edges. Two edges that
    # require the same literal (`DurableAgent` both ways; `@vercel/connect/eve` verbatim
    # both ways) demonstrably fire on the same text — that is a live loop. Edges with
    # disjoint literals MIGHT still co-occur (auth-in-middleware plausibly matches both
    # `export function middleware` and `next-auth`), so they are reported, but as the
    # weaker claim they are.
    # A longer cycle that already contains a reported 2-cycle is a DERIVATIVE of it: fix
    # the mutual pair and the long loop dissolves with it. Reporting both is one defect
    # counted twice (five of eleven findings on the reviewed library were this).
    two_cycles = {frozenset(c) for c in cycles if len(c) == 2}
    filtered = []
    for cycle in cycles:
        if len(cycle) > 2 and any(
                frozenset((cycle[i], cycle[(i + 1) % len(cycle)])) in two_cycles
                for i in range(len(cycle))):
            continue
        filtered.append(cycle)
    cycles = filtered

    for cycle in cycles:
        chain = " -> ".join(cycle + (cycle[0],))
        src_name = cycle[0]
        skill, rule = edge_rule.get((cycle[0], cycle[1 % len(cycle)]), (None, None))
        edges = [(cycle[i], cycle[(i + 1) % len(cycle)]) for i in range(len(cycle))]
        core_sets = [edge_cores.get(e, set()) for e in edges]
        # Containment, not equality: literal extraction collapses `@vercel/(postgres|kv)`
        # to the prefix `@vercel/`, and any file matching `@vercel/kv` contains that
        # prefix. Requiring identical cores misses exactly the loops whose two ends were
        # written at different levels of specificity — which is most of them.
        shared = set()
        if all(core_sets):
            for a in core_sets[0]:
                for other in core_sets[1:]:
                    if any(a in b or b in a for b in other):
                        shared.add(a)
                    else:
                        shared.discard(a)
                        break
        live = bool(shared) and len(cycle) == 2

        if live:
            severity, verdict = "medium", (
                "LIVE: every edge in this loop requires the literal(s) %s, so a single "
                "file containing one of them satisfies both rules and the loop actually "
                "closes. Break it by making one edge conditional or removing it."
                % ", ".join("`%s`" % c for c in sorted(shared)[:4]))
        elif len(cycle) == 2:
            severity, verdict = "low", (
                "The two edges require different literals (%s vs %s), so the loop closes "
                "only on text that matches both — plausible here, but not demonstrated. "
                "Confirm before editing."
                % (", ".join("`%s`" % c for c in sorted(core_sets[0])[:3]) or "unextractable",
                   ", ".join("`%s`" % c for c in sorted(core_sets[1])[:3]) or "unextractable"))
        else:
            severity, verdict = "low", (
                "A %d-hop loop: it closes only if one file matches all %d patterns at "
                "once, which is unlikely. Recorded for completeness, not as a live "
                "ping-pong." % (len(cycle), len(cycle)))

        out.append(Finding(
            "SK007", severity,
            "chainTo cycle%s: %s" % (" (live)" if live else "", chain),
            "These skills form a routing loop; without path history the router can "
            "oscillate and each hop consumes context. %s" % verdict,
            skill.path if skill else lib.root,
            rule.line() if rule else None,
            rule.label() if rule else "chainTo",
            src_name, "exact", None,
            {"cycle": list(cycle), "length": len(cycle), "live": live,
             "shared_literals": sorted(shared),
             "edge_literals": {"%s->%s" % e: sorted(c) for e, c in zip(edges, core_sets)}},
        ))
    return out


def detect_greedy_descriptions(lib):
    """SK008 — HEURISTIC (IDF + Bayes). Defect class 5.

    THE ARGUMENT. Trigger matching is retrieval. A description term's worth as a trigger
    is inversely proportional to its document frequency across the library — IDF. So:

      specificity(skill) = max over description terms of idf(term), normalized by log(N)

    A skill whose MOST distinctive term still appears in a dozen other descriptions has
    no anchor; it wins or loses on luck. Separately we score explicit universal claims
    ("ANY task", "whenever", "always use") which assert an unbounded activation domain.

    We then run the Bayes side: with N skills the prior for any one skill being the right
    one is ~1/N, so even a good-looking trigger has a low posterior; a trigger that also
    collides with K other skills has posterior roughly 1/(1+K). That collision count is
    computed from shared low-DF terms and reported per finding.

    Heuristic: descriptions are prose, IDF is bag-of-words, and a long precise
    description can score badly for stylistic reasons. Treat the ranked list as triage.
    """
    out = []
    index = lib.anchor_index()
    name_of = {s.rel: s.key for s in lib.skills}
    by_rel_pack = {s.rel: s.pack for s in lib.skills}

    HARD_QUANTIFIERS = (QUANTIFIER_PATTERNS[0][0], r"\bANY\b")

    # A description that explicitly claims prompts which do NOT contain the skill's own
    # anchor is greedy by construction, whatever its IDF profile says. This is the one
    # shape the reviewed library itself treats as a defect: `cursor-sdk` shipped
    # "even if they don't explicitly name the package" and the maintainers replaced that
    # clause with a scope boundary. Detecting the shape directly is far more reliable
    # than inferring it from term statistics.
    ANCHORLESS_CLAIM_RE = re.compile(
        r"even if (?:they|the user)?\s*(?:don't|do not|does not|doesn't|never)\s+"
        r"(?:explicitly\s+)?(?:mention|name|say|reference|specify)", re.I)

    for s in lib.skills:
        if not s.description:
            continue
        # A session-start skill is injected, never trigger-matched: its description is
        # documentation and cannot be "greedy". Scoring it asks the wrong question.
        if s.is_session_start():
            continue
        all_anchors = set(lib.doc_terms.get(s.rel, []))
        rare_anchors = {a for a in all_anchors if lib.df[a] <= 2}

        has_scoping = s.has_scoping_metadata()
        excluded = lib.excluded_claimants(s)
        anchorless_claim = bool(ANCHORLESS_CLAIM_RE.search(s.description))
        # Self-declared routers/umbrellas and hand-deconflicted skills are exempt from
        # the SOFT signals; a hard "ANY task involving X" claim or an explicit anchorless
        # claim still counts against them, because those are greedy no matter who is
        # making them.
        pre_deconflicted = s.declares_coordinator() or s.declares_scope_boundary()

        # Analyze each CLAUSE that makes a universal claim. A description may be precise
        # overall and still contain one sentence that claims the whole library — that
        # sentence is what fires.
        offenders = []
        for clause in SENTENCE_SPLIT_RE.split(s.description):
            if len(clause.split()) < 4:
                continue
            hard = any(re.search(p, clause, 0 if p == r"\bANY\b" else re.I)
                       for p in HARD_QUANTIFIERS)
            soft = any(re.search(p, clause, 0 if p == r"\bANY\b" else re.I)
                       for p, _ in QUANTIFIER_PATTERNS)
            if not soft:
                continue
            clause_anchors = set(anchor_terms(clause))
            clause_rare = {a for a in clause_anchors if lib.df[a] <= 2}
            # COLLISION = A RIVAL FOR *THIS CLAUSE*, NOT A SKILL SHARING ONE WORD.
            #
            # Counting every skill that shares any single anchor was the largest source of
            # phantom findings in the red-team pass: it read "SageMaker deployment,
            # training job, or other AWS automation" as colliding with nine skills because
            # nine descriptions somewhere contain "python" or "aws". A rival must satisfy
            # the clause's whole anchor CONJUNCTION — that is what the router would have
            # to confuse this skill with. Nested children, shared-prefix family siblings
            # and skills already named as an explicit boundary are then subtracted.
            shared_anchors = {a for a in clause_anchors if lib.df[a] >= 2}
            if shared_anchors:
                collisions = set.intersection(
                    *(index.get(a, set()) for a in shared_anchors))
            else:
                collisions = set()
            collisions.discard(s.rel)
            collisions -= excluded
            # A HARD quantifier ("ANY task involving Supabase") is greedy even when it is
            # perfectly anchored — being about Supabase is exactly the point; claiming ALL
            # Supabase work is what swallows the sibling specialists. So the anchoring
            # excuse applies only to soft quantifiers.
            if clause_rare and not hard:
                continue  # the claim is anchored to something almost unique to this skill
            if not clause_anchors and rare_anchors:
                # a clause with no identifier vocabulary at all, in a description that is
                # anchored elsewhere, is internal instruction prose rather than a
                # territory claim ("always use this skill to read it from config first")
                continue
            offenders.append({
                "clause": _short(clause, 180),
                "hard": hard,
                "anchors": sorted(clause_anchors),
                "collisions": sorted(name_of[r] for r in collisions),
                "collision_rels": sorted(collisions),
            })

        # "No rare anchor" IS NOT A FINDING ON ITS OWN.
        #
        # It was, and it produced the analyzer's least defensible output: `playwright-trace`
        # ("Inspect Playwright trace files from the command line — list actions, view
        # requests, console, errors, snapshots and screenshots") and `make-pr-easy-to-
        # review` were both accused of greed. Neither claims anything broad; they simply
        # describe themselves in ordinary nouns, and the anchor extractor only indexes
        # identifier-shaped tokens, so "trace" and "commits" are invisible to it. The
        # finding was therefore a statement about the extractor's vocabulary, not about
        # the skill.
        #
        # IDF now SCORES an over-claim; it no longer manufactures one. A skill must
        # actually assert a universal domain (an offender clause) or claim prompts that
        # lack its own anchor before the term statistics are brought to bear.
        no_rare_anchor_at_all = (not rare_anchors) and not has_scoping

        if not offenders and not anchorless_claim:
            continue

        worst = max(offenders, key=lambda o: (o["hard"], len(o["collisions"])), default=None)
        if worst:
            collision_count = len(worst["collisions"])
        else:
            rivals = set()
            for a in all_anchors:
                if lib.df[a] >= 2:
                    rivals |= index.get(a, set())
            collision_count = len((rivals - {s.rel} - excluded))

        # A greediness claim needs someone to be greedy AGAINST. With no rival claimant
        # left after family/nesting/boundary subtraction, "this description is broad" is
        # an observation about prose, not a routing defect, and the whole point of the
        # Bayes framing (posterior ~ 1/(1+K)) collapses at K=0.
        if collision_count == 0 and not anchorless_claim:
            continue

        # A SOFT claim whose every rival sits in its own pack is the "adjacent topics
        # share vocabulary" case, not a collision. Inside the `adobe` pack every skill
        # says "Adobe App Builder"; those words are the pack's name, so they cannot
        # discriminate between its members, and the word that DOES discriminate
        # ("testing", "scaffolding") is an ordinary noun the anchor index does not carry.
        # Cross-pack rivals are unaffected — that is where the recorded collisions were.
        # A hard quantifier or an anchorless claim still fires regardless of pack, because
        # "ANY task involving X" swallows its own siblings by construction.
        if worst and not worst["hard"] and not anchorless_claim:
            rival_packs = {by_rel_pack.get(r) for r in worst["collision_rels"]}
            if rival_packs and rival_packs <= {s.pack}:
                continue

        if anchorless_claim:
            # two independent over-claims (a hard universal quantifier AND an explicit
            # claim on prompts lacking this skill's anchor) is the strongest shape here
            severity = ("high" if (worst and worst["hard"] and collision_count >= 1)
                        else "medium" if collision_count >= 1 else "low")
        elif pre_deconflicted and not (worst and worst["hard"]):
            # self-declared router/umbrella, or a hand-written scope boundary: overlap
            # with the specialists it dispatches to (or ceded to) is the design
            continue
        elif worst and worst["hard"] and (collision_count >= 3 or worst["anchors"]):
            severity = "high" if collision_count >= 1 else "medium"
        elif worst and collision_count >= 3:
            severity = "medium"
        elif no_rare_anchor_at_all and collision_count >= 3:
            severity = "medium"
        elif worst or no_rare_anchor_at_all:
            severity = "low"
        else:
            continue

        posterior = 1.0 / (1.0 + collision_count) if collision_count else None
        detail = []
        if anchorless_claim:
            detail.append(
                "The description explicitly claims prompts that do NOT contain this "
                "skill's own anchor (\"even if they don't explicitly mention…\"). That "
                "clause asks the router to fire on exactly the prompts it has no evidence "
                "for; this library removed the same clause from another skill as a defect.")
        if worst:
            detail.append(
                'The clause "%s" makes a universal claim%s, and every anchor term in it '
                "(%s) is vocabulary shared across the library — none is rare enough to "
                "identify this skill."
                % (worst["clause"], " with a hard quantifier" if worst["hard"] else "",
                   ", ".join("`%s` (in %d descriptions)" % (a, lib.df[a])
                             for a in worst["anchors"][:5]) or "none at all"))
            if worst["collisions"]:
                detail.append(
                    "That vocabulary is also claimed by %d other skill(s): %s."
                    % (len(worst["collisions"]), ", ".join(worst["collisions"][:8])
                       + ("…" if len(worst["collisions"]) > 8 else "")))
        if no_rare_anchor_at_all:
            detail.append(
                "No identifier-shaped term in this whole description is rare in the "
                "library, so nothing in it can single this skill out.")
        if not has_scoping:
            detail.append(
                "There is no promptSignals/pathPatterns/importPatterns/bashPatterns "
                "metadata to narrow the match, so the description is the entire trigger.")
        if posterior:
            detail.append(
                "Bayes: with %d competing claimants the posterior that a firing on this "
                "vocabulary is correct is about %.0f%%." % (collision_count, 100 * posterior))

        out.append(Finding(
            "SK008", severity,
            "Greedy description: universal claim with no distinguishing anchor",
            " ".join(detail),
            s.path, s.doc.line_for(("description",)), "description", s.key, "heuristic", 5,
            {"unanchored_claims": offenders[:4],
             "rare_anchor_terms": sorted(rare_anchors)[:8],
             "collision_count": collision_count,
             "has_scoping_metadata": has_scoping,
             "anchorless_claim": anchorless_claim,
             "excluded_claimants": sorted(name_of[r] for r in excluded),
             "estimated_posterior": round(posterior, 3) if posterior else None},
        ))
    return out


def detect_unscoped(lib):
    """SK015 — HEURISTIC. A short description with no scoping metadata AND a live rival.

    THE GROUND-TRUTH CASE was `playwright-cli`: a bare 12-word description with no
    scoping metadata, matching on the bare word "Playwright" and therefore colliding with
    an Adobe AEM E2E skill that claims the same word. Note what makes it a defect — the
    COLLISION, not the missing metadata.

    WHY THE ABSENCE TEST ALONE IS WRONG. In the reviewed library 65 of 89 skills carry no
    routing metadata at all: only one pack uses that schema. Firing on "no metadata"
    therefore reports a house convention as a defect, and reports it arbitrarily — the
    original word-count cutoff selected 14 of the 65 for no reason connected to routing.
    Every one of those 14 was a false positive.

    THE RULE NOW: no scoping metadata, AND at least one rival in a DIFFERENT pack whose
    description claims this skill's whole distinguishing anchor set, AND no hand-written
    scope boundary already separating them. Cross-pack is the operative word: two
    Playwright skills in the Playwright pack divide one topic between them; a Playwright
    skill and an Adobe skill fighting over "Playwright" is the actual failure.
    """
    out = []
    index = lib.anchor_index()
    by_rel = {s.rel: s for s in lib.skills}
    for s in lib.skills:
        if not s.description or s.is_session_start():
            continue
        if s.has_scoping_metadata():
            continue
        if s.declares_scope_boundary():
            continue  # already deconflicted by hand, by name
        # The recorded case was characterised precisely: "a bare 12-word description with
        # NO scoping metadata". The original 30-word cutoff swept in `playwright-trace`
        # (18 words), which names its artifact ("Playwright trace files"), its interface
        # ("from the command line") and seven concrete outputs — a description that long
        # is a scope, even without metadata. Keep the window where the ground truth put it.
        words = len(s.description.split())
        if words > 12:
            continue

        anchors = {a for a in lib.doc_terms.get(s.rel, []) if lib.df[a] >= 2}
        if not anchors:
            continue
        rivals = set.intersection(*(index.get(a, set()) for a in anchors))
        rivals.discard(s.rel)
        rivals -= lib.excluded_claimants(s)
        cross_pack = {r for r in rivals if by_rel[r].pack != s.pack}
        if not cross_pack:
            continue

        names = sorted(by_rel[r].key for r in cross_pack)
        out.append(Finding(
            "SK015", "medium",
            "Unscoped skill: %d-word description, no scoping metadata, %d cross-pack rival(s)"
            % (words, len(cross_pack)),
            "There is no promptSignals block, no pathPatterns, no importPatterns and no "
            "bashPatterns, so this %d-word description is the entire trigger surface — and "
            "it is not exclusive: %s in %s claim(s) the same anchor vocabulary (%s) from a "
            "different pack. Neither description names the other as a boundary, so the "
            "router has nothing to break the tie with. Add a scope boundary naming the "
            "other skill, or add scoping metadata."
            % (words, ", ".join("`%s`" % n for n in names[:4]),
               ", ".join(sorted({by_rel[r].pack for r in cross_pack})),
               ", ".join("`%s`" % a for a in sorted(anchors)[:5])),
            s.path, s.doc.line_for(("description",)), "description", s.key, "heuristic", 5,
            {"word_count": words, "shared_anchors": sorted(anchors),
             "cross_pack_rivals": names},
        ))
    return out


def detect_territory(lib):
    """SK009 — HEURISTIC. Defect class 6.

    A skill claims territory through pathPatterns / bashPatterns / importPatterns. When a
    skill in pack P claims a path or package namespace that is uniquely owned by pack Q,
    it will acquire files and commands that belong to Q's specialist — and it will do so
    silently, because both skills look correct in isolation.

    Ownership is derived from names only (pack directory names + skill names). Heuristic
    because name-derived ownership can be wrong; a token claimed by two packs is skipped
    rather than guessed at.
    """
    out = []
    claims = defaultdict(list)  # (skill, owner pack) -> [(field, keypath, value, token)]
    for s in lib.skills:
        for field, keypath, value in s.acquisition_patterns():
            for token in extract_namespace_tokens(value):
                owner = lib.owner_pack(token)
                if not owner or owner == s.pack:
                    continue
                if normalize_token(token) in lib.pack_aliases.get(s.pack, set()):
                    continue
                claims[(s.rel, owner)].append((field, keypath, value, token))

    by_rel = {s.rel: s for s in lib.skills}
    for (rel, owner), items in sorted(claims.items()):
        s = by_rel[rel]
        fields = sorted({f for f, _, _, _ in items})
        tokens = sorted({t for _, _, _, t in items})
        first_keypath = items[0][1]
        listing = "; ".join("metadata.%s: `%s`" % (f, _short(v, 60))
                            for f, _, v, _ in items[:6])
        if len(items) > 6:
            listing += "; …and %d more" % (len(items) - 6)
        out.append(Finding(
            "SK009", "high",
            "Cross-pack territory claim: `%s` (pack `%s`) claims %d `%s` pattern(s)"
            % (s.key, s.pack, len(items), owner),
            "This skill's acquisition patterns claim namespace token(s) %s, which the `%s` "
            "pack owns: %s. pathPatterns/bashPatterns/importPatterns are how a skill says "
            "\"these files and commands are mine\", so this skill will be pulled in for work "
            "that belongs to the other pack's specialist — and both skills look correct in "
            "isolation. Routing to another vendor's skill via chainTo is legitimate; "
            "claiming its files and install commands is not."
            % (", ".join("`%s`" % t for t in tokens), owner, listing),
            s.path, s.doc.line_for(first_keypath),
            ".".join(str(p) for p in first_keypath), s.key, "heuristic", 6,
            {"fields": fields, "tokens": tokens, "owner_pack": owner,
             "claimant_pack": s.pack,
             "patterns": [{"field": f, "value": v, "token": t,
                           "line": s.doc.line_for(kp)} for f, kp, v, t in items]},
        ))
    return out


NAMESPACE_RE = re.compile(r"@([a-z0-9][a-z0-9\-]{2,})/")
PATHSEG_RE = re.compile(r"(?:^|[/'\"\\s])([a-z][a-z0-9\-]{3,})(?:/\*\*|/|\.\*)")
BAREWORD_RE = re.compile(r"\\b([a-z][a-z0-9\-]{3,})\\b")


def extract_namespace_tokens(pattern):
    """Namespace-ish tokens a pattern claims: @scope/, path roots, \\bbareword\\b."""
    if not isinstance(pattern, str):
        return set()
    low = pattern.lower()
    tokens = set(NAMESPACE_RE.findall(low))
    tokens |= set(PATHSEG_RE.findall(low))
    tokens |= set(BAREWORD_RE.findall(low))
    generic = {"lib", "src", "app", "apps", "test", "tests", "node", "dist", "build",
               "install", "add", "yarn", "pnpm", "npm", "bun", "client", "core", "next",
               "public", "scripts", "config", "types", "utils", "components", "pages"}
    return {t for t in tokens if t not in generic and len(t) >= 4}


def detect_rule_shadowing(lib):
    """SK010 — HEURISTIC (literal-core substring analysis). Defect class 7.

    Compiler analogy: two case labels whose value sets overlap. We approximate each
    rule's match set by the literals any match must contain. If every branch of rule B
    contains, as a substring, a required literal of some branch of rule A, then A fires
    whenever B does — A shadows B. Two shadowing rules with DIFFERENT targets is a real
    conflict: both fire, the router gets two answers. Same target is redundancy.

    Heuristic: literal containment is a sound approximation only for the simple
    `from ['"]pkg['"]` / bare-substring shapes these rules use. Anchors, lookarounds and
    character classes are ignored, so a flagged pair can still be disjoint in practice.
    """
    out = []

    # A core is only usable as evidence if it actually discriminates. `from`, `require`,
    # `export` and friends are regex scaffolding: they appear as the required literal of
    # dozens of rules, so "A's core is a substring of B's" tells us nothing. This is the
    # same IDF idea SK008 applies to descriptions, applied to the rule corpus: a core
    # that many rules share carries no information. A rule is analyzed only when EVERY
    # branch yields a usable core — otherwise we cannot bound its match set and we stay
    # silent rather than guess.
    SCAFFOLD = {"from", "require", "import", "export", "const", "function", "await",
                "return", "class", "async", "await(", "process", "process.env", "new",
                "default", "use", "client", "server", "config", "true", "false", "null"}
    core_df = Counter()
    staged = []
    for s in lib.skills:
        for rule in s.rules:
            cores = branch_cores(rule.pattern)
            if cores:
                lossy = any(branch_is_lossy(b)
                            for b in _split_top_level_alternation(rule.pattern or ""))
                staged.append((s, rule, cores, lossy))
                for c in set(cores):
                    core_df[c] += 1

    def usable(core):
        if len(core) < 5 or core in SCAFFOLD:
            return False
        # a namespaced/qualified token is inherently discriminating; a bare word must
        # also be rare across the rule corpus to count
        if any(ch in core for ch in "@/"):
            return True
        return core_df[core] <= 3

    rules = [(s, r, c, lossy) for (s, r, c, lossy) in staged if all(usable(x) for x in c)]

    def covers(a_cores, b_cores):
        """True if every branch of B contains some required literal of A."""
        return all(any(a in b for a in a_cores) for b in b_cores)

    # DIRECTIONALITY MATTERS. Literal extraction is an UNDER-approximation of what a
    # pattern requires, so it makes a rule look BROADER than it is. That is safe on the
    # narrow side of a shadowing claim and unsound on the broad side: reading
    # `@vercel/(postgres|kv)` as merely requiring `@vercel/` would "prove" it shadows
    # every @vercel rule in the pack, including `@vercel/connect`, which it does not
    # match at all. So only a rule with no lossy branch may be the broad side.

    # Pairs are collected first, then AGGREGATED per broad rule. One hub rule such as
    # marketplace's `NEON_|POSTGRES_|DATABASE_URL|...` legitimately subsumes six narrower
    # storage rules; that is one design observation, not six findings.
    pairs = defaultdict(list)
    seen = set()
    for i, (s_a, r_a, c_a, lossy_a) in enumerate(rules):
        for s_b, r_b, c_b, lossy_b in rules[i + 1:]:
            if s_a.pack != s_b.pack:
                continue  # cross-pack overlap is expected; same-pack is a real conflict
            if r_a.kind != r_b.kind:
                # a validate warning and a chainTo route on the same import are
                # complementary by design, not competing
                continue
            a_shadows_b = (not lossy_a) and (set(c_a) == set(c_b) or covers(c_a, c_b))
            b_shadows_a = (not lossy_b) and (set(c_a) == set(c_b) or covers(c_b, c_a))
            if not (a_shadows_b or b_shadows_a):
                continue
            broad, narrow = (s_a, r_a, c_a), (s_b, r_b, c_b)
            if b_shadows_a and not a_shadows_b:
                broad, narrow = (s_b, r_b, c_b), (s_a, r_a, c_a)
            sig = (broad[0].rel, broad[1].label(), narrow[0].rel, narrow[1].label())
            if sig in seen:
                continue
            seen.add(sig)
            pairs[(broad[0].rel, broad[1].label())].append((broad, narrow))

    # WHAT SURVIVES, AND WHY THE REST DOES NOT.
    #
    # The ground-truth instance of this class was two rules INSIDE ONE SKILL — a specific
    # `from '@vercel/postgres'` routing to `nextjs` and a bare `@vercel/postgres`
    # substring routing to `vercel-storage`. Both were evaluated together and disagreed.
    # Three weaker shapes were reported alongside it and all three are false positives:
    #
    #   * SAME TARGET ("redundancy"). A broad and a narrow rule both routing to the same
    #     place is not a conflict at all; the worst case is one extra advisory line. This
    #     produced 12 of 18 findings on the reviewed library and no action item.
    #   * CATALOGUE RULES. `vercel/marketplace` dispatches on a 13-alternative list of
    #     every database package in the ecosystem, on purpose — it is the pack's router.
    #     Subsuming each storage specialist's narrower rule IS its function. A rule
    #     enumerating >= 4 alternatives is treated as a dispatch table, not a competitor.
    #   * MUTUAL CROSS-REFERENCES. `eve` <-> `vercel-connect` point at each other on the
    #     same import so that whichever you are in you get the other; that is the SK007
    #     cycle finding, already reported once, and repeating it here is double-counting.
    #
    # Cross-skill conflicts that survive all three are kept, but at LOW: two rules in two
    # different skills are only in contention if the router evaluates both at once, which
    # is a property of the router this analyzer cannot read.
    for _, group in sorted(pairs.items()):
        broad = group[0][0]
        narrows = [n for _, n in group]
        conflicts = [n for n in narrows
                     if n[1].target and broad[1].target and n[1].target != broad[1].target]
        if not conflicts:
            continue  # same target: redundancy, not a routing defect

        is_catalogue = len(set(broad[2])) >= 4
        if is_catalogue:
            continue  # a dispatch table subsuming its own specialists is the design

        mutual = [n for n in conflicts
                  if n[0] is not broad[0]
                  and n[1].target == broad[0].name and broad[1].target == n[0].name]
        conflicts = [n for n in conflicts if n not in mutual]
        if not conflicts:
            continue  # pure A<->B cross-reference: SK007 reports this loop once

        same_skill_conflict = any(n[0] is broad[0] for n in conflicts)
        narrows = conflicts
        severity = "high" if same_skill_conflict else "low"
        verdict = (
            "%d of them route somewhere DIFFERENT (%s). Both rules fire on the same "
            "text and the router gets two answers, with no longest-prefix rule to "
            "break the tie — whichever the model reads last effectively wins."
            % (len(conflicts),
               ", ".join(sorted({"%s -> %s" % (n[1].label(), n[1].target)
                                 for n in conflicts})[:4])))
        if same_skill_conflict:
            verdict += (" Both rules are inside this one skill, so they are evaluated "
                        "together and the disagreement is unconditional.")
        else:
            verdict += (" The two rules live in different skills, so they contend only if "
                        "the router scores every skill's rules against the same file — "
                        "verify that before editing.")

        narrow_desc = "; ".join(
            "%s%s %s" % (("%s:" % n[0].key) if n[0] is not broad[0] else "",
                         n[1].label(), _short(n[1].pattern, 46))
            for n in narrows[:5])
        if len(narrows) > 5:
            narrow_desc += "; …and %d more" % (len(narrows) - 5)

        out.append(Finding(
            "SK010", severity,
            "Rule `%s %s` shadows %d narrower rule(s) in pack `%s`"
            % (broad[0].key, broad[1].label(), len(narrows), broad[0].pack),
            "Broad pattern %s requires only literal(s) %s, which every one of these "
            "narrower patterns already contains: %s. %s"
            % (_short(broad[1].pattern, 80), broad[2], narrow_desc, verdict),
            broad[0].path, broad[1].line("pattern"),
            "%s.pattern" % broad[1].label(), broad[0].key, "heuristic", 7,
            {"broad_skill": broad[0].key, "broad_rule": broad[1].label(),
             "broad_pattern": broad[1].pattern, "broad_target": broad[1].target,
             "broad_cores": broad[2], "kind": broad[1].kind,
             "shadowed_count": len(narrows),
             "conflicting_count": len(conflicts),
             "shadowed": [{"skill": n[0].key, "rule": n[1].label(),
                           "pattern": n[1].pattern, "target": n[1].target,
                           "file": n[0].path, "line": n[1].line("pattern")}
                          for n in narrows]},
        ))
    return out


def detect_dead_guards(lib):
    """SK011 + SK013 — Defect class 4. Two opposite ways a negative guard fails.

    A `skipIfFileContains` guard exists to suppress a rule's message once the author has
    already done the right thing. It can fail in exactly two directions:

    SK013 (EXACT) — the guard is TOO BROAD and fires on the very code the rule is meant
    to catch, so the rule is unreachable. Proven, not guessed: a guard branch that is a
    PURE LITERAL fires on any text containing that literal, so if such a literal sits
    inside a literal that every branch of the pattern REQUIRES, the guard is satisfied by
    every possible match. Pattern `from '@vercel/kv'` with guard `@vercel/kv` is the
    canonical case. See the inline note for why the guard side must be pure literals.

    SK011 (HEURISTIC) — the guard is TOO NARROW because it names something that does not
    exist, so it can never fire and the rule nags forever on already-correct code. This
    is the ground-truth `@vercel/ai-gateway` shape, where the real package is
    `@ai-sdk/gateway` and the guard's literal cannot occur inside it. With no network we
    cannot check a registry, so we ask the weaker but answerable question: does this
    library itself ever mention the name outside a guard? A wrong-scope near-miss
    (`@vercel/ai-gateway` vs the `@ai-sdk/gateway` the library does use) is the typo
    signal that promotes a finding to HIGH; without it the finding stays MEDIUM and says
    plainly that it cannot distinguish a typo from an unfamiliar-but-real package.
    """
    out = []
    for s in lib.skills:
        for rule in s.rules:
            if not rule.guard or not isinstance(rule.guard, str):
                continue
            guard_branches = _split_top_level_alternation(rule.guard)
            pattern_branches = _split_top_level_alternation(rule.pattern or "")

            # -- SK013 EXACT: the guard is satisfied by the pattern's own required text ---
            #
            # Sound form of the argument. A guard branch that is a PURE LITERAL (no regex
            # operators at all) fires on any text containing that literal. If, for every
            # branch of the pattern, one of those pure-literal guards sits inside a literal
            # the pattern branch REQUIRES, then every text the pattern can match already
            # satisfies the guard: the rule is skipped 100% of the time. Unreachable code.
            #
            # Restricting the guard side to pure literals is what makes this exact. An
            # earlier version compared extracted literal SETS, which under-approximates the
            # guard's requirements — reading `from\s+['"]ai['"]` as merely requiring "from"
            # — and that manufactured false positives on rules like "flag langchain unless
            # the file imports from 'ai'". Under-approximating the guard is never allowed;
            # under-approximating the pattern only costs us recall.
            pure_guards = [g for g in (pure_literal(b) for b in guard_branches) if g]
            if rule.pattern and pattern_branches and pure_guards:
                pattern_sets = [
                    [l.lower() for l in _literal_runs(b) if len(l.strip()) >= 3]
                    for b in pattern_branches]
                if all(pattern_sets) and len(pattern_sets) == len(pattern_branches):
                    def implied(plits):
                        return any(g in lit for g in pure_guards for lit in plits)
                    if all(implied(ps) for ps in pattern_sets):
                        hits = sorted({g for g in pure_guards
                                       for ps in pattern_sets for lit in ps if g in lit})
                        out.append(Finding(
                            "SK013", "high",
                            "Unreachable rule: the guard always fires on its own pattern",
                            "Every branch of %s requires text that already contains the "
                            "literal guard %s. skipIfFileContains is therefore satisfied by "
                            "the very code the pattern is written to catch, so the rule is "
                            "skipped 100%% of the time and can never emit its message."
                            % (rule.label(), ", ".join("`%s`" % h for h in hits)),
                            s.path, rule.line("skipIfFileContains"),
                            "%s.skipIfFileContains" % rule.label(), s.key, "exact", 4,
                            {"rule": rule.label(), "pattern": rule.pattern,
                             "guard": rule.guard,
                             "pattern_literals": sorted({l for ps in pattern_sets for l in ps}),
                             "always_matching_guards": hits},
                        ))
                        continue

            # -- SK011 heuristic: guard alternatives that name no real package -----------
            #
            # A guard alternative is normally the CORRECTED form of whatever the pattern
            # flags: "skip the nag once they are on @ai-sdk/gateway". We test each
            # package-shaped alternative against the package universe built from actual
            # import/require/install sites. If a package-shaped alternative is not a
            # substring of ANY package this library uses, it cannot fire on correct code.
            #
            # This is exactly the `@vercel/ai-gateway` / `ai-gateway` shape: the real
            # package is `@ai-sdk/gateway`, and the literal `ai-gateway` does not occur
            # inside it, so those alternatives are unreachable no matter what the author
            # intended. Reported per alternative rather than per rule, because a guard
            # with one live alternative and two dead ones is weaker than it looks but not
            # completely inert.
            alternatives = []
            for branch in guard_branches:
                lits = [l for l in _literal_runs(branch) if len(l.strip()) >= 4]
                if lits:
                    alternatives.append(max(lits, key=len).strip().lower())
            if not alternatives:
                continue

            # Only two token shapes are checkable with confidence:
            #   - a scoped package `@scope/name`, which is unambiguous, and
            #   - a pure-alphabetic kebab identifier (>=2 segments, no digits, no dots),
            #     which is the shape of a skill name or a plain npm package.
            # Model IDs (`gemini-3.1-flash-image-preview`), code fragments
            # (`function handleSubmit`) and path fragments (`app/layout.`) are excluded:
            # they are not names whose existence this analyzer can reason about.
            def checkable(lit):
                if re.fullmatch(r"@[a-z0-9][a-z0-9\-.]*/[a-z0-9][a-z0-9\-./]*", lit):
                    return True
                return bool(re.fullmatch(r"[a-z]{2,}(?:-[a-z]{2,}){1,4}", lit)) and len(lit) >= 8

            candidates = [a for a in alternatives if checkable(a)]
            if not candidates:
                continue
            unreachable = [a for a in candidates if not lib.mentioned_outside_guards(a)]
            if not unreachable:
                continue

            live = [a for a in alternatives
                    if a not in unreachable and lib.mentioned_outside_guards(a)]
            fully_dead = not live

            # A near-miss is what separates "package this library simply never discusses"
            # (could be perfectly real — @vercel/otel exists, we just cannot check the
            # registry offline) from "almost certainly a typo". The strongest signal is a
            # WRONG-SCOPE miss: the guard says `@vercel/ai-gateway` while the library
            # actually uses `@ai-sdk/gateway` — same trailing name, different scope. That
            # is the ground-truth shape, and it is the only case we call HIGH.
            near, typo_suspicion = {}, []
            for alt in unreachable:
                candidate = lib.nearest_package(alt)
                near[alt] = candidate
                if alt.startswith("@") and candidate and candidate.startswith("@"):
                    a_scope, _, a_tail = alt.partition("/")
                    c_scope, _, c_tail = candidate.partition("/")
                    if a_scope != c_scope and (a_tail in c_tail or c_tail in a_tail):
                        typo_suspicion.append((alt, candidate))
                elif not alt.startswith("@"):
                    skill_near = _closest(alt, lib.names)
                    # require a shared multi-segment tail, not just edit distance: skill
                    # names are the closed world here, so `next-best-practices` vs
                    # `react-best-practices` is decisive, but two names that merely look
                    # alike are not.
                    if skill_near and _shared_name_tail(alt, skill_near):
                        near[alt] = skill_near
                        typo_suspicion.append((alt, skill_near))

            # WITHOUT A NEAR-MISS THERE IS NO FINDING.
            #
            # "This library never mentions @vercel/otel" is true and uninteresting:
            # @vercel/otel is a real package, and a guard naming the corrected form of
            # code the skill is nagging about has no obligation to also discuss it in
            # prose. Offline and with no registry, absence is not evidence.
            #
            # What IS evidence is a near-miss with a name the library demonstrably uses —
            # `@vercel/ai-gateway` against the `@ai-sdk/gateway` in this very library
            # (same tail, wrong scope), or `next-best-practices` against `react-best-
            # practices` (a skill name, where this library is the closed world and
            # therefore authoritative). A "nearest match" that shares only the npm scope
            # (`@vercel/auth` -> `@vercel/kv`, `@vercel/otel` -> `@vercel/postgres`) is an
            # artifact of edit distance over a common prefix and proves nothing; those
            # four findings were all false positives on the reviewed library.
            if not typo_suspicion:
                continue
            severity = "high"
            near_text = "; ".join(
                "`%s` (nearest name the library does use: %s)"
                % (a, ("`%s`" % n) if n else "none")
                for a, n in near.items())

            if typo_suspicion:
                verdict = (
                    "This looks like a typo rather than an unfamiliar package: %s. If that "
                    "is right the guard can never fire, and the rule nags permanently on "
                    "code that is already correct."
                    % "; ".join("`%s` vs the `%s` this library actually uses" % (a, c)
                                for a, c in typo_suspicion))
            else:
                verdict = (
                    "The package may well be real — this analyzer has no registry access "
                    "and can only observe that the library never mentions it. VERIFY: if "
                    "the name is wrong, the guard cannot fire and the rule nags forever; if "
                    "it is right, the skill should reference it somewhere other than a "
                    "guard so a reader can act on the advice.")

            out.append(Finding(
                "SK011", severity,
                "%s guard: %d alternative(s) name something the library never mentions"
                % ("Likely-dead" if typo_suspicion else "Unverifiable", len(unreachable)),
                "%s skipIfFileContains offers %d alternative(s); %d of them name a package "
                "or skill that appears NOWHERE in this library outside of guard values — "
                "not in this rule's own message, not in any prose, not in any code sample: "
                "%s. %s%s"
                % (rule.label(), len(alternatives), len(unreachable), near_text, verdict,
                   ("" if fully_dead else
                    " Other alternative(s) in this guard do resolve, so the guard is "
                    "weakened rather than wholly inert.")),
                s.path, rule.line("skipIfFileContains"),
                "%s.skipIfFileContains" % rule.label(), s.key, "heuristic", 4,
                {"rule": rule.label(), "guard": rule.guard, "pattern": rule.pattern,
                 "unreachable_alternatives": unreachable,
                 "nearest_known_names": near,
                 "typo_suspicion": [{"guard_token": a, "library_uses": c}
                                    for a, c in typo_suspicion],
                 "live_alternatives": live,
                 "fully_dead": fully_dead},
            ))
    return out


def detect_vendor_steering(lib):
    """SK012 — HEURISTIC, FLAGGED FOR HUMAN REVIEW. Defect class 1 — the novel one.

    THE CLASS. Inside a vendor's own single-vendor plugin, "you imported a competitor's
    client, here is our alternative" is correct product behaviour. Dropped into a
    MULTI-VENDOR library, the same rule fires on a dependency the user deliberately
    chose and steers them off it. No single-vendor linting would ever flag this, because
    inside that vendor's repo it is not a defect.

    THE TEST. For each chainTo/validate rule we compare the vendor named by the PATTERN
    against the vendors named by the MESSAGE:

      - if the pattern names a product owned by the rule's OWN pack, this is a
        first-party deprecation ("@vercel/kv is sunset, use @upstash/redis") — legitimate,
        not flagged;
      - if NO pattern product belongs to the rule's own pack, the rule is reaching into
        someone else's stack. If the message then names a DIFFERENT product together with
        a steering cue ("alternative", "recommended", "instead", "migrate"), the rule is
        steering a user off a deliberate choice.

    Heuristic and lexicon-dependent — "is X a competitor of Y" is world knowledge, not
    file structure. Every hit needs a human to decide whether the steer is appropriate
    in THIS library. We never claim certainty.
    """
    out = []
    for s in lib.skills:
        for rule in s.rules:
            if not rule.message or not isinstance(rule.pattern, str):
                continue
            pattern_products = find_products(rule.pattern)
            if not pattern_products:
                continue
            own_pack_products = {p for p in pattern_products if lib.owner_pack(p) == s.pack}
            if own_pack_products:
                continue  # first-party deprecation: legitimate

            message_products = find_products(rule.message)
            pitched = message_products - pattern_products
            if not pitched:
                continue
            # routing to the skill that owns the pattern's product is not steering
            if isinstance(rule.target, str) and rule.target in lib.names:
                target_skill = lib.by_name[rule.target][0]
                if find_products(rule.target) & pattern_products:
                    continue
                if target_skill.pack != s.pack and not pitched:
                    continue

            cues = [c for c in STEERING_CUES if c in rule.message.lower()]
            if not cues:
                continue

            competitor_packs = {lib.owner_pack(p) for p in pattern_products}
            competitor_packs.discard(None)
            competitor_packs.discard(s.pack)

            # SEVERITY = HOW MUCH THIS LIBRARY HAS ALREADY COMMITTED TO THE STEERED-FROM
            # PRODUCT. The harm in this class is steering a user off something they chose;
            # the library itself is the only evidence available for what was chosen.
            #
            #   pack       — a whole vendor pack is vendored for it. Supabase in the
            #                reviewed library: the user's actual database provider, and
            #                the recorded ground-truth defect. HIGH.
            #   supported  — no pack, but the skill this rule ROUTES TO covers the product
            #                as a first-class option (`vercel/auth` lists `NextAuth` and
            #                `Auth.js` among its retrieval entities and its own body says
            #                "do not rewrite to Clerk unless asked"). Steering away then
            #                contradicts the destination's own guidance. MEDIUM.
            #   none       — the library has no content for it at all (MongoDB, Turso,
            #                Convex). Then this is a vendor plugin promoting its own
            #                products with nothing in the library to contradict, which is
            #                what every vendor plugin does. Recorded at LOW so the class
            #                stays visible without four standing accusations.
            supported_by = []
            if isinstance(rule.target, str) and rule.target in lib.names:
                target_skill = lib.by_name[rule.target][0]
                retrieval = target_skill.fm.get("retrieval")
                blob = " ".join([target_skill.description or ""] + [
                    str(v) for k in ("entities", "aliases", "intents")
                    for v in (retrieval.get(k) or [] if isinstance(retrieval, dict) else [])])
                supported_by = sorted(find_products(blob) & pattern_products)

            if competitor_packs:
                severity, basis = "high", (
                    " The matched product has its own pack in this library (`%s`), so the "
                    "user has clearly adopted it — this is the recorded defect shape."
                    % ", ".join(sorted(competitor_packs)))
            elif supported_by:
                severity, basis = "medium", (
                    " The skill this rule routes to (`%s`) itself lists %s as a supported "
                    "option, so the steer contradicts its own destination."
                    % (rule.target, ", ".join("`%s`" % p for p in supported_by)))
            else:
                severity, basis = "low", (
                    " No pack and no skill in this library covers %s, so nothing here "
                    "contradicts the steer — it is ordinary first-party promotion. Noted "
                    "only so the class stays visible: add a pack for that product and this "
                    "rule becomes a live defect."
                    % ", ".join("`%s`" % p for p in sorted(pattern_products)))

            out.append(Finding(
                "SK012", severity,
                "Possible vendor steering: rule on `%s` pitches `%s`"
                % (", ".join(sorted(pattern_products)), ", ".join(sorted(pitched))),
                "%s matches %s — a product this skill's pack (`%s`) does not own — and its "
                "message pitches %s using steering language (%s).%s Inside a single-vendor "
                "plugin this is normal product behaviour; inside a multi-vendor library it "
                "fires on a dependency the user deliberately chose. HUMAN REVIEW: decide "
                "whether the steer is appropriate here, or whether the rule should simply "
                "hand off to that product's own skill."
                % (rule.label(), ", ".join("`%s`" % p for p in sorted(pattern_products)),
                   s.pack, ", ".join("`%s`" % p for p in sorted(pitched)),
                   ", ".join('"%s"' % c for c in cues[:3]), basis),
                s.path, rule.line("message"), "%s.message" % rule.label(), s.key,
                "heuristic", 1,
                {"rule": rule.label(), "pattern": rule.pattern,
                 "message": _short(rule.message, 300),
                 "pattern_products": sorted(pattern_products),
                 "pitched_products": sorted(pitched),
                 "cues": cues, "target": rule.target,
                 "competitor_packs": sorted(competitor_packs),
                 "supported_by_target": supported_by},
            ))
    return out


PROSE_REF_RES = [
    re.compile(r"`([a-z][a-z0-9]*(?:-[a-z0-9]+){1,4})`\s+skill\b", re.I),
    re.compile(r"\bskill\s*[:=]?\s*`([a-z][a-z0-9]*(?:-[a-z0-9]+){1,4})`", re.I),
    re.compile(r"\buse\s+(?:the\s+)?`([a-z][a-z0-9]*(?:-[a-z0-9]+){1,4})`\b", re.I),
]
NEGATION_RE = re.compile(
    r"\b(no|not|never|does\s+not|doesn't|don't|isn't|is\s+not|unavailable|"
    r"missing|absent|nonexistent|non-existent|removed|deleted|there\s+is\s+no)\b", re.I)

# Clause boundaries. A negation only cancels a skill reference when it GOVERNS that
# reference, and English puts a governing negation in the same clause. Splitting on
# strong punctuation and on subordinating conjunctions is what separates
#
#   "delegate long runs to the `hugging-face-jobs` skill so the session is not held open"
#                                                     ^-- negation, different clause
#
# from the case the suppression exists for:
#
#   "there is no `hugging-face-jobs` skill in this snapshot"
#
# Testing the whole LINE, as an earlier version did, conflates the two and silently
# discards the finding whenever the sentence happens to contain "not"/"no"/"never"
# anywhere at all — which ordinary documentation prose does constantly.
CLAUSE_SPLIT_RE = re.compile(
    r"[.;:!?]"
    r"|\s+—\s+|\s+--\s+"
    r"|,\s+"
    r"|\s+(?:so|because|while|although|though|but|whereas|since|unless|and\s+then)\s+",
    re.I)

# A negation this close in front of a reference is treated as governing it even across a
# clause boundary, so list forms such as "not available: `foo-bar`, `baz-qux`" stay
# suppressed.
NEGATION_LOOKBACK = 40


def _clause_around(text, start, end):
    """The clause of `text` that contains the span [start, end)."""
    lo = 0
    for m in CLAUSE_SPLIT_RE.finditer(text):
        if m.end() <= start:
            lo = m.end()
        elif m.start() >= end:
            return text[lo:m.start()]
    return text[lo:]


def _reference_is_negated(line, start, end):
    if NEGATION_RE.search(_clause_around(line, start, end)):
        return True
    return bool(NEGATION_RE.search(line[max(0, start - NEGATION_LOOKBACK):start]))


def detect_prose_dangling(lib):
    """SK014 — HEURISTIC. Defect class 9 (the prose half).

    Bodies routinely say "use the `foo-bar` skill". If `foo-bar` is not in the library
    the model is being told to reach for something that does not exist, and will either
    hallucinate its content or stall.

    Heuristic on two counts: the extraction regexes can catch a package name or CLI
    subcommand that merely looks like a skill name, and we suppress references whose own
    clause carries a negation ("there is no `foo-bar` skill in this snapshot"), which can
    both over- and under-suppress.

    The negation test is CLAUSE-scoped, not line-scoped. Testing the whole line is the
    difference between catching and missing the ground-truth case: a sentence like
    "delegate long runs to the `hugging-face-jobs` skill so the session is not held open"
    is an instruction to use a skill that does not exist, but a line-wide test sees the
    trailing "is not" and throws the finding away. Ordinary documentation prose contains
    "no"/"not"/"never" constantly, so line-wide suppression silences most of this
    detector on exactly the bodies it is meant to read.
    """
    out = []
    for s in lib.skills:
        if not s.body:
            continue
        lines = s.body.splitlines()
        body_start = s.doc.text.count("\n", 0, len(s.doc.text) - len(s.body)) + 1
        seen = set()
        for i, line in enumerate(lines):
            for rx in PROSE_REF_RES:
                for m in rx.finditer(line):
                    ref = m.group(1).lower()
                    if ref in lib.names or ref in seen:
                        continue
                    if ref == s.name or ref == s.dirname:
                        continue
                    # a referenced name must plausibly be a skill: kebab-case, and the
                    # library must not contain it as a normal package/command token
                    if len(ref) < 6 or ref.count("-") < 1:
                        continue
                    if _reference_is_negated(line, m.start(), m.end()):
                        continue
                    seen.add(ref)
                    out.append(Finding(
                        "SK014", "medium",
                        "Prose references skill `%s`, which does not exist" % ref,
                        "The body tells the model to use `%s`, but no skill in this library "
                        "declares that name. Closest existing: %s. The model will either "
                        "hallucinate its contents or stall looking for it."
                        % (ref, ("`%s`" % _closest(ref, lib.names)) if _closest(ref, lib.names)
                           else "none"),
                        s.path, body_start + i, None, s.key, "heuristic", 9,
                        {"referenced": ref, "line_text": _short(line.strip(), 160)},
                    ))
    return out


# Single-segment names count here (unlike SK014, which requires a hyphen to keep
# nonexistent-name guesses conservative): this reference is validated against the real
# skill set, and the recorded case — "load the `marketplace` skill" — has no hyphen.
SKILL_REF_RE = re.compile(r"`([a-z][a-z0-9]{2,}(?:-[a-z0-9]+){0,4})`")
PRECEDENCE_VERB_RE = re.compile(
    r"\b(load|use|check|consult|read|run|invoke|reach for|start with|go to)\b", re.I)
PRECEDENCE_CUE_RE = re.compile(
    r"\b(first|before|ahead of|prior to|up front|to begin)\b", re.I)


def detect_priority_inversion(lib):
    """SK016 — HEURISTIC. Guidance says "consult X first" while X ranks near the bottom.

    THE ORIGINAL TEST WAS NOT A TEST. It fired whenever priority(source) > priority(target)
    across a chainTo edge. On the reviewed library that is 19 edges; flipping the
    comparison gives 18 edges. A predicate that flags roughly half the graph either way is
    measuring the graph's shape, not a defect — `chainTo` is an unconditional "also load
    this" edge that fires on its own pattern, so priority never gets a chance to suppress
    it. Both directions were false positives.

    THE SHAPE THE REVIEW ACTUALLY RECORDED is different and is checkable: a high-priority,
    always-loaded skill whose prose instructs the agent to consult another skill FIRST,
    while that other skill's own priority puts it below the library median — so the skill
    the guidance depends on loses every contest it enters. In the reviewed library this
    was `knowledge-update` ("check the Marketplace first") against `marketplace` at
    priority 3 of 10, and the fix was to raise `marketplace` to 9. Post-fix the library is
    correctly silent here.
    """
    out = []
    median = lib.median_priority()
    if median is None:
        return out
    seen = set()
    for s in lib.skills:
        text = "%s\n%s" % (s.description or "", s.body or "")
        for m in SKILL_REF_RE.finditer(text):
            ref = m.group(1)
            if ref not in lib.names or ref == s.name:
                continue
            # Precedence is asserted around the reference, not necessarily after it
            # ("your FIRST action is to load the `marketplace` skill ... BEFORE you
            # recommend a provider"), so read a window on both sides.
            window = text[max(0, m.start() - 90):m.end() + 90]
            if not (PRECEDENCE_VERB_RE.search(window) and PRECEDENCE_CUE_RE.search(window)):
                continue
            target = lib.by_name[ref][0]
            pb = target.priority()
            if pb is None or pb >= median:
                continue
            if (s.key, ref) in seen:
                continue
            seen.add((s.key, ref))
            out.append(Finding(
                "SK016", "medium",
                "Priority inversion: `%s` says consult `%s` first, but `%s` ranks %s of a "
                "median %s" % (s.key, ref, ref, pb, median),
                "This skill's guidance makes `%s` a precedence dependency (\"%s\"), yet "
                "`%s` carries priority %s against a library median of %s — below most of "
                "the skills it would have to beat to be loaded. The instruction and the "
                "ranking pull in opposite directions: raise `%s` above the specialists it "
                "is supposed to precede, or drop the precedence claim."
                % (ref, " ".join(window.split())[:110], ref, pb, median, ref),
                s.path, None, "body", s.key, "heuristic", None,
                {"source": s.key, "source_priority": s.priority(), "target": ref,
                 "target_priority": pb, "library_median_priority": median,
                 "quote": " ".join(window.split())[:160]},
            ))
    return out


DETECTORS = [
    detect_frontmatter,
    detect_duplicate_names,
    detect_schema_outliers,
    detect_overlay_drift,
    detect_dangling_routes,
    detect_self_routes,
    detect_cycles,
    detect_greedy_descriptions,
    detect_unscoped,
    detect_territory,
    detect_rule_shadowing,
    detect_dead_guards,
    detect_vendor_steering,
    detect_prose_dangling,
    detect_priority_inversion,
]

CODE_TITLES = {
    "SK001": "Invalid or missing frontmatter",
    "SK002": "Duplicate skill name",
    "SK003": "Schema-outlier key placement",
    "SK004": "SKILL.md / overlay.yaml drift",
    "SK005": "Dangling route reference",
    "SK006": "No-op self route",
    "SK007": "chainTo cycle",
    "SK008": "Greedy description",
    "SK009": "Cross-pack territory claim",
    "SK010": "Overlapping / shadowing rules",
    "SK011": "Unreachable / unverifiable guard token",
    "SK012": "Possible vendor steering",
    "SK013": "Unreachable rule (guard always fires)",
    "SK014": "Dangling prose skill reference",
    "SK015": "Unscoped skill",
    "SK016": "Priority inversion",
}

EXACT_CODES = {"SK001", "SK002", "SK004", "SK005", "SK006", "SK007", "SK013"}


# --------------------------------------------------------------------------------------
# Reporting
# --------------------------------------------------------------------------------------

def bayes_worked_example(n, sensitivity=0.90, specificity=0.95):
    prior = 1.0 / max(1, n)
    tp = sensitivity * prior
    fp = (1.0 - specificity) * (1.0 - prior)
    posterior = tp / (tp + fp) if (tp + fp) else 0.0
    return prior, posterior


def render_text(lib, findings, min_severity, stats):
    lines = []
    w = lines.append
    n = len(lib.skills)
    prior, posterior = bayes_worked_example(n)

    w("=" * 86)
    w("SKILL LIBRARY AUDIT — %s" % lib.root)
    w("=" * 86)
    w("")
    w("Library: %d skills across %d packs, %d overlay.yaml files, %d routing rules."
      % (n, len(lib.packs), len(lib.overlays), stats["rule_count"]))
    w("Packs: %s" % ", ".join("%s (%d)" % (p, len(s)) for p, s in sorted(lib.packs.items())))
    w("")
    w("-- Why scale changes the standard ------------------------------------------------")
    w("A trigger is a diagnostic test for \"is this the right skill?\". With N=%d the prior" % n)
    w("that any one skill is correct is 1/N = %.2f%%. A trigger with 90%% sensitivity and" % (100 * prior))
    w("95%% specificity therefore yields a posterior of just %.1f%% — about %.0f%% of its" % (
        100 * posterior, 100 * (1 - posterior)))
    w("firings would be wrong. That is the quantitative reason a description that would be")
    w("fine in a 5-skill plugin becomes destructive here, and why SK008 scores greediness")
    w("against library size (IDF over anchor terms) rather than against a fixed word count.")
    w("")

    by_sev = defaultdict(list)
    for f in findings:
        by_sev[f.severity].append(f)

    w("-- Findings by severity ----------------------------------------------------------")
    for sev in ("high", "medium", "low"):
        w("  %-6s %3d" % (SEV_LABEL[sev], len(by_sev[sev])))
    w("  %-6s %3d  (exact: %d, heuristic: %d)" % (
        "TOTAL", len(findings),
        sum(1 for f in findings if f.confidence == "exact"),
        sum(1 for f in findings if f.confidence == "heuristic")))
    w("")
    w("-- Findings by detector ----------------------------------------------------------")
    counts = Counter(f.code for f in findings)
    for code in sorted(CODE_TITLES):
        if counts.get(code):
            w("  %-6s %3d  %-38s [%s]" % (
                code, counts[code], CODE_TITLES[code],
                "exact" if code in EXACT_CODES else "heuristic"))
    w("")

    if not findings:
        w("No findings at or above severity '%s'." % min_severity)
        return "\n".join(lines)

    for sev in ("high", "medium", "low"):
        group = by_sev[sev]
        if not group:
            continue
        w("")
        w("=" * 86)
        w("%s — %d finding(s)" % (SEV_LABEL[sev], len(group)))
        w("=" * 86)
        for f in group:
            w("")
            w("[%s/%s] %s  (%s%s)" % (
                sev.upper()[0], f.code, f.title, f.confidence,
                (", ground-truth class %d" % f.defect_class) if f.defect_class else ""))
            w("      at %s" % f.location())
            if f.skill:
                w("   skill %s" % f.skill)
            for chunk in _wrap(f.detail, 80):
                w("      %s" % chunk)
            extra = _evidence_lines(f)
            for chunk in extra:
                w("      %s" % chunk)
    return "\n".join(lines)


def _evidence_lines(f):
    out = []
    ev = f.evidence
    if f.code == "SK010":
        for n in (ev.get("shadowed") or [])[:5]:
            out.append("shadowed: %s:%s  %s %s -> %s" % (
                n.get("file"), n.get("line"), n.get("skill"), n.get("rule"), n.get("target")))
    if f.code == "SK004" and ev.get("skill_md_path"):
        out.append("counterpart: %s:%s" % (ev["skill_md_path"], ev.get("skill_md_line")))
    if f.code == "SK012":
        out.append("message: %s" % ev.get("message"))
    if f.code in ("SK011", "SK013"):
        out.append("pattern: %s" % _short(ev.get("pattern"), 110))
        out.append("guard:   %s" % _short(ev.get("guard"), 110))
    if f.code == "SK014":
        out.append("line: %s" % ev.get("line_text"))
    return out


def _wrap(text, width):
    import textwrap
    return textwrap.wrap(" ".join(str(text).split()), width=width) or [""]


def render_json(lib, findings, min_severity, stats):
    n = len(lib.skills)
    prior, posterior = bayes_worked_example(n)
    return json.dumps({
        "root": lib.root,
        "summary": {
            "skills": n,
            "packs": {p: len(s) for p, s in sorted(lib.packs.items())},
            "overlay_files": len(lib.overlays),
            "routing_rules": stats["rule_count"],
            "min_severity": min_severity,
            "findings_total": len(findings),
            "findings_by_severity": {
                sev: sum(1 for f in findings if f.severity == sev)
                for sev in ("high", "medium", "low")},
            "findings_by_code": dict(Counter(f.code for f in findings)),
            "findings_by_confidence": dict(Counter(f.confidence for f in findings)),
            "bayes": {
                "prior_any_skill_correct": round(prior, 5),
                "assumed_sensitivity": 0.90,
                "assumed_specificity": 0.95,
                "posterior_given_fire": round(posterior, 4),
            },
        },
        "detectors": {
            code: {"title": title, "confidence": "exact" if code in EXACT_CODES else "heuristic"}
            for code, title in sorted(CODE_TITLES.items())
        },
        "findings": [f.to_dict() for f in findings],
    }, indent=2, default=str)


# --------------------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------------------

def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="audit_skill_library.py",
        description="Audit a Cursor/Claude skill library for routing-table and "
                    "retrieval-index defects.")
    parser.add_argument("root", help="path to the skills/ root directory")
    parser.add_argument("--json", action="store_true", dest="as_json",
                        help="emit machine-readable JSON instead of the text report")
    parser.add_argument("--min-severity", choices=("low", "medium", "high"), default="low",
                        help="suppress findings below this severity; exit 1 iff any remain")
    parser.add_argument("--only", metavar="CODES",
                        help="comma-separated detector codes to run (e.g. SK008,SK012)")
    args = parser.parse_args(argv)

    if not os.path.isdir(args.root):
        sys.stderr.write("error: %s is not a directory\n" % args.root)
        return 2

    lib = Library(args.root)
    if not lib.skills:
        sys.stderr.write("error: no SKILL.md files found under %s\n" % args.root)
        return 2

    only = {c.strip().upper() for c in args.only.split(",")} if args.only else None

    findings = []
    for detector in DETECTORS:
        try:
            findings.extend(detector(lib))
        except Exception as exc:  # a broken detector must not sink the audit
            sys.stderr.write("warning: detector %s failed: %s: %s\n"
                             % (detector.__name__, type(exc).__name__, exc))

    if only:
        findings = [f for f in findings if f.code in only]

    threshold = SEVERITY_ORDER[args.min_severity]
    findings = [f for f in findings if SEVERITY_ORDER[f.severity] >= threshold]
    findings.sort(key=lambda f: (
        -SEVERITY_ORDER[f.severity], f.code, f.file, f.line or 0, f.title))

    stats = {"rule_count": sum(len(s.rules) for s in lib.skills)}

    if args.as_json:
        print(render_json(lib, findings, args.min_severity, stats))
    else:
        print(render_text(lib, findings, args.min_severity, stats))

    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
