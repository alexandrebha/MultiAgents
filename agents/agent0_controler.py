from agents.base_agent import Agent
import json

class ControlerAgent(Agent):
    def __init__(self):
        super().__init__(
            name="Controlleur",
            description="Tu es un controlleur strict. Tu vas filtrer les questions pour ne laisser passer que les questions liés à la finance, l'économie ou bien l'investissement",
            modelName="mistral"
        )
    
    def run(self, userInput :str) -> dict:
        instructions = (
            "Analyse la demande de l'utilisateur. "
            "Ton objectif est de décider si cette demande concerne l'analyse financière, la bourse ou les entreprises. "
            "\n"
            "RÈGLES :"
            "- Si ça parle d'actions (Apple, Nvidia...), de marché, d'économie : Réponds OUI."
            "- Si ça parle de code, de recette de cuisine, de météo ou de politesse simple : Réponds NON."
            "\n"
            "Tu dois répondre UNIQUEMENT avec ce format JSON exact :"
            "{\"decision\": \"OUI\", \"raison\": \"explication courte\"}"
            "ou"
            "{\"decision\": \"NON\", \"raison\": \"explication courte\"}"
        )
        response = self.callLlm(instructions,f"Voici la demande : {userInput}", formatJson=True)


        # 3. CORRECTION ET PARSING (La partie importante)
        
        # Si c'est déjà un dictionnaire, tout va bien
        if isinstance(response, dict):
            return response
            
        # Si c'est une string, on doit la nettoyer et la convertir
        try:
            # Nettoyage : Parfois le LLM répond ```json ... ```, on enlève ça
            clean_response = response.replace("```json", "").replace("```", "").strip()
            
            # Conversion String -> Dictionnaire
            return json.loads(clean_response)
            
        except json.JSONDecodeError:
            # Si le LLM a vraiment mal répondu et que ce n'est pas du JSON
            print(f"⚠️ Erreur de parsing JSON. Réponse reçue : {response}")
            # On renvoie un dictionnaire de sécurité pour ne pas faire planter le main
            return {"decision": "NON", "raison": "Erreur technique du modèle (JSON invalide)"}
