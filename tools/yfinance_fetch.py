import yfinance as yf
import json
import requests
from bs4 import BeautifulSoup
import os
import certifi
import shutil
import urllib3

# Désactive les warnings SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Fix pour les chemins Windows avec caractères spéciaux (é, è, etc.)
# On copie le certificat dans un chemin sans accents
def setup_ssl_certs():
    cert_path = certifi.where()
    # Chemin de destination sans caractères spéciaux
    safe_cert_dir = os.path.join(os.environ.get('TEMP', 'C:\\Temp'), 'ssl_certs')
    safe_cert_path = os.path.join(safe_cert_dir, 'cacert.pem')

    try:
        if not os.path.exists(safe_cert_dir):
            os.makedirs(safe_cert_dir)
        if not os.path.exists(safe_cert_path) or os.path.getmtime(cert_path) > os.path.getmtime(safe_cert_path):
            shutil.copy2(cert_path, safe_cert_path)

        os.environ['CURL_CA_BUNDLE'] = safe_cert_path
        os.environ['REQUESTS_CA_BUNDLE'] = safe_cert_path
        os.environ['SSL_CERT_FILE'] = safe_cert_path
        return safe_cert_path
    except Exception as e:
        print(f"⚠️ Impossible de configurer les certificats SSL: {e}")
        # Fallback: désactiver la vérification
        os.environ['CURL_CA_BUNDLE'] = ''
        return None

SSL_CERT_PATH = setup_ssl_certs()

