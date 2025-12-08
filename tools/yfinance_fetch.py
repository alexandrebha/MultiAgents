import yfinance as yf
import json
import requests
from bs4 import BeautifulSoup

def scrape_article_content(url: str) -> str:
    """
    Télécharge le HTML de la page et extrait le texte des balises <p>.
    """
    # On se fait passer pour un vrai navigateur (Chrome sur Windows) pour ne pas être bloqué
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        # 1. On télécharge la page (timeout de 5 secondes pour pas bloquer si le site est lent)
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status() # Vérifie si on a une erreur 404 ou 403
        
        # 2. On parse le HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 3. On cherche tous les paragraphes <p>
        # C'est la balise standard pour le texte d'un article
        paragraphs = soup.find_all('p')
        
        # 4. On nettoie et on assemble le texte
        # On ignore les textes trop courts (souvent des liens ou menus pub)
        text_content = [p.get_text() for p in paragraphs if len(p.get_text()) > 50]
        full_text = " ".join(text_content)
        
        # 5. LIMITATION (Crucial pour Mistral)
        # On ne garde que les 1000 premiers caractères pour le contexte
        if len(full_text) > 1000:
            return full_text[:1000] + "... [Lire la suite sur le site]"
        return full_text

    except Exception as e:
        return f"Impossible de lire l'article : {str(e)}"


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
        url = news["content"]["canonicalUrl"].get('url')
        article_body = "Contenu non disponible."
        if url:
            article_body = scrape_article_content(url)
        clean_news.append({
            "title": news["content"].get('title'),
            "link": news["content"]["canonicalUrl"].get('url'),
            "context_article": article_body
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
    ##print(data_filtered)


data_fetcher_per_stock("NVDA")
