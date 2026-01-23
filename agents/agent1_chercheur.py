from agents.base_agent import Agent
from tools.yfinance_fetch import *
from agents.utils import save_to_file
import json

class ChercheurAgent(Agent):
    def __init__(self):
        super().__init__(
            name="Chercheur",
            description="Tu es un analyste financier expert. Ton rôle est de collecter des données et de produire une synthèse FACTUELLE.",
            modelName="mistral" # Attention: c'est souvent model_name ou modelName selon ta base_agent
        )
    
    def run(self, ticker: str) -> str:
        print(f"🕵️‍♂️ [Chercheur] Récupération des données pour {ticker}...")

        # 1. Appel de l'outil de scraping
        # Vérifie bien que cette fonction renvoie un dictionnaire ou une string
        raw_data = data_fetcher_per_stock(ticker)

        # Gestion d'erreur basique
        if isinstance(raw_data, dict) and "error" in raw_data:
             return f"❌ Impossible de récupérer les données pour {ticker}."
        
        # 2. Le Prompt "Anti-JSON"
        instructions = (
            "Tu es un analyste financier rigoureux. "
            "On va te fournir des données brutes au format JSON. "
            "Ta mission est de les TRADUIRE en un rapport TEXTUEL lisible par un humain. "
            "\n"
            "⛔ INTERDICTION FORMELLE DE RÉPONDRE EN JSON."
            "✅ RÉPONDS UNIQUEMENT EN FORMAT MARKDOWN."
            "\n"
            "STRUCTURE OBLIGATOIRE DU RAPPORT :"
            "1. ## 🏢 Identité (Nom, Prix, Secteur)"
            "2. ## 💰 Santé Financière (P/E, Dividendes, Profit)"
            "3. ## 📰 Synthèse des News (Résumé des articles fournis)"
            "4. ## 📉 Tendance (Analyse technique rapide)"
            "\n"
            "Sois précis, factuel, et utilise des listes à puces."
        )

        user_content = f"Voici les données brutes pour {ticker} :\n\n{raw_data}"

        # 3. Appel LLM avec formatJson=False (CRUCIAL)
        contexte = self.callLlm(
            systemPromptInput=instructions,
            userPromptInput=user_content,
            formatJson=False 
        )

        # 4. Sauvegarde dans le fichier partagé
        print(f"💾 [Chercheur] Enregistrement du contexte dans data/contexte.txt...")
        save_to_file(content=contexte, filename="contexte.txt", folder="data")
        
        return contexte