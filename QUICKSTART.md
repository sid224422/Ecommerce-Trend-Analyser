# Quick Start Guide

## Setup Steps

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

**Option A: Using .env file (Recommended)**
```bash
# Create .env file from template
python setup_env.py create

# Edit .env file and add your API key
# Get API key from: https://ai.google.dev/gemini-api/docs/quickstart
```

**Option B: System Environment Variable**
```powershell
# Windows PowerShell
$env:GEMINI_API_KEY='your_api_key_here'
```

### 3. Verify Setup
```bash
# Check environment configuration
python setup_env.py

# Test environment loading
python test_env_loading.py
```

### 4. Test the System

**Test Agents:**
```bash
python test_agents.py
```

**Test LLM Integration:**
```bash
python test_llm_comprehensive.py
```

**Test Full Pipeline:**
```bash
python test_full_pipeline.py
```

## Project Structure

```
/Final
  /agents          - Analytical agents (brand, pricing, feature, gap)
  /core            - Data ingestion and validation
  /llm             - LLM summarization (Gemini)
  /ui              - Streamlit UI (Phase 4)
  /reports         - Generated reports
  .env             - Environment variables (create from env_template.txt)
  requirements.txt - Python dependencies
```

## Usage Example

```python
from core.ingestion import read_csv_file
from core.validator import validate_and_clean
from agents.brand_agent import analyze_brands
from agents.pricing_agent import analyze_pricing
from agents.feature_agent import analyze_features
from agents.gap_agent import analyze_gaps
from llm.summarizer import summarize_agent_results

# Load and validate data
df = read_csv_file("your_data.csv")
cleaned_df = validate_and_clean(df)

# Run agents
agent_outputs = [
    analyze_brands(cleaned_df, brand_column="brand"),
    analyze_pricing(cleaned_df, price_column="price"),
    analyze_features(cleaned_df, feature_column="feature"),
    analyze_gaps(cleaned_df, brand_column="brand", feature_column="feature")
]

# Summarize with LLM (requires GEMINI_API_KEY)
summary = summarize_agent_results(agent_outputs)
print(summary['summary'])
```

## Files Reference

- `setup_env.py` - Environment setup helper
- `ENV_SETUP.md` - Detailed environment setup guide
- `ARCHITECTURE.md` - System architecture documentation
- `TEST_SUMMARY.md` - Testing documentation

## Next Steps

1. ✅ Phase 1: Core infrastructure (DONE)
2. ✅ Phase 2: Analytical agents (DONE)
3. ✅ Phase 3: LLM integration (DONE)
4. ⏳ Phase 4: Streamlit UI (NEXT)
5. ⏳ Phase 5: Testing and documentation

