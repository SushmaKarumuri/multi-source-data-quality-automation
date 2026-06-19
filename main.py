"""
╔══════════════════════════════════════════════════════════════╗
║     MULTI-SOURCE DATA QUALITY AUTOMATION                     ║
║     Sai Sushma Karumuri | Portfolio Project                  ║
╚══════════════════════════════════════════════════════════════╝

WHAT THIS PROJECT DOES:
  → Reads data from 5 different CSV "sources" (like different departments)
  → Cleans all the messy/missing/wrong data automatically
  → Checks quality at every step and flags problems
  → Merges everything into one clean master report
  → Generates charts + a final PDF-style HTML report

HOW TO RUN:
  1. Make sure you have Python installed
  2. Run:  pip install pandas numpy matplotlib seaborn
  3. Run:  python main.py
  4. Output files appear in the  output/  folder
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────
#  STEP 0 — Setup output folder
# ─────────────────────────────────────────────
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 60)
print("   MULTI-SOURCE DATA QUALITY AUTOMATION")
print("   Starting pipeline...", datetime.now().strftime("%H:%M:%S"))
print("=" * 60)


# ─────────────────────────────────────────────
#  STEP 1 — Simulate 5 raw data sources
#  (In real life these would be CSV files /
#   database tables / API responses)
# ─────────────────────────────────────────────
def generate_raw_sources():
    """Creates 5 messy, realistic data sources."""
    np.random.seed(42)
    n = 200

    # Source 1: HR Department — employee info
    hr_data = pd.DataFrame({
        'employee_id': [f"EMP{str(i).zfill(4)}" for i in range(1, n + 1)],
        'name':        [f"Employee_{i}" for i in range(1, n + 1)],
        'department':  np.random.choice(['IT', 'Finance', 'HR', 'Operations', None], n, p=[0.3, 0.25, 0.2, 0.2, 0.05]),
        'age':         np.where(np.random.rand(n) < 0.05, -5,
                       np.where(np.random.rand(n) < 0.05, np.nan,
                       np.random.randint(22, 60, n).astype(float))),
        'join_date':   pd.date_range('2018-01-01', periods=n, freq='2D').astype(str),
    })

    # Source 2: Payroll — salary records
    payroll_data = pd.DataFrame({
        'emp_id':      [f"EMP{str(i).zfill(4)}" for i in range(1, n + 1)],
        'salary':      np.where(np.random.rand(n) < 0.05, np.nan,
                       np.where(np.random.rand(n) < 0.03, -1000,
                       np.random.randint(25000, 120000, n).astype(float))),
        'bonus':       np.random.randint(0, 15000, n),
        'currency':    np.random.choice(['INR', 'inr', 'Inr', 'USD', None], n, p=[0.7, 0.1, 0.1, 0.05, 0.05]),
    })

    # Source 3: IT Asset Tracker — equipment
    it_data = pd.DataFrame({
        'employee_id': [f"EMP{str(i).zfill(4)}" for i in range(1, n + 1)],
        'laptop':      np.random.choice(['Dell', 'HP', 'Lenovo', None], n, p=[0.4, 0.3, 0.25, 0.05]),
        'os':          np.random.choice(['Windows 10', 'Windows 11', 'WINDOWS 11', 'macOS', None], n, p=[0.3, 0.3, 0.1, 0.25, 0.05]),
        'access_level':np.random.choice([1, 2, 3, 99, None], n, p=[0.4, 0.3, 0.2, 0.05, 0.05]),
    })

    # Source 4: Performance Reviews
    perf_data = pd.DataFrame({
        'id':          [f"EMP{str(i).zfill(4)}" for i in range(1, n + 1)],
        'rating':      np.where(np.random.rand(n) < 0.04, 10,   # outlier
                       np.where(np.random.rand(n) < 0.04, np.nan,
                       np.random.uniform(1, 5, n).round(1))),
        'projects_done': np.random.randint(0, 20, n),
        'reviewed':    np.random.choice(['Yes', 'No', 'yes', 'no', None], n, p=[0.5, 0.3, 0.1, 0.05, 0.05]),
    })

    # Source 5: Attendance Records
    attend_data = pd.DataFrame({
        'emp_id':       [f"EMP{str(i).zfill(4)}" for i in range(1, n + 1)],
        'days_present': np.where(np.random.rand(n) < 0.04, np.nan,
                        np.random.randint(180, 260, n).astype(float)),
        'leaves_taken': np.random.randint(0, 30, n),
        'location':     np.random.choice(['Bangalore', 'bangalore', 'BANGALORE',
                                          'Hyderabad', 'Mumbai', None],
                                         n, p=[0.3, 0.1, 0.1, 0.2, 0.2, 0.1]),
    })

    return {
        "HR Department":        hr_data,
        "Payroll":              payroll_data,
        "IT Assets":            it_data,
        "Performance Reviews":  perf_data,
        "Attendance":           attend_data,
    }


# ─────────────────────────────────────────────
#  STEP 2 — Data Quality Checker
# ─────────────────────────────────────────────
def check_quality(df, source_name):
    """
    Measures quality of a dataframe and returns a report dict.

    NOTE: We count BOTH missing values (NaN) AND invalid values
    (e.g. negative age, salary < 0, rating > 5) as "issues".
    This way the "before vs after" comparison is fair —
    cleaning converts invalid -> NaN -> filled, so the issue
    count should only ever go DOWN, never up.
    """
    total = len(df)
    missing = int(df.isnull().sum().sum())

    invalid = 0
    if 'age' in df.columns:
        invalid += int(((df['age'] < 18) | (df['age'] > 70)).sum())
    if 'salary' in df.columns:
        invalid += int((df['salary'] < 0).sum())
    if 'rating' in df.columns:
        invalid += int((df['rating'] > 5).sum())
    if 'access_level' in df.columns:
        invalid += int((~df['access_level'].isin([1, 2, 3]) & df['access_level'].notnull()).sum())

    total_issues = missing + invalid

    issues = {
        "source":         source_name,
        "total_records":  total,
        "missing_values": total_issues,
        "duplicate_rows": int(df.duplicated().sum()),
        "completeness_%": round((1 - total_issues / (total * len(df.columns))) * 100, 2),
    }
    return issues


# ─────────────────────────────────────────────
#  STEP 3 — Cleaning Functions (per source)
# ─────────────────────────────────────────────
def clean_hr(df):
    df = df.copy()
    df['age'] = pd.to_numeric(df['age'], errors='coerce')
    df.loc[df['age'] < 18, 'age'] = np.nan          # invalid ages
    df.loc[df['age'] > 70, 'age'] = np.nan
    df['age'].fillna(df['age'].median(), inplace=True)
    df['department'].fillna('Unknown', inplace=True)
    df['join_date'] = pd.to_datetime(df['join_date'], errors='coerce')
    return df

def clean_payroll(df):
    df = df.copy()
    df['salary'] = pd.to_numeric(df['salary'], errors='coerce')
    df.loc[df['salary'] < 0, 'salary'] = np.nan     # negative salary = error
    df['salary'].fillna(df['salary'].median(), inplace=True)
    df['currency'] = df['currency'].str.upper().fillna('INR')  # standardize
    return df

def clean_it(df):
    df = df.copy()
    df['os'] = df['os'].str.title().fillna('Unknown')          # normalize case
    df['laptop'].fillna('Unknown', inplace=True)
    df.loc[~df['access_level'].isin([1, 2, 3]), 'access_level'] = np.nan
    df['access_level'].fillna(2, inplace=True)                 # default mid-level
    return df

def clean_performance(df):
    df = df.copy()
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
    df.loc[df['rating'] > 5, 'rating'] = np.nan               # max rating is 5
    df['rating'].fillna(df['rating'].mean(), inplace=True)
    df['reviewed'] = df['reviewed'].str.capitalize().fillna('No')
    return df

def clean_attendance(df):
    df = df.copy()
    df['days_present'] = pd.to_numeric(df['days_present'], errors='coerce')
    df['days_present'].fillna(df['days_present'].median(), inplace=True)
    df['location'] = df['location'].str.title().fillna('Unknown')  # normalize case
    return df


# ─────────────────────────────────────────────
#  STEP 4 — Merge all sources into master
# ─────────────────────────────────────────────
def merge_sources(cleaned):
    hr   = cleaned["HR Department"].rename(columns={'name': 'emp_name'})
    pay  = cleaned["Payroll"].rename(columns={'emp_id': 'employee_id'})
    it   = cleaned["IT Assets"]
    perf = cleaned["Performance Reviews"].rename(columns={'id': 'employee_id'})
    att  = cleaned["Attendance"].rename(columns={'emp_id': 'employee_id'})

    master = hr.merge(pay,  on='employee_id', how='left')
    master = master.merge(it,   on='employee_id', how='left')
    master = master.merge(perf, on='employee_id', how='left')
    master = master.merge(att,  on='employee_id', how='left')
    return master


# ─────────────────────────────────────────────
#  STEP 5 — Generate Charts
# ─────────────────────────────────────────────
def generate_charts(quality_before, quality_after, master_df):
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.patch.set_facecolor('#0D1117')
    for ax in axes.flatten():
        ax.set_facecolor('#161B22')

    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']

    # ── Chart 1: Completeness Before vs After ──
    ax1 = axes[0, 0]
    sources   = [q['source'] for q in quality_before]
    before_pct = [q['completeness_%'] for q in quality_before]
    after_pct  = [q['completeness_%'] for q in quality_after]
    x = np.arange(len(sources))
    ax1.bar(x - 0.2, before_pct, 0.35, label='Before Cleaning', color='#FF6B6B', alpha=0.8)
    ax1.bar(x + 0.2, after_pct,  0.35, label='After Cleaning',  color='#4ECDC4', alpha=0.8)
    ax1.set_title('Data Completeness: Before vs After', color='white', fontsize=11, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels([s.split()[0] for s in sources], color='#8B949E', fontsize=8)
    ax1.set_ylabel('Completeness %', color='#8B949E')
    ax1.tick_params(colors='#8B949E')
    ax1.legend(facecolor='#21262D', labelcolor='white', fontsize=8)
    ax1.set_ylim(85, 101)
    ax1.spines[['top', 'right']].set_visible(False)
    for spine in ['left', 'bottom']:
        ax1.spines[spine].set_color('#30363D')

    # ── Chart 2: Missing Values Fixed ──
    ax2 = axes[0, 1]
    missing_b = [q['missing_values'] for q in quality_before]
    missing_a = [q['missing_values'] for q in quality_after]
    fixed     = [b - a for b, a in zip(missing_b, missing_a)]
    bars = ax2.barh([s.split()[0] for s in sources], fixed, color=colors)
    ax2.set_title('Missing Values Fixed per Source', color='white', fontsize=11, fontweight='bold')
    ax2.set_xlabel('Records Fixed', color='#8B949E')
    ax2.tick_params(colors='#8B949E')
    for spine in ['top', 'right']:
        ax2.spines[spine].set_visible(False)
    for spine in ['left', 'bottom']:
        ax2.spines[spine].set_color('#30363D')
    for bar, val in zip(bars, fixed):
        ax2.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
                 str(val), va='center', color='white', fontsize=9)

    # ── Chart 3: Department Distribution ──
    ax3 = axes[0, 2]
    dept_counts = master_df['department'].value_counts()
    wedges, texts, autotexts = ax3.pie(
        dept_counts, labels=dept_counts.index, autopct='%1.0f%%',
        colors=colors, startangle=90,
        textprops={'color': 'white', 'fontsize': 8}
    )
    for at in autotexts:
        at.set_color('#0D1117')
        at.set_fontweight('bold')
    ax3.set_title('Employee Distribution by Department', color='white', fontsize=11, fontweight='bold')

    # ── Chart 4: Salary Distribution ──
    ax4 = axes[1, 0]
    ax4.hist(master_df['salary'], bins=20, color='#45B7D1', edgecolor='#0D1117', alpha=0.85)
    ax4.set_title('Salary Distribution (After Cleaning)', color='white', fontsize=11, fontweight='bold')
    ax4.set_xlabel('Salary (₹)', color='#8B949E')
    ax4.set_ylabel('Count', color='#8B949E')
    ax4.tick_params(colors='#8B949E')
    for spine in ['top', 'right']:
        ax4.spines[spine].set_visible(False)
    for spine in ['left', 'bottom']:
        ax4.spines[spine].set_color('#30363D')

    # ── Chart 5: Performance Rating Distribution ──
    ax5 = axes[1, 1]
    ax5.hist(master_df['rating'], bins=15, color='#96CEB4', edgecolor='#0D1117', alpha=0.85)
    ax5.set_title('Performance Rating Distribution', color='white', fontsize=11, fontweight='bold')
    ax5.set_xlabel('Rating (1–5)', color='#8B949E')
    ax5.set_ylabel('Count', color='#8B949E')
    ax5.tick_params(colors='#8B949E')
    for spine in ['top', 'right']:
        ax5.spines[spine].set_visible(False)
    for spine in ['left', 'bottom']:
        ax5.spines[spine].set_color('#30363D')

    # ── Chart 6: Pipeline Summary ──
    ax6 = axes[1, 2]
    ax6.axis('off')
    total_before = sum(q['missing_values'] for q in quality_before)
    total_after  = sum(q['missing_values'] for q in quality_after)
    avg_before   = np.mean([q['completeness_%'] for q in quality_before])
    avg_after    = np.mean([q['completeness_%'] for q in quality_after])
    summary_text = (
        f"  PIPELINE SUMMARY\n"
        f"  {'─'*28}\n"
        f"  Sources Processed :  5\n"
        f"  Total Records     :  {len(master_df):,}\n"
        f"  Issues Fixed      :  {total_before - total_after:,}\n"
        f"  Avg Completeness  :\n"
        f"    Before  →  {avg_before:.1f}%\n"
        f"    After   →  {avg_after:.1f}%\n"
        f"  {'─'*28}\n"
        f"  Output: master_report.csv\n"
        f"          quality_report.csv"
    )
    ax6.text(0.05, 0.95, summary_text, transform=ax6.transAxes,
             fontsize=10, verticalalignment='top', fontfamily='monospace',
             color='#4ECDC4',
             bbox=dict(boxstyle='round,pad=0.6', facecolor='#21262D', edgecolor='#4ECDC4', linewidth=1.5))

    fig.suptitle('Multi-Source Data Quality Automation — Dashboard',
                 color='white', fontsize=14, fontweight='bold', y=1.01)
    plt.tight_layout()
    chart_path = os.path.join(OUTPUT_DIR, "dashboard.png")
    plt.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='#0D1117')
    plt.close()
    print(f"  ✔  Dashboard saved → {chart_path}")
    return chart_path


# ─────────────────────────────────────────────
#  STEP 6 — Generate HTML Report
# ─────────────────────────────────────────────
def generate_html_report(quality_before, quality_after, master_df):
    rows_before = ""
    rows_after  = ""
    for b, a in zip(quality_before, quality_after):
        rows_before += f"""
        <tr>
          <td>{b['source']}</td>
          <td>{b['total_records']}</td>
          <td class="bad">{b['missing_values']}</td>
          <td class="bad">{b['completeness_%']}%</td>
        </tr>"""
        rows_after += f"""
        <tr>
          <td>{a['source']}</td>
          <td>{a['total_records']}</td>
          <td class="good">{a['missing_values']}</td>
          <td class="good">{a['completeness_%']}%</td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Data Quality Report | Sai Sushma</title>
