# Supplementary Materials: Theory-Practice Gap in Adversarial ML (2022-2025)

This repository contains all supplementary materials for the paper "Bridging the Gap Between Theory and Practice in Adversarial Machine Learning: A Systematic Analysis of 454 Papers (2022--2025)" submitted to ACNS-ISC 2026.

## Contents

### 📊 Data (`data/`)
- **`all_conferences_analysis_results_2022_2025.csv`**: Complete dataset of 454 papers with coding results
  - Columns: Year, Conference, Filename, Title, Authors, G1-G7, T1-T2, Q1-Q3, Flags, Gap Score
  - 454 rows (papers) × 23 columns
  
- **`benchmark_criteria.csv`**: Machine-readable codebook
  - 12 dimensions with options, definitions, and examples
  - Used to generate the GPT-4o prompt

### 💻 Code (`code/`)
- **`benchmark_review_automation.py`**: GPT-4o-based paper coding pipeline
  - Extracts text from PDFs using PyPDF2
  - Sends structured prompts to GPT-4o (temperature=0)
  - Parses responses and calculates Gap Scores
  
- **`generate_figures.py`**: Figure generation script
  - Creates all 12 figures used in the paper
  - Uses matplotlib and seaborn
  
- **`requirements.txt`**: Python dependencies
  - openai, pandas, numpy, matplotlib, seaborn, PyPDF2, python-dotenv

### 📝 Prompts (`prompts/`)
- **`gpt4o_analysis_prompt.txt`**: Complete GPT-4o prompt template
  - Shows exact prompt structure used for all 454 papers
  - Includes all 12 questions with options and instructions
  - Temperature=0 for deterministic responses

### 📈 Results (`results/`)
- **`statistical_analysis_results.txt`**: Raw statistical analysis output
  - Confidence intervals (95% CI)
  - Logistic regression results (temporal trends)
  - Chi-square tests (cross-venue comparison)
  - Fisher's exact tests (attack vs. defense)
  - Per-domain Gap Score breakdown
  
- **`figures/`**: All figures used in the paper (PNG format)
  - fig01_dataset_overview.png
  - fig02_theory_practice_gap.png
  - fig03_threat_model.png
  - fig04_gradient_dependency.png
  - fig05_real_world_testing.png
  - fig06_query_budget.png
  - fig08_data_domains.png
  - fig09_attack_vs_defense.png
  - fig10_conference_comparison.png
  - fig11_yearly_trends.png
  - fig12_gap_score.png
  - claude.png (AI-orchestrated attack lifecycle)

### 📚 Documentation (`docs/`)
- (Reserved for additional documentation)

### 📄 Raw Papers (`raw_papers/`)
- (Not included due to copyright - papers available from conference proceedings)

## Replication Guide

### 1. Setup Environment

```bash
# Install Python dependencies
pip install -r code/requirements.txt

# Set up OpenAI API key (required for paper coding)
export OPENAI_API_KEY="your-api-key-here"
```

### 2. Reproduce Paper Coding

```bash
# Run the GPT-4o coding pipeline
python code/benchmark_review_automation.py

# This will:
# - Read PDFs from paper directories
# - Extract text using PyPDF2
# - Send prompts to GPT-4o
# - Save results to CSV
```

**Note**: You'll need the original PDF files (not included due to copyright). Papers are available from:
- ACM CCS: https://dl.acm.org/conference/ccs
- IEEE S&P: https://ieeexplore.ieee.org/xpl/conhome/1000646/all-proceedings
- NDSS: https://www.ndss-symposium.org/
- USENIX Security: https://www.usenix.org/conferences/byname/108

### 3. Reproduce Statistical Analysis

```bash
# The statistical analysis is embedded in the figure generation script
python code/generate_figures.py

# This will:
# - Load data/all_conferences_analysis_results_2022_2025.csv
# - Compute statistics (CIs, p-values, etc.)
# - Generate all figures
```

### 4. Reproduce Figures

```bash
# Generate all figures
python code/generate_figures.py

# Figures will be saved to results/figures/
```

## Data Dictionary

### CSV Columns

