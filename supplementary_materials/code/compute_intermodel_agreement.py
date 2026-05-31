#!/usr/bin/env python3
"""
Compute inter-model agreement between GPT-4o and Gemini codings,
and compare both to human ground truth on the 50-paper sample.

Run after both code_all_papers_gpt4o.py and code_all_papers_gemini.py complete.

Usage:
    python3 compute_intermodel_agreement.py
"""

import pandas as pd
import numpy as np
import re
import json
from sklearn.metrics import cohen_kappa_score

def gwet_ac1(r1, r2):
    n = len(r1)
    cats = sorted(set(list(r1) + list(r2)))
    k = len(cats)
    if k <= 1:
        return 1.0
    po = sum(a == b for a, b in zip(r1, r2)) / n
    pi = [(sum(r == c for r in r1) + sum(r == c for r in r2)) / (2 * n) for c in cats]
    pe = sum(p * (1 - p) for p in pi) / (k - 1) if k > 1 else 0
    return (po - pe) / (1 - pe) if pe != 1 else 1.0

def interpret(k):
    if k > 0.80: return "Almost Perfect"
    elif k > 0.60: return "Substantial"
    elif k > 0.40: return "Moderate"
    elif k > 0.20: return "Fair"
    else: return "Slight/Poor"

def core_fn(fn):
    fn = re.sub(r'^zz_\d+_', '', fn)
    fn = re.sub(r'^(ACM|IEEE|NDS|NDSS|USENIX)_\d{4}_', '', fn)
    return fn

# Load data
print("Loading data...")
gpt = pd.read_csv('../data/gpt4o_coding_results_v2.csv', keep_default_na=False)
gemini = pd.read_csv('../data/gemini_coding_results.csv', keep_default_na=False)

gpt = gpt.replace('', 'NA')
gemini = gemini.replace('', 'NA')

# Match by filename
gpt['core_fn'] = gpt['Filename'].apply(core_fn)
gemini['core_fn'] = gemini['Filename'].apply(core_fn)

merged = gpt.merge(gemini, on='core_fn', suffixes=('_gpt', '_gem'))
print(f"Matched {len(merged)} papers between GPT-4o and Gemini\n")

dims = ['G1', 'G2', 'G3', 'G4', 'G5', 'G6', 'T1', 'Q1', 'Q2']
dim_labels = {
    'G1': 'Focus', 'G2': 'Attack Type', 'G3': 'Domain',
    'G4': 'Economic', 'G5': 'Code', 'G6': 'Real System',
    'T1': 'Threat Model', 'Q1': 'Gradient', 'Q2': 'Query Budget'
}

# ============================================================================
# PART 1: GPT-4o vs Gemini agreement (full corpus)
# ============================================================================
print("=" * 70)
print("PART 1: GPT-4o vs Gemini Inter-Model Agreement (full corpus)")
print("=" * 70)
print(f"\n{'Dim':<5} {'Description':<15} {'Agree%':>8} {'Kappa':>8} {'AC1':>8} {'Interp':<15}")
print("-" * 65)

results_intermodel = []
for dim in dims:
    g = merged[f'{dim}_gpt'].str.strip().values
    m = merged[f'{dim}_gem'].str.strip().values
    agree = 100 * sum(a == b for a, b in zip(g, m)) / len(g)
    try:
        kappa = cohen_kappa_score(g, m)
    except:
        kappa = float('nan')
    try:
        ac1 = gwet_ac1(g, m)
    except:
        ac1 = float('nan')
    interp = interpret(kappa) if not np.isnan(kappa) else "N/A (zero var)"
    print(f"{dim:<5} {dim_labels[dim]:<15} {agree:>7.1f}% {kappa:>8.3f} {ac1:>8.3f} {interp}")
    results_intermodel.append({
        'dimension': dim, 'description': dim_labels[dim],
        'n': len(g), 'agreement_pct': round(agree, 1),
        'kappa': round(kappa, 3) if not np.isnan(kappa) else None,
        'ac1': round(ac1, 3) if not np.isnan(ac1) else None,
        'interpretation': interp
    })

# Show disagreement patterns for key dimensions
print("\n\nDisagreement patterns (top 5 per dimension):")
for dim in dims:
    g = merged[f'{dim}_gpt'].str.strip().values
    m = merged[f'{dim}_gem'].str.strip().values
    patterns = {}
    for gv, mv in zip(g, m):
        if gv != mv:
            key = f"GPT={gv} -> Gem={mv}"
            patterns[key] = patterns.get(key, 0) + 1
    if patterns:
        print(f"\n  {dim} ({dim_labels[dim]}):")
        for pat, count in sorted(patterns.items(), key=lambda x: -x[1])[:5]:
            print(f"    {pat}: {count}x")

# ============================================================================
# PART 2: Both models vs human ground truth (50-paper sample)
# ============================================================================
print("\n\n" + "=" * 70)
print("PART 2: Both Models vs Human Ground Truth (50-paper sample)")
print("=" * 70)

