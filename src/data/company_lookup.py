"""
Company Lookup Module
Maps tickers to CIK numbers (for SEC) and standardizes company names.
"""
import requests
import re
from dataclasses import dataclass
from typing import Optional, Dict

@dataclass
class CompanyInfo:
    ticker: str
    cik: str
    name: str
    fiscal_year_end: str = "12-31"

class CompanyLookup:
    SEC_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
    
    def __init__(self):
        # Local cache of common tech/finance names to save API calls
        self._cache: Dict[str, CompanyInfo] = {
            "AAPL": CompanyInfo("AAPL", "0000320193", "Apple Inc.", "09-30"),
            "NVDA": CompanyInfo("NVDA", "0001045810", "NVIDIA Corporation", "01-31"),
            "MSFT": CompanyInfo("MSFT", "0000789019", "Microsoft Corporation", "06-30"),
            "GOOG": CompanyInfo("GOOG", "0001652044", "Alphabet Inc.", "12-31"),
            "GOOGL": CompanyInfo("GOOGL", "0001652044", "Alphabet Inc.", "12-31"),
            "AMZN": CompanyInfo("AMZN", "0001018724", "Amazon.com, Inc.", "12-31"),
            "TSLA": CompanyInfo("TSLA", "0001318605", "Tesla, Inc.", "12-31"),
            "META": CompanyInfo("META", "0001326801", "Meta Platforms, Inc.", "12-31"),
            "LLY":  CompanyInfo("LLY",  "0000059478", "Eli Lilly & Co", "12-31"),
        }
        self._sec_map_loaded = False

    def lookup(self, ticker: str) -> Optional[CompanyInfo]:
        """Returns metadata for a given ticker."""
        ticker = ticker.upper().strip()
        
        # 1. Check Local Cache
        if ticker in self._cache:
            return self._cache[ticker]
        
        # 2. Lazy Load SEC Database (only if needed)
        if not self._sec_map_loaded:
            self._load_sec_data()
            
        return self._cache.get(ticker)

    def extract_ticker(self, text: str) -> Optional[str]:
        """Smart Regex to find the primary ticker in a document."""
        # Priority 1: "NVIDIA (NVDA)" format
        match = re.search(r'\b[A-Z][a-zA-Z\s,\.]+\(([A-Z]{1,5})\)', text)
        if match:
            return match.group(1)
            
        # Priority 2: "Ticker: NVDA"
        match = re.search(r'(?:Ticker|Symbol)[:\s]+([A-Z]{1,5})\b', text, re.IGNORECASE)
        if match:
            return match.group(1)
            
        # Priority 3: Look for known tickers in the first 200 chars
        header = text[:500].upper()
        for known_ticker in self._cache.keys():
            # Check for standalone word (e.g. " NVDA ")
            if re.search(rf'\b{known_ticker}\b', header):
                return known_ticker
                
        return None

    def _load_sec_data(self):
        """Fetches the official SEC ticker map."""
        try:
            headers = {"User-Agent": "EquityScorerBot/1.0 (contact@example.com)"}
            resp = requests.get(self.SEC_TICKERS_URL, headers=headers, timeout=5)
            data = resp.json()
            
            for entry in data.values():
                t = entry['ticker']
                self._cache[t] = CompanyInfo(
                    ticker=t,
                    cik=str(entry['cik_str']).zfill(10),
                    name=entry['title']
                )
            self._sec_map_loaded = True
        except Exception as e:
            print(f"⚠️ Warning: Failed to load SEC ticker list: {e}")