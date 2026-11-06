#!/usr/bin/env python
"""Build the DYNAMIC Data Catalogue: python atlas/catalogue/build.py (run from DYNAMIC/).
Merges extraction/*.json + hand-checked links below, re-verifies every quote against papers/, writes catalogue.json and ../data-catalogue.html."""
import json,glob,os,re,collections as C,statistics as st
H=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.abspath(H+'/../..'); PP=ROOT+'/papers'
SNAP='2026-11-06'
VERSION='1.0'  # shown in the banner of both pages
sq=lambda s:re.sub(r'[^a-z0-9]','',(s or '').lower())
def meta(p): return json.load(open(f'{PP}/{p}/metadata.json'))
_s={}
def src(p):
    if p not in _s:
        t=meta(p).get('abstract') or ''; f=f'{PP}/{p}/fulltext.md'
        if os.path.exists(f): t+=open(f).read()
        _s[p]=sq(t)
    return _s[p]
R={}
for f in sorted(glob.glob(H+'/extraction/batch_*.json')):
    for r in json.load(open(f)): R[r['pmid']]=r
FIRST=json.loads(json.dumps(R))  # keep first pass for agreement
# ---- demographic rescue
applied=C.Counter()
for f in sorted(glob.glob(H+'/extraction/demog_out_*.json')):
    for x in json.load(open(f)):
        s=R[x['pmid']]['samples'][x['i']]; used=False
        for k in('pct_female','age_mean','age_sd','age_min','age_max','n_analysed'):
            v=x.get(k)
            if v is None or s.get(k) is not None: continue
            if k=='pct_female' and not 0<=v<=100: continue
            if k.startswith('age') and k!='age_sd' and not 0<v<105: continue
            s[k]=v; used=True; applied[k]+=1
            if k=='pct_female' and x.get('pct_female_derived'): s['pct_female_derived']=True
            if k=='age_mean' and x.get('age_mean_derived'): s['age_mean_derived']=True
            if k=='n_analysed' and x.get('n_analysed_derived'): s['n_derived']=True
        if used:
            s.setdefault('xq',[]).extend(x.get('quotes') or [])
            if x.get('derivation'): s['qn']=(s.get('qn','')+' Derived: '+x['derivation']).strip()
# ---- hand-checked cohort links: (pmid, sample index, changes, verbatim quote)
OV=[('41572735',0,{'canonical':'FOR2107','kind':'Named cohort'},'from the FOR2107 cohort'),
 ('40948223',0,{'canonical':'FOR2107','kind':'Named cohort'},'were drawn from the baseline assessment of the Marburg-Münster Affective Disorders Cohort Study (MACS)'),
 ('41243355',0,{'canonical':'FOR2107','kind':'Named cohort'},'The data used in this work is part of the Marburg–Münster Affective Disorders Cohort Study (MACS)'),
 ('40691132',0,{'canonical':'EU-AIMS','kind':'Named cohort'},'These data were derived from participants enrolled in the EU-AIMS Longitudinal European Autism Project (LEAP'),
 ('41067133',0,{'canonical':'PROTECT-AD'},'PROTECT-AD P1 grant number: 01EE1402A'),
 ('42628150',0,{'canonical':'PROTECT-AD'},'PROTECT-AD P1 grant number: 01EE1402A'),
 ('41261989',0,{'canonical':'ACSID','kind':'Named cohort'},'FOR2974'),
 ('42778181',0,{'canonical':'LORA','name':'LORA','n_analysed':102,'n_quote':'at the sample sizes here (N∼102, T∼10)','evidence':'Full text'},'We consider the longitudinal resilience assessment (LORA) study'),
]
for p,i,ch,q in OV:
    s=R[p]['samples'][i]; assert sq(q) in src(p),(p,q)
    ev=ch.pop('evidence',None)
    if ev: R[p]['evidence']=ev
    s.update(ch); s.setdefault('xq',[]).append(q); s['qn']=(s.get('qn','')+' Dataset link checked by hand.').strip()
