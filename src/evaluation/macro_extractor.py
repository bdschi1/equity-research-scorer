import os
import json
from typing import List, Optional
from openai import OpenAI
from pydantic import BaseModel, Field
from src.prompts.manager import PromptManager # <--- NEW IMPORT

# --- 1. DATA STRUCTURES ---
class InvestableIdea(BaseModel):
    name: str = Field(..., description="The Ticker or Theme")
    type: str = Field(..., description="'Ticker' or 'Theme'")
    rationale: str = Field(..., description="Why this is a beneficiary")

class KeyStat(BaseModel):
    metric: str = Field(..., description="Name of metric")
    value: str = Field(..., description="Value (e.g. 695m tons)")
    context: str = Field(..., description="Brief context")

class MacroReport(BaseModel):
    topic: str = Field(..., description="Main subject")
    summary: str = Field(..., description="Executive summary")
    variant_view: str = Field(..., description="A contrarian or non-obvious take.")
    bear_case: str = Field(..., description="Structural counter-argument.")
    top_5_ideas: List[InvestableIdea] = Field(..., description="Top 5 targets.")
    key_stats: List[KeyStat] = Field(..., description="Crucial data points.")
    investment_implication: str = Field(..., description="The 'So What?'")

# --- 2. THE EXTRACTOR ENGINE ---
class MacroExtractor:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.prompts = PromptManager() # <--- Initialize Manager

    def analyze(self, text: str, filename: str) -> dict:
        structured_data = self._llm_extract(text)
        return {
            "source_file": filename,
            "topic": structured_data.topic,
            "summary": structured_data.summary,
            "variant_view": structured_data.variant_view,
            "bear_case": structured_data.bear_case,
            "investment_implication": structured_data.investment_implication,
            "top_ideas": [i.model_dump() for i in structured_data.top_5_ideas],
            "key_stats": [k.model_dump() for k in structured_data.key_stats],
        }

    def _llm_extract(self, text: str) -> MacroReport:
        truncated_text = text[:60000] 
        
        # <--- LOAD FROM YAML
        system_prompt = self.prompts.get_prompt("macro_extractor_system")
        
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
            print(f"⚠️ Extraction Failed: {e}")
            return MacroReport(
                topic="Error", summary="Failed", variant_view="N/A", bear_case="N/A", 
                top_5_ideas=[], key_stats=[], investment_implication=""
            )