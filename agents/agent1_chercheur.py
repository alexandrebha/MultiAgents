from agents.base_agent import Agent
from tools.yfinance_fetch import data_fetcher_per_stock
from agents.utils import save_to_file
import json
import datetime

class ChercheurAgent(Agent):
    def __init__(self):
        super().__init__(
            name="Chercheur",
            description="Expert en extraction de données financières.",
            modelName="mistral"
        )
    
    def _get_safe(self, data, path, default="N/A"):
        """Récupère une valeur dans un dictionnaire imbriqué sans planter."""
        try:
            keys = path.split('.')
            val = data
            for key in keys:
                if val is None: return default
                val = val.get(key)
            return val if val is not None else default
        except:
            return default

    def _format_number(self, val, suffix=""):
        """Formate proprement les chiffres si ce sont des floats."""
        if isinstance(val, (int, float)):
            return f"{val:.2f}{suffix}"
        return str(val)

    def run(self, ticker: str) -> str:
        print(f"[Chercheur] Récupération des données brutes pour {ticker}...")

   
        try:
            raw_data_json = data_fetcher_per_stock(ticker)
            data = json.loads(raw_data_json) if isinstance(raw_data_json, str) else raw_data_json
        except Exception as e:
            return f"❌ Erreur critique : {e}"

        if isinstance(data, dict) and "error" in data:
             return f"❌ Impossible de récupérer les données pour {ticker}."

        print(f"[Chercheur] Génération des parties textuelles via LLM...")

        summary_raw = data.get('business_summary', 'No summary available.')
        news_raw = data.get('latest_news', [])
        
      
        news_list_txt = ""
        count = 0
        for n in news_raw:
            content = n.get('context_article', '')
            title = n.get('title', 'Sans titre')
            link = n.get('link', '')

        
            if not content or "Error" in content or "403" in content or len(content) < 50:
             
                news_list_txt += f"ARTICLE {count+1}: {title}\nLIEN: {link}\nCONTENU: (Contenu non accessible - utilise le titre pour resumer)\n\n"
            else:
              
                news_list_txt += f"ARTICLE {count+1}: {title}\nLIEN: {link}\nCONTENU: {content[:500]}...\n\n"

            count += 1
            if count >= 5: break  

        if not news_list_txt:
            news_list_txt = "Aucune actualite disponible."

        
        prompt_text = f"""
Ta tache est de traiter les textes ci-dessous EN FRANCAIS.

FORMAT DE REPONSE OBLIGATOIRE:
[Traduction complete du resume d'activite en francais]
|||SEP|||
[Resume de CHAQUE article en francais - meme si tu n'as que le titre, fais une phrase explicative]

REGLES:
- Traduis TOUT en francais
- Pour les articles sans contenu, deduis le sujet a partir du titre
- Inclus le lien de chaque article
- Fais des resumes de 2-3 phrases par article

--- DONNEES A TRAITER ---
RESUME D'ACTIVITE A TRADUIRE:
"{summary_raw}"

ACTUALITES A RESUMER (5 articles):
{news_list_txt}
"""
     
        llm_response = self.callLlm(
            systemPromptInput="Tu es un assistant de synthèse financière. Tu respectes strictement le format demandé.",
            userPromptInput=prompt_text,
            formatJson=False,
            useHistory=False
        )

     
        separator = "|||SEP|||"
        if separator in llm_response:
            parts = llm_response.split(separator)
            traduction_activite = parts[0].replace("FORMAT DE RÉPONSE ATTENDU :", "").strip()
            synthese_news = parts[1].strip()
        else:
          
            print("[Chercheur] Le LLM n'a pas utilise le separateur. Recuperation en cours...")
            traduction_activite = llm_response
            synthese_news = "Voir la description ci-dessus pour les informations sur les actualites."

      
        traduction_activite = traduction_activite.replace('Traduction du résumé :', '').strip('" ')

     
        print(f"[Chercheur] Assemblage du rapport structuré...")
        d = data 
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        
        final_report = f"""# RAPPORT D'ANALYSE: {self._get_safe(d, 'company_name')} ({ticker})

## 1. PRESENTATION DE L'ENTREPRISE
- **Nom complet:** {self._get_safe(d, 'company_name')}
- **Secteur:** {self._get_safe(d, 'sector')}
- **Industrie:** {self._get_safe(d, 'industry')}
- **Pays:** {self._get_safe(d, 'country')}
- **Site Web:** {self._get_safe(d, 'website')}
- **Employés:** {self._get_safe(d, 'employees')}

### Description de l'activité
{traduction_activite}

## 2. DONNEES DE MARCHE
- **Prix actuel:** {self._get_safe(d, 'current_price')} $
- **Var. 52 semaines:** {self._get_safe(d, 'fifty_two_week_low')} - {self._get_safe(d, 'fifty_two_week_high')} $
- **Moyenne 50j:** {self._format_number(self._get_safe(d, 'fifty_day_average'))} $
- **Capitalisation:** {self._get_safe(d, 'market_cap')} (Brut)
- **Beta:** {self._get_safe(d, 'beta')}

## 3. RATIOS DE VALORISATION
- **P/E (Actuel):** {self._format_number(self._get_safe(d, 'pe_ratio'))}
- **P/E (Forward):** {self._format_number(self._get_safe(d, 'forward_pe'))}
- **PEG Ratio:** {self._get_safe(d, 'peg_ratio')}
- **Price-to-Sales:** {self._format_number(self._get_safe(d, 'price_to_sales'))}
- **EV/EBITDA:** {self._format_number(self._get_safe(d, 'ev_to_ebitda'))}

## 4. RENTABILITE
- **Marge Opérationnelle:** {self._format_number(float(self._get_safe(d, 'operating_margins', 0))*100, "%")}
- **Marge Nette:** {self._format_number(float(self._get_safe(d, 'profit_margins', 0))*100, "%")}
- **ROE:** {self._format_number(float(self._get_safe(d, 'return_on_equity', 0))*100, "%")}

## 5. RESULTATS FINANCIERS
- **Revenus Totaux:** {self._get_safe(d, 'total_revenue')}
- **EBITDA:** {self._get_safe(d, 'ebitda')}
- **EPS (Trailing):** {self._get_safe(d, 'earnings_per_share')} $
- **Croissance Revenus:** {self._format_number(float(self._get_safe(d, 'revenue_growth', 0))*100, "%")}

## 6. BILAN
- **Cash Total:** {self._get_safe(d, 'total_cash')}
- **Dette Totale:** {self._get_safe(d, 'total_debt')}
- **Ratio Dette/Equity:** {self._get_safe(d, 'debt_to_equity')}

## 7. DIVIDENDES
- **Rendement (Yield):** {self._get_safe(d, 'dividends.yield_percent')}
- **Payout Ratio:** {self._get_safe(d, 'dividends.payout_ratio')}

## 8. AVIS DES ANALYSTES
- **Consensus:** {self._get_safe(d, 'recommendation').upper()}
- **Cible Moyenne:** {self._get_safe(d, 'target_price_mean')} $
- **Nb Analystes:** {self._get_safe(d, 'number_of_analysts')}

## 9. ACTUALITES RECENTES ET ANALYSE
{synthese_news}

### Liens des articles sources
{chr(10).join([f"- {n.get('title', 'Article')[:80]} : {n.get('link', '#')}" for n in d.get('latest_news', [])[:5] if n.get('link')])}

---
Rapport genere le {current_date}
"""

       
        print(f"[Chercheur] Sauvegarde dans data/contexte.txt...")
        save_to_file(content=final_report, filename="contexte.txt", folder="data")
        
        return final_report