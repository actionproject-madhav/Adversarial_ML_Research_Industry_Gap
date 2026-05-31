#!/usr/bin/env python3
"""
Compute all statistics from GPT-4o v2 coding results for ACNS paper update.
Generates comprehensive statistics with confidence intervals.
"""

import pandas as pd
import numpy as np
from scipy import stats
import json

def compute_ci_95(count, total):
    """Compute 95% confidence interval for proportion using Wilson score interval."""
    if total == 0:
        return 0.0, 0.0

    p = count / total
    z = 1.96  # 95% confidence

    denominator = 1 + z**2/total
    center = (p + z**2/(2*total)) / denominator
    margin = z * np.sqrt(p*(1-p)/total + z**2/(4*total**2)) / denominator

    lower = max(0, center - margin)
    upper = min(1, center + margin)

    return lower, upper

def format_pct_with_ci(count, total):
    """Format percentage with 95% CI."""
    if total == 0:
        return "N/A"

    pct = 100 * count / total
    lower, upper = compute_ci_95(count, total)

    return {
        "percentage": round(pct, 1),
        "count": int(count),
        "total": int(total),
        "ci_lower": round(100 * lower, 1),
        "ci_upper": round(100 * upper, 1),
        "formatted": f"{pct:.1f}% [{100*lower:.1f}%, {100*upper:.1f}%] ({count}/{total})"
    }

def compute_gap_score(row):
    """
    Compute Gap Score (0-5) for a paper.

    Flags (5 binary indicators):
    1. White-box assumption (T1 contains 'White-box')
    2. Gradient requirement (Q1 == 'Yes')
    3. High query budget (Q2 == 'High')
    4. No real-system testing (G6 == 'No')
    5. No economic consideration (G4 == 'No')

    Note: Computational resources are not part of the v2 coding framework,
    so the camera-ready paper uses a 5-point score.
    """
    score = 0

    # 1. White-box assumption
    if pd.notna(row['T1']) and 'White-box' in str(row['T1']):
        score += 1

    # 2. Gradient requirement
    if row['Q1'] == 'Yes':
        score += 1

    # 3. High query budget
    if row['Q2'] == 'High':
        score += 1

    # 4. No real-system testing
    if row['G6'] == 'No':
        score += 1

    # 5. No economic consideration
    if row['G4'] == 'No':
        score += 1

    return score

# Load data
print("Loading GPT-4o v2 coding results...")
data_path = '../data/gpt4o_coding_results_v2.csv'
df = pd.read_csv(data_path, keep_default_na=False, na_values=[''])

# Replace empty strings with 'NA' for consistency
df = df.replace('', 'NA')

print(f"Total papers: {len(df)}")

# ============================================================================
# BASIC COUNTS
# ============================================================================

stats_output = {
    "total_papers": len(df),
    "by_conference": {},
    "by_year": {},
    "by_conference_and_year": {}
}

# Conference distribution
conf_counts = df['Conference'].value_counts().to_dict()
for conf, count in conf_counts.items():
    pct = 100 * count / len(df)
    stats_output["by_conference"][conf] = {
        "count": int(count),
        "percentage": round(pct, 1)
    }

# Year distribution
year_counts = df['Year'].value_counts().sort_index().to_dict()
for year, count in year_counts.items():
    stats_output["by_year"][int(year)] = {
        "count": int(count),
        "percentage": round(100 * count / len(df), 1)
    }

# Conference x Year crosstab
conf_year = pd.crosstab(df['Conference'], df['Year'])
stats_output["by_conference_and_year"] = conf_year.to_dict()

# ============================================================================
# KEY GAP INDICATORS
# ============================================================================

# Real-world testing (G6 = Yes)
real_world_yes = (df['G6'] == 'Yes').sum()
stats_output["real_world_testing"] = format_pct_with_ci(real_world_yes, len(df))

