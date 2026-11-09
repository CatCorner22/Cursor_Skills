# Active-voice checker test sets

Each line holds a label and a sentence: P = has a passive clause, S = has a condition participle, A = fully active.
dev.txt and holdout.txt through holdout5.txt shaped the checker's rules. holdout6.txt came last, after tuning ended. all.txt combines every set (496 lines: 262 P, 38 S, 196 A).

score.py finds the checker in this skill's `scripts/` folder. Run it from this folder:

    python3 score.py holdout6.txt v

Add `sp en_core_web_sm` to turn on the spaCy pass (spaCy and the model must be installed).
