# Extraction task: DYNAMIC data catalogue

Extract, for each paper, WHICH DATA THE AUTHORS ANALYSED IN THIS PAPER. Read only the given packet. Be exact: null beats a guess. Never use outside knowledge for values. Exclude cohorts merely cited.

Output: a JSON array with one record per PMID, no commentary:

{"pmid":"…",
 "paper_type":"Original|Protocol|Review|Systematic review/meta-analysis|Methods/simulation|Commentary|Case report",
 "species":"Human|Animal|In silico|None",
 "design":"Cross-sectional|Case-control|Longitudinal cohort|Intensive longitudinal (EMA)|RCT|Non-randomised intervention|Experimental|Secondary analysis|Evidence synthesis|Not applicable",
 "approach":[any of "Network (cross-sectional)","Network (idiographic/time-varying)","Network control theory","Machine/deep learning","NLP","Computational modelling","Conventional statistics","Normative modelling"],
 "topic":"≤12 words: what was analysed, plain English",
 "samples":[ one per distinct analysed dataset; [] for reviews/commentaries/theory with no participant data
  {"name":"name exactly as the paper uses it, or null when the paper gives none",
   "canonical":"the entry from the REFERENCE LIST below if the paper clearly says data come from it, else null. Never infer from authorship or site",
   "kind":"Named cohort|Consortium|Trial|Registry|Study sample|Meta-analysis pool|Public dataset",
   "role":"primary|replication|validation|training",
   "n_analysed":int|null, "n_derived":true only when n_analysed is the sum of reported groups,
   "n_quote":"VERBATIM sentence stating n",
   "groups":[{"label":"as in paper","condition":"controlled","n":int}],
   "pct_female":num|null, "pct_female_derived":true only if computed from counts,
   "age_mean":num|null,"age_sd":num|null,"age_min":num|null,"age_max":num|null,
   "age_group":"Children|Adolescents|Youth (mixed)|Adults|Older adults|All ages|Not reported",
   "demog_quote":"VERBATIM sentence or table row with sex/age values, or null",
   "countries":["DE",…],"sites":["Marburg",…],
   "recruitment":"Clinic|Community|Online|Registry/biobank|School|Mixed|Not reported",
   "longitudinal":bool,"waves":int|null,"followup_months":num|null,"ema_detail":"e.g. 5 prompts/day for 14 days"|null,
   "modalities":[controlled],"modality_detail":{"sMRI":"3T T1, FreeSurfer"},
   "instruments":["BDI-II","SCID",…],
   "conditions":[controlled],
   "reuse":"Existing dataset|New data collection|Unclear"}],
 "open_science":{"data_access":"Open repository|On request|Restricted/controlled|Not available|Not stated","url":str|null,"quote":"VERBATIM data-availability sentence"|null,"code_available":bool|null,"preregistered":bool|null,"registration_id":str|null},
 "evidence":"Full text|Abstract only|Metadata only"}

Controlled modalities: sMRI, task-fMRI, rs-fMRI, dMRI, PET/MRS, EEG/MEG, Physiology, EMA, Actigraphy/wearable, Smartphone sensing, Glucose monitoring, Genetics, Epigenetics, Omics, Microbiome, Blood biomarkers, Clinical interview/rating, Questionnaire, Therapy records, Registry/EHR, Behavioural task, Speech/language, Video/nonverbal.
(Speech/language covers speech audio and text/NLP data. Physiology covers ECG, HRV, SCR, fitness, anthropometry measured in lab. Modelled outputs are not modalities.)

Controlled conditions: Major depression, Bipolar disorder, Schizophrenia/psychosis, Anxiety disorders, PTSD/trauma, OCD, Autism, ADHD, Conduct/externalising, Eating disorders, Substance use, Behavioural addiction, Somatic symptom/pain, Personality disorder, Medical/neurological, Mixed/transdiagnostic, At-risk/subclinical, Healthy/general population.

REFERENCE LIST for "canonical" (Vollantrag Anhang Tab. 1 plus common consortia). Use if paper names it, incl. obvious aliases (MACS, Marburg-Münster Affective Cohort Study = FOR2107; LEAP = EU-AIMS):
ACSID, A-FFIP, AMIS_EPIGEN, APPetite, ASD-Net, BESTFORCAN, BipoLife, BIU-872, CBASP-CBT, CNL, CoCA, COGITO, COMPARE, DEFLAME, Depressometer, DREAM_EPI, DynAMoND, EMA-PRED, ENCERT, ENHANCE, EpiBurn, EU-AIMS, FemNAT-CD, FOR2107, Human Connectome, KODAP, LORA, OASIS-D, Optima, P4D, Panic-Net, PaZ, PROTECT-AD, PSYHEART, R-LiNK, SASCHA, SGTreat, SOPHONet, Z-Projekt, ENIGMA, PGC, UK Biobank, ABCD, ADNI, Global Bipolar Cohort.
If a named dataset is not on the list, set canonical null and keep its "name".

Rules
- Quotes must be copied character-for-character from the packet (one continuous stretch; no ellipses, no joining). Pick a short stretch. Every number you report must occur inside its quote: n and groups in n_quote or demog_quote; pct_female, age_* in demog_quote. If values come from different places and cannot fit in one stretch, keep those you can quote and null the rest.
- If a percentage is not reported but counts are, give pct_female and set pct_female_derived:true (quote the counts).
- Report n actually analysed; if several analyses, largest analysed in the main analysis. Protocols: planned n goes in n_analysed only with a quote, and set paper_type Protocol.
- Meta-analyses: one sample, kind "Meta-analysis pool", n = pooled participants.
- Consortium papers: kind "Consortium".
- HasBody false or a thin packet: use the abstract, set evidence accordingly.
