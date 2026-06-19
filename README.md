# Multi-Source Data Quality Automation

A Python pipeline that pulls data from **5 different sources** (like 5 different
company departments), cleans it automatically, checks quality before & after,
merges it all into one master file, and generates a dashboard + HTML report.

---

## 🚀 How to Run (3 steps)

### Step 1 — Install Python
Make sure Python 3.8+ is installed. Check with:
```bash
python3 --version
```

### Step 2 — Install the required libraries
Open a terminal/command prompt **inside this folder** and run:
```bash
pip install -r requirements.txt
```

### Step 3 — Run the project
```bash
python3 main.py
```

That's it! Watch the terminal — it prints progress for every step.

---

## 📂 What you'll get (in the `output/` folder)

| File                  | What it is                                          |
|------------------------|------------------------------------------------------|
| `master_report.csv`    | The final, cleaned, merged dataset (all 5 sources combined) |
| `quality_report.csv`   | Quality score for each source after cleaning        |
| `dashboard.png`        | 6 charts showing before/after quality, distributions, summary |
| `report.html`          | A full visual report — **double-click to open in your browser** |

---

## 🧠 What the code actually does (in order)

1. **Generates 5 messy datasets** (HR, Payroll, IT Assets, Performance, Attendance) — on purpose with missing values, wrong data types, inconsistent text casing, and invalid numbers, just like real-world data.
2. **Checks data quality** of each source — counts missing/invalid values and calculates a completeness %.
3. **Cleans each source** with rules specific to it (e.g., fixes negative ages, standardizes currency codes, fixes inconsistent capitalization like "windows 11" vs "Windows 11").
4. **Checks quality again** after cleaning, to prove the cleaning worked.
5. **Merges all 5 cleaned sources** into a single master table using the employee ID as the common key.
6. **Builds a dashboard and an HTML report** so the results are easy to see and share.

---

## ⚙️ Want to use YOUR OWN data instead of the sample data?

Replace the `generate_raw_sources()` function call with your own CSV reads, e.g.:
```python
hr_data = pd.read_csv("your_hr_file.csv")
```
Then adjust the cleaning functions (`clean_hr`, `clean_payroll`, etc.) to match your real column names.

---

**Project by:** Sai Sushma Karumuri
