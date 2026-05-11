import requests

# Lista predefinida: (ticker, nombre, mercado)
POPULAR_COMPANIES = [
    # IBEX 35
    ("ITX.MC", "Inditex", "IBEX 35"),
    ("SAN.MC", "Banco Santander", "IBEX 35"),
    ("BBVA.MC", "BBVA", "IBEX 35"),
    ("TEF.MC", "Telefónica", "IBEX 35"),
    ("IBE.MC", "Iberdrola", "IBEX 35"),
    ("REP.MC", "Repsol", "IBEX 35"),
    ("CABK.MC", "CaixaBank", "IBEX 35"),
    ("AMS.MC", "Amadeus IT", "IBEX 35"),
    ("FER.MC", "Ferrovial", "IBEX 35"),
    ("ACS.MC", "ACS", "IBEX 35"),
    ("IAG.MC", "IAG (Iberia)", "IBEX 35"),
    ("MAP.MC", "Mapfre", "IBEX 35"),
    ("MTS.MC", "ArcelorMittal", "IBEX 35"),
    ("CLNX.MC", "Cellnex", "IBEX 35"),
    ("ELE.MC", "Endesa", "IBEX 35"),
    ("GRF.MC", "Grifols", "IBEX 35"),
    ("COL.MC", "Inmobiliaria Colonial", "IBEX 35"),
    ("ENG.MC", "Enagás", "IBEX 35"),
    ("RED.MC", "Red Eléctrica", "IBEX 35"),
    ("ACX.MC", "Acerinox", "IBEX 35"),
    # S&P 500 — Top empresas
    ("AAPL", "Apple", "NASDAQ"),
    ("MSFT", "Microsoft", "NASDAQ"),
    ("GOOGL", "Alphabet (Google)", "NASDAQ"),
    ("AMZN", "Amazon", "NASDAQ"),
    ("NVDA", "NVIDIA", "NASDAQ"),
    ("META", "Meta (Facebook)", "NASDAQ"),
    ("TSLA", "Tesla", "NASDAQ"),
    ("BRK-B", "Berkshire Hathaway", "NYSE"),
    ("JPM", "JPMorgan Chase", "NYSE"),
    ("JNJ", "Johnson & Johnson", "NYSE"),
    ("V", "Visa", "NYSE"),
    ("PG", "Procter & Gamble", "NYSE"),
    ("MA", "Mastercard", "NYSE"),
    ("HD", "Home Depot", "NYSE"),
    ("CVX", "Chevron", "NYSE"),
    ("MRK", "Merck", "NYSE"),
    ("ABBV", "AbbVie", "NYSE"),
    ("PEP", "PepsiCo", "NASDAQ"),
    ("KO", "Coca-Cola", "NYSE"),
    ("BAC", "Bank of America", "NYSE"),
    ("WMT", "Walmart", "NYSE"),
    ("DIS", "Walt Disney", "NYSE"),
    ("NFLX", "Netflix", "NASDAQ"),
    ("ADBE", "Adobe", "NASDAQ"),
    ("CRM", "Salesforce", "NYSE"),
    ("AMD", "AMD", "NASDAQ"),
    ("INTC", "Intel", "NASDAQ"),
    ("QCOM", "Qualcomm", "NASDAQ"),
    ("PYPL", "PayPal", "NASDAQ"),
    ("UBER", "Uber", "NYSE"),
    ("ABNB", "Airbnb", "NASDAQ"),
    ("SPOT", "Spotify", "NYSE"),
    ("SHOP", "Shopify", "NYSE"),
    ("SQ", "Block (Square)", "NYSE"),
    ("COIN", "Coinbase", "NASDAQ"),
    ("PLTR", "Palantir", "NYSE"),
    ("ARM", "ARM Holdings", "NASDAQ"),
    ("TSM", "TSMC", "NYSE"),
    ("ASML", "ASML", "NASDAQ"),
    ("NVO", "Novo Nordisk", "NYSE"),
    ("SAP", "SAP", "NYSE"),
    # DAX
    ("BMW.DE", "BMW", "DAX"),
    ("VOW3.DE", "Volkswagen", "DAX"),
    ("SAP.DE", "SAP", "DAX"),
    ("SIE.DE", "Siemens", "DAX"),
    ("ALV.DE", "Allianz", "DAX"),
    ("BAS.DE", "BASF", "DAX"),
    ("BAYN.DE", "Bayer", "DAX"),
    ("MBG.DE", "Mercedes-Benz", "DAX"),
    ("DTE.DE", "Deutsche Telekom", "DAX"),
    ("DBK.DE", "Deutsche Bank", "DAX"),
    ("ADS.DE", "Adidas", "DAX"),
    ("MUV2.DE", "Munich Re", "DAX"),
    # CAC 40
    ("MC.PA", "LVMH", "CAC 40"),
    ("OR.PA", "L'Oréal", "CAC 40"),
    ("SAN.PA", "Sanofi", "CAC 40"),
    ("AIR.PA", "Airbus", "CAC 40"),
    ("BNP.PA", "BNP Paribas", "CAC 40"),
    ("TTE.PA", "TotalEnergies", "CAC 40"),
    ("SU.PA", "Schneider Electric", "CAC 40"),
    ("KER.PA", "Kering", "CAC 40"),
    ("RI.PA", "Pernod Ricard", "CAC 40"),
    ("CAP.PA", "Capgemini", "CAC 40"),
    # FTSE 100
    ("SHEL.L", "Shell", "FTSE 100"),
    ("AZN.L", "AstraZeneca", "FTSE 100"),
    ("HSBA.L", "HSBC", "FTSE 100"),
    ("ULVR.L", "Unilever", "FTSE 100"),
    ("BP.L", "BP", "FTSE 100"),
    ("RIO.L", "Rio Tinto", "FTSE 100"),
    ("GSK.L", "GSK", "FTSE 100"),
    ("VOD.L", "Vodafone", "FTSE 100"),
    ("BARC.L", "Barclays", "FTSE 100"),
    ("LLOY.L", "Lloyds Banking", "FTSE 100"),
    # ETFs populares
    ("SPY", "S&P 500 ETF (SPY)", "ETF"),
    ("QQQ", "NASDAQ 100 ETF (QQQ)", "ETF"),
    ("VTI", "Vanguard Total Market ETF", "ETF"),
    ("VOO", "Vanguard S&P 500 ETF", "ETF"),
    ("IWM", "Russell 2000 ETF", "ETF"),
    ("EWG", "iShares Germany ETF", "ETF"),
    ("EWP", "iShares Spain ETF", "ETF"),
]


