from langchain_ollama import ChatOllama
from langchain.messages import HumanMessage
from langchain_core.messages import SystemMessage
from tools.yfinance_fetch import data_fetcher_per_stock
from agents.metrics import get_collector
import json
import datetime
import re
import time


class MonoAgent:
    """
    Agent unique qui fait tout le travail du système multi-agents:
    - Extraction du ticker
    - Récupération des données Yahoo Finance
    - Analyse complète (Bull + Bear + Score)
    - Génération du rapport final

    But: Comparer les performances avec le système multi-agents
    """

    def __init__(self, modelName: str = "mistral-nemo"):
        self.name = "MonoAgent"
        self.model = ChatOllama(model=modelName)
        print(f"[MonoAgent] Initialisé avec le modèle {modelName}")

    def _call_llm(self, system_prompt: str, user_prompt: str, format_json: bool = False) -> str:
        """Appelle le LLM avec les prompts fournis."""
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]

        if format_json:
            response = self.model.bind(format="json").invoke(messages)
        else:
            response = self.model.invoke(messages)

        return response.content

    def _extract_ticker(self, user_question: str) -> dict:
        """Extrait le ticker de la question utilisateur."""
        print(f"[MonoAgent] Extraction du ticker...")

        system_prompt = """
        Tu es un expert en identification de tickers boursiers.

        RÈGLES:
        - Transforme le nom d'entreprise en symbole boursier (Ex: "Microsoft" -> "MSFT")
        - Pour les entreprises françaises, ajoute .PA (ex: "Total" -> "TTE.PA", "LVMH" -> "MC.PA")
        - Si aucune entreprise n'est citée, mets null

        EXEMPLES:
        - "investir sur microsoft" -> ticker: "MSFT"
        - "LVMH est-il rentable ?" -> ticker: "MC.PA"
        - "Tesla" -> ticker: "TSLA"
        - "Google" -> ticker: "GOOGL"

        FORMAT JSON OBLIGATOIRE:
        {
            "ticker": "SYMBOLE" ou null,
            "raison": "explication courte"
        }
        """

        response = self._call_llm(system_prompt, f"Question: {user_question}", format_json=True)

        try:
            clean_response = response.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_response)
        except json.JSONDecodeError:
            return {"ticker": None, "raison": "Erreur de parsing"}

    def _fetch_financial_data(self, ticker: str) -> dict:
        """Récupère les données financières depuis Yahoo Finance."""
        print(f"[MonoAgent] Récupération des données pour {ticker}...")

        try:
            raw_data_json = data_fetcher_per_stock(ticker)
            data = json.loads(raw_data_json) if isinstance(raw_data_json, str) else raw_data_json
            return data
        except Exception as e:
            print(f"[MonoAgent] Erreur lors de la récupération: {e}")
            return {"error": str(e)}

    def _translate_and_summarize(self, data: dict) -> dict:
        """Traduit et résume les informations de l'entreprise."""
        print(f"[MonoAgent] Traduction et résumé des données...")

        summary_raw = data.get('business_summary', 'Aucune description disponible.')
        news_raw = data.get('latest_news', [])

        
        news_list_txt = ""
        for idx, n in enumerate(news_raw[:5], 1):
            title = n.get('title', 'Sans titre')
            content = n.get('context_article', '')
            link = n.get('link', '')

            if content and len(content) > 50 and "Error" not in content:
                news_list_txt += f"ARTICLE {idx}: {title}\nCONTENU: {content[:500]}...\n\n"
            else:
                news_list_txt += f"ARTICLE {idx}: {title}\n(Contenu non accessible)\n\n"

        if not news_list_txt:
            news_list_txt = "Aucune actualité disponible."

   
        system_prompt = """Tu es un assistant de synthèse financière.

        FORMAT DE REPONSE:
        [Traduction du résumé d'activité en français]
        |||SEP|||
        [Résumé des actualités en français - 2-3 phrases par article]
        """

        user_prompt = f"""
        RESUME D'ACTIVITE A TRADUIRE:
        "{summary_raw}"

        ACTUALITES A RESUMER:
        {news_list_txt}
        """

        llm_response = self._call_llm(system_prompt, user_prompt, format_json=False)

        # Parser la réponse
        separator = "|||SEP|||"
        if separator in llm_response:
            parts = llm_response.split(separator)
            traduction_activite = parts[0].strip()
            synthese_news = parts[1].strip()
        else:
            traduction_activite = llm_response
            synthese_news = "Actualités incluses dans la description."

        return {
            "description": traduction_activite,
            "news_summary": synthese_news
        }

    def _format_number(self, val, suffix=""):
        """Formate les nombres."""
        if isinstance(val, (int, float)):
            return f"{val:.2f}{suffix}"
        return str(val) if val is not None else "N/A"

    def _analyze_complete(self, data: dict, translated: dict) -> str:
        """Fait l'analyse complète (Bull + Bear + Score + Recommandation)."""
        print(f"[MonoAgent] Analyse complète en cours...")

        # Préparer un contexte résumé
        d = data
        context_summary = f"""
        ENTREPRISE: {d.get('company_name', 'N/A')} ({d.get('ticker', 'N/A')})
        SECTEUR: {d.get('sector', 'N/A')}

        DESCRIPTION: {translated['description'][:500]}

        PRIX ACTUEL: {d.get('current_price')} $
        CAPITALISATION: {d.get('market_cap')}

        RATIOS DE VALORISATION:
        - P/E (Actuel): {self._format_number(d.get('pe_ratio'))}
        - P/E (Forward): {self._format_number(d.get('forward_pe'))}
        - PEG Ratio: {self._format_number(d.get('peg_ratio'))}
        - Price-to-Sales: {self._format_number(d.get('price_to_sales'))}

        RENTABILITE:
        - Marge Opérationnelle: {self._format_number(float(d.get('operating_margins', 0))*100, "%")}
        - Marge Nette: {self._format_number(float(d.get('profit_margins', 0))*100, "%")}
        - ROE: {self._format_number(float(d.get('return_on_equity', 0))*100, "%")}

        CROISSANCE:
        - Revenus: {self._format_number(float(d.get('revenue_growth', 0))*100, "%")}
        - Bénéfices: {self._format_number(float(d.get('earnings_growth', 0))*100, "%")}

        BILAN:
        - Cash Total: {d.get('total_cash')}
        - Dette Totale: {d.get('total_debt')}
        - Ratio Dette/Equity: {self._format_number(d.get('debt_to_equity'))}

        ANALYSTES:
        - Consensus: {d.get('recommendation', 'N/A').upper()}
        - Cible Moyenne: {d.get('target_price_mean')} $
        - Nb Analystes: {d.get('number_of_analysts')}

        ACTUALITES:
        {translated['news_summary'][:800]}
        """

        system_prompt = """Tu es un analyste financier expert qui doit faire une analyse COMPLETE d'un investissement.

        Tu dois analyser 3 dimensions:

        1. THESE BULL (Points Positifs):
           - Croissance et marges
           - Avantages compétitifs
           - Valorisation attractive
           - Catalyseurs positifs

        2. THESE BEAR (Risques):
           - Valorisation excessive
           - Ralentissement de croissance
           - Problèmes de dette ou liquidité
           - Risques concurrentiels ou réglementaires

        3. SCORING (Note sur 10 avec pondération):
           - Valorisation (20%)
           - Croissance (20%)
           - Rentabilité (15%)
           - Santé financière (15%)
           - Sentiment analystes (10%)
           - Momentum (10%)
           - Risques (10%)

        FORMAT JSON OBLIGATOIRE:
        {
          "bull_arguments": [
            "Argument bull 1 avec chiffres",
            "Argument bull 2 avec chiffres",
            "Argument bull 3 avec chiffres"
          ],
          "bear_arguments": [
            "Risque 1 avec chiffres",
            "Risque 2 avec chiffres",
            "Risque 3 avec chiffres"
          ],
          "scores": {
            "valorisation": 7,
            "croissance": 8,
            "rentabilite": 7,
            "sante_financiere": 6,
            "sentiment_analystes": 8,
            "momentum": 7,
            "risques": 6
          },
          "score_final": 7.1,
          "recommandation": "ACHAT MODERE",
          "conclusion": "Synthèse en 2-3 phrases"
        }

        IMPORTANT: Les scores doivent être des entiers de 0 à 10.
        """

        user_prompt = f"Analyse ces données financières:\n\n{context_summary}"

        response = self._call_llm(system_prompt, user_prompt, format_json=True)

        try:
            clean_response = response.strip()
            if clean_response.startswith("```"):
                clean_response = re.sub(r'^```json?\n?', '', clean_response)
                clean_response = re.sub(r'\n?```$', '', clean_response)

            analysis = json.loads(clean_response)
            return analysis
        except json.JSONDecodeError as e:
            print(f"[MonoAgent] Erreur parsing JSON: {e}")
            return {
                "bull_arguments": ["Erreur d'analyse"],
                "bear_arguments": ["Erreur d'analyse"],
                "scores": {},
                "score_final": 5.0,
                "recommandation": "INDETERMINE",
                "conclusion": "Erreur lors de l'analyse."
            }

    def _generate_final_report(self, user_question: str, ticker: str, data: dict,
                              translated: dict, analysis: dict) -> str:
        """Genere le rapport final (version simplifiee)."""
        print(f"[MonoAgent] Generation du rapport final...")

        d = data
        current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

        score_final = analysis.get('score_final', 5.0)
        recommandation = analysis.get('recommandation', 'INDETERMINE')
        conclusion = analysis.get('conclusion', '')

     
        bull_args = analysis.get('bull_arguments', [])
        bear_args = analysis.get('bear_arguments', [])

        rapport = f"""# RAPPORT MONO-AGENT

Question: {user_question}
Entreprise: {d.get('company_name')} ({ticker})
Date: {current_date}

---

RECOMMANDATION: {recommandation}
Score: {score_final:.1f}/10

{conclusion}

---

Points positifs:
{chr(10).join(['- ' + arg for arg in bull_args[:2]])}

Points negatifs:
{chr(10).join(['- ' + arg for arg in bear_args[:2]])}

---

Donnees:
- Prix: {d.get('current_price')} $
- Capitalisation: {d.get('market_cap')}
- P/E: {self._format_number(d.get('pe_ratio'))}

---

*Rapport genere par le Mono-Agent*
"""

        return rapport

    def run(self, user_question: str) -> str:
        """
        Point d'entrée principal du mono-agent.

        Args:
            user_question: Question de l'utilisateur (ex: "Faut-il investir sur NVIDIA?")

        Returns:
            Rapport d'analyse complet
        """
        print("\n" + "="*50)
        print(f"[MonoAgent] Démarrage de l'analyse...")
        print("="*50 + "\n")

        # Initialisation des métriques
        metrics = get_collector()

        # Extraction du ticker
        ticker_result = self._extract_ticker(user_question)
        ticker = ticker_result.get('ticker')

        if not ticker:
            return f"❌ Impossible d'identifier le ticker. Raison: {ticker_result.get('raison')}"

        print(f"✅ Ticker identifié: {ticker}")

        # Démarrer la collecte de métriques
        metrics.start_analysis("mono-agent", ticker, user_question)
        metrics.set_ticker_info(ticker, True, True)  # On suppose correct pour mono-agent

        # Récupération des données
        metrics.start_agent("MonoAgent_Fetch")
        data = self._fetch_financial_data(ticker)
        metrics.end_agent("MonoAgent_Fetch")

        if "error" in data:
            metrics.end_agent("MonoAgent_Fetch", success=False, error_message=data['error'])
            return f"❌ Erreur lors de la récupération des données: {data['error']}"

        print(f"✅ Données récupérées")

        # Traduction et résumé
        metrics.start_agent("MonoAgent_Translate")
        translated = self._translate_and_summarize(data)
        metrics.end_agent("MonoAgent_Translate")
        print(f"✅ Traduction et résumé terminés")

        # Analyse complète
        metrics.start_agent("MonoAgent_Analyze")
        analysis = self._analyze_complete(data, translated)
        metrics.end_agent("MonoAgent_Analyze")
        print(f"✅ Analyse complète terminée")

        # Génération du rapport
        metrics.start_agent("MonoAgent_Report")
        rapport = self._generate_final_report(user_question, ticker, data, translated, analysis)
        metrics.end_agent("MonoAgent_Report")
        print(f"✅ Rapport généré")

        # Collecter les métriques de qualité
        nb_bull = len(analysis.get('bull_arguments', []))
        nb_bear = len(analysis.get('bear_arguments', []))
        score_final = analysis.get('score_final', 0)
        recommandation = analysis.get('recommandation', 'N/A')
        metrics.set_report_quality(nb_bull, nb_bear, score_final, recommandation)

        # Sauvegarder le rapport
        try:
            import os
            os.makedirs("data", exist_ok=True)
            with open("data/rapport_mono_agent.txt", "w", encoding="utf-8") as f:
                f.write(rapport)
            print(f"✅ Rapport sauvegardé dans data/rapport_mono_agent.txt")
        except Exception as e:
            print(f"⚠️ Impossible de sauvegarder le rapport: {e}")

        # Finaliser les métriques
        metrics.end_analysis()
        metrics.save_report()
        print(f"✅ Métriques sauvegardées dans data/metriques.txt")

        print("\n" + "="*50)
        print("[MonoAgent] Analyse terminée")
        print("="*50 + "\n")

        return rapport


def main():
    """
    Point d'entrée pour tester le mono-agent.
    """
    print("="*50)
    print("     MONO-AGENT - Analyse d'Investissement")
    print("="*50)

    while True:
        try:
            print("\n" + "-"*50)
            user_input = input("🗣️  Pose ta question (ou 'q' pour quitter) : ")

            if user_input.lower() in ['q', 'quit', 'exit']:
                print("Au revoir !")
                break

    
            import time
            start_time = time.time()

            mono_agent = MonoAgent(modelName="mistral-nemo")
            rapport = mono_agent.run(user_input)

            end_time = time.time()

        
            print("\n" + "="*15 + " RAPPORT FINAL " + "="*15)
            print(rapport)
            print("="*45)
            print(f"\n⏱️ Temps d'exécution: {round(end_time - start_time, 2)}s")

        except KeyboardInterrupt:
            print("\nInterrompu par l'utilisateur.")
            break
        except Exception as e:
            print(f"❌ Erreur: {e}")


if __name__ == "__main__":
    main()