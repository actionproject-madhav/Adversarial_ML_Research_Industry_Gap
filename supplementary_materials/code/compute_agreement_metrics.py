#!/usr/bin/env python3
"""
Compute inter-rater reliability metrics between human and GPT-4o codings.
Reports: Cohen's kappa, Krippendorff's alpha, Gwet's AC1, PABAK, and ICC.
"""

import pandas as pd
import numpy as np
import re
import json
from sklearn.metrics import cohen_kappa_score
import krippendorff

def gwet_ac1(rater1, rater2):
    """Compute Gwet's AC1 for two raters on nominal data."""
    n = len(rater1)
    categories = sorted(set(list(rater1) + list(rater2)))
    k = len(categories)

    if k <= 1:
        return 1.0

    po = sum(r1 == r2 for r1, r2 in zip(rater1, rater2)) / n

    pi = []
    for cat in categories:
        p_k = (sum(r == cat for r in rater1) + sum(r == cat for r in rater2)) / (2 * n)
        pi.append(p_k)

    pe = sum(p * (1 - p) for p in pi) / (k - 1) if k > 1 else 0

    if pe == 1:
        return 1.0

    ac1 = (po - pe) / (1 - pe)
    return ac1


def pabak(rater1, rater2):
    """Compute Prevalence-Adjusted Bias-Adjusted Kappa."""
    n = len(rater1)
    po = sum(r1 == r2 for r1, r2 in zip(rater1, rater2)) / n
    return 2 * po - 1


def icc_21(rater1_vals, rater2_vals):
    """Compute ICC(2,1) two-way random effects, single measures."""
    n = len(rater1_vals)
    data = np.column_stack([rater1_vals, rater2_vals])
    k = 2

    grand_mean = data.mean()
    row_means = data.mean(axis=1)
    col_means = data.mean(axis=0)

    ss_total = np.sum((data - grand_mean) ** 2)
    ss_rows = k * np.sum((row_means - grand_mean) ** 2)
    ss_cols = n * np.sum((col_means - grand_mean) ** 2)
    ss_error = ss_total - ss_rows - ss_cols

    ms_rows = ss_rows / (n - 1)
    ms_cols = ss_cols / (k - 1)
    ms_error = ss_error / ((n - 1) * (k - 1))

    icc = (ms_rows - ms_error) / (ms_rows + (k - 1) * ms_error + k * (ms_cols - ms_error) / n)
    return icc


def interpret_kappa(k):
    """Interpret Cohen's kappa value."""
    if k > 0.80:
        return "Almost Perfect"
    elif k > 0.60:
        return "Substantial"
    elif k > 0.40:
        return "Moderate"
    elif k > 0.20:
        return "Fair"
    else:
        return "Slight/Poor"


# Load data
manual = pd.read_csv('../validation/manual_coding_sample_50.csv', keep_default_na=False)
gpt = pd.read_csv('../data/gpt4o_coding_results_v2.csv', keep_default_na=False)

# Match filenames
def extract_core_filename(fn):
    """Strip zz_NN_ and CONF_YEAR_ prefixes to get core filename."""
    fn = re.sub(r'^zz_\d+_', '', fn)
    fn = re.sub(r'^(ACM|IEEE|NDS|NDSS|USENIX)_\d{4}_', '', fn)
    return fn

manual['core_fn'] = manual['Filename'].apply(extract_core_filename)
gpt['core_fn'] = gpt['Filename'].apply(extract_core_filename)

matched = []
for _, m_row in manual.iterrows():
    g_matches = gpt[gpt['core_fn'] == m_row['core_fn']]
    if len(g_matches) == 0:
        print(f"WARNING: No GPT match for {m_row['Filename']} (core: {m_row['core_fn']})")
        continue
    g_row = g_matches.iloc[0]
    matched.append({
        'Paper_ID': m_row['Paper_ID'],
        'Filename': m_row['Filename'],
        'human_G1': m_row['YOUR_G1'].strip(),
        'gpt_G1': g_row['G1'].strip(),
        'human_G2': m_row['YOUR_G2'].strip(),
        'gpt_G2': g_row['G2'].strip(),
        'human_G3': m_row['YOUR_G3'].strip() if '/' not in str(m_row['YOUR_G3']) else 'Multiple',
        'gpt_G3': g_row['G3'].strip(),
        'human_G4': m_row['YOUR_G4'].strip(),
        'gpt_G4': g_row['G4'].strip(),
        'human_G5': m_row['YOUR_G5'].strip(),
        'gpt_G5': g_row['G5'].strip(),
        'human_G6': m_row['YOUR_G6'].strip(),
        'gpt_G6': g_row['G6'].strip(),
        'human_T1': m_row['YOUR_T1'].strip(),
        'gpt_T1': g_row['T1'].strip(),
        'human_Q1': m_row['YOUR_Q1'].strip(),
        'gpt_Q1': g_row['Q1'].strip(),
        'human_Q2': m_row['YOUR_Q2'].strip(),
        'gpt_Q2': g_row['Q2'].strip(),
    })

df = pd.DataFrame(matched)
print(f"Matched {len(df)} papers out of {len(manual)} manual codings\n")

# Compute metrics for each dimension
dimensions = [
    ('G1', 'Focus (atk/def/both)', 'nominal'),
    ('G2', 'Attack Type', 'nominal'),
    ('G3', 'Data Modality', 'nominal'),
    ('G4', 'Economic Analysis', 'nominal'),
    ('G5', 'Code Release', 'nominal'),
    ('G6', 'Real System Testing', 'nominal'),
    ('T1', 'Threat Model', 'nominal'),
    ('Q1', 'Gradient Dependency', 'nominal'),
    ('Q2', 'Query Budget', 'ordinal'),
]