def scrape_article_content(url: str, max_chars: int = 5000) -> str:
    """
    Télécharge le HTML de la page et extrait le contenu textuel complet.
    Récupère les paragraphes, titres et listes pour un contexte riche.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Supprimer les éléments non pertinents (scripts, styles, nav, footer, ads)
        for element in soup(['script', 'style', 'nav', 'footer', 'aside', 'header',
                            'form', 'button', 'iframe', 'noscript']):
            element.decompose()

        # Supprimer les divs de pub/cookies courants
        for div in soup.find_all(['div', 'section'], class_=lambda x: x and any(
            word in str(x).lower() for word in ['ad', 'cookie', 'banner', 'popup', 'newsletter', 'sidebar']
        )):
            div.decompose()

        # Récupérer le contenu principal (article, main, ou body)
        main_content = soup.find('article') or soup.find('main') or soup.find('body')

        if not main_content:
            main_content = soup

        # Extraire les titres (h1, h2, h3)
        titles = []
        for h in main_content.find_all(['h1', 'h2', 'h3']):
            text = h.get_text(strip=True)
            if len(text) > 10:
                titles.append(f"[{h.name.upper()}] {text}")

        # Extraire les paragraphes
        paragraphs = []
        for p in main_content.find_all('p'):
            text = p.get_text(strip=True)
            if len(text) > 30:  # Ignorer les textes trop courts
                paragraphs.append(text)

        # Extraire les listes (ul, ol)
        lists = []
        for ul in main_content.find_all(['ul', 'ol']):
            items = [li.get_text(strip=True) for li in ul.find_all('li') if len(li.get_text(strip=True)) > 20]
            if items:
                lists.append(" | ".join(items[:5]))  # Max 5 items par liste

        # Assembler le contenu
        content_parts = []

        if titles:
            content_parts.append("TITRES: " + " // ".join(titles[:3]))

        if paragraphs:
            content_parts.append("CONTENU: " + " ".join(paragraphs))

        if lists:
            content_parts.append("POINTS CLES: " + " // ".join(lists[:3]))

        full_text = "\n".join(content_parts)

        # Nettoyer les espaces multiples
        full_text = " ".join(full_text.split())

        # Limiter la taille (5000 caractères par défaut)
        if len(full_text) > max_chars:
            return full_text[:max_chars] + "... [Article tronque]"

        return full_text if full_text else "Contenu non extractible"

    except Exception as e:
        return f"Erreur scraping: {str(e)}"


def data_fetcher_per_stock(stockName : str):
    data = yf.Ticker(stockName)
  
    info = data.info
  
    raw_news = data.news[:5]  # 5 news au lieu de 3
    clean_news = []

    # Historique des prix sur 1 mois
    history = data.history(period="1mo")
    historySummary = history['Close'].tail(30).to_dict()
    history_clean = {str(key.date()): value for key, value in historySummary.items()}

    # Historique des volumes
    volume_history = history['Volume'].tail(30).to_dict()
    volume_clean = {str(key.date()): int(value) for key, value in volume_history.items()}

    # Données financières trimestrielles
    financials = data.quarterly_income_stmt
    quarterly_results = {}
    quarterly_revenue = {}

    if not financials.empty:
        if "Net Income" in financials.index:
            net_income_series = financials.loc["Net Income"]
            for date, value in net_income_series.head(4).items():
                quarterly_results[str(date.date())] = f"{value / 1e6:.1f} M$"

        if "Total Revenue" in financials.index:
            revenue_series = financials.loc["Total Revenue"]
            for date, value in revenue_series.head(4).items():
                quarterly_revenue[str(date.date())] = f"{value / 1e9:.2f} Mrd$"

    # Bilan (Balance Sheet)
    balance_sheet = data.quarterly_balance_sheet
    balance_data = {}
    if not balance_sheet.empty:
        latest = balance_sheet.iloc[:, 0]  # Dernière colonne
        balance_data = {
            "total_assets": f"{latest.get('Total Assets', 0) / 1e9:.2f} Mrd$" if latest.get('Total Assets') else None,
            "total_debt": f"{latest.get('Total Debt', 0) / 1e9:.2f} Mrd$" if latest.get('Total Debt') else None,
            "cash": f"{latest.get('Cash And Cash Equivalents', 0) / 1e9:.2f} Mrd$" if latest.get('Cash And Cash Equivalents') else None,
            "total_equity": f"{latest.get('Stockholders Equity', 0) / 1e9:.2f} Mrd$" if latest.get('Stockholders Equity') else None,
        }

    # Cash Flow
    cashflow = data.quarterly_cashflow
    cashflow_data = {}
    if not cashflow.empty:
        latest_cf = cashflow.iloc[:, 0]
        cashflow_data = {
            "operating_cashflow": f"{latest_cf.get('Operating Cash Flow', 0) / 1e9:.2f} Mrd$" if latest_cf.get('Operating Cash Flow') else None,
            "free_cashflow": f"{latest_cf.get('Free Cash Flow', 0) / 1e9:.2f} Mrd$" if latest_cf.get('Free Cash Flow') else None,
            "capex": f"{latest_cf.get('Capital Expenditure', 0) / 1e9:.2f} Mrd$" if latest_cf.get('Capital Expenditure') else None,
        }

    # News
    for news in raw_news:
        url = news["content"]["canonicalUrl"].get('url')
        article_body = "Contenu non disponible."
        if url:
            article_body = scrape_article_content(url)
        clean_news.append({
            "title": news["content"].get('title'),
            "link": news["content"]["canonicalUrl"].get('url'),
            "context_article": article_body
        })

    # Recommandations des analystes
    recommendations = {}
    try:
        reco = data.recommendations
        if reco is not None and not reco.empty:
            latest_reco = reco.tail(5).to_dict('records')
            recommendations = latest_reco
    except:
        recommendations = {}

    # Dividendes
    dividend_rate = info.get("dividendRate")
    dividend_yield = info.get("dividendYield")
    payout_ratio = info.get("payoutRatio")

    data_filtered = {
        # === IDENTITE ===
        "company_name": info.get("longName"),
        "ticker": stockName,
        "sector": info.get("sector"),
        "industry": info.get("industry"),
        "country": info.get("country"),
        "website": info.get("website"),
        "employees": info.get("fullTimeEmployees"),
        "business_summary": info.get("longBusinessSummary"),  # Description complete

        # === PRIX & MARCHE ===
        "current_price": info.get("currentPrice"),
        "previous_close": info.get("previousClose"),
        "open_price": info.get("open"),
        "day_high": info.get("dayHigh"),
        "day_low": info.get("dayLow"),
        "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
        "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
        "fifty_day_average": info.get("fiftyDayAverage"),
        "two_hundred_day_average": info.get("twoHundredDayAverage"),
        "market_cap": info.get("marketCap"),
        "enterprise_value": info.get("enterpriseValue"),
        "volume": info.get("volume"),
        "average_volume": info.get("averageVolume"),
        "beta": info.get("beta"),  # Volatilite par rapport au marche

        # === VALORISATION ===
        "pe_ratio": info.get("trailingPE"),
        "forward_pe": info.get("forwardPE"),
        "peg_ratio": info.get("pegRatio"),  # PE / Croissance
        "price_to_book": info.get("priceToBook"),
        "price_to_sales": info.get("priceToSalesTrailing12Months"),
        "ev_to_revenue": info.get("enterpriseToRevenue"),
        "ev_to_ebitda": info.get("enterpriseToEbitda"),

        # === RENTABILITE ===
        "profit_margins": info.get("profitMargins"),
        "operating_margins": info.get("operatingMargins"),
        "gross_margins": info.get("grossMargins"),
        "return_on_equity": info.get("returnOnEquity"),  # ROE
        "return_on_assets": info.get("returnOnAssets"),  # ROA

        # === CROISSANCE ===
        "revenue_growth": info.get("revenueGrowth"),
        "earnings_growth": info.get("earningsGrowth"),
        "earnings_quarterly_growth": info.get("earningsQuarterlyGrowth"),

        # === DIVIDENDES ===
        "dividends": {
            "amount_per_share": dividend_rate,
            "yield_percent": f"{dividend_yield * 100:.2f}%" if dividend_yield else "0%",
            "payout_ratio": f"{payout_ratio * 100:.2f}%" if payout_ratio else "0%",
            "ex_dividend_date": str(info.get("exDividendDate")) if info.get("exDividendDate") else None,
        },

        # === ANALYSTES ===
        "target_price_low": info.get("targetLowPrice"),
        "target_price_mean": info.get("targetMeanPrice"),
        "target_price_high": info.get("targetHighPrice"),
        "recommendation": info.get("recommendationKey"),  # buy, hold, sell
        "number_of_analysts": info.get("numberOfAnalystOpinions"),
        "analyst_recommendations": recommendations,

        # === DONNEES FINANCIERES ===
        "total_revenue": info.get("totalRevenue"),
        "revenue_per_share": info.get("revenuePerShare"),
        "ebitda": info.get("ebitda"),
        "net_income_to_common": info.get("netIncomeToCommon"),
        "earnings_per_share": info.get("trailingEps"),
        "forward_eps": info.get("forwardEps"),
        "book_value": info.get("bookValue"),
        "total_cash": info.get("totalCash"),
        "total_debt": info.get("totalDebt"),
        "debt_to_equity": info.get("debtToEquity"),
        "current_ratio": info.get("currentRatio"),
        "quick_ratio": info.get("quickRatio"),

        # === HISTORIQUES ===
        "recent_price_history_30_days": history_clean,
        "recent_volume_history_30_days": volume_clean,
        "net_income_quarterly": quarterly_results,
        "revenue_quarterly": quarterly_revenue,
        "balance_sheet": balance_data,
        "cashflow": cashflow_data,

        # === NEWS ===
        "latest_news": clean_news,
    }

    return json.dumps(data_filtered, indent=2, ensure_ascii=False)
    ##print(data_filtered)


if __name__ == "__main__":
    data_fetcher_per_stock("NVDA")
