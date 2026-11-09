# Active-voice checker test sets

Each line holds a label and a sentence: P = has a passive clause, S = has a condition participle, A = fully active.
dev.txt and holdout.txt through holdout5.txt shaped the checker's rules. holdout6.txt came last, after tuning ended. all.txt combines every set (496 lines: 262 P, 38 S, 196 A).

score.py finds the checker in this skill's `scripts/` folder. Run it from this folder:

    python3 score.py holdout6.txt v

Add `sp en_core_web_sm` (or `sp en_core_web_trf`) to turn on the spaCy pass, which needs spaCy and that model.

Results on all.txt (9 November 2026): the regex pass caught 262 of 262 passives and left 196 of 196 active sentences clean. With en_core_web_sm, 194 of 196 stayed clean; with en_core_web_trf, 195 of 196, at about 7 times the run time.