<style>
  body {{ font-family: 'Segoe UI', sans-serif; background: #0D1117; color: #C9D1D9; margin: 0; padding: 30px; }}
  h1   {{ color: #4ECDC4; border-bottom: 2px solid #4ECDC4; padding-bottom: 10px; }}
  h2   {{ color: #45B7D1; margin-top: 30px; }}
  table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
  th   {{ background: #21262D; color: #4ECDC4; padding: 10px; text-align: left; }}
  td   {{ padding: 9px 10px; border-bottom: 1px solid #30363D; }}
  tr:hover td {{ background: #161B22; }}
  .good {{ color: #3FB950; font-weight: bold; }}
  .bad  {{ color: #FF6B6B; font-weight: bold; }}
  .stat {{ display: inline-block; background: #21262D; border: 1px solid #30363D;
           border-radius: 8px; padding: 15px 25px; margin: 8px; text-align: center; }}
  .stat-num {{ font-size: 28px; font-weight: bold; color: #4ECDC4; }}
  .stat-lbl {{ font-size: 12px; color: #8B949E; margin-top: 4px; }}
  img  {{ max-width: 100%; border-radius: 8px; margin: 20px 0; border: 1px solid #30363D; }}
  footer {{ text-align: center; color: #8B949E; margin-top: 40px; font-size: 12px; }}
</style>
</head>
<body>
<h1>🔍 Multi-Source Data Quality Automation Report</h1>
<p>Generated: {datetime.now().strftime("%d %B %Y, %H:%M:%S")} &nbsp;|&nbsp; By: Sai Sushma Karumuri</p>

<div>
  <div class="stat"><div class="stat-num">5</div><div class="stat-lbl">Sources Processed</div></div>
  <div class="stat"><div class="stat-num">{len(master_df):,}</div><div class="stat-lbl">Total Records</div></div>
  <div class="stat"><div class="stat-num">{sum(b['missing_values']-a['missing_values'] for b,a in zip(quality_before,quality_after)):,}</div><div class="stat-lbl">Issues Fixed</div></div>
  <div class="stat"><div class="stat-num">{np.mean([a['completeness_%'] for a in quality_after]):.1f}%</div><div class="stat-lbl">Avg Completeness (After)</div></div>
</div>

<h2>📊 Dashboard</h2>
<img src="dashboard.png" alt="Dashboard">

<h2>📋 Data Quality — Before Cleaning</h2>
<table>
  <tr><th>Source</th><th>Records</th><th>Missing Values</th><th>Completeness</th></tr>
  {rows_before}
</table>

<h2>✅ Data Quality — After Cleaning</h2>
<table>
  <tr><th>Source</th><th>Records</th><th>Missing Values</th><th>Completeness</th></tr>
  {rows_after}
</table>

<h2>📁 Master Dataset Preview (First 10 rows)</h2>
{master_df.head(10).to_html(index=False, classes='', border=0)}

<footer>Multi-Source Data Quality Automation — Portfolio Project | Sai Sushma Karumuri</footer>
</body></html>"""

    path = os.path.join(OUTPUT_DIR, "report.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  ✔  HTML Report saved → {path}")


# ─────────────────────────────────────────────
#  MAIN PIPELINE — runs everything in order
# ─────────────────────────────────────────────
def run_pipeline():
    # 1. Generate raw sources
    print("\n[1/6] Generating raw data sources...")
    sources = generate_raw_sources()
    for name, df in sources.items():
        print(f"      {name}: {len(df)} records, {df.shape[1]} columns")

    # 2. Check quality BEFORE cleaning
    print("\n[2/6] Checking data quality (before cleaning)...")
    quality_before = [check_quality(df, name) for name, df in sources.items()]
    for q in quality_before:
        print(f"      {q['source']:<22} Completeness: {q['completeness_%']}%  |  Missing: {q['missing_values']}")

    # 3. Clean each source
    print("\n[3/6] Cleaning all sources...")
    cleaners = {
        "HR Department":       clean_hr,
        "Payroll":             clean_payroll,
        "IT Assets":           clean_it,
        "Performance Reviews": clean_performance,
        "Attendance":          clean_attendance,
    }
    cleaned = {name: cleaners[name](df) for name, df in sources.items()}
    print("      All 5 sources cleaned ✔")

    # 4. Check quality AFTER cleaning
    print("\n[4/6] Checking data quality (after cleaning)...")
    quality_after = [check_quality(df, name) for name, df in cleaned.items()]
    for q in quality_after:
        print(f"      {q['source']:<22} Completeness: {q['completeness_%']}%  |  Missing: {q['missing_values']}")

    # 5. Merge into master
    print("\n[5/6] Merging all sources into master dataset...")
    master = merge_sources(cleaned)
    master_path = os.path.join(OUTPUT_DIR, "master_report.csv")
    master.to_csv(master_path, index=False)
    print(f"      Master dataset: {master.shape[0]} rows × {master.shape[1]} columns")
    print(f"  ✔  Saved → {master_path}")

    # Save quality report
    qr = pd.DataFrame(quality_after)
    qr.to_csv(os.path.join(OUTPUT_DIR, "quality_report.csv"), index=False)

    # 6. Generate charts + report
    print("\n[6/6] Generating dashboard & HTML report...")
    generate_charts(quality_before, quality_after, master)
    generate_html_report(quality_before, quality_after, master)

    print("\n" + "=" * 60)
    print("  PIPELINE COMPLETE!")
    print("  Open  output/report.html  in your browser to see results")
    print("=" * 60)


if __name__ == "__main__":
    run_pipeline()
