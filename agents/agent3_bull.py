from agents.base_agent import Agent
import os

class BullAgent(Agent):
    def __init__(self):
        super().__init__(
            name="Bull (Optimiste)",
            description="Analyste financier spécialisé dans la croissance et les opportunités d'achat.",
            modelName="mistral-nemo"
        )
    
    def run(self) -> str:
     
        try:
            with open("data/contexte.txt", "r", encoding="utf-8") as f:
                contexte = f.read()
        except FileNotFoundError:
            return "ERREUR: Le fichier contexte.txt est introuvable."

        print(f"[Bull] 📈 Recherche des signaux d'ACHAT (Growth/Value)...")

   
        system_prompt = """
Tu es l'Agent BULL (Investisseur Optimiste).
Ta mission : Identifier pourquoi ce titre pourrait EXPLOSER à la hausse.

CONSIGNES :
1. Ignore les risques (l'Agent Bear s'en occupe).
2. Concentre-toi UNIQUEMENT sur les points forts :
   - Croissance des revenus et marges élevées.
   - Avantage compétitif (Moat) et position dominante.
   - Ratios de valorisation attractifs (ex: PEG bas, P/E raisonnable pour la croissance).
   - Actualités positives et catalyseurs futurs (IA, nouveaux produits).
   - Santé financière solide (Cash flow, Trésorerie).

FORMAT DE RÉPONSE ATTENDU (Markdown) :
## 🚀 ARGUMENTS POUR L'ACHAT (THÈSE BULL)
- **Point Fort 1** : Explication chiffrée.
- **Point Fort 2** : Explication chiffrée.
- **Point Fort 3** : Explication chiffrée.
- **Conclusion Bull** : Une phrase résumant le potentiel de hausse.
"""
        
        # 3. Appel LLM
        response = self.callLlm(
            systemPromptInput=system_prompt,
            userPromptInput=f"Voici les données de l'entreprise :\n{contexte}",
            formatJson=False,
            useHistory=False
        )
        
        return response