#!/usr/bin/env python3
"""Count the body words of a Markdown deliverable and compare them with a mode budget.

The body is everything before the first heading named Sources, References,
Appendix, or "Note to Blake", including the title block and the label key. Table pipes, rule lines, and Markdown symbols
do not count as words; a token counts only if it contains a letter or digit.

Usage:
  python3 word_budget.py FILE --mode quick|briefing|memo|standard
  python3 word_budget.py FILE --limit 1200
  python3 word_budget.py - --mode quick < draft.md   (read from stdin)

Exit status: 0 within budget, 1 over budget, 2 usage error.
"""
import argparse
import re
import sys

BUDGETS = {"quick": 400, "briefing": 1000, "memo": 900, "standard": 1500}
# Stop at "## Sources", "## References (accessed ...)", "## Appendix ...", or "## Note to Blake ...".
# "## 3. Sources reviewed" is a body section, so a bare Sources/References heading must end the line.
STOP = re.compile(
    r"^#{1,6}\s*(?:\d+\.\s*)?(?:(?:sources|references)\s*(?:\(.*\))?\s*:?\s*$|appendix\b|appendices\b|note to blake\b)",
    re.I,
)
WORD = re.compile(r"[A-Za-z0-9]")


def body_words(text):
    """Return (word count, body lines) for the text before the first stop heading."""
    lines = []
    for line in text.splitlines():
        if STOP.match(line.strip()):
            break
        lines.append(line)
    tokens = re.split(r"[\s|]+", "\n".join(lines))
    return sum(1 for t in tokens if WORD.search(t)), lines


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("file")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--mode", choices=sorted(BUDGETS))
    g.add_argument("--limit", type=int)
    a = p.parse_args()
    try:
        text = sys.stdin.read() if a.file == "-" else open(a.file, encoding="utf-8").read()
    except OSError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    limit = a.limit if a.limit is not None else BUDGETS[a.mode]
    n, lines = body_words(text)
    over = n - limit
    print(f"body_words: {n}")
    print(f"limit: {limit}")
    if over > 0:
        print(f"status: OVER by {over} words ({over / limit:.0%}). Cut before delivering:"
              " merge overlapping bullets, move tables or detail to an appendix, drop restated points.")
        return 1
    print(f"status: within budget ({-over} words to spare)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
