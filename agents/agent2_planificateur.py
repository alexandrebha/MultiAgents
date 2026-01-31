from agents.base_agent import Agent

class PlanificateurAgent(Agent):
    def __init__(self):
        super().__init__(
            name="Planificateur",
            description="Tu es un chef de projet. Ton rôle est d'analyser la demande de l'utilisateur pour diriger le flux de travail vers les bons experts.",
            modelName="mistral"
        )
    
    def run(self, user_question: str) -> str:
        print(f"[Planificateur] Analyse de l'intention utilisateur : '{user_question}'...")


        system_prompt = """
Tu es un routeur intelligent dans un système multi-agents financier.
Tu dois analyser la question de l'utilisateur et choisir la prochaine étape.

SCÉNARIO 1 : "INFO_SIMPLE"
L'utilisateur demande des faits bruts, des chiffres spécifiques, une description de l'entreprise ou des résultats passés. Il ne demande pas d'avis ni de prévision.
Exemples : 
- "Quel est le chiffre d'affaires de Nvidia ?"
- "Donne-moi le bilan de Tesla."
- "Qui est le CEO de Microsoft ?"
- "Résume-moi les dernières news."

SCÉNARIO 2 : "ANALYSE_COMPLETE"
L'utilisateur demande un conseil d'investissement, une opinion, une prévision future, une analyse des risques, ou demande si c'est le moment d'acheter/vendre. Il veut comprendre la dynamique (Bull vs Bear).
Exemples :
- "Est-ce que je dois investir sur Apple ?"
- "Quels sont les risques pour Nvidia ?"
- "Fais-moi une analyse complète."
- "Est-ce le bon moment pour acheter ?"
- "Bull ou Bear sur ce stock ?"

TA RÉPONSE DOIT CONTENIR UNIQUEMENT UN SEUL MOT : "INFO_SIMPLE" ou "ANALYSE_COMPLETE".
"""
        
        user_content = f"La question de l'utilisateur est : \"{user_question}\""

       
        response = self.callLlm(
            systemPromptInput=system_prompt,
            userPromptInput=user_content,
            formatJson=False,
            useHistory=False
        )

       
        decision = response.strip().upper()
        
       
        if "ANALYSE" in decision:
            decision = "ANALYSE_COMPLETE"
        elif "INFO" in decision:
            decision = "INFO_SIMPLE"
        else:
            
            print(f"[Planificateur] ⚠️ Réponse ambiguë ('{decision}'). Par défaut -> INFO_SIMPLE")
            decision = "INFO_SIMPLE"

        print(f"[Planificateur] Décision prise : {decision}")
        return decision