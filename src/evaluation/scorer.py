import os
import json
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import List, Optional
from src.prompts.manager import PromptManager  # <--- NEW IMPORT

# --- 1. ROBUST DATA STRUCTURES ---
class DimensionScore(BaseModel):
    score: int = Field(..., description="Integer score from 1-5")
    reasoning: str = Field(..., description="Justification for the score")
    quote_verbatim: str = Field(..., description="Exact sentence from text proving this score.")
    red_flags: List[str] = Field(default=[], description="Bullet points of specific concerns")

class PMPerspective(BaseModel):
    variant_view: str = Field(..., description="A non-obvious, second-level insight.")
    bear_case: str = Field(..., description="The smartest counter-argument (Bear Thesis).")
    catalyst_timing: str = Field(..., description="Specific dates/events mentioned.")
    pre_mortem: str = Field(..., description="Specific failure condition.")
    mosaic_data_points: List[str] = Field(..., description="Alt-data validation ideas.")
    decision: str = Field(..., description="PASS or INVESTIGATE")

class ScoreResponse(BaseModel):
    verdict: str = Field(..., description="STRONG, WEAK, or NEUTRAL")
    confidence_score: int = Field(..., description="0-100% confidence based on text availability.")
    thesis_logic: DimensionScore
    catalyst_quality: DimensionScore
    risk_analysis: DimensionScore
    professional_standards: DimensionScore
    pm_perspective: PMPerspective
    improvement_plan: List[str]

# --- 2. THE SCORER ENGINE ---
class EquityScorer:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.prompts = PromptManager()  # <--- Initialize Manager

    def evaluate(self, text: str, filename: str) -> Optional[dict]:
        truncated_text = text[:50000]

        # <--- LOAD FROM YAML INSTEAD OF HARDCODING
        system_prompt = self.prompts.get_prompt("equity_scorer_system")

        try:
            completion = self.client.beta.chat.completions.parse(
                model="gpt-4o-2024-08-06",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Review this research note:\n\n{truncated_text}"}
                ],
                response_format=ScoreResponse,
            )
            
            result = completion.choices[0].message.parsed.model_dump()
            
            # Deterministic Math for Overall Score
            math_score = (
                (result['thesis_logic']['score'] * 0.3) +
                (result['catalyst_quality']['score'] * 0.3) +
                (result['risk_analysis']['score'] * 0.2) +
                (result['professional_standards']['score'] * 0.2)
            )
            result['overall_score'] = round(math_score, 1)
            return result

        except Exception as e:
            print(f"❌ Scorer Error: {e}")
            return None