def search_local(query: str) -> list[tuple[str, str, str]]:
    """Busca en la lista predefinida. Devuelve lista de (ticker, nombre, mercado)."""
    if not query or len(query) < 2:
        return []
    q = query.lower()
    results = []
    for ticker, name, market in POPULAR_COMPANIES:
        if q in ticker.lower() or q in name.lower():
            results.append((ticker, name, market))
    return results[:10]


def search_yahoo(query: str) -> list[tuple[str, str, str]]:
    """Busca en Yahoo Finance API en tiempo real. Devuelve lista de (ticker, nombre, mercado)."""
    if not query or len(query) < 2:
        return []
    try:
        url = "https://query2.finance.yahoo.com/v1/finance/search"
        params = {
            "q": query,
            "quotesCount": 10,
            "newsCount": 0,
            "enableFuzzyQuery": True,
            "quotesQueryId": "tss_match_phrase_query",
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        }
        r = requests.get(url, params=params, headers=headers, timeout=5)
        data = r.json()
        results = []
        for q in data.get("quotes", []):
            ticker = q.get("symbol", "")
            name = q.get("longname") or q.get("shortname") or ticker
            exchange = q.get("exchange") or q.get("typeDisp") or ""
            if ticker:
                results.append((ticker, name, exchange))
        return results[:10]
    except Exception:
        return []
