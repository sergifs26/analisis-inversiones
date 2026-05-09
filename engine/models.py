from dataclasses import dataclass
from typing import Any, Optional
import pandas as pd


@dataclass
class Multiples:
    per: Optional[float] = None
    pfcf: Optional[float] = None
    ev_ebitda: Optional[float] = None
    ev_ebit: Optional[float] = None


@dataclass
class Scenarios:
    bull_3y: float = 0.0
    bull_5y: float = 0.0
    mid_3y: float = 0.0
    mid_5y: float = 0.0
    bear_3y: float = 0.0
    bear_5y: float = 0.0


@dataclass
class Assumptions:
    growth: float = 0.05
    ebit_margin: float = 0.10
    tax_rate: float = 0.25
    price: float = 0.0
    div_yield: float = 0.0
    buyback_pct: float = 0.50


@dataclass
class AnalysisResult:
    ticker: str
    company_name: str
    sector: str
    industry: str
    currency: str
    years: list[Any]
    income: pd.DataFrame
    balance: pd.DataFrame
    cashflow: pd.DataFrame
    history: pd.DataFrame
    assumptions: Assumptions
    multiples: Multiples
    scenarios: Scenarios
    year_col: dict[Any, int]
