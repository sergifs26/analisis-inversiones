from engine.fetcher import fetch_company_data
from engine.calculator import (
    compute_assumptions, calculate_historical_multiples,
    build_scenarios, calc_buyback_pct, analyst_growth, build_year_col_map
)
from engine.models import AnalysisResult, Assumptions


def run_analysis(ticker_symbol: str) -> AnalysisResult:
    """Descarga datos y calcula todos los inputs. Devuelve AnalysisResult listo para Excel y UI."""
    data = fetch_company_data(ticker_symbol)
    info     = data["info"]
    income   = data["income"]
    balance  = data["balance"]
    cashflow = data["cashflow"]
    history  = data["history"]

    if income.empty:
        raise ValueError(f"No se encontraron datos financieros para '{ticker_symbol}'")

    dates    = list(income.columns)
    year_col = build_year_col_map(dates)

    assumptions = compute_assumptions(income, cashflow, dates)
    growth_an   = analyst_growth(data["rev_est"], data["earn_est"])

    price     = info.get("currentPrice") or info.get("regularMarketPrice") or 0.0
    div_yield = info.get("dividendYield") or 0.0
    if div_yield > 0.20:
        div_yield /= 100

    assumptions.price       = round(price, 2)
    assumptions.div_yield   = round(div_yield, 4)
    assumptions.buyback_pct = calc_buyback_pct(cashflow, dates)
    if growth_an:
        assumptions.growth = growth_an

    multiples = calculate_historical_multiples(history, income, balance, cashflow, dates)
    scenarios = build_scenarios(info, assumptions.growth)

    return AnalysisResult(
        ticker=ticker_symbol,
        company_name=info.get("longName") or info.get("shortName") or ticker_symbol,
        sector=info.get("sector", "N/D"),
        industry=info.get("industry", "N/D"),
        currency=info.get("currency", "USD"),
        years=dates,
        income=income,
        balance=balance,
        cashflow=cashflow,
        history=history,
        assumptions=assumptions,
        multiples=multiples,
        scenarios=scenarios,
        year_col=year_col,
    )
