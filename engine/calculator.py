from statistics import median
from typing import Optional
import pandas as pd
from engine.models import Assumptions, Multiples, Scenarios

DA_KEYS   = ["Depreciation And Amortization", "Depreciation Amortization Depletion",
             "Reconciled Depreciation"]
CASH_KEYS = ["Cash And Cash Equivalents", "CashAndCashEquivalents",
             "Cash Cash Equivalents And Short Term Investments"]
EBIT_KEYS = ["Operating Income", "Ebit", "EBIT"]
DEBT_KEYS = ["Total Debt", "TotalDebt"]
OPCF_KEYS = ["Operating Cash Flow", "Total Cash From Operating Activities"]
CAPEX_KEYS = ["Capital Expenditure", "CapitalExpenditures"]
BUY_KEYS  = ["Repurchase Of Capital Stock", "Common Stock Repurchased"]
SHARE_KEYS = ["Diluted Average Shares", "WeightedAverageShsDiluted"]
FIRST_COL, LAST_COL = 3, 9


def get_value(df: pd.DataFrame, keys: list, date) -> Optional[float]:
    for key in keys:
        if key in df.index:
            try:
                v = df.at[key, date]
                if v is not None and str(v) not in ("nan", "None", "NaT", ""):
                    return float(v)
            except Exception:
                pass
        if key in df.columns:
            try:
                v = df.at[date, key]
                if v is not None and str(v) not in ("nan", "None", "NaT", ""):
                    return float(v)
            except Exception:
                pass
    return None


def _safe_median(lst: list) -> Optional[float]:
    if not lst:
        return None
    return round(median(lst), 1)


def build_year_col_map(dates: list) -> dict:
    year_col = {}
    for i, d in enumerate(reversed(dates)):
        col = LAST_COL - i
        if col >= FIRST_COL:
            year_col[d] = col
    return dict(reversed(list(year_col.items())))


def compute_assumptions(income: pd.DataFrame, cashflow: pd.DataFrame,
                        dates: list) -> Assumptions:
    revenues, margins, taxes = [], [], []
    for date in dates:
        rev    = get_value(income, ["Total Revenue", "TotalRevenue"], date)
        ebit   = get_value(income, EBIT_KEYS, date)
        tax    = get_value(income, ["Tax Provision", "IncomeTaxExpense"], date)
        pretax = get_value(income, ["Pretax Income", "Income Before Tax"], date)
        if rev:
            revenues.append(rev)
        if rev and ebit:
            margins.append(ebit / rev)
        if tax and pretax and pretax > 0:
            taxes.append(abs(tax) / pretax)

    growth = 0.05
    if len(revenues) >= 2:
        n = len(revenues) - 1
        if revenues[0] > 0:
            growth = round((revenues[-1] / revenues[0]) ** (1 / n) - 1, 4)

    return Assumptions(
        growth=growth,
        ebit_margin=round(median(margins[-3:]), 4) if margins else 0.10,
        tax_rate=round(median(taxes[-3:]), 4) if taxes else 0.25,
    )


def calculate_historical_multiples(history: pd.DataFrame, income: pd.DataFrame,
                                   balance: pd.DataFrame, cashflow: pd.DataFrame,
                                   dates: list) -> Multiples:
    pe_l, pfcf_l, ev_ebitda_l, ev_ebit_l = [], [], [], []

    for date in dates:
        sub = history[history.index.date <= date.date()] if not history.empty else pd.DataFrame()
        if sub.empty:
            continue
        price  = float(sub["Close"].iloc[-1])
        shares = get_value(income, SHARE_KEYS, date)
        ni     = get_value(income, ["Net Income", "NetIncome"], date)
        ebit   = get_value(income, EBIT_KEYS, date)
        debt   = get_value(balance, DEBT_KEYS, date)
        cash   = get_value(balance, CASH_KEYS, date)
        opcf   = get_value(cashflow, OPCF_KEYS, date)
        capex  = get_value(cashflow, CAPEX_KEYS, date)
        da     = get_value(cashflow, DA_KEYS, date)

        if not price or not shares or price <= 0 or shares <= 0:
            continue

        mcap = price * shares
        ev   = mcap + (debt or 0) - (cash or 0)

        if ni and ni > 0:
            pe_l.append(mcap / ni)
        if opcf and capex:
            fcf = opcf + capex
            if fcf > 0:
                pfcf_l.append(mcap / fcf)
        if ebit is not None and da is not None:
            ebitda = ebit + abs(da)
            if ebitda > 0 and ev > 0:
                ev_ebitda_l.append(ev / ebitda)
        if ebit and ebit > 0 and ev > 0:
            ev_ebit_l.append(ev / ebit)

    return Multiples(
        per=_safe_median(pe_l),
        pfcf=_safe_median(pfcf_l),
        ev_ebitda=_safe_median(ev_ebitda_l),
        ev_ebit=_safe_median(ev_ebit_l),
    )


def build_scenarios(info: dict, growth: float) -> Scenarios:
    current = info.get("currentPrice") or info.get("regularMarketPrice") or 0
    if not current or current <= 0:
        return Scenarios()

    low  = info.get("targetLowPrice")
    mean = info.get("targetMeanPrice") or info.get("targetMedianPrice")
    high = info.get("targetHighPrice")

    t1y = {
        "bull": high  or current * (1 + max(growth * 2.0, growth + 0.08)),
        "mid":  mean  or current * (1 + growth),
        "bear": low   or current * (1 + min(growth * 0.0, -0.05)),
    }
    g = {
        "bull": max(growth * 1.5, growth + 0.05),
        "mid":  growth,
        "bear": max(growth * 0.2, 0.01),
    }

    def proj(base, rate, extra):
        return round(base * (1 + rate) ** extra, 2)

    return Scenarios(
        bull_3y=proj(t1y["bull"], g["bull"], 2),
        bull_5y=proj(t1y["bull"], g["bull"], 4),
        mid_3y=proj(t1y["mid"],  g["mid"],  2),
        mid_5y=proj(t1y["mid"],  g["mid"],  4),
        bear_3y=proj(t1y["bear"], g["bear"], 2),
        bear_5y=proj(t1y["bear"], g["bear"], 4),
    )


def calc_buyback_pct(cashflow: pd.DataFrame, dates: list) -> float:
    pcts = []
    for date in dates[-3:]:
        opcf  = get_value(cashflow, OPCF_KEYS, date)
        capex = get_value(cashflow, CAPEX_KEYS, date)
        buyb  = get_value(cashflow, BUY_KEYS, date)
        if opcf and capex:
            fcf = opcf + capex
            if fcf > 0 and buyb and abs(buyb) > 0:
                pct = abs(buyb) / fcf
                if 0 < pct < 2.0:
                    pcts.append(pct)
    return round(median(pcts), 2) if pcts else 0.50


def analyst_growth(rev_est, earn_est) -> Optional[float]:
    for df in (rev_est, earn_est):
        if df is None or df.empty:
            continue
        for period in ("+1y", "0y"):
            if period in df.index and "growth" in df.columns:
                try:
                    v = float(df.loc[period, "growth"])
                    if str(v) not in ("nan", "None") and -0.5 < v < 2.0:
                        return round(v, 4)
                except Exception:
                    pass
    return None