s0=R['42330189']['samples'][0]
ext=dict(s0); ext.update(name='FOR2107',canonical='FOR2107',role='replication',n_analysed=590,n_quote='an external sample of 590 participants aged 15‐35 years from the FOR2107 longitudinal sample',groups=[],age_min=15,age_max=35,age_mean=None,age_sd=None,pct_female=None,demog_quote=None,sites=[],xq=[],qn='External validation sample, added by hand.',age_group='Youth (mixed)')
R['42330189']['samples'].append(ext)
FEEDS=[('41764298',0,'FOR2107','more than two-thirds originating from the Marburg-Münster Affective Disorders Cohort Study (MACS)'),
 ('41338325',0,'FOR2107','FOR2107- MR'),('42105630',0,'FOR2107','FOR2107 (Germany)'),('40506530',0,'EU-AIMS','AIMS-2-TRIALS-Biomarkers of Neurodevelopmental Outcomes (BONO)')]
NOTES={'40313139':'CoSS pools MACS and the Münster Neuroimaging Cohort; the paper does not split them here.','41076451':'Abstract and table disagree on group sizes; table values used.','42092437':'Subjects section gives 449 BD and 510 controls; abstract says 450 and 509.','39024740':'Mean age differs between text (44.59) and Table 1 (42.62); text used.','40667504':'27 recruited, 5 later excluded; analysed n not stated.','40256822':'32 reported, 1 later excluded; analysed n not stated.','39763023':'n = included in analysis (11), of 18 enrolled.'}
# ---- data availability statements found in full text, classified by hand from da.json
DA={'On request':'39706901 41764298 41526712 41935030 39380071 41764586 42571020 41857208 42368888 40506530 42463908 39970620 42008786 38801091 39472472 41844582 42330189 40817168 38337673 40169979 40210648',
 'Open repository':'41076451 40113972 41540261 40481455 41316488 41053084 41202447',
 'Restricted/controlled':'40691132 42092045 41369840 41420114 41327287','Not available':'42624880 40313139 42795927'}
dast=json.load(open(H+'/extraction/da.json'))
for lab,ids in DA.items():
    for p in ids.split():
        o=R[p].setdefault('open_science',{}); q=dast[p][1]
        if p=='42092045': q='To facilitate data requests, a list of included datasets is publicly available'
        o['data_access']=lab; o['quote']=q
        m=re.search(r'https?://[^\s)\]]+|10\.\d{4,}/[^\s)\]]+',q)
        if m and lab=='Open repository': o['url']=m.group(0).rstrip('.,') if m.group(0).startswith('http') else 'https://doi.org/'+m.group(0).rstrip('.,')
