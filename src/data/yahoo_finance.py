"""
Yahoo Finance Client
Fetches market consensus, pricing, and forward estimates.
"""
import yfinance as yf
from typing import Optional, Dict

class YahooFinanceClient:
    def __init__(self):
        pass

    def get_consensus(self, ticker: str) -> Dict:
        """
        Fetches analyst estimates to compare against the pitch.
        Returns: { 'consensus_eps': 5.20, 'current_price': 150.00, 'target_mean': 180.00 }
        """
        result = {
            "current_price": None,
            "consensus_eps": None,
            "target_mean": None,
            "market_cap": None
        }
        
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # 1. Price Data
            result["current_price"] = info.get("currentPrice") or info.get("regularMarketPrice")
            result["market_cap"] = info.get("marketCap")
            
            # 2. Analyst Targets
            result["target_mean"] = info.get("targetMeanPrice")
            
            # 3. EPS Estimates (Forward)
            # Try to grab the basic forward EPS from info first
            result["consensus_eps"] = info.get("forwardEps")
            
            # If missing, try deeper logic (calendar year estimates)
            if not result["consensus_eps"]:
                # Sometimes yfinance moves this data structure
                try:
                    calendar = stock.calendar
                    if calendar and "Earnings" in calendar:
                        # Logic to extract estimate would go here
                        pass
                except:
                    pass
                    
        except Exception as e:
            print(f"⚠️ Yahoo Finance lookup failed for {ticker}: {e}")
            
        return result

if __name__ == "__main__":
    client = YahooFinanceClient()
    print(client.get_consensus("NVDA"))