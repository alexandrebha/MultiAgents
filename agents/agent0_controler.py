from agents.base_agent import Agent
import json

class ControlerAgent(Agent):
    def __init__(self):
        super().__init__(
            name="Controlleur",
            description="Filtre les demandes et extrait les tickers boursiers.",
            modelName="mistral"
        )
    
    def run(self, userInput :str) -> dict:
       
        instructions = """
        Ta mission est double :
        1. VALIDATION : Décide si la demande concerne la finance, l'économie, la bourse ou une entreprise (OUI/NON).
        2. EXTRACTION : Identifie l'entreprise mentionnée et trouve son TICKER boursier officiel.

        RÈGLES POUR LE TICKER :
        - Transforme le nom commun en symbole boursier (Ex: "Microsoft" -> "MSFT").
        - Ça marche même si c'est écrit en minuscule (ex: "apple" -> "AAPL").
        - Si c'est une entreprise française, essaie d'ajouter le suffixe .PA (ex: "Total" -> "TTE.PA", "LVMH" -> "MC.PA").
        - Si aucune entreprise n'est citée, mets null.

        EXEMPLES DE MAPPING À SUIVRE :
        - "investir sur microsoft" -> ticker: "MSFT"
        - "LVMH est-il rentable ?" -> ticker: "MC.PA"
        - "Analyse de Tesla" -> ticker: "TSLA"
        - "Cours du bitcoin" -> ticker: "BTC-USD"
        - "Google" -> ticker: "GOOGL"

        FORMAT JSON OBLIGATOIRE (Réponds uniquement le JSON) :
        {
            "decision": "OUI" ou "NON",
            "raison": "explication courte",
            "ticker": "SYMBOLE" ou null
        }
        """
        
     
        response = self.callLlm(instructions, f"Voici la demande : {userInput}", formatJson=True)

      
        try:
            if isinstance(response, dict):
                return response
            
        
            clean_response = response.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_response)
            
        except json.JSONDecodeError:
          
            return {
                "decision": "NON", 
                "raison": "Erreur technique JSON", 
                "ticker": None
            }