R['42137962'].setdefault('open_science',{})['code_available']=True
# ---- dataset naming
ALIAS=[(r'M(ü|ue)nster Neuroimaging Cohort','Münster Neuroimaging Cohort'),(r'^mPRIME','mPRIME'),(r'Transdiagnostic Investigation of Emotional Processing','TIP'),(r'\bBANDA\b','BANDA'),(r'ENIGMA.*(Bipolar|BD)','ENIGMA Bipolar Disorder'),(r'ENIGMA.*Anxiety','ENIGMA Anxiety'),(r'ENIGMA.*Schizotypy','ENIGMA Schizotypy'),(r'^PGC','PGC Bipolar Disorder'),(r'PSY-?HEART I$','PSY-HEART I'),(r'^FOR2974','ACSID')]
GENERIC=re.compile(r'^(study \d|therapists|.*\bsample\b|pre-covid cohort|covid cohort|spanish study|german study|rct on |clinical routine|cohort study sample)',re.I)
NOTTAB={'ENIGMA','PGC'}
TAB1=[('ACSID','ACSID',1000,'Computer use disorder','J','J','J','T','N','Stark',[],'Research unit on internet-use disorder'),
('A-FFIP','A-FFIP',130,'F84','T','J','J','N','J','Freitag',['Video/nonverbal'],'Multi-centre RCT and longitudinal study with many video data'),
('AMIS_EPIGEN','AMIS_EPIGEN',500,'At risk','J','J','N','N','J','Alexander',['Epigenetics'],'Longitudinal study of epigenetic change after childhood abuse and therapeutic intervention'),
('APPetite','APPetite',300,'F3x, F9x','J','J','N','N','J','Reif',[],'Longitudinal study of eating behaviour and impulsivity'),
('ASD-Net','ASD-Net',3500,'F84x','T','J','J','T','T','Kamp-Becker',[],'Multi-centre study of autism aetiology, diagnostics (predictive symptoms and AI) and therapy'),
('BESTFORCAN','BESTFORCAN',500,'F43.1','J','J','N','N','N','Steil',[],'Large German dissemination study of CBT for children and adolescents with PTSD, with data from 150 therapists'),
('BipoLife','BipoLife',1200,'F31','J','J','N','T','J','Reif, Kircher',['Genetics'],'Longitudinal study of risk states for bipolar disorder, with imaging and DNA'),
('BIU-872','BIU-872',60,'F3x','J','J','N','N','N','Gurevych',['Speech/language'],'Transcribed and annotated data set of therapy conversations'),
('CBASP-CBT','CBASP-CBT',170,'F3x','J','J','N','N','J','Rief',[],'Comparison of three psychotherapy conditions in major depression'),
('CNL','CNL',380,'At risk','N','J','N','J','J','Nenadić',[],'Multimodally characterised at-risk participants'),
('CoCA','CoCA',300,'F3x, F9x','J','J','N','J','J','Reif, Grimm, Freitag',[],'Longitudinal therapy study of ADHD and comorbid disorders'),
('COGITO','COGITO',200,'Controls','J','J','J','J','J','Schmiedek',['EMA'],'Measurement-intensive study with 100 daily lab sessions and broad cognitive and emotional variables'),
('COMPARE','COMPARE',400,'Transdiagnostic','J','J','N','T','N','Stark',[],'Multi-centre study of children of parents with mental illness'),
('COMPARE (families)','COMPARE (families)',350,'Transdiagnostic','J','J','N','T','N','Christiansen',[],'National consortium; therapy study of effects of parental therapy on the children'),
('D-CPT','D-CPT',90,'F43.1','J','J','N','N','J','Steil',[],'Multi-centre RCT of PTSD in children and adolescents, CBT vs waitlist'),
('DEFLAME','DEFLAME',200,'F3x','J','J','N','J','J','Reif',['Blood biomarkers'],'Longitudinal imaging study of neuroinflammation in affective disorders'),
('Depressometer','Depressometer',60,'F33','J','J','N','N','J','Gurevych',['Speech/language','Video/nonverbal'],'Multimodal (audio, video, text) data set of therapy conversations'),
('DREAM_EPI','DREAM_EPI',300,'At risk','J','J','N','N','J','Alexander',['Epigenetics'],'Longitudinal study of epigenetic change in early childhood after perinatal parental stress'),
('DynAMoND','DynAMoND',500,'F31, F6x, F9x','J','J','J','N','J','Reif',['EMA','Smartphone sensing'],'High-frequency EMA of affect and activity over 12 months; started 2023'),
('EMA-PRED','EMA-PRED',100,'F32, F33','J','J','N','N','N','Rubel',['EMA'],'Longitudinal prediction of psychotherapy response and dropout from intensive baseline data'),
('ENCERT','ENCERT',250,'F45','J','J','N','N','N','Rief, Stark',[],'Multi-centre RCT comparing two psychotherapy variants in somatoform disorders'),
('ENHANCE','ENHANCE',400,'F43.1','J','J','N','T','T','Stark',[],'Multi-centre study comparing two therapy programmes for PTSD after childhood maltreatment'),
('EpiBurn','EpiBurn',300,'At risk','J','J','N','N','J','Alexander',['Epigenetics'],'Longitudinal: epigenetic risk scores and pathways from work stress to burnout'),
('EU-AIMS','EU-AIMS / AIMS-2-Trials',800,'F84','J','J','J','J','J','Ecker, Freitag',[],'Longitudinal EU study of biomarkers for autism spectrum disorder'),
('FemNAT-CD','FemNAT-CD',1200,'F91','T','J','J','T','J','Freitag',[],'International consortium on conduct disorder in girls'),
('FOR2107','FOR2107',2500,'F2x, F3x','J','J','J','J','J','Kircher, Nenadić, Repple',['Speech/language'],'Longitudinal study of illness trajectories in affective disorders'),
('Human Connectome','Human Connectome',1200,'Controls','N','J','J','J','N','Grimm',[],'International consortium, suited as ML training data'),
('KODAP','KODAP',10000,'Transdiagnostic','J','J','N','N','N','Stark',[],'Network of university psychotherapy training institutes'),
('LORA','LORA',1100,'Controls','J','J','J','N','J','Reif',['EMA'],'Longitudinal studies of resilience with many repeated EMA stress measures'),
('OASIS-D','OASIS-D',1000,'F3x','J','J','N','N','N','Reif',[],'Longitudinal symptom assessment (incl. suicidality) in inpatients with depression'),
('Optima','Optima',300,'F33','J','J','J','N','J','Gurevych',['Speech/language'],'RCT of schema therapy for MDD; multimodal data set of therapy conversations'),
('P4D','P4D',1000,'F3x','J','J','J','J','J','Reif',['EEG/MEG'],'Multidimensional longitudinal biomarkers in depression; EEG; started 2024'),
('Panic-Net I','Panic-Net I',370,'F40.01','J','J','J','T','J','Kircher',[],'Longitudinal study of therapy effects in panic disorder'),
('Panic-Net II','Panic-Net II',270,'F40','J','J','J','T','J','Kircher, Straube',[],'Longitudinal study of therapy effects in panic disorder'),
('PaZ','PaZ',130,'F42','J','J','N','N','J','Fischer',['EMA','Video/nonverbal','Speech/language'],'Multi-method study with EMA and social interaction (video and voice analysis)'),
('PROTECT-AD','PROTECT-AD',730,'Anxiety disorders','J','J','J','T','J','Straube, Kircher',[],'Longitudinal study of therapy effects across anxiety disorders'),
('PSYHEART','PSYHEART II',560,'I25','J','J','N','N','J','Rief',[],'Multi-centre RCT of expectation optimisation before heart surgery'),
('R-LiNK','R-LiNK',200,'F31','J','J','N','N','J','Reif',['Omics'],'Longitudinal omics study predicting response to lithium'),
('SASCHA','SASCHA',200,'Controls','J','J','N','N','N','Schmiedek',['EMA'],'Measurement-intensive study around the transition to secondary school'),
('SGTreat','SGTreat',250,'At risk','J','J','J','J','J','Alexander',[],'Long-term effects of prenatal glucocorticoid therapy on volitional control in childhood'),
('SOPHONet','SOPHONet',500,'F40.1','J','J','N','N','N','Stangier, Stark',[],'Multi-centre RCT of psychodynamic therapy vs CBT in social anxiety disorder')]
FAM=[dict(id='img',l='Neuroimaging',m=['sMRI','task-fMRI','rs-fMRI','dMRI','PET/MRS']),dict(id='ephys',l='Electrophysiology & physiology',m=['EEG/MEG','Physiology']),dict(id='digital',l='Digital & intensive longitudinal',m=['EMA','Actigraphy/wearable','Smartphone sensing','Glucose monitoring']),dict(id='bio',l='Biological',m=['Genetics','Epigenetics','Omics','Microbiome','Blood biomarkers']),dict(id='clin',l='Clinical & self-report',m=['Clinical interview/rating','Questionnaire','Therapy records','Registry/EHR']),dict(id='cog',l='Cognitive & experimental',m=['Behavioural task']),dict(id='lang',l='Language & audio-visual',m=['Speech/language','Video/nonverbal'])]
FAMOF={m:f['id'] for f in FAM for m in f['m']}
tab_ids={t[0] for t in TAB1}
INST=[(r'^(SCID|Structured Clinical Interview)','SCID'),(r'^M\.?I\.?N\.?I','MINI'),(r'^(HAM-?D|HDRS|HRSD|HAMD)','HAM-D'),(r'^BDI','BDI'),(r'^(HAM-?A|HARS)','HAM-A'),(r'^PSS','PSS'),(r'^Life Chart','Life Chart'),(r'^PHQ-?9','PHQ-9'),(r'^PHQ','PHQ'),(r'^GAD','GAD-7'),(r'^DASS','DASS'),(r'^CTQ','CTQ'),(r'^PANSS','PANSS'),(r'^SAPS','SAPS'),(r'^SANS','SANS'),(r'^YMRS','YMRS'),(r'^GAF','GAF'),(r'^CGI','CGI'),(r'^STAI','STAI'),(r'^AUDIT','AUDIT'),(r'^NEO','NEO'),(r'^WHODAS','WHODAS'),(r'^MADRS','MADRS'),(r'^QIDS','QIDS'),(r'^(MWT|MWTB)','MWT-B'),(r'^TMT','TMT'),(r'^ASI','ASI'),(r'^SPQ','SPQ'),(r'^ADOS','ADOS'),(r'^ADI','ADI-R'),(r'^FAST\b','FAST')]
def ninst(x):
    for pat,lab in INST:
        if re.match(pat,x.strip(),re.I): return lab
    return x.strip()
