"""
SEC EDGAR Client
Fetches verified financial numbers (Revenue, EPS) from official XBRL filings.
"""
import requests
import json
import time
import os
from datetime import datetime
from typing import Optional, Tuple
from src.data.company_lookup import CompanyLookup

class SECEdgarClient:
    BASE_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
    
    def __init__(self, user_agent: str = "EquityResearchBot/1.0 (internal@test.com)"):
        self.user_agent = user_agent
        self.lookup = CompanyLookup()
        
        # Auto-create a cache folder to prevent rate-limit bans
        self.cache_dir = "data/cache/sec"
        os.makedirs(self.cache_dir, exist_ok=True)

    def get_latest_revenue(self, ticker: str) -> Optional[Tuple[float, int, str]]:
        """
        Returns (Revenue_Value, Fiscal_Year, Form_Type)
        Example: (52000000000.0, 2024, '10-K')
        """
        facts = self._get_company_facts(ticker)
        if not facts: return None
        
        # Concepts to search for (GAAP Revenue)
        concepts = [
            "RevenueFromContractWithCustomerExcludingAssessedTax",
            "Revenues",
            "SalesRevenueNet"
        ]
        
        us_gaap = facts.get("facts", {}).get("us-gaap", {})
        
        best_fact = None
        
        for concept in concepts:
            if concept in us_gaap:
                # Get all annual filings (10-K)
                entries = [x for x in us_gaap[concept]["units"].get("USD", []) 
                           if x.get("form") == "10-K"]
                
                if entries:
                    # Sort by latest date
                    entries.sort(key=lambda x: x["end"], reverse=True)
                    latest = entries[0]
                    
                    # Return immediately if we found a valid 10-K number
                    return (float(latest["val"]), latest["fy"], "10-K")
                    
        return None

    def _get_company_facts(self, ticker: str) -> dict:
        """Fetches XBRL JSON with filesystem caching."""
        company = self.lookup.lookup(ticker)
        if not company:
            print(f"❌ SEC Client: Could not resolve CIK for {ticker}")
            return {}

        cik = company.cik
        cache_path = os.path.join(self.cache_dir, f"{cik}.json")
        
        # 1. Check Cache (Valid for 7 days)
        if os.path.exists(cache_path):
            mtime = os.path.getmtime(cache_path)
            if (time.time() - mtime) < (7 * 86400): 
                with open(cache_path, 'r') as f:
                    return json.load(f)

        # 2. Fetch from SEC (Rate Limited)
        url = self.BASE_URL.format(cik=cik)
        try:
            # Sleep to respect SEC 10 req/sec limit
            time.sleep(0.15) 
            resp = requests.get(url, headers={"User-Agent": self.user_agent}, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            
            # Save to cache
            with open(cache_path, 'w') as f:
                json.dump(data, f)
                
            return data
        except Exception as e:
            print(f"⚠️ SEC Fetch failed for {ticker}: {e}")
            return {}