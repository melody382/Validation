import json, sys, textwrap
rules = json.load(open('rules.json', encoding='utf-8'))
obj = sys.argv[1]
sel = [r for r in rules if obj in r['objects'] and r['doc'] != 'IIIb']
print(f"### {obj.upper()} — {len(sel)} rules\n")
for r in sel:
    loc = f"{r['doc']} §{r['section']}" + (f".{r['subsection']}" if r['subsection'] else "")
    print(f"[{r['rule_id']}] {loc}  ({r['kind']})")
    for ln in textwrap.wrap(r['text'], 108):
        print("    " + ln)
    print()
