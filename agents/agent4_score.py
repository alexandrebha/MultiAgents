from agents.base_agent import Agent
from agents.utils import save_to_file
import json
import re

class ScoreAgent(Agent):
    """
    Agent Score avec systeme de coefficients d'importance.
    Chaque critere a un poids different dans le score final.
    """

  
    COEFFICIENTS = {
        "valorisation": 0.20,   
        "croissance": 0.20,        
        "rentabilite": 0.15,    
        "sante_financiere": 0.15, 
        "sentiment_analystes": 0.10,  
        "momentum": 0.10,          
        "risques_identifies": 0.10,   
    }

    def __init__(self):
        super().__init__(
            name="Juge (Score)",
            description="Arbitre financier avec systeme de scoring pondere.",
            modelName="mistral-nemo"
        )

    def run(self) -> str:
        print(f"[Score] Arbitrage en cours avec coefficients ponderes...")

   
        try:
            with open("data/avis_bull.txt", "r", encoding="utf-8") as f:
                avis_bull = f.read()
            with open("data/avis_bear.txt", "r", encoding="utf-8") as f:
                avis_bear = f.read()
            with open("data/contexte.txt", "r", encoding="utf-8") as f:
                contexte = f.read()
        except FileNotFoundError as e:
            return f"ERREUR: Fichier introuvable - {e}"

      
        coef_display = "\n".join([f"- {k.replace('_', ' ').title()}: {int(v*100)}%"
                                   for k, v in self.COEFFICIENTS.items()])

     
        system_prompt = f"""Tu es l'Agent SCORE, un analyste quantitatif rigoureux.

Tu dois evaluer un investissement en attribuant une NOTE DE 0 A 10 pour CHAQUE critere ci-dessous.
Chaque critere a un COEFFICIENT D'IMPORTANCE different dans le score final:

{coef_display}

=== GRILLE DE NOTATION PAR CRITERE (0-10) ===

1. VALORISATION (coef {int(self.COEFFICIENTS['valorisation']*100)}%)
   - 0-3: Tres surevalue (P/E > 50, PEG > 3)
   - 4-6: Valorisation moyenne
   - 7-10: Sous-evalue (P/E < 15, PEG < 1)

2. CROISSANCE (coef {int(self.COEFFICIENTS['croissance']*100)}%)
   - 0-3: Decroissance ou stagnation
   - 4-6: Croissance moderee (5-15%)
   - 7-10: Forte croissance (>20%)

3. RENTABILITE (coef {int(self.COEFFICIENTS['rentabilite']*100)}%)
   - 0-3: Marges negatives ou tres faibles
   - 4-6: Marges correctes (10-20%)
   - 7-10: Excellentes marges (>25%)

4. SANTE FINANCIERE (coef {int(self.COEFFICIENTS['sante_financiere']*100)}%)
   - 0-3: Dette elevee, cash faible, risque de liquidite
   - 4-6: Bilan equilibre
   - 7-10: Tresorerie solide, peu de dette

5. SENTIMENT ANALYSTES (coef {int(self.COEFFICIENTS['sentiment_analystes']*100)}%)
   - 0-3: Majorite SELL, objectif sous le prix actuel
   - 4-6: HOLD, objectif proche du prix
   - 7-10: STRONG BUY, objectif bien au-dessus

6. MOMENTUM (coef {int(self.COEFFICIENTS['momentum']*100)}%)
   - 0-3: Tendance baissiere, sous les moyennes mobiles
   - 4-6: Neutre, consolidation
   - 7-10: Tendance haussiere, au-dessus des MM

7. RISQUES IDENTIFIES (coef {int(self.COEFFICIENTS['risques_identifies']*100)}%)
   - 0-3: Risques majeurs (fraude, faillite, bulle)
   - 4-6: Risques moderes et geres
   - 7-10: Peu de risques identifies

=== FORMAT DE REPONSE OBLIGATOIRE ===

Tu DOIS repondre avec ce format JSON exact:
{{
  "scores_par_critere": {{
    "valorisation": X,
    "croissance": X,
    "rentabilite": X,
    "sante_financiere": X,
    "sentiment_analystes": X,
    "momentum": X,
    "risques_identifies": X
  }},
  "justifications": {{
    "valorisation": "Explication courte",
    "croissance": "Explication courte",
    "rentabilite": "Explication courte",
    "sante_financiere": "Explication courte",
    "sentiment_analystes": "Explication courte",
    "momentum": "Explication courte",
    "risques_identifies": "Explication courte"
  }},
  "conclusion": "Synthese en 2-3 phrases"
}}

IMPORTANT: Les valeurs X doivent etre des nombres entiers de 0 a 10.
"""

        user_content = f"""
=== DONNEES FINANCIERES (CONTEXTE) ===
{contexte[:3000]}

=== ARGUMENTATION BULL (OPTIMISTE) ===
{avis_bull}

=== ARGUMENTATION BEAR (PESSIMISTE) ===
{avis_bear}

Analyse ces donnees et attribue une note a chaque critere.
"""

      
        response = self.callLlm(
            systemPromptInput=system_prompt,
            userPromptInput=user_content,
            formatJson=True,
            useHistory=False
        )

    
        try:
           
            clean_response = response.strip()
            if clean_response.startswith("```"):
                clean_response = re.sub(r'^```json?\n?', '', clean_response)
                clean_response = re.sub(r'\n?```$', '', clean_response)

            data = json.loads(clean_response)
            scores = data.get("scores_par_critere", {})
            justifications = data.get("justifications", {})
            conclusion = data.get("conclusion", "")

        
            score_final = 0
            details = []

            for critere, coef in self.COEFFICIENTS.items():
                note = scores.get(critere, 5) 
                note = max(0, min(10, note))  
                contribution = note * coef
                score_final += contribution
                justif = justifications.get(critere, "N/A")
                details.append(f"- **{critere.replace('_', ' ').title()}**: {note}/10 (x{int(coef*100)}% = {contribution:.1f})\n  _{justif}_")

          
            if score_final <= 3:
                reco = "VENTE FORTE - DANGER"
                emoji = "🔴"
            elif score_final <= 5:
                reco = "NEUTRE / HOLD"
                emoji = "🟡"
            elif score_final <= 7:
                reco = "ACHAT MODERE"
                emoji = "🟢"
            else:
                reco = "ACHAT FORT"
                emoji = "🟢🟢"

        except (json.JSONDecodeError, KeyError) as e:
           
            print(f"[Score] Erreur parsing JSON: {e}")
            score_final = 5.0
            reco = "INDETERMINE (erreur de parsing)"
            emoji = "⚠️"
            details = [f"Reponse brute du LLM:\n{response}"]
            conclusion = "Erreur lors de l'analyse automatique."

       
        rapport = f"""# VERDICT FINAL DE L'AGENT SCORE

## {emoji} Score Global: {score_final:.1f}/10
**Recommandation: {reco}**

---

## Detail des Scores par Critere

{chr(10).join(details)}

---

## Conclusion
{conclusion}

---

### Methodologie
Le score final est calcule en ponderant chaque critere:
{coef_display}

Score = Somme(Note_critere x Coefficient)
"""

        
        save_to_file(rapport, "avis_score.txt", "data")
        print(f"[Score] Score final: {score_final:.1f}/10 - {reco}")

        return rapport