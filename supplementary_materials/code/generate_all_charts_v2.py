#!/usr/bin/env python3
"""
Generate analysis charts for the ACNS paper from GPT-4o v2 results.
Writes regenerated PNG files to ../results/generated_figures/. 
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10

# Color palette
COLORS = {
    'primary': '#2E86AB',
    'secondary': '#A23B72',
    'accent': '#F18F01',
    'success': '#06A77D',
    'warning': '#D6573B',
    'neutral': '#6C757D'
}

# Load data
print("Loading data...")
df = pd.read_csv('gpt4o_coding_results_v2.csv', keep_default_na=False)
df = df.replace('', 'NA')

# Compute Gap Score
def compute_gap_score(row):
    score = 0
    if pd.notna(row['T1']) and 'White-box' in str(row['T1']):
        score += 1
    if row['Q1'] == 'Yes':
        score += 1
    if row['Q2'] == 'High':
        score += 1
    if row['G6'] == 'No':
        score += 1
    if row['G4'] == 'No':
        score += 1
    return score

df['gap_score'] = df.apply(compute_gap_score, axis=1)

output_dir = '../results/generated_figures/'
import os
os.makedirs(output_dir, exist_ok=True)

# ============================================================================
# FIGURE 1: Dataset Overview (Conference x Year)
# ============================================================================
print("\nGenerating Figure 1: Dataset Overview...")

fig, ax = plt.subplots(figsize=(10, 6))

# Create crosstab
ct = pd.crosstab(df['Conference'], df['Year'])
ct = ct.reindex(['ACM', 'IEEE', 'NDSS', 'USENIX'])

# Stacked bar chart
ct.T.plot(kind='bar', stacked=False, ax=ax,
          color=[COLORS['primary'], COLORS['secondary'], COLORS['accent'], COLORS['success']],
          width=0.7)

ax.set_xlabel('Year', fontweight='bold')
ax.set_ylabel('Number of Papers', fontweight='bold')
ax.set_title('Distribution of 459 Papers by Conference and Year', fontweight='bold', pad=20)
ax.legend(title='Conference', frameon=True, fancybox=True, shadow=True)
ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
ax.grid(axis='y', alpha=0.3)

# Add total counts on top
for i, year in enumerate(ct.columns):
    total = ct[year].sum()
    ax.text(i, total + 5, str(int(total)), ha='center', va='bottom', fontweight='bold')

plt.tight_layout()
plt.savefig(f'{output_dir}fig1_dataset.png', bbox_inches='tight')
plt.close()
print("✓ Saved fig1_dataset.png")

# ============================================================================
# FIGURE 2: Theory-Practice Gap Overview
# ============================================================================
print("Generating Figure 2: Gap Overview...")

fig, ax = plt.subplots(figsize=(10, 6))

# Calculate percentages
dont_test_real = 100 * (df['G6'] == 'No').sum() / len(df)
q1_valid = df[df['Q1'] != 'NA']
req_gradients = 100 * (q1_valid['Q1'] == 'Yes').sum() / len(q1_valid)
whitebox = 100 * df[df['T1'].str.contains('White-box', na=False)].shape[0] / len(df)
no_query_discuss = 100 * ((df['Q2'] == 'None') | (df['Q2'] == 'NA')).sum() / len(df)
no_economics = 100 * (df['G4'] == 'No').sum() / len(df)

metrics = ['Don\'t Test on\nReal Systems', 'Require\nGradients*', 'White-box\nAssumption',
           'Don\'t Discuss\nQuery Budgets', 'No Economic\nAnalysis']
values = [dont_test_real, req_gradients, whitebox, no_query_discuss, no_economics]
colors_list = [COLORS['warning'], COLORS['secondary'], COLORS['accent'], COLORS['primary'], COLORS['success']]

bars = ax.barh(metrics, values, color=colors_list, edgecolor='black', linewidth=1.2)

# Add value labels
for i, (bar, val) in enumerate(zip(bars, values)):
    ax.text(val + 2, i, f'{val:.1f}%', va='center', fontweight='bold', fontsize=11)

ax.set_xlabel('Percentage of Papers', fontweight='bold')
ax.set_title('Key Indicators of Theory-Practice Gap (N=459)', fontweight='bold', pad=20)
ax.set_xlim(0, 105)
ax.grid(axis='x', alpha=0.3)
ax.text(0.5, -0.15, '*Among 276 papers where gradient access is applicable',
        transform=ax.transAxes, fontsize=9, style='italic', ha='center')

plt.tight_layout()
plt.savefig(f'{output_dir}fig2_overview.png', bbox_inches='tight')
plt.close()
print("✓ Saved fig2_overview.png")

# ============================================================================
# FIGURE 3: Threat Model Distribution
# ============================================================================
print("Generating Figure 3: Threat Models...")

fig, ax = plt.subplots(figsize=(10, 6))

t1_counts = df['T1'].value_counts()
threat_models = ['Black-box', 'White-box', 'White-box/Black-box', 'NA', 'Gray-box']
counts = [t1_counts.get(tm, 0) for tm in threat_models]
percentages = [100 * c / len(df) for c in counts]

colors_tm = [COLORS['primary'], COLORS['warning'], COLORS['accent'], COLORS['neutral'], COLORS['secondary']]
bars = ax.bar(threat_models, percentages, color=colors_tm, edgecolor='black', linewidth=1.2)

# Add value labels
for bar, pct, cnt in zip(bars, percentages, counts):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + 1,
            f'{pct:.1f}%\n(n={cnt})', ha='center', va='bottom', fontweight='bold')

ax.set_ylabel('Percentage of Papers', fontweight='bold')
ax.set_xlabel('Threat Model', fontweight='bold')
ax.set_title('Threat Model Assumptions (N=459)', fontweight='bold', pad=20)
ax.set_ylim(0, 45)
ax.grid(axis='y', alpha=0.3)
plt.xticks(rotation=15, ha='right')

plt.tight_layout()
plt.savefig(f'{output_dir}fig4_threat.png', bbox_inches='tight')
plt.close()
print("✓ Saved fig4_threat.png")

# ============================================================================
# FIGURE 4: Gradient Dependency Over Time
# ============================================================================
print("Generating Figure 4: Gradient Dependency Trends...")

fig, ax = plt.subplots(figsize=(10, 6))

years = sorted(df['Year'].unique())
grad_pcts = []
grad_cis_lower = []
grad_cis_upper = []

for year in years:
    year_df = df[df['Year'] == year]
    year_q1_valid = year_df[year_df['Q1'] != 'NA']
    if len(year_q1_valid) > 0:
        grad_yes = (year_q1_valid['Q1'] == 'Yes').sum()
        pct = 100 * grad_yes / len(year_q1_valid)
        # Wilson CI
        p = grad_yes / len(year_q1_valid)
        n = len(year_q1_valid)
        z = 1.96
        denom = 1 + z**2/n
        center = (p + z**2/(2*n)) / denom
        margin = z * np.sqrt(p*(1-p)/n + z**2/(4*n**2)) / denom
        lower = max(0, center - margin)
        upper = min(1, center + margin)

        grad_pcts.append(pct)
        grad_cis_lower.append(100 * lower)
        grad_cis_upper.append(100 * upper)
    else:
        grad_pcts.append(0)
        grad_cis_lower.append(0)
        grad_cis_upper.append(0)

ax.plot(years, grad_pcts, marker='o', linewidth=2.5, markersize=10,
        color=COLORS['secondary'], label='Gradient Dependency')
ax.fill_between(years, grad_cis_lower, grad_cis_upper, alpha=0.2, color=COLORS['secondary'])

ax.set_xlabel('Year', fontweight='bold')
ax.set_ylabel('Percentage Requiring Gradients', fontweight='bold')
ax.set_title('Gradient Dependency Over Time (Among Applicable Papers)', fontweight='bold', pad=20)
ax.set_ylim(0, 80)
ax.grid(True, alpha=0.3)
ax.legend(frameon=True, fancybox=True, shadow=True)

# Add sample sizes
for year, pct in zip(years, grad_pcts):
    year_df = df[df['Year'] == year]
    year_q1_valid = year_df[year_df['Q1'] != 'NA']
    n = len(year_q1_valid)
    ax.text(year, pct + 3, f'n={n}', ha='center', fontsize=8, style='italic')

plt.tight_layout()
plt.savefig(f'{output_dir}fig4_gradient_dependency_extra.png', bbox_inches='tight')
plt.close()
print("✓ Saved fig4_gradient_dependency_extra.png")

# ============================================================================
# FIGURE 5: Real-World Testing
# ============================================================================
print("Generating Figure 5: Real-World Testing...")

fig, ax = plt.subplots(figsize=(10, 6))

# Overall + by year
rw_yes_total = (df['G6'] == 'Yes').sum()
rw_pct_total = 100 * rw_yes_total / len(df)

years = sorted(df['Year'].unique())
rw_pcts = []
for year in years:
    year_df = df[df['Year'] == year]
    rw_yes = (year_df['G6'] == 'Yes').sum()
    rw_pcts.append(100 * rw_yes / len(year_df))

# Bar chart
labels = ['Overall'] + [str(y) for y in years]
values = [rw_pct_total] + rw_pcts
colors_rw = [COLORS['success']] + [COLORS['primary']] * len(years)

bars = ax.bar(labels, values, color=colors_rw, edgecolor='black', linewidth=1.2)

# Add value labels
for bar, val in zip(bars, values):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
            f'{val:.1f}%', ha='center', va='bottom', fontweight='bold')

ax.set_ylabel('Percentage of Papers', fontweight='bold')
ax.set_xlabel('Year', fontweight='bold')
rw_pct_label = 100 * (df['G6'] == 'Yes').sum() / len(df)
ax.set_title(f'Real-World Testing Rate: {rw_pct_label:.1f}% Overall (N={len(df)})', fontweight='bold', pad=20)
ax.set_ylim(0, 30)
ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig(f'{output_dir}fig3_realworld.png', bbox_inches='tight')
plt.close()
print("✓ Saved fig3_realworld.png")

# ============================================================================
# FIGURE 6: Query Budget Distribution
# ============================================================================
print("Generating Figure 6: Query Budgets...")

fig, ax = plt.subplots(figsize=(10, 6))

q2_counts = df['Q2'].value_counts()
query_cats = ['None', 'NA', 'High', 'Low']
counts = [q2_counts.get(qc, 0) for qc in query_cats]
percentages = [100 * c / len(df) for c in counts]

colors_q2 = [COLORS['neutral'], COLORS['neutral'], COLORS['warning'], COLORS['success']]
bars = ax.bar(query_cats, percentages, color=colors_q2, edgecolor='black', linewidth=1.2, alpha=0.8)

# Add value labels
for bar, pct, cnt in zip(bars, percentages, counts):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + 1,
            f'{pct:.1f}%\n(n={cnt})', ha='center', va='bottom', fontweight='bold')

ax.set_ylabel('Percentage of Papers', fontweight='bold')
ax.set_xlabel('Query Budget Category', fontweight='bold')
no_query_pct = 100 * ((df['Q2'] == 'None') | (df['Q2'] == 'NA')).sum() / len(df)
ax.set_title(f'Query Budget Distribution: {no_query_pct:.1f}% Don\'t Discuss Queries (N={len(df)})', fontweight='bold', pad=20)
ax.set_ylim(0, 50)
ax.grid(axis='y', alpha=0.3)

# Add annotation
ax.text(0.5, 0.95, 'Among 126 papers discussing queries: 61.1% assume High (>1000)',
        transform=ax.transAxes, ha='center', va='top',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5), fontsize=9)

plt.tight_layout()
plt.savefig(f'{output_dir}fig5_query.png', bbox_inches='tight')
plt.close()
print("✓ Saved fig5_query.png")

# ============================================================================
# FIGURE 7: Attack Types
# ============================================================================
print("Generating Figure 7: Attack Types...")

fig, ax = plt.subplots(figsize=(10, 6))

g2_counts = df['G2'].value_counts()
attack_types = ['Evasion', 'Poisoning', 'Privacy', 'NA', 'Multiple']
counts = [g2_counts.get(at, 0) for at in attack_types]
percentages = [100 * c / len(df) for c in counts]

colors_g2 = [COLORS['primary'], COLORS['warning'], COLORS['accent'], COLORS['neutral'], COLORS['secondary']]
bars = ax.bar(attack_types, percentages, color=colors_g2, edgecolor='black', linewidth=1.2)

# Add value labels
for bar, pct, cnt in zip(bars, percentages, counts):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
            f'{pct:.1f}%\n(n={cnt})', ha='center', va='bottom', fontweight='bold')

ax.set_ylabel('Percentage of Papers', fontweight='bold')
ax.set_xlabel('Attack Type', fontweight='bold')
ax.set_title('Attack Type Distribution (N=459)', fontweight='bold', pad=20)
ax.set_ylim(0, 45)
ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig(f'{output_dir}fig7_attack_types_extra.png', bbox_inches='tight')
plt.close()
print("✓ Saved fig7_attack_types_extra.png")

# ============================================================================
# FIGURE 8: Data Domains
# ============================================================================
print("Generating Figure 8: Data Domains...")

fig, ax = plt.subplots(figsize=(10, 7))

g3_counts = df['G3'].value_counts()
domains = ['Images', 'Other', 'Text', 'Audio', 'Malware', 'Multiple']
counts = [g3_counts.get(d, 0) for d in domains]
percentages = [100 * c / len(df) for c in counts]

# Pie chart with better colors
colors_domains = [COLORS['primary'], COLORS['neutral'], COLORS['accent'],
                  COLORS['secondary'], COLORS['warning'], COLORS['success']]

wedges, texts, autotexts = ax.pie(percentages, labels=domains, autopct='%1.1f%%',
                                    colors=colors_domains, startangle=90,
                                    textprops={'fontweight': 'bold'},
                                    wedgeprops={'edgecolor': 'black', 'linewidth': 1.5})

# Add counts to labels
for i, (text, count) in enumerate(zip(texts, counts)):
    text.set_text(f'{text.get_text()}\n(n={count})')

img_pct = 100 * (df['G3'] == 'Images').sum() / len(df)
ax.set_title(f'Data Modality Distribution: Images {img_pct:.1f}%, Increasing Diversity (N={len(df)})',
             fontweight='bold', pad=20)

plt.tight_layout()
plt.savefig(f'{output_dir}fig7_domains.png', bbox_inches='tight')
plt.close()
print("✓ Saved fig7_domains.png")

# ============================================================================
# FIGURE 9: Attack vs Defense Comparison
# ============================================================================
print("Generating Figure 9: Attack vs Defense...")

fig, ax = plt.subplots(figsize=(10, 6))

# Compute metrics for attack and defense
atk_df = df[df['G1'] == 'atk']
def_df = df[df['G1'] == 'def']

# Gradient dependency
atk_q1_valid = atk_df[atk_df['Q1'] != 'NA']
atk_grad = 100 * (atk_q1_valid['Q1'] == 'Yes').sum() / len(atk_q1_valid) if len(atk_q1_valid) > 0 else 0

def_q1_valid = def_df[def_df['Q1'] != 'NA']
def_grad = 100 * (def_q1_valid['Q1'] == 'Yes').sum() / len(def_q1_valid) if len(def_q1_valid) > 0 else 0

# Real-world testing
atk_rw = 100 * (atk_df['G6'] == 'Yes').sum() / len(atk_df)
def_rw = 100 * (def_df['G6'] == 'Yes').sum() / len(def_df)

# High query budget
atk_q2_queries = atk_df[(atk_df['Q2'] != 'None') & (atk_df['Q2'] != 'NA')]
atk_high_q = 100 * (atk_q2_queries['Q2'] == 'High').sum() / len(atk_q2_queries) if len(atk_q2_queries) > 0 else 0

def_q2_queries = def_df[(def_df['Q2'] != 'None') & (def_df['Q2'] != 'NA')]
def_high_q = 100 * (def_q2_queries['Q2'] == 'High').sum() / len(def_q2_queries) if len(def_q2_queries) > 0 else 0

metrics = ['Gradient\nDependency*', 'High Query\nBudget**', 'Real-World\nTesting']
atk_values = [atk_grad, atk_high_q, atk_rw]
def_values = [def_grad, def_high_q, def_rw]

x = np.arange(len(metrics))
width = 0.35

bars1 = ax.bar(x - width/2, atk_values, width, label='Attack Papers (n=213)',
               color=COLORS['warning'], edgecolor='black', linewidth=1.2)
bars2 = ax.bar(x + width/2, def_values, width, label='Defense Papers (n=195)',
               color=COLORS['success'], edgecolor='black', linewidth=1.2)

# Add value labels
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 2,
                f'{height:.1f}%', ha='center', va='bottom', fontweight='bold', fontsize=9)

ax.set_ylabel('Percentage', fontweight='bold')
ax.set_xlabel('Metric', fontweight='bold')
ax.set_title('Attack vs Defense Papers: Key Metrics Comparison', fontweight='bold', pad=20)
ax.set_xticks(x)
ax.set_xticklabels(metrics)
ax.legend(frameon=True, fancybox=True, shadow=True)
ax.set_ylim(0, 90)
ax.grid(axis='y', alpha=0.3)

ax.text(0.5, -0.18, '*Among applicable papers  **Among papers with queries',
        transform=ax.transAxes, fontsize=8, style='italic', ha='center')

plt.tight_layout()
plt.savefig(f'{output_dir}fig10_atkdef.png', bbox_inches='tight')
plt.close()
print("✓ Saved fig10_atkdef.png")

# ============================================================================
# FIGURE 10: Conference Comparison (Heatmap)
# ============================================================================
print("Generating Figure 10: Conference Comparison...")

fig, ax = plt.subplots(figsize=(12, 6))

# Compute metrics for each conference
conferences = ['ACM', 'IEEE', 'NDSS', 'USENIX']
metrics_conf = ['Real-World\nTesting', 'Gradient\nDependency', 'White-box\nAssumption',
                'High Query\nBudget', 'No Economic\nAnalysis', 'Mean Gap\nScore']

heatmap_data = []

for conf in conferences:
    conf_df = df[df['Conference'] == conf]

    # Real-world testing
    rw = 100 * (conf_df['G6'] == 'Yes').sum() / len(conf_df)

    # Gradient dependency
    conf_q1_valid = conf_df[conf_df['Q1'] != 'NA']
    grad = 100 * (conf_q1_valid['Q1'] == 'Yes').sum() / len(conf_q1_valid) if len(conf_q1_valid) > 0 else 0

    # White-box
    wb = 100 * conf_df[conf_df['T1'].str.contains('White-box', na=False)].shape[0] / len(conf_df)

    # High query budget
    conf_q2_queries = conf_df[(conf_df['Q2'] != 'None') & (conf_df['Q2'] != 'NA')]
    high_q = 100 * (conf_q2_queries['Q2'] == 'High').sum() / len(conf_q2_queries) if len(conf_q2_queries) > 0 else 0

    # No economics
    no_econ = 100 * (conf_df['G4'] == 'No').sum() / len(conf_df)

    # Gap score
    gap = conf_df['gap_score'].mean()

    heatmap_data.append([rw, grad, wb, high_q, no_econ, gap])

heatmap_df = pd.DataFrame(heatmap_data, index=conferences, columns=metrics_conf)

# Create heatmap
sns.heatmap(heatmap_df.T, annot=True, fmt='.1f', cmap='RdYlGn_r',
            cbar_kws={'label': 'Percentage / Score'},
            linewidths=1, linecolor='black', ax=ax, vmin=0, vmax=100)

ax.set_title('Cross-Venue Comparison: Key Metrics by Conference', fontweight='bold', pad=20)
ax.set_xlabel('Conference', fontweight='bold')
ax.set_ylabel('Metric', fontweight='bold')

plt.tight_layout()
plt.savefig(f'{output_dir}fig9_venue.png', bbox_inches='tight')
plt.close()
print("✓ Saved fig9_venue.png")

# ============================================================================
# FIGURE 11: Yearly Trends (Multi-line)
# ============================================================================
print("Generating Figure 11: Temporal Trends...")

fig, ax = plt.subplots(figsize=(12, 7))

years = sorted(df['Year'].unique())

# Collect data for each metric
rw_trend = []
grad_trend = []
wb_trend = []
no_econ_trend = []
gap_trend = []

for year in years:
    year_df = df[df['Year'] == year]

    # Real-world testing
    rw = 100 * (year_df['G6'] == 'Yes').sum() / len(year_df)
    rw_trend.append(rw)

    # Gradient dependency
    year_q1_valid = year_df[year_df['Q1'] != 'NA']
    grad = 100 * (year_q1_valid['Q1'] == 'Yes').sum() / len(year_q1_valid) if len(year_q1_valid) > 0 else 0
    grad_trend.append(grad)

    # White-box
    wb = 100 * year_df[year_df['T1'].str.contains('White-box', na=False)].shape[0] / len(year_df)
    wb_trend.append(wb)

    # No economics
    no_econ = 100 * (year_df['G4'] == 'No').sum() / len(year_df)
    no_econ_trend.append(no_econ)

    # Gap score (scaled to percentage)
    gap = 20 * year_df['gap_score'].mean()  # Scale 0-5 to 0-100
    gap_trend.append(gap)

# Plot trends
ax.plot(years, rw_trend, marker='o', linewidth=2.5, markersize=8,
        label='Real-World Testing', color=COLORS['success'])
ax.plot(years, grad_trend, marker='s', linewidth=2.5, markersize=8,
        label='Gradient Dependency*', color=COLORS['secondary'])
ax.plot(years, wb_trend, marker='^', linewidth=2.5, markersize=8,
        label='White-box Assumption', color=COLORS['warning'])
ax.plot(years, no_econ_trend, marker='D', linewidth=2.5, markersize=8,
        label='No Economic Analysis', color=COLORS['accent'])
ax.plot(years, gap_trend, marker='*', linewidth=2.5, markersize=12,
        label='Gap Score (scaled)', color=COLORS['primary'])

ax.set_xlabel('Year', fontweight='bold')
ax.set_ylabel('Percentage', fontweight='bold')
ax.set_title('Temporal Trends: Mixed Patterns, No Consistent Improvement (2022-2025)',
             fontweight='bold', pad=20)
ax.set_ylim(0, 105)
ax.set_xticks(years)
ax.set_xticklabels([int(y) for y in years])
ax.grid(True, alpha=0.3)
ax.legend(frameon=True, fancybox=True, shadow=True, loc='best')

ax.text(0.5, -0.12, '*Among applicable papers',
        transform=ax.transAxes, fontsize=8, style='italic', ha='center')

plt.tight_layout()
plt.savefig(f'{output_dir}fig8_trends.png', bbox_inches='tight')
plt.close()
print("✓ Saved fig8_trends.png")

# ============================================================================
# FIGURE 12: Gap Score Distribution
# ============================================================================
print("Generating Figure 12: Gap Score Distribution...")

fig, ax = plt.subplots(figsize=(10, 6))

gap_counts = df['gap_score'].value_counts().sort_index()
scores = range(6)
counts = [gap_counts.get(s, 0) for s in scores]
percentages = [100 * c / len(df) for c in counts]

colors_gap = [COLORS['success'], COLORS['success'], COLORS['primary'],
              COLORS['accent'], COLORS['warning'], COLORS['warning']]

bars = ax.bar(scores, percentages, color=colors_gap, edgecolor='black', linewidth=1.2, alpha=0.8)

# Add value labels
for score, pct, cnt in zip(scores, percentages, counts):
    ax.text(score, pct + 1, f'{pct:.1f}%\n(n={cnt})', ha='center', va='bottom', fontweight='bold')

ax.set_xlabel('Gap Score (0-5)', fontweight='bold')
ax.set_ylabel('Percentage of Papers', fontweight='bold')
mean_val = df['gap_score'].mean()
median_val = df['gap_score'].median()
ax.set_title(f'Gap Score Distribution: Mean = {mean_val:.2f}, Median = {median_val:.0f} (N={len(df)})', fontweight='bold', pad=20)
ax.set_xticks(scores)
ax.set_ylim(0, 35)
ax.grid(axis='y', alpha=0.3)

# Add annotation
mean_gap = df['gap_score'].mean()
median_gap = df['gap_score'].median()
ax.axvline(mean_gap, color='red', linestyle='--', linewidth=2, label=f'Mean = {mean_gap:.2f}')
ax.axvline(median_gap, color='blue', linestyle='--', linewidth=2, label=f'Median = {median_gap:.0f}')
ax.legend(frameon=True, fancybox=True, shadow=True)

# Add zones
ax.text(0.5, 0.95, '← Low Gap (0-1): 10.0%', transform=ax.transAxes,
        bbox=dict(boxstyle='round', facecolor=COLORS['success'], alpha=0.3),
        ha='left', va='top', fontsize=9)
ax.text(0.95, 0.95, 'High Gap (4-5): 13.7% →', transform=ax.transAxes,
        bbox=dict(boxstyle='round', facecolor=COLORS['warning'], alpha=0.3),
        ha='right', va='top', fontsize=9)

plt.tight_layout()
plt.savefig(f'{output_dir}fig6_gapscore.png', bbox_inches='tight')
plt.close()
print("✓ Saved fig6_gapscore.png")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "="*80)
print("✓ ALL 12 CHARTS GENERATED SUCCESSFULLY!")
print("="*80)
print(f"\nOutput directory: {output_dir}")
print("\nGenerated files:")
for i in range(1, 13):
    print(f"  ✓ fig{i:02d}_*.png")
print("\n" + "="*80)