au1=lambda m:(m['authors'][0]['family'] if m.get('authors') else 'Anon')
papers=[];samples=[];ds={};feeds=[];qc=C.Counter();PROBLEMS=[]
FE={(p,i):(f,q) for p,i,f,q in FEEDS}
for p,r in sorted(R.items()):
    m=meta(p); fa=au1(m); na=len(m.get('authors') or []); y=int(m['year'])
    os_=r.get('open_science') or {}
    url=os_.get('url'); url=url if url and url.startswith('http') else None
    qa=os_.get('quote')
    if qa:
        qc['quotes']+=1
        if sq(qa) not in src(p): PROBLEMS.append((p,'access quote',qa[:60]))
    papers.append(dict(id=p,pmid=p,pmcid=m.get('pmcid'),doi=m.get('doi'),t=m['title'],au=fa+(' et al.' if na>1 else ''),auf=', '.join(f"{a.get('family')} {a.get('given') or ''}".strip() for a in (m.get('authors') or [])[:12])+(' … ' if na>12 else ''),la=(m['authors'][-1]['family'] if na>1 else fa),j=m.get('journal'),y=y,ty=r.get('paper_type'),sp=r.get('species'),de=r.get('design'),ap=r.get('approach') or [],tp=r.get('topic') or '',ev=r.get('evidence'),ac=os_.get('data_access') or 'Not stated',acq=qa,url=url,code=bool(os_.get('code_available')),pre=os_.get('preregistered'),reg=os_.get('registration_id')))
    for i,s in enumerate(r.get('samples',[])):
        nm=s.get('name'); can=s.get('canonical')
        if nm and 'BANDA' in nm: can=None  # Connectome Studies of Human Disease; not the Tab. 1 Human Connectome row (controls)
        if can and can in NOTTAB or (nm and not can) or (can and nm and re.search('ENIGMA|PGC|PSY-?HEART I$',nm)):
            for pat,lab in ALIAS:
                if nm and re.search(pat,nm): can=lab if lab in tab_ids else None; nm=lab; break
        if s.get('canonical')=='PSYHEART' and nm=='PSY-HEART I': can=None
        generic=not can and (not nm or GENERIC.search(nm))
        if can: dsid=can; label=next((t[1] for t in TAB1 if t[0]==can),can)
        elif generic: label=f"{fa} {y}"+(f": {nm}" if nm else ' sample'); dsid=f"s-{p}-{i}"
        else: label=nm; dsid=nm
        d=ds.setdefault(dsid,dict(id=dsid,name=label,aliases=[],kind=s['kind'],named=bool(not generic),tab1=dsid in tab_ids,pool=False))
        if nm and nm!=label and nm not in d['aliases'] and not generic: d['aliases'].append(nm)
        if (s['kind'] in('Consortium','Registry','Meta-analysis pool') and not d['tab1']) or (s.get('n_analysed') or 0)>=50000: d['pool']=True
        if can: d['kind']='Named cohort' if s['kind'] not in('Trial','Consortium') else s['kind']
        sid=f"{p}-{i}"
        for q in [s.get('n_quote'),s.get('demog_quote')]+(s.get('xq') or []):
            if q:
                qc['quotes']+=1
                if sq(q) not in src(p): PROBLEMS.append((p,'quote',q[:60]))
        n=s.get('n_analysed')
        if n is not None and not s.get('n_derived') and str(n) not in sq(' '.join(filter(None,[s.get('n_quote'),s.get('demog_quote')]+(s.get('xq') or [])))): PROBLEMS.append((p,'n not in quote',n))
        rd=lambda v:None if v is None else (round(v,1) if isinstance(v,float) else v)
        samples.append(dict(id=sid,p=p,ds=dsid,nm=nm,k=s['kind'],role=s.get('role'),n=n,nd=bool(s.get('n_derived')),nq=s.get('n_quote'),g=[dict(l=g.get('label'),n=g.get('n')) for g in (s.get('groups') or [])],f=rd(s.get('pct_female')),fd=bool(s.get('pct_female_derived')),am=rd(s.get('age_mean')),asd=rd(s.get('age_sd')),a0=rd(s.get('age_min')),a1=rd(s.get('age_max')),ag=s.get('age_group') or 'Not reported',dq=s.get('demog_quote'),xq=s.get('xq') or [],ct=s.get('countries') or [],st=s.get('sites') or [],rec=s.get('recruitment') or 'Not reported',lon=bool(s.get('longitudinal')),w=s.get('waves'),fu=s.get('followup_months'),ema=s.get('ema_detail'),m=s.get('modalities') or [],md=s.get('modality_detail') or {},ins=s.get('instruments') or [],insn=sorted({ninst(x) for x in s.get('instruments') or []}),c=s.get('conditions') or [],re=s.get('reuse') or 'Unclear',qn=' '.join(filter(None,[s.get('qn'),NOTES.get(p)])) or None))
        if (p,i) in FE:
            f,q=FE[(p,i)]; assert sq(q) in src(p),(p,q); feeds.append(dict(**{'from':f},sample=sid,quote=q))
