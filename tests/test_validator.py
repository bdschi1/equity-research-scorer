import pytest
from src.evaluation.financial_validator import FinancialValidator

# --- MOCKS ---
class MockSECClient:
    def get_latest_revenue(self, ticker):
        if ticker == "NVDA":
            return (60_000_000_000.0, 2024, "10-K") 
        return None

class MockYahooClient:
    def get_consensus(self, ticker):
        return {} 

@pytest.fixture
def validator():
    val = FinancialValidator()
    val.sec = MockSECClient()
    val.yahoo = MockYahooClient()
    return val

def test_revenue_match(validator):
    """Expect MATCH for accurate numbers"""
    text = "Nvidia reported revenue of $60 billion for fiscal year 2024."
    results = validator.validate(text, "NVDA")
    rev_check = next(r for r in results if "Revenue" in r['metric'])
    assert rev_check['status'] == "MATCH"

def test_revenue_hallucination(validator):
    """Expect MISMATCH for fake numbers"""
    text = "Nvidia reported revenue of $100 billion!"
    results = validator.validate(text, "NVDA")
    rev_check = next(r for r in results if "Revenue" in r['metric'])
    assert rev_check['status'] == "MISMATCH"
