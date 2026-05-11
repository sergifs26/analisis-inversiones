import concurrent.futures
import time
import warnings
import pandas as pd
import yfinance as yf

warnings.filterwarnings("ignore")


def fetch_company_data(ticker_symbol: str) -> dict:
    """Descarga todos los datos de Yahoo Finance en paralelo. Devuelve dict con DataFrames."""
    # Reintenta hasta 3 veces con espera si Yahoo Finance da rate limit
    for attempt in range(3):
        try:
            t = yf.Ticker(ticker_symbol)
            info = t.info
            break
        except Exception as e:
            if attempt == 2:
                raise
            time.sleep(5 * (attempt + 1))
            continue

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
    rev_est  = fr.result()
    earn_est = fe.result()

    for df in [income, balance, cashflow]:
        if df is not None and not df.empty:
            df.sort_index(axis=1, inplace=True)

    def _df(v):
        return v if v is not None else pd.DataFrame()

    return {
        "ticker":   ticker_symbol,
        "info":     info,
        "income":   _df(income),
        "balance":  _df(balance),
        "cashflow": _df(cashflow),
        "history":  _df(history),
        "rev_est":  _df(rev_est),
        "earn_est": _df(earn_est),
    }