assert not PROBLEMS,PROBLEMS
# ---- publication months and iCite metrics, fetched 2026-11-06 via pubmed-cyanheads
_ps=json.load(open(H+'/extraction/pubstats.json'))
for _p in papers:
    _o=_ps[_p['id']]; _p.update(oy=_o['y'],om=_o['m'],rcr=_o.get('rcr'),rp=_o.get('prov'),pc=_o.get('pct'),ci=_o.get('cites'))
# ---- agreement: blind second extraction vs first pass
dbl=json.load(open(H+'/extraction/double.json')); rows=[]
big=lambda r:max([s.get('n_analysed') or 0 for s in r.get('samples',[])] or [0])
un=lambda r,k:{x for s in r.get('samples',[]) for x in s.get(k,[])}
jac=lambda a,b:(len(a&b)/len(a|b) if a|b else 1)
canon=lambda r:{(s.get('canonical') or '') for s in r.get('samples',[])}
A=[(FIRST[d['pmid']],d) for d in dbl]; N=len(A)
ne=sum(big(a)==big(b) for a,b in A); nc=sum(abs(big(a)-big(b))<=.05*max(big(a),1) for a,b in A)
agree=dict(papers=N,n_exact=round(100*ne/N),rows=[
 ['Largest n, exact',round(100*ne/N),'Same largest analysed n per paper'],['Largest n, within 5%',round(100*nc/N),'Tolerance for sub-sample choices'],
 ['Number of samples',round(100*sum(len(a.get('samples',[]))==len(b.get('samples',[])) for a,b in A)/N),'Same count of analysed datasets'],
 ['Tab. 1 or consortium link',round(100*sum(canon(a)==canon(b) for a,b in A)/N),'Same reference dataset(s), before hand-checked links'],
 ['Study design',round(100*sum(a.get('design')==b.get('design') for a,b in A)/N),'Exact category'],
 ['Age group',round(100*sum(un(a,'age_group')==un(b,'age_group') or {s.get('age_group') for s in a.get('samples',[])}=={s.get('age_group') for s in b.get('samples',[])} for a,b in A)/N),'Same set per paper'],
 ['Modalities',round(100*st.mean(jac(un(a,'modalities'),un(b,'modalities')) for a,b in A)),'Mean Jaccard overlap per paper'],
 ['Conditions',round(100*st.mean(jac(un(a,'conditions'),un(b,'conditions')) for a,b in A)),'Mean Jaccard overlap per paper'],
 ['Data access',round(100*sum((a.get('open_science')or{}).get('data_access')==(b.get('open_science')or{}).get('data_access') for a,b in A)/N),'Exact category']])
