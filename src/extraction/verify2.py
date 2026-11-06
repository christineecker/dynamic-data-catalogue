#!/usr/bin/env python
"""verify2.py <demog_out.json>: every rescued value must sit in a verbatim quote from the paper."""
import json,re,sys,os
R='/Users/sphache/Projects/paper-rag/DYNAMIC/papers'
sq=lambda s:re.sub(r'[^a-z0-9]','',(s or '').lower())
cache={}
def src(p):
    if p not in cache:
        m=json.load(open(f'{R}/{p}/metadata.json')); t=m.get('abstract') or ''
        f=f'{R}/{p}/fulltext.md'
        if os.path.exists(f): t+=open(f).read()
        cache[p]=sq(t)
    return cache[p]
errs=0
for r in json.load(open(sys.argv[1])):
    p=r['pmid']; qs=r.get('quotes') or []
    for q in qs:
        if sq(q) not in src(p): errs+=1; print(p,'quote not verbatim:',q[:90])
    J=sq(' '.join(qs))
    for k in ('pct_female','age_mean','age_sd','age_min','age_max','n_analysed'):
        v=r.get(k)
        if v is None or r.get(k+'_derived'): continue
        if sq(str(v)) not in J: errs+=1; print(p,k,v,'not in quotes')
    if any(r.get(k+'_derived') for k in('pct_female','age_mean','n_analysed')) and not r.get('derivation'): errs+=1; print(p,'derived without derivation')
print('problems',errs)
