import pandas as pd
import pytest
from engine.calculator import (
    get_value,
    compute_assumptions,
    calculate_historical_multiples,
    build_scenarios,
    calc_buyback_pct,
    analyst_growth,
    build_year_col_map,
)
from engine.models import Assumptions, Multiples, Scenarios

DATES = pd.to_datetime(["2022-09-30", "2023-09-30", "2024-09-30"])

def make_income():
    return pd.DataFrame({
        DATES[0]: {"Total Revenue": 390000000000, "Operating Income": 119000000000,
                   "Net Income": 99000000000, "Tax Provision": 19000000000,
                   "Pretax Income": 118000000000,
                   "Diluted Average Shares": 16000000000},
        DATES[1]: {"Total Revenue": 383000000000, "Operating Income": 114000000000,
                   "Net Income": 96000000000, "Tax Provision": 17000000000,
                   "Pretax Income": 113000000000,
                   "Diluted Average Shares": 15500000000},
        DATES[2]: {"Total Revenue": 391000000000, "Operating Income": 123000000000,
                   "Net Income": 94000000000, "Tax Provision": 30000000000,
                   "Pretax Income": 124000000000,
                   "Diluted Average Shares": 15000000000},
    }).T

def make_cashflow():
    return pd.DataFrame({
        DATES[0]: {"Depreciation And Amortization": 11000000000,
                   "Operating Cash Flow": 122000000000,
                   "Capital Expenditure": -11000000000,
                   "Repurchase Of Capital Stock": -89000000000},
        DATES[1]: {"Depreciation And Amortization": 11500000000,
                   "Operating Cash Flow": 110000000000,
                   "Capital Expenditure": -11000000000,
                   "Repurchase Of Capital Stock": -77000000000},
        DATES[2]: {"Depreciation And Amortization": 11700000000,
                   "Operating Cash Flow": 118000000000,
                   "Capital Expenditure": -9500000000,
                   "Repurchase Of Capital Stock": -95000000000},
    }).T

def test_get_value_finds_first_key():
    df = make_income()
    val = get_value(df, ["Total Revenue", "Revenue"], DATES[0])
    assert val == 390000000000.0

def test_get_value_returns_none_for_missing():
    df = make_income()
    val = get_value(df, ["NonExistentKey"], DATES[0])
    assert val is None

def test_compute_assumptions_returns_valid_values():
    income = make_income()
    cashflow = make_cashflow()
    assumptions = compute_assumptions(income, cashflow, list(DATES))
    assert 0.0 < assumptions.ebit_margin < 1.0
    assert 0.0 < assumptions.tax_rate < 1.0
    assert -0.5 < assumptions.growth < 2.0

def test_build_scenarios_with_analyst_targets():
    info = {
        "currentPrice": 293.0,
        "targetLowPrice": 200.0,
        "targetMeanPrice": 350.0,
        "targetHighPrice": 500.0,
    }
    scenarios = build_scenarios(info, growth=0.08)
    assert scenarios.bull_3y > scenarios.mid_3y > scenarios.bear_3y
    assert scenarios.bull_5y > scenarios.bull_3y

def test_build_scenarios_without_analyst_targets():
    info = {"currentPrice": 100.0}
    scenarios = build_scenarios(info, growth=0.10)
    assert scenarios.bull_3y > 100.0
    assert scenarios.bear_3y > 0.0

def test_calc_buyback_pct_returns_fraction():
    cashflow = make_cashflow()
    pct = calc_buyback_pct(cashflow, list(DATES))
    assert 0.0 < pct <= 1.5

def test_build_year_col_map_last_col_is_9():
    col_map = build_year_col_map(list(DATES))
    assert max(col_map.values()) == 9
    assert min(col_map.values()) >= 3
