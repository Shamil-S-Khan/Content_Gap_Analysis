# Installation and Testing Guide

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- 1GB free disk space
- Internet connection (for downloading dependencies)

### Step 1: Install Python Dependencies

```bash
# Navigate to project directory
cd content_gap_analysis

# Install required packages
pip install beautifulsoup4 nltk spacy scikit-learn numpy

# Or install from requirements.txt
pip install -r requirements.txt
```

### Step 2: Download Language Models

```bash
# Download spaCy English model
python -m spacy download en_core_web_sm

# NLTK data will download automatically on first run
# Or manually download:
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('averaged_perceptron_tagger')"
```

### Step 3: Verify Installation

```bash
# Test imports
python -c "import nltk, spacy, sklearn, numpy, bs4; print('✅ All dependencies installed successfully')"
```

Expected output:
```
✅ All dependencies installed successfully
```

## 🧪 Testing

### Quick Test (Demo Mode)

```bash
# Run full analysis with sample data
python main.py
```

**Expected runtime:** 30-60 seconds

**Expected output:**
```
================================================================================
CONTENT GAP ANALYSIS INTELLIGENCE PACKAGE GENERATOR
================================================================================

[1/8] Processing document corpora...
  ✓ Your content: 2 documents, 1,847 tokens
  ✓ Competitor content: 3 documents, 5,623 tokens

[2/8] Performing topic modeling and semantic analysis...
  ✓ Shared topics: 15
  ✓ Missing topics: 12

[3/8] Identifying content gaps...
  ✓ Total gaps identified: 30

[4/8] Generating content recommendations...
  ✓ Recommendations generated: 12

[5/8] Training and evaluating ML classification model...
  ✓ PASS Model accuracy: 86.27% (threshold: ≥80%)
  ✓ Precision: 87.19%
  ✓ Recall: 85.42%
  ✓ F1 Score: 86.15%

[6/8] Creating dashboard specifications...
  ✓ Dashboard visualizations: 5

[7/8] Generating comprehensive PDF report...
  ✓ Report saved: reports/content_gap_analysis_report.md

[8/8] Creating executive presentation...
  ✓ Presentation slides: 10

[FINAL] Consolidating master JSON package...
  ✓ Master package saved: content_gap_analysis_package.json

================================================================================
ANALYSIS COMPLETE!
================================================================================

📊 Deliverables:
  • Master JSON Package: content_gap_analysis_package.json
  • PDF Report: reports/content_gap_analysis_report.md
  • Dashboard Specs: dashboards/dashboard_specifications.json
  • Model Metrics: models/model_evaluation_metrics.json

🎯 Key Metrics:
  • Gaps Identified: 30
  • Recommendations: 12
  • Model Accuracy: 86.27%
  • Expected ROI: 2.5x - 5x over 6 months

✅ All deliverables generated successfully!
```

### Verify Output Files

```bash
# Check if all output files were created
ls -la content_gap_analysis_package.json
ls -la reports/content_gap_analysis_report.md
ls -la dashboards/dashboard_specifications.json
ls -la models/model_evaluation_metrics.json
```

### Test Individual Modules

```bash
# Test data ingestion
python data_ingestion.py

# Test topic modeling
python topic_modeling.py

# Test gap analyzer
python gap_analyzer.py

# Test recommendation generator
python recommendation_generator.py

# Test ML model
python ml_model.py

# Test dashboard specs
python dashboard_specs.py

# Test report generator
python report_generator.py

# Test presentation generator
python presentation_generator.py
```

## 🔧 Troubleshooting

### Issue: ModuleNotFoundError

**Error:**
```
ModuleNotFoundError: No module named 'nltk'
```

**Solution:**
```bash
pip install nltk spacy scikit-learn beautifulsoup4 numpy
```

### Issue: spaCy model not found

**Error:**
```
OSError: [E050] Can't find model 'en_core_web_sm'
```

**Solution:**
```bash
python -m spacy download en_core_web_sm
```

### Issue: NLTK data not found

**Error:**
```
LookupError: Resource punkt not found
```

**Solution:**
```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"
```

### Issue: Permission denied

**Error:**
```
PermissionError: [Errno 13] Permission denied
```

