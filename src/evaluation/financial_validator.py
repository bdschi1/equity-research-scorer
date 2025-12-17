import re
from dataclasses import dataclass
from typing import List, Dict, Optional
from src.data.sec_edgar import SECEdgarClient
from src.data.yahoo_finance import YahooFinanceClient

@dataclass
class FactCheck:
    metric: str
    claimed_value: str
    actual_value: str
    source: str
    status: str
    diff_pct: float

class FinancialValidator:
    def __init__(self):
        self.sec = SECEdgarClient()
        self.yahoo = YahooFinanceClient()

    def validate(self, text: str, ticker: str) -> List[Dict]:
        """
        Scans text for financial claims and cross-references them with real data.
        Returns a list of dicts.
        """
        results = []
        if not ticker:
            return []

        # --- CHECK 1: REVENUE (SEC Data) ---
        # UPDATED REGEX: Now handles "Revenue of $52B", "Revenue: $52B", "Revenue $52B"
        rev_pattern = r"revenue\s*(?:of\b)?[:\s]*\$?([\d,.]+)\s*(?:billion|B)"
        matches = re.findall(rev_pattern, text, re.IGNORECASE)
        
        if matches:
            try:
                # Take the first revenue number found (heuristic)
                claimed_raw = float(matches[0].replace(",", ""))
                claimed_rev = claimed_raw * 1e9 
                
                # Fetch Actuals
                actual_data = self.sec.get_latest_revenue(ticker) # (val, year, form)
                
                if actual_data:
                    actual_val, year, form = actual_data
                    
                    # Calculate mismatch
                    diff = (claimed_rev - actual_val) / actual_val
                    abs_diff = abs(diff)
                    
                    status = "MATCH" if abs_diff < 0.05 else "MISMATCH" # 5% tolerance
                    
                    results.append({
                        "metric": f"Revenue (FY{year})",
                        "claimed": f"${claimed_raw}B",
                        "actual": f"${actual_val/1e9:.2f}B",
                        "source": f"SEC {form}",
                        "status": status,
                        "diff_pct": round(diff * 100, 1)
                    })
            except Exception as e:
                print(f"⚠️ Revenue validation error: {e}")

        # --- CHECK 2: CONSENSUS EPS (Yahoo Data) ---
        # Pattern: "EPS of $3.50" or "EPS: $3.50"
        eps_pattern = r"EPS\s*(?:of\b)?[:\s]*\$?([\d.]+)"
        matches = re.findall(eps_pattern, text, re.IGNORECASE)
        
        if matches:
            try:
                claimed_eps = float(matches[0])
                
                # Fetch Consensus
                consensus_data = self.yahoo.get_consensus(ticker)
                actual_eps = consensus_data.get("consensus_eps")
                
                if actual_eps:
                    diff = (claimed_eps - actual_eps) / actual_eps
                    abs_diff = abs(diff)
                    
                    status = "MATCH" if abs_diff < 0.10 else "MISMATCH" # 10% tolerance for estimates
                    
                    results.append({
                        "metric": "Forward EPS (Consensus)",
                        "claimed": f"${claimed_eps}",
                        "actual": f"${actual_eps}",
                        "source": "Yahoo Analyst Consensus",
                        "status": status,
                        "diff_pct": round(diff * 100, 1)
                    })
            except Exception as e:
                print(f"⚠️ EPS validation error: {e}")
        
        return results