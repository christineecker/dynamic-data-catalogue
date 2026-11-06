# DYNAMIC Data Catalogue

The data catalogue of the LOEWE Center DYNAMIC. Live: https://christineecker.github.io/dynamic-data-catalogue/

What the papers of the LOEWE Center DYNAMIC analysed: cohorts, data modalities, sample sizes and participant details, extracted from the full text of every paper in the centre's library and checked against verbatim quotes.

Two pages, both built from the same `catalogue.json`:

| Page | For whom |
|---|---|
| [index.html](index.html) · Overview | An overview of the data: every analysed sample in one picture, then breadth, multimodality, cohorts, people, growth and what pooling makes possible |
| [catalogue.html](catalogue.html) · Catalogue | Researchers: filters, dataset cards and tables, CSV export, coverage map, participant charts, instrument network, available-vs-analysed, pooling planner with shortlist |

## How the numbers are made

- One record per analysed sample per paper. Sample sizes are what a paper analysed, not what a cohort holds.
- Every n, group size, share female and age sits inside a quote that a script found in the source text. Derived values (for example a percentage computed from counts) are marked.
- Participant totals take the largest n per dataset and never sum across papers. Consortia, registries and meta-analytic pools are listed, not counted.
- A blind second extraction of 15 % of papers measures repeatability; a hand pass corrected cohort links both passes had missed.
- Preprints are excluded.

Dataset reference rows (name, approximate size, diagnosis, availability, responsible PI, remark) come from the centre's proposal, Anhang Tab. 1.

## Rebuilding

The build reads the paper library (`papers/<PMID>/metadata.json` and `fulltext.md`) to re-verify every quote. The library is not in this repository: papers are copyrighted. From a machine that has it:

```
cd <DYNAMIC library>
python <this repo>/src/build.py --site <this repo>
```

`src/extraction/` holds the extraction output, `SCHEMA.md` with the rules the extraction agents followed, and the quote checkers `verify.py` and `verify2.py`.

Snapshot 2026-11-06 · 175 papers.
