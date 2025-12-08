import yfinance as yf
import json


def data_fetcher_per_stock(stockName : str):
    data = yf.Ticker(stockName)
    info = data.info
    raw_news = data.news[:3]
    clean_news = []
    history = data.history(period = "1mo")
    historySummary = history['Close'].tail(30).to_dict()
    history_clean = {str(key.date()) : value for key,value in historySummary.items()}


    financials = data.quarterly_income_stmt
        
    quarterly_results = {}
    if not financials.empty and "Net Income" in financials.index:
        # On prend la ligne "Net Income" (Bénéfice Net)
        net_income_series = financials.loc["Net Income"]
        # On garde les 4 derniers trimestres et on formate en milliards/millions pour la lisibilité
        for date, value in net_income_series.head(4).items():
            quarterly_results[str(date.date())] = f"{value / 1e6:.1f} M$" # En Millions

    
    for news in raw_news :
        clean_news.append({
            "title": news["content"].get('title'),
            "link": news["content"]["canonicalUrl"].get('url'),
        })

    dividend_rate = info.get("dividendRate") # Montant en $ par an
    dividend_yield = info.get("dividendYield") # Rendement en % (ex: 0.05 pour 5%)
    payout_ratio = info.get("payoutRatio") # % des bénéfices reversés en dividendes
    
    data_filtered = {
            "company_name": info.get("longName"),
            "current_price": info.get("currentPrice"),
            "market_cap": info.get("marketCap"),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "profit_margins": info.get("profitMargins"),
            "pe_ratio": info.get("trailingPE"), # Ratio Cours/Bénéfice
            "target_price": info.get("targetMeanPrice"),
            "recent_price_history_30_days": history_clean,
            "latest_news": clean_news,
            "net_income_quarterly": quarterly_results, # Bénéfice par trimestre
            "dividends": {
                "amount_per_share": dividend_rate, # ex: 0.16$
                "yield_percent": f"{dividend_yield * 100:.2f}%" if dividend_yield else "0%", # ex: 0.04%
                "payout_ratio": f"{payout_ratio * 100:.2f}%" if payout_ratio else "0%" # Part des bénéfices versée
            },
    }

    return json.dumps(data_filtered, indent=2, ensure_ascii=False)


data_fetcher_per_stock("NVDA")
