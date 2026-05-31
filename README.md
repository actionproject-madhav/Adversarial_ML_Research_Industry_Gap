# Theory-Practice Gap in Adversarial ML

This repository contains the camera-ready ACNS-ISC 2026 workshop paper and
supplementary materials for:

**Examining the Gap Between Theory and Practice in Adversarial Machine Learning:
A Study of 459 Papers (2022--2025)**

Authors: Madhav Khanal and Jasser Jasser.

## Repository Layout

- `ACNS/` - final camera-ready paper files for ACNS-ISC 2026.
- `ACNS/paper/` - LaTeX source for the final 20-page LNCS paper.
- `supplementary_materials/` - public replication package with data, prompts,
  validation results, analysis scripts, and figures.
- `supplementary_materials_submission.zip` - zipped copy of
  `supplementary_materials/` for convenient upload/sharing.

## Final Paper

The final camera-ready PDF is:

`ACNS/ISC-1-main.pdf`

It is 20 pages total in standard Springer LNCS format, under the 22-page ACNS
camera-ready limit. The source archive submitted to ACNS is:

`ACNS/ISC-1-archive.zip`

## Supplementary Materials

The supplementary package contains:

- Primary GPT-4o coding results for all 459 papers.
- Independent Gemini coding results for dual-LLM validation.
- Manual 50-paper validation sample and agreement metrics.
- Codebook and GPT-4o prompt.
- Statistical summary JSON and final paper figures.
- Scripts for coding, statistics, inter-model agreement, and reliability checks.

Raw copyrighted paper PDFs are not included. The scripts expect users to provide
their own local copies of papers from the relevant conference proceedings.

## Key Results

- 459 papers from ACM CCS, IEEE S&P, NDSS, and USENIX Security.
- 84.3% of papers do not evaluate on deployed systems.
- 44.6% of applicable papers require gradient access.
- 27.5% assume white-box or mixed white-box/black-box threat models.
- 72.5% do not explicitly discuss query budgets.
- 97.2% lack strict economic analysis with explicit monetary figures.
- Mean Gap Score: 2.53 out of 5.

## Citation

```bibtex
@inproceedings{khanal2026examining,
  title={Examining the Gap Between Theory and Practice in Adversarial Machine Learning: A Study of 459 Papers (2022--2025)},
  author={Khanal, Madhav and Jasser, Jasser},
  booktitle={ACNS-ISC 2026 Workshop},
  year={2026}
}
```
