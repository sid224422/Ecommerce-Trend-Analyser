# AI-Assisted Market Analytics System - Architecture Document

## 1. System Overview

This system is an academic project designed to analyze market data from CSV files and generate insights through deterministic analytical agents. The system follows a clear pipeline: data ingestion → validation → analysis → summarization.

**Key Principle**: All computational analysis is performed using pure Python and Pandas. The LLM (Gemini) is used **only once** at the final stage to summarize pre-computed results into natural language.

## 2. Architecture Components

### 2.1 Data Flow Pipeline

```
CSV Input
  ↓
Data Ingestion (ingestion.py)
  ↓
Data Validation & Cleaning (validator.py)
  ↓
Analytical Agents (agents/*.py)
  ├─ Brand Agent → Brand statistics
  ├─ Pricing Agent → Price analysis
  ├─ Feature Agent → Feature extraction
  └─ Gap Agent → Market gaps identification
  ↓
Structured JSON Outputs
  ↓
LLM Summarization (llm/summarizer.py) - SINGLE CALL
  ↓
Streamlit UI (ui/app.py)
  ↓
Optional PDF Report
```

### 2.2 Component Descriptions

#### **Core Layer** (`/core`)
- **ingestion.py**: Reads CSV files and loads data into Pandas DataFrames
- **validator.py**: Validates data integrity, handles missing values, ensures data quality

#### **Analytical Layer** (`/agents`)
- **brand_agent.py**: Computes top brands, counts, and market share
- **pricing_agent.py**: Calculates min/max prices, optimal price ranges, pricing statistics
- **feature_agent.py**: Extracts and counts most common product features
- **gap_agent.py**: Identifies underrepresented brand-feature combinations

**Agent Design Principle**: Each agent is deterministic, pure Python/Pandas-based, returns structured JSON, and has no AI dependencies.

#### **LLM Layer** (`/llm`)
- **summarizer.py**: Makes a single Gemini API call to summarize agent outputs
- **prompt.txt**: Fixed, versioned prompt template for consistent summarization
- **Configuration**: Temperature ≤ 0.3, single call per analysis run

#### **Presentation Layer** (`/ui`)
- **app.py**: Streamlit interface for data upload, visualization, and report display
- Uses Plotly for all visualizations
- Displays agent outputs and LLM summary

#### **Output Layer** (`/reports`)
- Stores generated JSON outputs and PDF reports (if enabled)

## 3. Technical Stack

- **Language**: Python 3.11
- **Data Processing**: Pandas
- **Visualization**: Plotly (only visualization library)
- **UI Framework**: Streamlit (local deployment)
- **LLM**: Gemini 1.5 Flash (single call, temperature ≤ 0.3)
- **Optional Database**: Firebase Firestore (minimal usage, if needed)
- **Containerization**: Docker (local only)

## 4. Key Design Decisions

### 4.1 Deterministic Analysis
All analytical computations are performed using standard statistical methods in Pandas. This ensures:
- Reproducible results
- Explainable outcomes for viva presentations
- No dependency on external AI services for core analysis

### 4.2 Confidence Scoring
Confidence scores are calculated using the formula:
```
confidence = count / total_records
```
This provides a simple, interpretable measure of data reliability.

### 4.3 Single LLM Call
The LLM is invoked exactly once per analysis run, only for summarizing pre-computed structured data. This approach:
- Minimizes API costs
- Ensures fast analysis execution
- Keeps the system explainable (agents produce results independently)

### 4.4 Structured Output Format
All agents return JSON with consistent structure:
```json
{
  "agent_name": "...",
  "results": {...},
  "confidence": 0.0-1.0,
  "timestamp": "..."
}
```

## 5. Development Phases

1. **Phase 1**: Core infrastructure (ingestion, validation) ✅
2. **Phase 2**: Analytical agents (brand, pricing, feature, gap)
3. **Phase 3**: LLM integration (summarizer)
4. **Phase 4**: Streamlit UI
5. **Phase 5**: Testing and documentation

## 6. Constraints and Guidelines

- **No over-engineering**: Simple, straightforward implementations
- **No unnecessary frameworks**: Use only specified technologies
- **Explainability**: All code must be understandable in academic viva
- **Small functions**: Prefer functions with focused, single responsibilities
- **Testability**: Each agent must be independently testable

## 7. Data Assumptions

The system expects CSV files with market/product data containing columns such as:
- Brand/Product names
- Prices
- Features/Attributes
- Other market-relevant fields

Exact schema will be validated during the ingestion phase.