results = []
print("=" * 100)
print(f"{'Dim':<5} {'Description':<25} {'Agree%':<10} {'Kappa':<8} {'K-Alpha':<8} {'AC1':<8} {'PABAK':<8} {'ICC':<8} {'Interp':<15}")
print("=" * 100)

for dim_id, desc, dtype in dimensions:
    h_col = f'human_{dim_id}'
    g_col = f'gpt_{dim_id}'

    human_vals = df[h_col].values
    gpt_vals = df[g_col].values

    n = len(human_vals)
    agreement = sum(h == g for h, g in zip(human_vals, gpt_vals))
    agree_pct = 100 * agreement / n

    # Cohen's kappa
    try:
        kappa = cohen_kappa_score(human_vals, gpt_vals)
    except Exception:
        kappa = float('nan')

    # Krippendorff's alpha
    try:
        all_cats = sorted(set(list(human_vals) + list(gpt_vals)))
        cat_map = {c: i for i, c in enumerate(all_cats)}
        h_numeric = [cat_map[v] for v in human_vals]
        g_numeric = [cat_map[v] for v in gpt_vals]
        reliability_data = np.array([h_numeric, g_numeric])
        k_alpha = krippendorff.alpha(reliability_data=reliability_data, level_of_measurement='nominal')
    except Exception as e:
        k_alpha = float('nan')

    # Gwet's AC1
    try:
        ac1 = gwet_ac1(human_vals, gpt_vals)
    except Exception:
        ac1 = float('nan')

    # PABAK
    pabak_val = pabak(human_vals, gpt_vals)

    # ICC (encode categorically as integers)
    try:
        all_cats = sorted(set(list(human_vals) + list(gpt_vals)))
        cat_map = {c: i for i, c in enumerate(all_cats)}
        h_num = np.array([cat_map[v] for v in human_vals], dtype=float)
        g_num = np.array([cat_map[v] for v in gpt_vals], dtype=float)
        icc_val = icc_21(h_num, g_num)
    except Exception:
        icc_val = float('nan')

    interp = interpret_kappa(kappa) if not np.isnan(kappa) else "N/A"

    print(f"{dim_id:<5} {desc:<25} {agree_pct:<10.1f} {kappa:<8.3f} {k_alpha:<8.3f} {ac1:<8.3f} {pabak_val:<8.3f} {icc_val:<8.3f} {interp:<15}")

    results.append({
        'dimension': dim_id,
        'description': desc,
        'n': n,
        'agreement_count': agreement,
        'agreement_pct': round(agree_pct, 1),
        'cohens_kappa': round(kappa, 3) if not np.isnan(kappa) else None,
        'krippendorff_alpha': round(k_alpha, 3) if not np.isnan(k_alpha) else None,
        'gwet_ac1': round(ac1, 3) if not np.isnan(ac1) else None,
        'pabak': round(pabak_val, 3),
        'icc_21': round(icc_val, 3) if not np.isnan(icc_val) else None,
        'interpretation': interp,
    })

print("=" * 100)

# Save results
with open('../validation/agreement_metrics_results.json', 'w') as f:
    json.dump(results, f, indent=2)

# Also save as CSV
results_df = pd.DataFrame(results)
results_df.to_csv('../validation/agreement_metrics_results.csv', index=False)

print(f"\nResults saved to agreement_metrics_results.json and .csv")

# Print LaTeX table
print("\n\n=== LATEX TABLE ===\n")
print(r"\begin{table}[htbp]")
print(r"\caption{Inter-rater reliability between human and GPT-4o coding (N=50)}")
print(r"\label{tab:agreement}")
print(r"\centering")
print(r"\small")
print(r"\begin{tabular}{llccccc}")
print(r"\hline")
print(r"\textbf{Dim.} & \textbf{Description} & \textbf{Agree\%} & \textbf{$\kappa$} & \textbf{$\alpha_K$} & \textbf{AC1} & \textbf{Interp.} \\")
print(r"\hline")
for r in results:
    kappa_str = f"{r['cohens_kappa']:.2f}" if r['cohens_kappa'] is not None else "N/A"
    alpha_str = f"{r['krippendorff_alpha']:.2f}" if r['krippendorff_alpha'] is not None else "N/A"
    ac1_str = f"{r['gwet_ac1']:.2f}" if r['gwet_ac1'] is not None else "N/A"
    interp = r['interpretation']
    if r['dimension'] == 'G4':
        interp = "Perfect*"
        kappa_str = "N/A*"
        alpha_str = "N/A*"
    print(f"{r['dimension']} & {r['description']} & {r['agreement_pct']:.0f}\\% & {kappa_str} & {alpha_str} & {ac1_str} & {interp} \\\\")
print(r"\hline")
print(r"\end{tabular}")
print()
print(r"{\small $\kappa$: Cohen's kappa; $\alpha_K$: Krippendorff's alpha; AC1: Gwet's AC1.}")
print(r"{\small *G4: Zero variance (all 50 papers coded ``No'' by both raters); $\kappa$ and $\alpha_K$ undefined.}")
print(r"{\small Interpretation (Landis \& Koch): $>$0.80 Almost Perfect, 0.61--0.80 Substantial, 0.41--0.60 Moderate.}")
print(r"\end{table}")