# ---- tables
def avail(t):
    a={}
    for col,f in((t[5],'clin'),(t[6],'cog'),(t[7],'img'),(t[8],'bio')):
        if col!='N': a[f]='part' if col=='T' else 'yes'
    for e in t[10]: a.setdefault(FAMOF[e],'yes')
    return a
tab1=[dict(ds=t[0],name=t[1],n=t[2],dx=t[3],long=t[4],pi=t[9],avail=avail(t),note=t[11]) for t in TAB1]
L=dict(i='Clinical interview/rating',q='Questionnaire',e='EMA',ss='Smartphone sensing',sp='Speech/language',ph='Physiology',b='Behavioural task',ee='EEG/MEG',rs='rs-fMRI',t='task-fMRI',sm='sMRI',dm='dMRI',v='Video/nonverbal')
planned=[('Z-Projekt',3140,'Transdiagnostic + controls','Kircher, Mulert, Reif, Rief, Stark, Stangier, Straube','i q e ss sp ph b ee rs t sm dm','Anhang Tab. 2 and 3, §5.1'),('TP3.1/3.2 child cohort',200,'Children 1.5–16 y','Christiansen, Schwenck, Freitag','sp v q e','Anhang Tab. 2 (TP3.1; TP3.2 row blank); MS 3.1.2, 3.1.3, 3.2.3'),('TP3.4 pain / Long-COVID',180,'Pain, Long-COVID','Alexander, Hermann','e t q','Anhang Tab. 2; MS 3.4.1, 3.4.2'),('TP4.3 EEG-MR schizophrenia',60,'F20','Mulert, Grimm','ee t rs e','Anhang Tab. 2; MS 4.3.1, 4.3.2'),('TP4.7 JITAI',500,'Transdiagnostic','Lindenberg, Rubel, Schmiedek','e ss','Anhang Tab. 2; MS 4.7.1–4.7.3')]
planned=[dict(name=a,n=b,dx=c,pi=d,mods=[L[x] for x in e.split()],src=f) for a,b,c,d,e,f in planned]
ORD=dict(cond=['Major depression','Bipolar disorder','Schizophrenia/psychosis','Anxiety disorders','PTSD/trauma','OCD','Autism','ADHD','Conduct/externalising','Eating disorders','Substance use','Behavioural addiction','Somatic symptom/pain','Personality disorder','Medical/neurological','Mixed/transdiagnostic','At-risk/subclinical','Healthy/general population'],
 kind=['Named cohort','Trial','Study sample','Public dataset','Consortium','Registry','Meta-analysis pool'],age=['Children','Adolescents','Youth (mixed)','Adults','Older adults','All ages','Not reported'],
 rec=['Clinic','Community','Online','School','Registry/biobank','Mixed','Not reported'],reuse=['Existing dataset','New data collection','Unclear'],access=['Open repository','On request','Restricted/controlled','Not available','Not stated'])
