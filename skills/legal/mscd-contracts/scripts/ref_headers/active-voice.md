# Active voice

**House rule: active voice only, in every sentence and clause.** Read `house-style.md` section 1 for the recast patterns (unknown actor, legal fiction, amendment, party action) and the contingencies (linking verbs and adjectival participles aren't passive; quoted text stays; never change meaning to satisfy the rule).

## How to detect the passive

A passive verb is a form of *be* (or *get*) plus a past participle, with the actor either missing or in a *by* phrase: *is delivered*, *will be paid*, *has been terminated*, *shall be deemed*. `scripts/mscd_lint.py` flags candidates; confirm each one by asking "who does this?" If the sentence names no doer of the action, it is passive.

Not passive: *is void*, *is effective*, *is liable*, *is entitled*, *is responsible* (linking verb plus adjective); *the attached form* (participle as adjective).

MSCD's own rules below still matter: they explain why the passive hides the actor (3.15) and how to rephrase buried-actor policies (3.336-3.338). The MSCD allowances for the passive carry the HOUSE mark.
