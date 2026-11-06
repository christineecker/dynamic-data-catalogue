#!/usr/bin/env python
"""verify.py <batch.json> : checks schema, controlled lists, verbatim quotes, numbers-in-quotes."""
import json,re,sys,os
R='/Users/sphache/Projects/paper-rag/DYNAMIC/papers'
MOD={"sMRI","task-fMRI","rs-fMRI","dMRI","PET/MRS","EEG/MEG","Physiology","EMA","Actigraphy/wearable","Smartphone sensing","Glucose monitoring","Genetics","Epigenetics","Omics","Microbiome","Blood biomarkers","Clinical interview/rating","Questionnaire","Therapy records","Registry/EHR","Behavioural task","Speech/language","Video/nonverbal"}
COND={"Major depression","Bipolar disorder","Schizophrenia/psychosis","Anxiety disorders","PTSD/trauma","OCD","Autism","ADHD","Conduct/externalising","Eating disorders","Substance use","Behavioural addiction","Somatic symptom/pain","Personality disorder","Medical/neurological","Mixed/transdiagnostic","At-risk/subclinical","Healthy/general population"}
KIND={"Named cohort","Consortium","Trial","Registry","Study sample","Meta-analysis pool","Public dataset"}
sq=lambda s:re.sub(r'[^a-z0-9]','',(s or '').lower())
def src(p):
    m=json.load(open(f'{R}/{p}/metadata.json')); t=m.get('abstract') or ''
    f=f'{R}/{p}/fulltext.md'
    if os.path.exists(f): t+=open(f).read()
    return sq(t)
data=json.load(open(sys.argv[1])); errs=0; nq=0
for r in data:
    p=r['pmid']; S=src(p)
    def E(msg):
        global errs; errs+=1; print(p,msg)
    for s in r.get('samples',[]):
        if s.get('kind') not in KIND: E(f"bad kind {s.get('kind')}")
        for x in s.get('modalities',[]):
            if x not in MOD: E(f"bad modality {x}")
        for x in s.get('conditions',[]):
            if x not in COND: E(f"bad condition {x}")
        nq_,dq=s.get('n_quote'),s.get('demog_quote')
        for q in (nq_,dq):
            if q:
                nq+=1
                if sq(q) not in S: E(f"quote not verbatim: {q[:90]}")
        both=sq((nq_ or '')+' '+(dq or ''))
        n=s.get('n_analysed')
        if n is not None and not s.get('n_derived') and str(n) not in sq(nq_): E(f"n {n} not in n_quote")
        for g in s.get('groups',[]):
            if g.get('n') is not None and str(g['n']) not in both: E(f"group n {g['n']} not in quotes")
        for k in ('pct_female','age_mean','age_min','age_max'):
            v=s.get(k)
            if v is not None and not s.get('pct_female_derived') and sq(str(v)) not in sq(dq): E(f"{k} {v} not in demog_quote")
    oa=r.get('open_science') or {}
    q=oa.get('quote')
    if q and sq(q) not in S: E(f"open_science quote not verbatim: {q[:90]}")
print(f"{len(data)} papers, {nq} quotes, {errs} problems")