used=lambda g:{v for s in samples for v in g(s)}
fac=dict(cond=[c for c in ORD['cond'] if c in used(lambda s:s['c'])],kind=ORD['kind'],age=ORD['age'],rec=ORD['rec'],reuse=ORD['reuse'],access=ORD['access'],
 design=[d for d,_ in C.Counter(R[s['p']]['design'] for s in samples).most_common()],approach=[a for a,_ in C.Counter(a for r in R.values() for a in r.get('approach') or []).most_common()],
 ctry=[c for c,_ in C.Counter(c for s in samples for c in s['ct']).most_common()],year=sorted({str(p['y']) for p in papers},reverse=True))
S=samples; ct=lambda g:sum(1 for s in S if g(s))
gaps=[f"{len(papers)-sum(p['ev']=='Full text' for p in papers)} papers rest on abstract or metadata only (see metadata_only.md). Supplying the PDFs lifts this.",
 f"{ct(lambda s:s['f'] is None)} of {len(S)} samples have no share female, and {ct(lambda s:s['am'] is None)} no mean age, even after a second pass over the full text.",
 "Many analyses of named cohorts name them only in cited methods papers. Those stay as single-study samples until someone maps them, so reuse is under-counted.",
 "Instruments and modalities come from the methods text read. A cohort usually holds more than its papers report.",
 "Largest n can mean different things across papers (all groups, patients only, one wave). The quote shows which.",
 "Tab. 1 availability is per family, so modalities in rings are coarser than the published dots.",
 "Planned cohorts and proposal sizes come from the Vollantrag and are targets. Nothing here reports recruitment.",
 "TP assignment, milestones and collaboration are left to the atlas; none of them is in this catalogue."]
