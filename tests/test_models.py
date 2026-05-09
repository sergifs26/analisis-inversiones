from engine.models import Multiples, Scenarios, Assumptions, AnalysisResult
import pandas as pd

def test_multiples_defaults():
    m = Multiples()
    assert m.per is None
    assert m.pfcf is None
    assert m.ev_ebitda is None
    assert m.ev_ebit is None

def test_multiples_with_values():
    m = Multiples(per=25.5, pfcf=20.0, ev_ebitda=15.3, ev_ebit=18.7)
    assert m.per == 25.5
    assert m.pfcf == 20.0

def test_scenarios_defaults():
    s = Scenarios()
    assert s.bull_3y == 0.0
    assert s.bear_5y == 0.0

def test_assumptions_defaults():
    a = Assumptions()
    assert a.growth == 0.05
    assert a.ebit_margin == 0.10
    assert a.tax_rate == 0.25

def test_analysis_result_creation():
    result = AnalysisResult(
        ticker="AAPL",
        company_name="Apple Inc.",
        sector="Technology",
        industry="Consumer Electronics",
        currency="USD",
        years=[],
        income=pd.DataFrame(),
        balance=pd.DataFrame(),
        cashflow=pd.DataFrame(),
        history=pd.DataFrame(),
        assumptions=Assumptions(),
        multiples=Multiples(),
        scenarios=Scenarios(),
        year_col={},
    )
    assert result.ticker == "AAPL"
    assert result.currency == "USD"
