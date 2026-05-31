# Supplementary Materials

Supplementary materials for:

**Examining the Gap Between Theory and Practice in Adversarial Machine Learning:
A Study of 459 Papers (2022--2025)**

This directory contains the public replication and validation package for the
camera-ready ACNS-ISC 2026 paper.

## Contents

- `data/gpt4o_coding_results_v2.csv` - primary coding dataset for all 459 papers.
- `data/gemini_coding_results.csv` - independent Gemini coding for dual-LLM validation.
- `data/codebook.md` - operational definitions for all nine coding dimensions.
- `prompts/gpt4o_analysis_prompt.txt` - complete GPT-4o coding prompt.
- `validation/manual_coding_sample_50.csv` - human-coded validation sample.
- `validation/agreement_metrics_results.csv` - human vs. GPT-4o reliability metrics.
- `validation/intermodel_agreement.json` - GPT-4o vs. Gemini agreement and model-vs-human comparison.
- `results/stats_v2_summary.json` - full statistical summary for the camera-ready paper.
- `results/figures/` - final figures used in the camera-ready paper.
- `docs/appendix_tables.md` - appendix tables moved out of the proceedings PDF.
- `code/` - scripts used for coding, statistics, figures, and validation.

Raw paper PDFs are not included because they are copyrighted by their
publishers. To rerun the coding pipeline, place locally obtained paper PDFs in a
`raw_papers/` directory and set `RAW_PAPERS_DIR` if needed.

## Reproducing the Main Statistics

From this directory:

```bash
cd code
python3 compute_stats_v2.py
python3 compute_agreement_metrics.py
python3 compute_intermodel_agreement.py
```

The coding scripts require API keys:

```bash
export OPENAI_API_KEY="..."
export GOOGLE_API_KEY="..."
```

Then run:

```bash
cd code
python3 code_all_papers_gpt4o.py
python3 code_all_papers_gemini.py
```

By default, these scripts read PDFs from `../raw_papers` and write CSV output to
`../data`. You can override those locations with `RAW_PAPERS_DIR` and
`OUTPUT_DIR`.

## Core Dataset

The primary dataset is `data/gpt4o_coding_results_v2.csv`.

It contains 459 rows and the following fields:

- `Paper_ID`
- `Year`
- `Conference`
- `Filename`
- `G1`, `G2`, `G3`, `G4`, `G5`, `G6`
- `T1`, `Q1`, `Q2`

The paper reports GPT-4o as the primary coding because it aligned more closely
with human judgment on 7 of 9 dimensions in the validation sample and produced
conservative estimates for real-system testing and economic analysis.

## Notes

The camera-ready paper includes the headline validation and sensitivity results.
Full appendix-style tables are provided in `docs/appendix_tables.md`.
