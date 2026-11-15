# usage: ovr.py CH "para:who para:who,who ..."  (who = cast key; a comma list = one per quote)
import json, sys, os
p = os.path.join(os.path.dirname(__file__), 'ovr.json'); d = json.load(open(p)) if os.path.exists(p) else {}
ch = sys.argv[1]
for tok in sys.argv[2].split():
    para, who = tok.split(':'); w = who.split(',')
    d['%s:%s' % (ch, para)] = w if len(w) > 1 else w[0]
json.dump(dict(sorted(d.items(), key=lambda kv: tuple(map(int, kv[0].split(':'))))), open(p, 'w'), indent=0)
print(len(d), 'overrides')