manual = pd.read_csv('../validation/manual_coding_sample_50.csv',
                      keep_default_na=False)
manual['core_fn'] = manual['Filename'].apply(core_fn)

print(f"\n{'Dim':<5} {'Description':<15} {'GPT κ':>8} {'Gem κ':>8} {'GPT Agr%':>10} {'Gem Agr%':>10} {'Closer':<8}")
print("-" * 70)

results_vs_human = []
for dim in dims:
    h_col = f'YOUR_{dim}'
    # Match manual to both models
    matched_rows = []
    for _, m_row in manual.iterrows():
        g_match = gpt[gpt['core_fn'] == m_row['core_fn']]
        gem_match = gemini[gemini['core_fn'] == m_row['core_fn']]
        if len(g_match) > 0 and len(gem_match) > 0:
            matched_rows.append({
                'human': str(m_row[h_col]).strip(),
                'gpt': str(g_match.iloc[0][dim]).strip(),
                'gemini': str(gem_match.iloc[0][dim]).strip()
            })

    if not matched_rows:
        print(f"{dim:<5} {dim_labels[dim]:<15} -- no matches --")
        continue

    h_vals = [r['human'] for r in matched_rows]
    g_vals = [r['gpt'] for r in matched_rows]
    m_vals = [r['gemini'] for r in matched_rows]

    gpt_agree = 100 * sum(h == g for h, g in zip(h_vals, g_vals)) / len(h_vals)
    gem_agree = 100 * sum(h == m for h, m in zip(h_vals, m_vals)) / len(h_vals)

    try:
        k_gpt = cohen_kappa_score(h_vals, g_vals)
    except:
        k_gpt = float('nan')
    try:
        k_gem = cohen_kappa_score(h_vals, m_vals)
    except:
        k_gem = float('nan')

    closer = "Gemini" if (not np.isnan(k_gem) and (np.isnan(k_gpt) or k_gem > k_gpt)) else "GPT-4o"
    if np.isnan(k_gpt) and np.isnan(k_gem):
        closer = "Tie"

    k_gpt_s = f"{k_gpt:.3f}" if not np.isnan(k_gpt) else "N/A"
    k_gem_s = f"{k_gem:.3f}" if not np.isnan(k_gem) else "N/A"

    print(f"{dim:<5} {dim_labels[dim]:<15} {k_gpt_s:>8} {k_gem_s:>8} {gpt_agree:>9.1f}% {gem_agree:>9.1f}% {closer}")

    results_vs_human.append({
        'dimension': dim, 'description': dim_labels[dim],
        'gpt_kappa': round(k_gpt, 3) if not np.isnan(k_gpt) else None,
        'gemini_kappa': round(k_gem, 3) if not np.isnan(k_gem) else None,
        'gpt_agreement_pct': round(gpt_agree, 1),
        'gemini_agreement_pct': round(gem_agree, 1),
        'closer_to_human': closer
    })

# ============================================================================
# PART 3: Headline statistics comparison
# ============================================================================
print("\n\n" + "=" * 70)
print("PART 3: Headline Statistics Comparison")
print("=" * 70)

for label, df_model, name in [(gpt, gpt, "GPT-4o"), (gemini, gemini, "Gemini")]:
    n = len(df_model)
    wb = 100 * df_model['T1'].str.contains('White-box', na=False).sum() / n
    q1_app = df_model[df_model['Q1'] != 'NA']
    grad = 100 * (q1_app['Q1'] == 'Yes').sum() / len(q1_app) if len(q1_app) > 0 else 0
    rs = 100 * (df_model['G6'] == 'Yes').sum() / n
    econ = 100 * (df_model['G4'] == 'Yes').sum() / n
    q2_disc = df_model[(df_model['Q2'] != 'None') & (df_model['Q2'] != 'NA')]
    hq = 100 * (q2_disc['Q2'] == 'High').sum() / len(q2_disc) if len(q2_disc) > 0 else 0
    code = 100 * (df_model['G5'] == 'Yes').sum() / n

    print(f"\n  {name} (N={n}):")
    print(f"    White-box:      {wb:.1f}%")
    print(f"    Gradient (app): {grad:.1f}% (of {len(q1_app)} applicable)")
    print(f"    Real-system:    {rs:.1f}%")
    print(f"    Economic:       {econ:.1f}%")
    print(f"    High query:     {hq:.1f}% (of {len(q2_disc)} with queries)")
    print(f"    Code release:   {code:.1f}%")

# Save results
output = {
    'intermodel_agreement': results_intermodel,
    'vs_human_ground_truth': results_vs_human
}
with open('../validation/intermodel_agreement.json', 'w') as f:
    json.dump(output, f, indent=2)

print(f"\n\nResults saved to intermodel_agreement.json")
print("Done!")
