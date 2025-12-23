# 🤖 AI Investment Committee (Equity Research Scorer)

**An Institutional-Grade AI Analyst that reads, grades, and validates investment research.**

This tool automates the "First Pass" review of stock pitches and macro reports. It acts as a digital Portfolio Manager, switching context between **Single Stock Analysis** (Validation + Scoring) and **Macro Deep Dives** (Thematic Extraction).

![Status](https://img.shields.io/badge/Status-Production%20Ready-green)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![OpenAI](https://img.shields.io/badge/AI-GPT--4o-orange)

---

## 🚀 Key Features

### 1. The "Smart Router" Engine
The system automatically detects the document type:
* **Single Stock Mode:** Triggered if a specific ticker (e.g., "NVDA", "LLY") is the primary subject.
* **Macro/Sector Mode:** Triggered for broad reports (e.g., "China Agriculture", "Global AI Trends").

### 2. Institutional Scoring ("The Alpha Test")
Instead of generic summaries, the AI mimics a Senior Portfolio Manager:
* **👁️ The Variant View:** Identifies the non-obvious, second-level insight (the "Edge").
* **🐻 The Bear Case:** Constructs a structural counter-argument to the thesis.
* **💀 Pre-Mortem:** Identifies the specific "Kill Shot" event that invalidates the trade.
* **🔭 Mosaic Strategy:** Suggests alternative data sources (Satellite, Credit Card data, etc.) to track the idea.

### 3. Financial Fact-Checking
* **Revenue/EPS Verification:** Cross-references claims in the text against **SEC EDGAR** and **Yahoo Finance** consensus estimates.
* **Hallucination Guard:** If the numbers don't match, the specific claim is flagged as ❌.

### 4. Macro Extraction & Basket Generation
* **Investable Universe:** Extracts the "Top 5 Investable Ideas" (Tickers or Themes) from unstructured text.
* **Data Structuring:** Converts dense paragraphs into clean Key Statistics tables.

---

## 🛠️ Installation

1.  **Clone the Repo**
    ```bash
    git clone [https://github.com/bdschi1/equity-research-scorer.git](https://github.com/bdschi1/equity-research-scorer.git)
    cd equity-research-scorer
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Setup Environment**
    Create a `.env` file in the root directory:
    ```bash
    OPENAI_API_KEY="your-key-here"
    ```

---

## ⚡ Usage Workflow

### 1. Drop PDFs
Place your research reports (PDFs) into the raw data folder:
`data/raw_pdfs/`

### 2. Run the Analysis Engine
This script identifies the doc type, extracts data, and runs the AI Judge.
```bash
python3 main.py