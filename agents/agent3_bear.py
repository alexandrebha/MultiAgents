from agents.base_agent import Agent
import os

class BearAgent(Agent):
    def __init__(self):
        super().__init__(
            name="Bear (Pessimiste)",
            description="Analyste financier spécialisé dans la gestion des risques et la vente à découvert (Short).",
            modelName="mistral-nemo"
        )
    
    def run(self) -> str:

        try:
            with open("data/contexte.txt", "r", encoding="utf-8") as f:
                contexte = f.read()
        except FileNotFoundError:
            return "ERREUR: Le fichier contexte.txt est introuvable."

        print(f"[Bear] 📉 Recherche des signaux de VENTE (Risques)...")

       
        system_prompt = """
Tu es l'Agent BEAR (Vendeur à découvert / Gestionnaire de Risque).
Ta mission : Identifier pourquoi ce titre pourrait S'EFFONDRER ou SOUS-PERFORMER.

CONSIGNES :
1. Ignore le potentiel de rêve (l'Agent Bull s'en occupe).
2. Concentre-toi UNIQUEMENT sur les points faibles et les dangers :
   - Valorisation excessive (Bulle, P/E trop haut).
   - Ralentissement de la croissance ou marges en baisse.
   - Dette élevée ou problèmes de liquidité (Ratio de liquidité < 1).
   - Concurrence féroce, régulation, procès ou mauvaises nouvelles.
   - Ventes d'initiés ou dilution des actions.

FORMAT DE RÉPONSE ATTENDU (Markdown) :
## ⚠️ ARGUMENTS CONTRE L'ACHAT (THÈSE BEAR)
- **Risque Majeur 1** : Explication chiffrée.
- **Risque Majeur 2** : Explication chiffrée.
- **Risque Majeur 3** : Explication chiffrée.
- **Conclusion Bear** : Une phrase résumant le danger de baisse.
"""
        
        
        response = self.callLlm(
            systemPromptInput=system_prompt,
            userPromptInput=f"Voici les données de l'entreprise :\n{contexte}",
            formatJson=False,
            useHistory=False
        )
        
        return response