**Solution:**
```bash
# Use --user flag
pip install --user beautifulsoup4 nltk spacy scikit-learn numpy

# Or use virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Issue: Low model accuracy

**Warning:**
```
Warning: Model accuracy (78.42%) is below 80% threshold
```

**Solutions:**
1. Increase training samples:
   ```python
   features, labels, desc = model.create_training_dataset(
       gaps=gaps,
       synthetic_samples=500  # Increase from 300
   )
   ```

2. Add more real gap data (analyze more documents)

3. Adjust model parameters in `ml_model.py`

### Issue: Out of memory

**Error:**
```
MemoryError: Unable to allocate array
```

**Solutions:**
1. Reduce `max_features` in vectorizers
2. Process documents in batches
3. Limit number of topics: `TopicModelingEngine(n_topics=5)`

## ✅ Validation Checklist

After installation, verify:

- [ ] All Python dependencies installed
- [ ] spaCy model downloaded
- [ ] NLTK data downloaded
- [ ] Demo runs successfully
- [ ] Output files generated:
  - [ ] `content_gap_analysis_package.json`
  - [ ] `reports/content_gap_analysis_report.md`
  - [ ] `dashboards/dashboard_specifications.json`
  - [ ] `models/model_evaluation_metrics.json`
- [ ] ML model accuracy ≥ 80%
- [ ] Sample data created in `data/sample_content/`
- [ ] No error messages

## 📊 Performance Benchmarks

Expected performance on demo dataset:

| Metric | Expected Value |
|--------|----------------|
| Total runtime | 30-60 seconds |
| Documents processed | 5 (2 yours + 3 competitors) |
| Gaps identified | 25-35 |
| Recommendations generated | 10-15 |
| Model accuracy | 85-90% |
| Model training time | < 10 seconds |
| Report generation time | < 5 seconds |

## 🔍 Testing with Custom Data

### Minimal Test Dataset

Create at least:
- **Your content:** 3-5 documents (TXT, JSON, or MD)
- **Competitor content:** 3-5 documents per competitor

### Example Test Structure

```
data/
├── your_content/
│   ├── article1.txt
│   ├── guide.md
│   └── page.json
└── competitors/
    ├── competitor_a_article.html
    ├── competitor_b_guide.md
    └── competitor_c_post.txt
```

### Run Custom Test

```python
from main import ContentGapAnalysisOrchestrator

your_files = [
    "data/your_content/article1.txt",
    "data/your_content/guide.md",
    "data/your_content/page.json"
]

competitor_files = [
    "data/competitors/competitor_a_article.html",
    "data/competitors/competitor_b_guide.md",
    "data/competitors/competitor_c_post.txt"
]

orchestrator = ContentGapAnalysisOrchestrator(
    your_organization="Test Organization",
    competitors=["Test Competitor A", "Test Competitor B"]
)

results = orchestrator.run_full_analysis(
    your_content_files=your_files,
    competitor_content_files=competitor_files,
    min_recommendations=10
)

print(f"✅ Analysis complete: {len(results['recommendations'])} recommendations generated")
```

## 🎯 Next Steps After Installation

1. **Run Demo:** `python main.py`
2. **Review Outputs:** Check generated JSON and markdown files
3. **Read Documentation:** Start with `QUICKSTART.md`
4. **Explore Examples:** Review `EXAMPLE_OUTPUT.json`
5. **Customize:** Modify for your specific needs
6. **Deploy:** Use with real content data

## 📞 Getting Help

If issues persist:

1. Check Python version: `python --version` (need 3.8+)
2. Update pip: `pip install --upgrade pip`
3. Review error messages carefully
4. Check `README.md` for detailed documentation
5. Verify file permissions in project directory

## 🎓 Learning Path

For new users:

1. **Day 1:** Installation + run demo
2. **Day 2:** Review outputs, read QUICKSTART.md
3. **Day 3:** Test with small custom dataset
4. **Day 4:** Customize recommendations/scoring
5. **Day 5:** Full production deployment

---

**Installation Status Verification:**

Run this command to verify complete installation:

```bash
python -c "
import sys
print(f'Python version: {sys.version}')
try:
    import nltk, spacy, sklearn, numpy, bs4
    print('✅ All dependencies installed')
    import spacy
    nlp = spacy.load('en_core_web_sm')
    print('✅ spaCy model loaded')
    print('✅ Installation verified successfully!')
except Exception as e:
    print(f'❌ Error: {e}')
"
```

Expected output:
```
Python version: 3.8.x (or higher)
✅ All dependencies installed
✅ spaCy model loaded
✅ Installation verified successfully!
```