| Column | Type | Description | Values |
|--------|------|-------------|--------|
| Year | int | Publication year | 2022-2025 |
| Conference | str | Venue | ACM, IEEE, NDS, USENIX |
| Filename | str | PDF filename | e.g., "3548606.3559335.pdf" |
| Title | str | Paper title | Extracted from PDF |
| Authors | str | Author names | Extracted from PDF |
| G1 | str | Research focus | atk, def, both |
| G2 | str | Attack type | Evasion, Poisoning, Privacy, Multiple, NA |
| G3 | str | ML type | DL, Traditional, Both |
| G4 | str | Data domain | Images, Text, Audio, Malware, Other |
| G5 | str | Economics mentioned | YES, NO |
| G6 | str | Code released | YES, NO |
| G7 | str | Real system testing | YES, NO |
| T1 | str | Threat model | White-box, Gray-box, Black-box |
| T2 | str | Training data access | Full, Partial, None |
| Q1 | str | Gradient requirement | YES, NO |
| Q2 | str | Query budget | High, Low, None |
| Q3 | str | Computational resources | High, Low |
| Flag_Grad | int | Requires gradients (1=yes) | 0, 1 |
| Flag_HighQ | int | High query budget (1=yes) | 0, 1 |
| Flag_WB | int | White-box assumption (1=yes) | 0, 1 |
| Flag_NoEcon | int | No economics (1=yes) | 0, 1 |
| Flag_NoCode | int | No code released (1=yes) | 0, 1 |
| Flag_NoReal | int | No real system testing (1=yes) | 0, 1 |
| Traditional_Score | int | Gap Score (sum of flags) | 0-6 |

### Gap Score Calculation

```
Gap Score = Flag_WB + Flag_Grad + Flag_HighQ + Flag_HighComp + Flag_NoReal + Flag_NoEcon
```

Where:
- **Flag_WB**: 1 if T1 = "White-box", else 0
- **Flag_Grad**: 1 if Q1 = "YES", else 0
- **Flag_HighQ**: 1 if Q2 = "High", else 0
- **Flag_HighComp**: 1 if Q3 = "High", else 0
- **Flag_NoReal**: 1 if G7 = "NO", else 0
- **Flag_NoEcon**: 1 if G5 = "NO", else 0

**Interpretation**:
- 0-1: Highly practical (aligned with deployment constraints)
- 2-3: Moderately practical
- 4: Typical academic paper (some impractical assumptions)
- 5-6: Highly idealized (many impractical assumptions)

## Key Statistics

### Overall Findings (454 papers)
- **Real-world testing**: 5.3% [95% CI: 3.6%, 7.6%]
- **Gradient dependency**: 67.8% [63.4%, 72.0%]
- **White-box assumptions**: 63.2% [58.7%, 67.5%]
- **High query budgets**: 80.4% [76.5%, 83.8%]
- **Mean Gap Score**: 3.17 out of 6

### Temporal Trends (2022-2025)
- No statistically significant improvement on any indicator
- Logistic regression: all p > 0.28

### Cross-Venue Comparison
- All four conferences show similar gap patterns
- Chi-square tests: all p > 0.20
- Mean Gap Scores: CCS 3.04, NDSS 3.12, S&P 3.18, USENIX 3.25

### Attack vs. Defense
- Attack papers: 72.7% gradient dependency, 90.0% high query budgets
- Defense papers: 59.4% gradient dependency, 64.6% high query budgets
- Significant differences: p = 0.004 (gradients), p < 0.001 (queries)

### Per-Domain Analysis
- **Images**: Gap Score 3.57 (83.3% gradients, 1.7% real-system)
- **Text/LLM**: Gap Score 2.62 (43.8% gradients, 4.2% real-system)
- **Audio**: Gap Score 1.83 (26.7% gradients, 36.7% real-system)
- **Malware**: Gap Score 2.41 (37.0% gradients, 7.4% real-system)

## Citation

If you use this dataset or code, please cite:

```bibtex
@inproceedings{anonymous2026gap,
  title={Bridging the Gap Between Theory and Practice in Adversarial Machine Learning: A Systematic Analysis of 454 Papers (2022--2025)},
  author={Anonymous},
  booktitle={ACNS-ISC 2026 Workshop},
  year={2026}
}
```

## License

This dataset and code will be released under an open license (MIT or CC-BY) upon paper acceptance.

## Contact

For questions or issues, please contact [to be added after acceptance].

## Acknowledgments

This work builds on the framework introduced by Apruzzese et al. in "Real Attackers Don't Compute Gradients: Bridging the Gap Between Adversarial ML Research and Practice" (IEEE S&P 2023).
