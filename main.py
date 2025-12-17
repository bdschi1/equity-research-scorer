import json
import os
import datetime
from dotenv import load_dotenv  # <--- THIS WAS MISSING
from src.ingestion.pdf_loader import PDFLoader
from src.evaluation.scorer import EquityScorer
from src.evaluation.financial_validator import FinancialValidator
from src.data.company_lookup import CompanyLookup
from src.evaluation.macro_extractor import MacroExtractor

# Load environment variables immediately
load_dotenv()

def main():
    # 1. Setup paths
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    RAW_DIR = os.path.join(BASE_DIR, "data/raw_pdfs")
    OUTPUT_FILE = os.path.join(BASE_DIR, "data/processed/scores.json")
    
    # 2. Initialize Engines
    # Now this will work because env vars are loaded
    loader = PDFLoader(raw_dir=RAW_DIR)
    scorer = EquityScorer()
    validator = FinancialValidator()
    lookup = CompanyLookup()
    macro_tool = MacroExtractor()
    
    print("\n🚀 STARTING RESEARCH PIPELINE")
    print("==================================================")

    # 3. Ingestion
    documents = loader.load_documents()
    
    if not documents:
        print("⚠️  No documents found. Please drop PDFs in data/raw_pdfs/")
        return

    # 4. Processing Loop
    all_results = []
    
    # Load existing history to append to it
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, 'r') as f:
                all_results = json.load(f)
        except:
            all_results = []

    for doc in documents:
        print(f"\n📄 Analyzing: {doc['source']}")
        
        # Check cache (skip if already processed)
        if any(r['file'] == doc['source'] for r in all_results):
            print("   ⏩ Skipping (Already in database)")
            continue

        # --- STEP 4a: IDENTIFY TICKER ---
        ticker = lookup.extract_ticker(doc['content'])

        # ====================================================
        # ROUTE A: SINGLE STOCK PITCH (e.g., "Buy NVDA")
        # ====================================================
        if ticker:
            print(f"   🎯 Mode: Single Stock ({ticker})")
            
            # 1. Financial Fact Check
            print("   🔍 Verifying Financials...")
            fact_checks = validator.validate(doc['content'], ticker)
            for check in fact_checks:
                icon = "✅" if check['status'] == "MATCH" else "❌"
                print(f"      {icon} {check['metric']}: Claimed {check['claimed']} vs Actual {check['actual']}")

            # 2. AI Judge
            print("   🧠 Running AI Judge...")
            score_data = scorer.evaluate(doc['content'], doc['source'])
            
            if score_data:
                record = {
                    "file": doc['source'],
                    "timestamp": datetime.datetime.now().isoformat(),
                    "type": "single_stock",
                    "ticker": ticker,
                    "boilerplate_removed": doc.get('boilerplate_removed_pct', "0%"),
                    "fact_checks": fact_checks,
                    **score_data
                }
                all_results.insert(0, record)
                print(f"   ✅ Final Score: {record['overall_score']}/5.0")

        # ====================================================
        # ROUTE B: MACRO / SECTOR DEEP DIVE (e.g. "China Ag")
        # ====================================================
        else:
            print("   🌍 Mode: Macro/Sector Deep Dive (No single ticker found)")
            
            # 1. Run Macro Extraction
            print("   ⛏️  Extracting Thematic Data...")
            macro_data = macro_tool.analyze(doc['content'], doc['source'])
            
            # 2. Print Summary for User
            print(f"      📊 Topic: {macro_data['topic']}")
            print(f"      💡 Implication: {macro_data['investment_implication'][:100]}...")
            
            print("      🏆 Top 5 Investable Ideas:")
            for idea in macro_data['top_ideas']:
                icon = "🏢" if idea['type'] == 'Ticker' else "🌊"
                print(f"         {icon} {idea['name']}: {idea['rationale']}")
            
            # 3. Save Record
            record = {
                "file": doc['source'],
                "timestamp": datetime.datetime.now().isoformat(),
                "type": "macro_deep_dive",
                "ticker": "MACRO", # Placeholder for UI sorting
                "boilerplate_removed": doc.get('boilerplate_removed_pct', "0%"),
                **macro_data
            }
            all_results.insert(0, record)
            print("   ✅ Macro Analysis Complete")

    # 5. Save Database
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print("==================================================")
    print(f"💾 Database updated: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()