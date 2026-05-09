from unittest.mock import patch, MagicMock
import pandas as pd
import pytest
from engine.fetcher import fetch_company_data

def make_mock_ticker(ticker_symbol="AAPL"):
    mock = MagicMock()
    mock.info = {
        "longName": "Apple Inc.",
        "sector": "Technology",
        "industry": "Consumer Electronics",
        "currency": "USD",
        "currentPrice": 293.32,
        "dividendYield": 0.0037,
        "targetLowPrice": 200.0,
        "targetMeanPrice": 350.0,
        "targetHighPrice": 500.0,
        "numberOfAnalystOpinions": 42,
    }
    dates = pd.to_datetime(["2022-09-30", "2023-09-30", "2024-09-30"])
    mock.financials = pd.DataFrame(
        {"Total Revenue": [390000000000, 383000000000, 391000000000]},
        index=["Total Revenue"],
        columns=dates,
    ).T.T
    mock.balance_sheet = pd.DataFrame()
    mock.cashflow = pd.DataFrame()
    mock.history = MagicMock(return_value=pd.DataFrame(
        {"Close": [150.0, 170.0, 190.0]},
        index=dates,
    ))
    mock.revenue_estimate = pd.DataFrame()
    mock.earnings_estimate = pd.DataFrame()
    return mock

@patch("engine.fetcher.yf.Ticker")
def test_fetch_returns_dataframes(mock_ticker_cls):
    mock_ticker_cls.return_value = make_mock_ticker()
    result = fetch_company_data("AAPL")
    assert result["info"]["longName"] == "Apple Inc."
    assert not result["income"].empty

@patch("engine.fetcher.yf.Ticker")
def test_fetch_sorts_columns_ascending(mock_ticker_cls):
    mock_ticker_cls.return_value = make_mock_ticker()
    result = fetch_company_data("AAPL")
    cols = list(result["income"].columns)
    assert cols == sorted(cols)