# Gradient dependency (Q1 = Yes, excluding NA)
q1_valid = df[df['Q1'] != 'NA']
gradient_yes = (q1_valid['Q1'] == 'Yes').sum()
stats_output["gradient_dependency"] = format_pct_with_ci(gradient_yes, len(q1_valid))
stats_output["gradient_dependency"]["excluding_na"] = True

# Threat models (T1)
t1_counts = df['T1'].value_counts()
stats_output["threat_models"] = {}
for tm in ['White-box', 'Black-box', 'Gray-box', 'White-box/Black-box', 'NA']:
    count = t1_counts.get(tm, 0)
    stats_output["threat_models"][tm] = format_pct_with_ci(count, len(df))

# White-box assumption (T1 contains 'White-box')
whitebox_count = df[df['T1'].str.contains('White-box', na=False)].shape[0]
stats_output["whitebox_assumption"] = format_pct_with_ci(whitebox_count, len(df))

# Query budgets (Q2) - among papers with queries (exclude None and NA)
q2_with_queries = df[(df['Q2'] != 'None') & (df['Q2'] != 'NA')]
q2_high = (q2_with_queries['Q2'] == 'High').sum()
stats_output["query_budget_high"] = format_pct_with_ci(q2_high, len(q2_with_queries))
stats_output["query_budget_high"]["denominator_description"] = "Among papers with queries (excluding None/NA)"

# Query budget distribution
stats_output["query_budget_distribution"] = {}
for qb in ['High', 'Low', 'None', 'NA']:
    count = (df['Q2'] == qb).sum()
    stats_output["query_budget_distribution"][qb] = format_pct_with_ci(count, len(df))

# Economic analysis (G4 = Yes)
econ_yes = (df['G4'] == 'Yes').sum()
stats_output["economic_analysis"] = format_pct_with_ci(econ_yes, len(df))

# Code release (G5 = Yes)
code_yes = (df['G5'] == 'Yes').sum()
stats_output["code_release"] = format_pct_with_ci(code_yes, len(df))

# ============================================================================
# DATA MODALITIES (G3)
# ============================================================================

g3_counts = df['G3'].value_counts()
stats_output["data_modalities"] = {}
for modality in ['Images', 'Text', 'Audio', 'Malware', 'Other', 'Multiple']:
    count = g3_counts.get(modality, 0)
    stats_output["data_modalities"][modality] = format_pct_with_ci(count, len(df))

# ============================================================================
# ATTACK vs DEFENSE (G1)
# ============================================================================

g1_counts = df['G1'].value_counts()
stats_output["focus"] = {}
for focus in ['atk', 'def', 'both']:
    count = g1_counts.get(focus, 0)
    stats_output["focus"][focus] = format_pct_with_ci(count, len(df))

# ============================================================================
# ATTACK TYPES (G2)
# ============================================================================

g2_counts = df['G2'].value_counts()
stats_output["attack_types"] = {}
for attack_type in ['Evasion', 'Poisoning', 'Privacy', 'Multiple', 'NA']:
    count = g2_counts.get(attack_type, 0)
    stats_output["attack_types"][attack_type] = format_pct_with_ci(count, len(df))

# ============================================================================
# GAP SCORE
# ============================================================================

print("\nComputing Gap Scores...")
df['gap_score'] = df.apply(compute_gap_score, axis=1)

gap_score_dist = df['gap_score'].value_counts().sort_index()
stats_output["gap_score"] = {
    "mean": round(df['gap_score'].mean(), 2),
    "median": float(df['gap_score'].median()),
    "std": round(df['gap_score'].std(), 2),
    "distribution": {}
}

for score in range(6):  # 0-5
    count = gap_score_dist.get(score, 0)
    stats_output["gap_score"]["distribution"][score] = format_pct_with_ci(count, len(df))

# Low Gap Score (0-1)
low_gap = (df['gap_score'] <= 1).sum()
stats_output["gap_score"]["low_gap_0_to_1"] = format_pct_with_ci(low_gap, len(df))

