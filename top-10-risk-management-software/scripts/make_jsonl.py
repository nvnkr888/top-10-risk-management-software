#!/usr/bin/env python3
import csv, json, os
os.makedirs('data/jsonl', exist_ok=True)
with open('sources.csv', newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    out = []
    for row in reader:
        out.append(row)
with open('data/jsonl/all.jsonl', 'w', encoding='utf-8') as outf:
    for o in out:
        outf.write(json.dumps(o, ensure_ascii=False) + '\n')
print('wrote', len(out), 'records')
