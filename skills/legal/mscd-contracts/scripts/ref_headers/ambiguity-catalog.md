# Ambiguity catalog

**The skill removes every ambiguity it finds.** For each one, the finding states each possible meaning in plain words before proposing a fix. If the fix requires choosing a meaning, never choose silently: ask which meaning Blake intends, or, in a redline, comment with 1 wording for each meaning.

## Definitions

- Text is **ambiguous** if it can express 2 or more inconsistent meanings (7.5). It is still ambiguous if context resolves it (7.6).
- A dispute alone doesn't make text ambiguous, and a comma alone shouldn't decide meaning (7.28-7.29; 12.75-12.78; Adams, "What We Talk About When We Talk About Ambiguity").
- The 6 sources of uncertain meaning (7.3): ambiguity; not being sufficiently specific; mistake; conflict; not addressing an issue; vagueness (see `vagueness.md`).

## Causes added by the riders

- **Right-node-raising pivot ambiguity**: 2 coordinated clauses share a final element, and it's unclear which words the shared element attaches to (*subject to the jurisdiction of and be construed according to the laws of the State of Florida*). Offsetting commas "aren't optional"; better, repeat the shared element. MSCD's "delimiting commas in coordination" (12.79-12.87) are now "offsetting commas in right node raising."
- **Each or in the aggregate**: a quantity attributed to several items or payments (*monthly severance payments ... in the amount of $680,000*). Say *each* or *in the aggregate*.
- **Ambiguity of the specific versus the general**: *ejusdem generis* and *including* (*insects, birds, rodents, or other animals*). Apply the *including* rules (13.360-13.407).
- **11.106, second printing**: for a single item, the *every/each/all* ambiguity also afflicts *the whole* and *the entire*.

## Elaboration: terms of art in their everyday sense

MSCD 1.57 says not to use 1 word for different meanings. A word that contracts use as a term of art invites the legal reading when it appears in its everyday sense, above all in a contract that also uses the legal sense. Flag these and offer the plain word:

| Everyday use | Legal sense it collides with | Write instead |
|---|---|---|
| *execute the services* | signing (MSCD prefers *sign*, 5.7) | *perform* |
| *if Acme notices an error* | a notice under the notices provision | *discovers*, *becomes aware of* |
| *if circumstances warrant* | warranty | *justify*, *require* |
| *fees represent 15% of* | a representation (a statement of fact) | *are*, *constitute* |
| *assign personnel*; *work assignment* | assignment of rights | *designate*; *task*, *work order* |
| *for Acme's consideration* | consideration for a promise | *review*, *evaluation* |
| *release payment* (outside an escrow) | release of claims | *pay*, *disburse* |
| *strategic partner* | a legal partnership | the actual relationship |

This is house rule 13 (it applies MSCD 1.57 and 1.8-1.13; MSCD doesn't list these words): severity 1 when the contract also uses the word in its legal sense, otherwise 2 (house-style.md section 13). Cite "house rule 13", not "elaboration". The lint flags these as `term-of-art`.

## How to use the list below

Records of kind `ambiguity-cause` give the signal to look for, the test, and the fix. `scripts/mscd_lint.py` flags candidates where a regex can; many causes (modifier scope, part versus whole) need you to read the sentence, so check every sentence against the causes in pass 4.
