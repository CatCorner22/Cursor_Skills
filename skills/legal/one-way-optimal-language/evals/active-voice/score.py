import os, sys
sys.path.insert(0, ".")
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "scripts"))
import active_voice_check as av
fn = sys.argv[1]; verbose = "v" in sys.argv[2:]; use_sp = "sp" in sys.argv[2:]
if use_sp:
    import spacy; av.SPACY_NLP = spacy.load(sys.argv[sys.argv.index("sp")+1])
tot = {"P":0,"A":0,"S":0}; ok = {"P":0,"A":0,"S":0}; stateonly = 0
for line in open(fn):
    lab, s = line.rstrip("\n").split("|", 1); tot[lab] += 1
    codes = {c for _, c, _ in av.check_text(s, use_sp)}
    blocking = codes & av.BLOCKING
    if lab == "P":
        good = bool(blocking); stateonly += (not blocking and "STATE?" in codes)
    elif lab == "S":
        good = bool(codes)
    else:
        good = not codes
    ok[lab] += good
    if verbose and not good:
        print(f"{'MISS' if lab!='A' else 'FALSE'} [{lab}] {s}  -> {sorted(codes)}")
print(f"{fn} ({'spaCy '+sys.argv[sys.argv.index('sp')+1] if use_sp else 'regex'}): passives caught {ok['P']}/{tot['P']} (state-only {stateonly}); statives surfaced {ok['S']}/{tot['S']}; actives clean {ok['A']}/{tot['A']}")