# ============================================================================
# DOMAIN-SPECIFIC GAP SCORES
# ============================================================================

stats_output["gap_score_by_domain"] = {}
for modality in ['Images', 'Text', 'Audio', 'Malware', 'Other']:
    domain_df = df[df['G3'] == modality]
    if len(domain_df) > 0:
        stats_output["gap_score_by_domain"][modality] = {
            "mean_gap_score": round(domain_df['gap_score'].mean(), 2),
            "n_papers": len(domain_df),
            "gradient_dependency": format_pct_with_ci(
                (domain_df['Q1'] == 'Yes').sum(),
                len(domain_df[domain_df['Q1'] != 'NA'])
            ),
            "real_world_testing": format_pct_with_ci(
                (domain_df['G6'] == 'Yes').sum(),
                len(domain_df)
            )
        }

# ============================================================================
# TEMPORAL TRENDS
# ============================================================================

print("\nComputing temporal trends...")
stats_output["temporal_trends"] = {}

for year in sorted(df['Year'].unique()):
    year_df = df[df['Year'] == year]

    # Real-world testing
    rw_yes = (year_df['G6'] == 'Yes').sum()

    # Gradient dependency (excluding NA)
    year_q1_valid = year_df[year_df['Q1'] != 'NA']
    grad_yes = (year_q1_valid['Q1'] == 'Yes').sum()

    # White-box assumption
    wb_count = year_df[year_df['T1'].str.contains('White-box', na=False)].shape[0]

    # High query budget (among papers with queries)
    year_q2_with_queries = year_df[(year_df['Q2'] != 'None') & (year_df['Q2'] != 'NA')]
    q2_high_year = (year_q2_with_queries['Q2'] == 'High').sum()

    # Economic analysis
    econ_yes_year = (year_df['G4'] == 'Yes').sum()

    # Mean Gap Score
    mean_gap = year_df['gap_score'].mean()

    stats_output["temporal_trends"][int(year)] = {
        "n_papers": len(year_df),
        "real_world_testing": format_pct_with_ci(rw_yes, len(year_df)),
        "gradient_dependency": format_pct_with_ci(grad_yes, len(year_q1_valid)),
        "whitebox_assumption": format_pct_with_ci(wb_count, len(year_df)),
        "high_query_budget": format_pct_with_ci(q2_high_year, len(year_q2_with_queries)),
        "economic_analysis": format_pct_with_ci(econ_yes_year, len(year_df)),
        "mean_gap_score": round(mean_gap, 2)
    }

# ============================================================================
# CROSS-VENUE ANALYSIS
# ============================================================================

print("\nComputing cross-venue comparisons...")
stats_output["by_venue"] = {}

for conf in sorted(df['Conference'].unique()):
    conf_df = df[df['Conference'] == conf]

    # Same metrics as temporal trends
    rw_yes = (conf_df['G6'] == 'Yes').sum()

    conf_q1_valid = conf_df[conf_df['Q1'] != 'NA']
    grad_yes = (conf_q1_valid['Q1'] == 'Yes').sum()

    wb_count = conf_df[conf_df['T1'].str.contains('White-box', na=False)].shape[0]

    conf_q2_with_queries = conf_df[(conf_df['Q2'] != 'None') & (conf_df['Q2'] != 'NA')]
    q2_high_conf = (conf_q2_with_queries['Q2'] == 'High').sum()

    econ_yes_conf = (conf_df['G4'] == 'Yes').sum()

    mean_gap = conf_df['gap_score'].mean()

    stats_output["by_venue"][conf] = {
        "n_papers": len(conf_df),
        "real_world_testing": format_pct_with_ci(rw_yes, len(conf_df)),
        "gradient_dependency": format_pct_with_ci(grad_yes, len(conf_q1_valid)),
        "whitebox_assumption": format_pct_with_ci(wb_count, len(conf_df)),
        "high_query_budget": format_pct_with_ci(q2_high_conf, len(conf_q2_with_queries)),
        "economic_analysis": format_pct_with_ci(econ_yes_conf, len(conf_df)),
        "mean_gap_score": round(mean_gap, 2)
    }

