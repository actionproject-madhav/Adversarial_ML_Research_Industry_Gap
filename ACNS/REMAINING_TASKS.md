# Remaining Tasks for ACNS-ISC 2026 Submission

## ✅ COMPLETED (By AI)

### Paper Content
- [x] Condensed paper from 19 to 17 pages
- [x] Added confidence intervals (95% CI) to all key percentages
- [x] Added statistical tests (logistic regression, chi-square, Fisher's exact)
- [x] Restructured sections (merged Thematic Findings, added Foundation Models section)
- [x] Removed bullet-point style paragraphs
- [x] Fixed figure placement issues
- [x] Added appendix with codebook and GPT-4o prompt
- [x] Moved appendix to after references (correct format)
- [x] Added "Why This Gap Matters" section addressing LLMs, multimodal, agentic systems
- [x] Fixed all citation keys
- [x] Restored important real-world incidents detail
- [x] Added attack vs. defense comparison with statistical significance

### Current Status
- **Page count**: 17 pages (14 main + 3 appendix)
- **Format**: Springer LNCS, double-blind
- **Figures**: 12 figures, properly placed
- **Statistics**: Full statistical rigor with CIs and p-values
- **Structure**: 10 main sections + 2 appendix sections

---

## 🔴 CRITICAL - YOUR TASKS (Before Submission)

### 1. **Manual Verification of AI-Assisted Coding** ⚠️ MOST IMPORTANT
**What:** Manually verify a sample of papers (50-100) to validate AI coding accuracy

**Why:** Reviewers will ask about reliability. You need inter-annotator reliability metrics.

**How:**
1. Randomly select 50-100 papers from your dataset
2. Manually code them yourself using the codebook (Appendix A)
3. Compare your coding to GPT-4o's coding
4. Calculate:
   - Agreement rate (% papers where you agree)
   - Per-dimension agreement
   - Cohen's kappa (if possible)
   - Error patterns (which dimensions are hardest?)

**Where to add:**
- Add a paragraph in Methodology section: "To validate AI-assisted coding, we manually verified [N] randomly selected papers, achieving [X]% agreement (Cohen's κ = [Y])."
- Or in Limitations: "Manual verification of [N] papers showed [X]% agreement..."

**Time estimate:** 2-4 hours for 50 papers

---

### 2. **Prepare Supplementary Materials**
**What:** Create a ZIP file with all supplementary materials

**Contents:**
```
supplementary_materials/
├── README.md                                    # Brief guide to contents
├── data/
│   └── all_conferences_analysis_results_2022_2025.csv
├── code/
│   ├── benchmark_review_automation.py           # GPT-4o coding pipeline
│   ├── compute_statistics.py                    # Statistical analysis
│   ├── generate_figures.py                      # Figure generation
│   └── requirements.txt                         # Python dependencies
├── codebook/
│   └── benchmark_criteria.csv                   # Machine-readable codebook
└── prompts/
    └── gpt4o_analysis_prompt.txt                # Full GPT-4o prompt
```

**Files to include:**
- `/Users/madhav/Documents/Adversarial-Machine-Learning/overall/all_conferences_analysis_results_2022_2025.csv`
- `/Users/madhav/Documents/Adversarial-Machine-Learning/review_benchmarks_acm/benchmark_review_automation.py`
- `/Users/madhav/Documents/Adversarial-Machine-Learning/ACNS/compute_statistics.py`
- `/Users/madhav/Documents/Adversarial-Machine-Learning/overall/generate_figures.py`
- `/Users/madhav/Documents/Adversarial-Machine-Learning/review_benchmarks_acm/benchmark_criteria.csv`
- `/Users/madhav/Documents/Adversarial-Machine-Learning/review_benchmarks_acm/requirements.txt`

**Time estimate:** 30 minutes

---

### 3. **Final Proofreading**
**What:** Read through the entire paper once more

**Check for:**
- [ ] Typos and grammatical errors
- [ ] Consistent terminology (e.g., "Gap Score" vs "gap score")
- [ ] All figure references work (Fig.~\ref{...})
- [ ] All citations render correctly
- [ ] No [??] or missing references
- [ ] Abstract matches final content
- [ ] Page limit compliance (check workshop CFP)

**Time estimate:** 1 hour

---

### 4. **Verify ACNS-ISC Submission Requirements**
**What:** Check the workshop's call for papers

**Verify:**
- [ ] Page limit (is 17 pages acceptable? Check if appendix counts)
- [ ] Submission deadline
- [ ] Double-blind requirements (no author info in PDF metadata)
- [ ] Supplementary materials allowed?
- [ ] Submission platform (EasyChair, HotCRP, etc.)
- [ ] Required sections (abstract, keywords, etc.)

**Where to check:** ACNS-ISC 2026 workshop website

**Time estimate:** 15 minutes

---

### 5. **Check PDF Metadata (Double-Blind)**
**What:** Ensure no author information in PDF metadata

**How:**
```bash
cd /Users/madhav/Documents/Adversarial-Machine-Learning/ACNS/paper
pdfinfo main.pdf | grep -i "author\|creator\|producer"
```

**If author info appears:**
- Use `exiftool` to strip metadata:
```bash
exiftool -all= main.pdf
```

**Time estimate:** 5 minutes

---

### 6. **Create GitHub Repository (After Acceptance)**
**What:** Prepare GitHub repo structure (but keep private until acceptance)

**Structure:**
```
adversarial-ml-gap-analysis/
├── README.md
├── data/
├── code/
├── prompts/
├── results/
├── docs/
└── LICENSE
```

**Time estimate:** 30 minutes (but do this AFTER acceptance)

---

## 📋 OPTIONAL (Nice to Have, Not Critical)

### 1. **Sensitivity Analysis**
- Re-run analysis with alternative thresholds (e.g., >500 queries instead of >1000)
- See if conclusions change
- **Why optional:** Already acknowledged in limitations
- **Time:** 2-3 hours

### 2. **Additional Statistical Tests**
- Subgroup analysis (e.g., year × venue interactions)
- Effect sizes (Cohen's d, odds ratios)
- **Why optional:** Current statistical tests are sufficient
- **Time:** 1-2 hours

### 3. **Extended Related Work**
- Add more citations to recent work
- Expand background section
- **Why optional:** Paper is already comprehensive
- **Time:** 1 hour

---

## 📊 SUBMISSION CHECKLIST

Before you click "Submit":

- [ ] **Manual verification completed** (50-100 papers, agreement rate calculated)
- [ ] **Supplementary materials ZIP created** (data + code + prompts)
- [ ] **Final proofreading done** (no typos, all refs work)
- [ ] **Page limit verified** (17 pages OK for workshop?)
- [ ] **PDF metadata stripped** (double-blind compliant)
- [ ] **All figures render correctly** (check PDF visually)
- [ ] **Abstract updated** (matches final content)
- [ ] **Keywords appropriate** (5 keywords listed)
- [ ] **References formatted correctly** (LNCS style)
- [ ] **Appendix after references** (correct order)
- [ ] **Supplementary materials referenced in paper** (conclusion mentions them)

---

## 🎯 PRIORITY ORDER

1. **CRITICAL - Manual verification** (2-4 hours) ⚠️
2. **CRITICAL - Prepare supplementary materials** (30 min)
3. **IMPORTANT - Final proofreading** (1 hour)
4. **IMPORTANT - Verify submission requirements** (15 min)
5. **IMPORTANT - Check PDF metadata** (5 min)
6. Optional tasks (only if time permits)

**Total time for critical tasks: ~4-6 hours**

---

## 📝 NOTES

### What's Already Done (You Don't Need to Do)
- ✅ Paper is formatted correctly (Springer LNCS)
- ✅ All statistics are computed and included
- ✅ Confidence intervals on all key findings
- ✅ Statistical tests for all major claims
- ✅ Appendix with codebook and prompt
- ✅ Foundation models section showing relevance
- ✅ Figures properly placed and referenced
- ✅ Citations all correct
- ✅ Structure logical and flowing

### What You MUST Do
- ⚠️ **Manual verification** - This is the only thing reviewers will definitely ask about
- 📦 **Supplementary materials** - Required for submission
- 👀 **Proofreading** - Catch any remaining errors
- ✅ **Submission requirements** - Make sure you comply

### What's Nice But Optional
- Sensitivity analysis (acknowledged in limitations)
- Additional statistical tests (current tests sufficient)
- Extended related work (paper already comprehensive)

---

## 🚀 READY TO SUBMIT WHEN:

1. ✅ Manual verification done (agreement rate in paper)
2. ✅ Supplementary materials ZIP ready
3. ✅ Final proofread complete
4. ✅ Submission requirements verified
5. ✅ PDF metadata stripped

**Then you're good to go!**
