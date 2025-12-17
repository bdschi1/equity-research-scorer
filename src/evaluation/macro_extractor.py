import os
import json
from typing import List, Optional
from openai import OpenAI
from pydantic import BaseModel, Field

# --- 1. DATA STRUCTURES ---

class InvestableIdea(BaseModel):
    name: str = Field(..., description="The Ticker (e.g. 'DE') or Theme (e.g. 'Seed Security')")
    type: str = Field(..., description="Must be either 'Ticker' or 'Theme'")
    rationale: str = Field(..., description="1 sentence explaining why this is a beneficiary")

class KeyStat(BaseModel):
    metric: str = Field(..., description="The name of the metric (e.g., 'Grain Output')")
    value: str = Field(..., description="The value found (e.g., '695 million tons')")
    context: str = Field(..., description="Brief context")

class MacroReport(BaseModel):
    topic: str = Field(..., description="The main subject (e.g., 'China Food Security')")
    summary: str = Field(..., description="Executive summary of the macro thesis")
    
    # NEW FIELDS for Deep Analysis
    variant_view: str = Field(..., description="A contrarian or non-obvious take on this theme. What is the hidden implication?")
    bear_case: str = Field(..., description="The structural counter-argument. Why might this macro theme fail to materialize?")
    
    top_5_ideas: List[InvestableIdea] = Field(..., description="The top 5 most important tickers OR themes mentioned.")
    key_stats: List[KeyStat] = Field(..., description="List of 5-10 crucial data points extracted from text")
    investment_implication: str = Field(..., description="The 'So What?' for investors")

# --- 2. THE EXTRACTOR ENGINE ---
class MacroExtractor:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def analyze(self, text: str, filename: str) -> dict:
        """
        Turns a Macro PDF into a structured dataset and thematic basket.
        """
        structured_data = self._llm_extract(text)
        
        return {
            "source_file": filename,
            "topic": structured_data.topic,
            "summary": structured_data.summary,
            "variant_view": structured_data.variant_view, # <--- Passing it through
            "bear_case": structured_data.bear_case,       # <--- Passing it through
            "investment_implication": structured_data.investment_implication,
            "top_ideas": [i.model_dump() for i in structured_data.top_5_ideas],
            "key_stats": [k.model_dump() for k in structured_data.key_stats],
        }

    def _llm_extract(self, text: str) -> MacroReport:
        """Uses OpenAI to structure the unstructured text."""
        # Truncate text to fit context window
        truncated_text = text[:60000] 
        
        system_prompt = """
        You are a Senior Macro Strategist. Extract a structured dataset from this report.
        
        CRITICAL INSTRUCTIONS:
        1. Find the VARIANT VIEW: Look for non-obvious, second-level insights. What is the market missing?
        2. Identify the BEAR CASE: Why is this thesis wrong? (e.g., 'If commodity prices crash, this whole theme unwinds.')
        3. Curate the TOP 5 Investable Ideas (Tickers or Themes).
        """
        
        try:
            completion = self.client.beta.chat.completions.parse(
                model="gpt-4o-2024-08-06",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Analyze this report:\n\n{truncated_text}"}
                ],
                response_format=MacroReport,
            )
            return completion.choices[0].message.parsed
            
        except Exception as e:
            print(f"⚠️ LLM Extraction Failed: {e}")
            return MacroReport(
                topic="Error", summary="Extraction failed", 
                variant_view="N/A", bear_case="N/A", 
                top_5_ideas=[], key_stats=[], investment_implication=""
            )