# ============================================================================
# ATTACK vs DEFENSE COMPARISON
# ============================================================================

print("\nComputing attack vs defense comparisons...")
stats_output["attack_vs_defense"] = {}

for focus in ['atk', 'def']:
    focus_df = df[df['G1'] == focus]

    # Gradient dependency
    focus_q1_valid = focus_df[focus_df['Q1'] != 'NA']
    grad_yes = (focus_q1_valid['Q1'] == 'Yes').sum()

    # Query budget
    focus_q2_with_queries = focus_df[(focus_df['Q2'] != 'None') & (focus_df['Q2'] != 'NA')]
    q2_high = (focus_q2_with_queries['Q2'] == 'High').sum()

    # Real-world testing
    rw_yes = (focus_df['G6'] == 'Yes').sum()

    stats_output["attack_vs_defense"][focus] = {
        "n_papers": len(focus_df),
        "gradient_dependency": format_pct_with_ci(grad_yes, len(focus_q1_valid)),
        "high_query_budget": format_pct_with_ci(q2_high, len(focus_q2_with_queries)),
        "real_world_testing": format_pct_with_ci(rw_yes, len(focus_df))
    }

# ============================================================================
# SAVE RESULTS
# ============================================================================

output_file = '../results/stats_v2_summary.json'
with open(output_file, 'w') as f:
    json.dump(stats_output, f, indent=2)

print(f"\n✓ Statistics saved to {output_file}")

# ============================================================================
# PRINT KEY NUMBERS FOR QUICK REFERENCE
# ============================================================================

print("\n" + "="*80)
print("KEY NUMBERS FOR PAPER UPDATE")
print("="*80)

print(f"\nTOTAL PAPERS: {len(df)}")

print(f"\nBY CONFERENCE:")
for conf in sorted(stats_output["by_conference"].keys()):
    info = stats_output["by_conference"][conf]
    print(f"  {conf}: {info['count']} ({info['percentage']}%)")

print(f"\nBY YEAR:")
for year in sorted(stats_output["by_year"].keys()):
    info = stats_output["by_year"][year]
    print(f"  {year}: {info['count']} ({info['percentage']}%)")

print(f"\nKEY GAP INDICATORS:")
print(f"  Real-world testing: {stats_output['real_world_testing']['formatted']}")
print(f"  Gradient dependency: {stats_output['gradient_dependency']['formatted']}")
print(f"  White-box assumption: {stats_output['whitebox_assumption']['formatted']}")
print(f"  High query budget: {stats_output['query_budget_high']['formatted']}")
print(f"  Economic analysis: {stats_output['economic_analysis']['formatted']}")

print(f"\nGAP SCORE:")
print(f"  Mean: {stats_output['gap_score']['mean']}")
print(f"  Low Gap (0-1): {stats_output['gap_score']['low_gap_0_to_1']['formatted']}")

print(f"\nDATA MODALITIES:")
for modality in ['Images', 'Text', 'Audio', 'Malware', 'Other']:
    info = stats_output['data_modalities'][modality]
    print(f"  {modality}: {info['formatted']}")

print(f"\nDOMAIN-SPECIFIC GAP SCORES:")
for modality in ['Images', 'Text', 'Audio', 'Malware', 'Other']:
    if modality in stats_output['gap_score_by_domain']:
        info = stats_output['gap_score_by_domain'][modality]
        print(f"  {modality}: Mean Gap Score = {info['mean_gap_score']}")
        print(f"    - Gradient dependency: {info['gradient_dependency']['formatted']}")
        print(f"    - Real-world testing: {info['real_world_testing']['formatted']}")

print("\n" + "="*80)
print("✓ Complete! Check ../results/stats_v2_summary.json for full details.")
print("="*80)
