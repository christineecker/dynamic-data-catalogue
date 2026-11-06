#!/usr/bin/env python
"""Reduce a saved pubmed_fetch_articles result to author -> DYNAMIC sites per paper. Usage: extract_sites.py <articles.json> <out.json>"""
import json,re,sys
RX={'MR':r'marburg|philipps[- ]univ','F':r'frankfurt|goethe','GI':r'gie(ss|ß)en|justus[- ]liebig','DA':r'darmstadt'}
# joint structures name several sites without saying where the person works
JOINT=re.compile(r'cent(er|re) (for|of) mind,? brain and behavio|\bcmbb\b|loewe[- ](center|centre)|dynamic center|dynamic centre|center for dynamic',re.I)
# hospital and lung-centre names that contain both cities; the city after them still says where the person is
SHARED=re.compile(r'gie(ss|ß)en[- ](and |und )?marburg|marburg (and|und) gie(ss|ß)en',re.I)
def sites(aff):
    aff=SHARED.sub('',aff)
    if JOINT.search(aff):
        # keep only what the rest of the string says, after cutting the joint clause
        aff=JOINT.split(aff)[0]
    return [k for k,p in RX.items() if re.search(p,aff,re.I)]
def main(src,dst):
    out={}
    for x in json.load(open(src))['articles']:
        A=x.get('affiliations') or [];r=[]
        for u in x.get('authors') or []:
            if not u.get('lastName'):continue
            s=sorted({k for i in (u.get('affiliationIndices') or []) if i<len(A) for k in sites(A[i])})
            r.append([f"{u['lastName']} {(u.get('initials') or ' ')[0]}".strip(),s,u.get('orcid'),u.get('initials') or ''])
        out[x['pmid']]=r
    json.dump(out,open(dst,'w'),ensure_ascii=False,indent=0)
if __name__=='__main__':main(*sys.argv[1:3])
