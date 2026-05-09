import concurrent.futures
import warnings
import pandas as pd
import yfinance as yf

warnings.filterwarnings("ignore")


def fetch_company_data(ticker_symbol: str) -> dict:
    """Descarga todos los datos de Yahoo Finance en paralelo. Devuelve dict con DataFrames."""
    t = yf.Ticker(ticker_symbol)
    info = t.info

    def safe(fn):
        try:
            return fn()
        except Exception:
            return None

    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
        fi = ex.submit(safe, lambda: t.financials)
        fb = ex.submit(safe, lambda: t.balance_sheet)
        fc = ex.submit(safe, lambda: t.cashflow)
        fh = ex.submit(safe, lambda: t.history(period="7y"))
        fr = ex.submit(safe, lambda: t.revenue_estimate)
        fe = ex.submit(safe, lambda: t.earnings_estimate)

    income   = fi.result()
    balance  = fb.result()
    cashflow = fc.result()
    history  = fh.result()

    for df in [income, balance, cashflow]:
        if df is not None and not df.empty:
            df.sort_index(axis=1, inplace=True)

    return {
        "ticker":   ticker_symbol,
        "info":     info,
        "income":   income   if income   is not None else pd.DataFrame(),
        "balance":  balance  if balance  is not None else pd.DataFrame(),
        "cashflow": cashflow if cashflow is not None else pd.DataFrame(),
        "history":  history  if history  is not None else pd.DataFrame(),
        "rev_est":  fr.result(),
        "earn_est": fe.result(),
    }
