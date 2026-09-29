import json, sys
rules = json.load(open('rules.json', encoding='utf-8'))
for obj in sys.argv[1:]:
    sel = [r for r in rules if obj in r['objects'] and r['doc'] != 'IIIb']
    print(f"\n{'='*100}\n### {obj.upper()} — {len(sel)} rules\n{'='*100}")
    for r in sel:
        loc = f"{r['doc']}§{r['section']}" + (f".{r['subsection']}" if r['subsection'] else "")
        print(f"[{r['rule_id']}] {loc[:34]:<34} {r['text'][:190]}")