lineage=[['Evidence map with fixed scale and whole-library ring','atlas.html Explorer','Coverage tab; gains Datasets measure and rows by type, age, design'],['Condition → cohort → data flow','atlas.html Explorer','Connections tab, rebuilt on full-text data'],['Cohort tracks and non-independence warning','atlas.html Explorer','Reuse tracks; warning on every reused card'],['UpSet of modality combinations','atlas.html Explorer','Coverage tab'],['7 families, modality taxonomy','PLAN-atlas.md Data model','Kept, plus Video/nonverbal'],['De-duplication; consortia and registries not counted','PLAN-atlas.md','Kept in every total'],['Tab. 1 × modality rings and dots','atlas.html, final-mockup.html','Available vs analysed tab, now with real links'],['Pooling query','final-mockup.html, PLAN-atlas.md','Grown into the Pooling planner'],['Family trends','data-landscape-mockup.html','Left out: 3 publication years give too little to plot'],['Reviewer tour, TP and milestone views','All atlas files','Left out: evaluation story, different audience'],['Full-text extraction for all 175 papers','PLAN-atlas.md Phase 1 (planned)','New: done here, replacing abstract-level and illustrative values'],['Blind double extraction','PLAN-atlas.md Phase 5 (planned)','New: 15 % run, results above'],['Dataset sheets, modality fingerprint, shortlist and compare, data-request draft','New','Researcher looking for data, not a reviewer'],['Participants view: age × sex, age spans, size by condition, reporting gaps','New','Who was studied, and what papers leave out'],['Instrument-overlap network and matrix','Extends Z-protocol idea','Which datasets can be harmonised']]
out=dict(meta=dict(snapshot=SNAP,papers=len(papers),fulltext=sum(p['ev']=='Full text' for p in papers),qc=dict(quotes=qc['quotes']),agree=agree,gaps=gaps,lineage=lineage,rescued=dict(applied)),families=FAM,facets=fac,papers=papers,samples=samples,datasets=list(ds.values()),feeds=feeds,tab1=tab1,planned=planned)
json.dump(out,open(H+'/catalogue.json','w'),ensure_ascii=False,indent=0)
payload=json.dumps(out,ensure_ascii=False).replace('</','<\\/')
import base64
def datauri(fn,mime): return 'data:%s;base64,%s'%(mime,base64.b64encode(open(H+'/assets/'+fn,'rb').read()).decode())
LOGOS={'/*__LOGO_DYN__*/':datauri('dynamic-logo.png','image/png'),'/*__LOGO_LOEWE__*/':datauri('loewe-logo.jpg','image/jpeg')}
import sys
ART={'home':'https://claude.ai/artifact/LyY6ymdMfPR1R7EBk8XxUU','explore':'https://claude.ai/artifact/PgxkehQRhrJuqXRHU1Dh9c','catalogue':'https://claude.ai/artifact/PgxkehQRhrJuqXRHU1Dh9c'}
SITE={'home':'index.html','explore':'catalogue.html','catalogue':'catalogue.html'}
def render(tpl,page,links):
    html=open(H+'/'+tpl).read().replace('/*__FILTERBAR__*/',open(H+'/filterbar.js').read()).replace('/*__FILTERBAR_CSS__*/',open(H+'/filterbar.css').read()).replace('/*__SHELL_CSS__*/',open(H+'/shell.css').read()).replace('/*__SHELL_JS__*/',open(H+'/shell.js').read()).replace('/*__VERSION__*/',VERSION).replace('/*__DATA__*/null',payload).replace('/*__PAGE__*/"story"',json.dumps(page)).replace('/*__LINKS__*/{home:"index.html",explore:"explore.html",catalogue:"catalogue.html"}',json.dumps(links))
    for k,v in LOGOS.items(): html=html.replace(k,v)
    return html
site=sys.argv[sys.argv.index('--site')+1] if '--site' in sys.argv else None
if site:
    os.makedirs(site,exist_ok=True)
    open(site+'/index.html','w').write(render('showcase.html','story',SITE))
    open(site+'/catalogue.html','w').write(render('template.html','catalogue',SITE))
    json.dump(out,open(site+'/catalogue.json','w'),ensure_ascii=False,indent=0)
    print('site written to',site)
else:
    open(H+'/../data-showcase.html','w').write(render('showcase.html','story',ART))
    open(H+'/../data-catalogue.html','w').write(render('template.html','catalogue',ART))
# ---- report
print('papers',len(papers),'samples',len(S),'datasets',len(ds),'named',sum(d['named'] for d in ds.values()),'quotes',qc['quotes'],'problems',len(PROBLEMS),'rescued',dict(applied))
for f in('n','f','am','a0'): print(f,sum(1 for s in S if s[f] is not None),'/',len(S))
print('tab1 used',sorted(t['ds'] for t in tab1 if t['ds'] in ds))
print('reused',[(d['name'],c) for d,c in sorted(((ds[k],len({s['p'] for s in S if s['ds']==k})) for k in ds),key=lambda x:-x[1]) if c>1])
print('named other',sorted(d['name'] for d in ds.values() if d['named'] and not d['tab1']))
print('access',C.Counter(p['ac'] for p in papers).most_common())
print('agree',agree); print('dedup n',sum(max([s['n'] or 0 for s in S if s['ds']==k] or [0]) for k,d in ds.items() if not d['pool']))
print('html kB',os.path.getsize(H+'/../data-catalogue.html')//1024)
