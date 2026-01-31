from agents.base_agent import Agent
from agents.utils import save_to_file, load_history_from_file
import json
import datetime
import os
import re


class CritiqueAgent(Agent):
    """
    Agent Critique - Evalue la qualite du rapport final et demande des corrections si necessaire.

    Criteres d'evaluation (strict):
    - Presence de toutes les sections obligatoires
    - Coherence des chiffres avec le contexte
    - Qualite de l'argumentation
    - Clarte de la recommandation
    - Presence des sources

    Si le rapport est insuffisant -> renvoie au Redacteur avec corrections.txt
    """

 
    CRITERES = {
        "sections_completes": {"poids": 20, "description": "Toutes les sections obligatoires sont presentes"},
        "chiffres_corrects": {"poids": 25, "description": "Les chiffres correspondent au contexte source"},
        "argumentation": {"poids": 20, "description": "Arguments Bull/Bear bien developpes avec donnees"},
        "recommandation_claire": {"poids": 15, "description": "La recommandation est claire et justifiee"},
        "sources_citees": {"poids": 10, "description": "Les actualites et sources sont mentionnees"},
        "coherence_globale": {"poids": 10, "description": "Le rapport est coherent et bien structure"},
    }

  
    SEUIL_VALIDATION = 50

    
    SECTIONS_OBLIGATOIRES = [
        "REPONSE DIRECTE",
        "ARGUMENTS POUR L'INVESTISSEMENT",
        "RISQUES IDENTIFIES",
        "CHIFFRES CLES",
        "DETAIL DES SCORES",
        "CONSEIL FINAL"
    ]

    def __init__(self):
        super().__init__(
            name="Critique",
            description="Expert en evaluation et controle qualite des rapports financiers.",
            modelName="mistral-nemo"
        )
        self.corrections_history = []

    def _load_file_safe(self, filepath: str) -> str:
        """Charge un fichier de maniere securisee."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return None
        except Exception as e:
            return f"Erreur: {e}"

    def _check_sections_presentes(self, rapport: str) -> dict:
        """Verifie que toutes les sections obligatoires sont presentes."""
        sections_manquantes = []
        sections_trouvees = []

        for section in self.SECTIONS_OBLIGATOIRES:
    
            if section.upper() in rapport.upper() or section in rapport:
                sections_trouvees.append(section)
            else:
                sections_manquantes.append(section)

        score = (len(sections_trouvees) / len(self.SECTIONS_OBLIGATOIRES)) * 100

        return {
            "score": score,
            "sections_trouvees": sections_trouvees,
            "sections_manquantes": sections_manquantes,
            "probleme": f"Sections manquantes: {', '.join(sections_manquantes)}" if sections_manquantes else None
        }

    def _check_chiffres_coherents(self, rapport: str, contexte: str) -> dict:
        """Verifie que les chiffres du rapport correspondent au contexte."""
        problemes = []

     
        prix_ctx = re.search(r'\*\*Prix actuel:\*\*\s*([\d.,]+)', contexte)
        cap_ctx = re.search(r'\*\*Capitalisation:\*\*\s*([\d.,\s]+)', contexte)
        pe_ctx = re.search(r'\*\*P/E \(Actuel\):\*\*\s*([\d.,]+)', contexte)

    
        chiffres_verifies = 0
        chiffres_total = 0

        if prix_ctx:
            chiffres_total += 1
            prix_val = prix_ctx.group(1).replace(',', '.')
            if prix_val in rapport or prix_ctx.group(1) in rapport:
                chiffres_verifies += 1
            else:
                problemes.append(f"Prix actuel ({prix_ctx.group(1)}$) non trouve ou different dans le rapport")

        if cap_ctx:
            chiffres_total += 1
            cap_val = cap_ctx.group(1).strip()
        
            if cap_val[:6] in rapport: 
                chiffres_verifies += 1
            else:
                problemes.append(f"Capitalisation ({cap_val}) non trouvee ou differente")

        if pe_ctx:
            chiffres_total += 1
            pe_val = pe_ctx.group(1)
            if pe_val in rapport:
                chiffres_verifies += 1
            else:
                problemes.append(f"P/E ratio ({pe_val}) non trouve ou different")

        score = (chiffres_verifies / max(chiffres_total, 1)) * 100

        return {
            "score": score,
            "chiffres_verifies": chiffres_verifies,
            "chiffres_total": chiffres_total,
            "problemes": problemes,
            "probleme": "; ".join(problemes) if problemes else None
        }

    def _evaluate_with_llm(self, rapport: str, contexte: str) -> dict:
        """Utilise le LLM pour evaluer la qualite du rapport."""
        system_prompt = """Tu es un critique STRICT de rapports financiers.

MISSION: Evaluer la qualite du rapport fourni et identifier les problemes.

CRITERES D'EVALUATION (note sur 10 chacun):
1. ARGUMENTATION: Les arguments Bull/Bear sont-ils bien developpes avec des chiffres?
2. RECOMMANDATION: La recommandation finale est-elle claire et justifiee?
3. SOURCES: Les actualites et donnees sont-elles bien citees?
4. COHERENCE: Le rapport est-il logique et bien structure?

REPONSE JSON OBLIGATOIRE:
{
    "note_argumentation": 7,
    "note_recommandation": 8,
    "note_sources": 6,
    "note_coherence": 7,
    "problemes_identifies": [
        "Probleme 1 precis",
        "Probleme 2 precis"
    ],
    "corrections_demandees": [
        "Correction 1 precise a faire",
        "Correction 2 precise a faire"
    ],
    "verdict": "VALIDE" ou "A_CORRIGER"
}

SOIS STRICT: Un bon rapport doit avoir des arguments solides avec des chiffres, pas juste des generalites.
"""

        user_prompt = f"""RAPPORT A EVALUER:
{rapport[:3000]}

CONTEXTE SOURCE (pour verification):
{contexte[:1500]}

Evalue ce rapport de maniere STRICTE."""

        response = self.callLlm(
            systemPromptInput=system_prompt,
            userPromptInput=user_prompt,
            formatJson=True,
            useHistory=False
        )

        try:
        
            clean_response = response.strip()
            if clean_response.startswith("```"):
                clean_response = re.sub(r'^```json?\n?', '', clean_response)
                clean_response = re.sub(r'\n?```$', '', clean_response)

            evaluation = json.loads(clean_response)
            return evaluation
        except json.JSONDecodeError as e:
            print(f"[Critique] Erreur parsing JSON: {e}")
            return {
                "note_argumentation": 5,
                "note_recommandation": 5,
                "note_sources": 5,
                "note_coherence": 5,
                "problemes_identifies": ["Erreur d'evaluation"],
                "corrections_demandees": [],
                "verdict": "A_CORRIGER"
            }

    def _calculate_score_global(self, check_sections: dict, check_chiffres: dict, eval_llm: dict) -> float:
        """Calcule le score global pondere."""
        scores = {
            "sections_completes": check_sections["score"],
            "chiffres_corrects": check_chiffres["score"],
            "argumentation": eval_llm.get("note_argumentation", 5) * 10,
            "recommandation_claire": eval_llm.get("note_recommandation", 5) * 10,
            "sources_citees": eval_llm.get("note_sources", 5) * 10,
            "coherence_globale": eval_llm.get("note_coherence", 5) * 10,
        }

        score_pondere = 0
        for critere, info in self.CRITERES.items():
            score_pondere += (scores.get(critere, 50) * info["poids"]) / 100

        return round(score_pondere, 1)

    def _generate_corrections_file(self, check_sections: dict, check_chiffres: dict, eval_llm: dict, score_global: float) -> str:
        """Genere le contenu du fichier corrections.txt."""
        current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

        corrections = f"""# CORRECTIONS DEMANDEES PAR L'AGENT CRITIQUE
Date: {current_date}
Score du rapport: {score_global}/100 (Seuil: {self.SEUIL_VALIDATION}/100)
Verdict: {"VALIDE" if score_global >= self.SEUIL_VALIDATION else "A CORRIGER"}

---

## PROBLEMES IDENTIFIES

### 1. Sections du rapport
"""
        if check_sections.get("probleme"):
            corrections += f"- {check_sections['probleme']}\n"
        else:
            corrections += "- OK: Toutes les sections sont presentes\n"

        corrections += "\n### 2. Coherence des chiffres\n"
        if check_chiffres.get("problemes"):
            for p in check_chiffres["problemes"]:
                corrections += f"- {p}\n"
        else:
            corrections += "- OK: Les chiffres sont coherents avec le contexte\n"

        corrections += "\n### 3. Problemes identifies par l'analyse\n"
        for probleme in eval_llm.get("problemes_identifies", []):
            corrections += f"- {probleme}\n"

        corrections += """
---

## CORRECTIONS A EFFECTUER

"""
        for i, correction in enumerate(eval_llm.get("corrections_demandees", []), 1):
            corrections += f"{i}. {correction}\n"

        if check_sections.get("sections_manquantes"):
            corrections += f"\n{len(eval_llm.get('corrections_demandees', [])) + 1}. Ajouter les sections manquantes: {', '.join(check_sections['sections_manquantes'])}\n"

        corrections += """
---

## SCORES DETAILLES

| Critere | Score |
|---------|-------|
"""
        corrections += f"| Sections completes | {check_sections['score']:.0f}/100 |\n"
        corrections += f"| Chiffres corrects | {check_chiffres['score']:.0f}/100 |\n"
        corrections += f"| Argumentation | {eval_llm.get('note_argumentation', 5)*10}/100 |\n"
        corrections += f"| Recommandation | {eval_llm.get('note_recommandation', 5)*10}/100 |\n"
        corrections += f"| Sources citees | {eval_llm.get('note_sources', 5)*10}/100 |\n"
        corrections += f"| Coherence globale | {eval_llm.get('note_coherence', 5)*10}/100 |\n"
        corrections += f"| **SCORE GLOBAL** | **{score_global}/100** |\n"

        corrections += """
---
*Fichier genere par l'Agent Critique*
"""
        return corrections

    def run(self, max_iterations: int = 3) -> dict:
        """
        Execute l'agent critique.

        Args:
            max_iterations: Nombre maximum de cycles correction/regeneration

        Returns:
            dict avec:
                - "valide": bool
                - "score": float
                - "iterations": int
                - "rapport_final": str
        """
        print(f"[Critique] Debut de l'evaluation du rapport...")

       
        rapport = self._load_file_safe("data/rapport_final.txt")
        contexte = self._load_file_safe("data/contexte.txt")

        if not rapport:
            return {"valide": False, "erreur": "Rapport non trouve", "iterations": 0}

        if not contexte:
            return {"valide": False, "erreur": "Contexte non trouve", "iterations": 0}

        iteration = 0

        while iteration < max_iterations:
            iteration += 1
            print(f"\n[Critique] === Iteration {iteration}/{max_iterations} ===")

          
            print(f"[Critique] Verification des sections...")
            check_sections = self._check_sections_presentes(rapport)

            
            print(f"[Critique] Verification des chiffres...")
            check_chiffres = self._check_chiffres_coherents(rapport, contexte)

         
            print(f"[Critique] Evaluation approfondie...")
            eval_llm = self._evaluate_with_llm(rapport, contexte)

         
            score_global = self._calculate_score_global(check_sections, check_chiffres, eval_llm)
            print(f"[Critique] Score global: {score_global}/100 (seuil: {self.SEUIL_VALIDATION})")

         
            corrections_content = self._generate_corrections_file(
                check_sections, check_chiffres, eval_llm, score_global
            )

        
            save_to_file(corrections_content, "corrections.txt", "data")
            print(f"[Critique] Corrections sauvegardees dans data/corrections.txt")

       
            if score_global >= self.SEUIL_VALIDATION:
                print(f"[Critique] RAPPORT VALIDE (score: {score_global}/100)")
                return {
                    "valide": True,
                    "score": score_global,
                    "iterations": iteration,
                    "rapport_final": rapport
                }
            else:
                print(f"[Critique] RAPPORT A CORRIGER (score: {score_global}/100)")

                if iteration < max_iterations:
                    print(f"[Critique] Demande de regeneration au Redacteur...")

                  
                    from agents.agent5_redacteur import RedacteurAgent
                    redacteur = RedacteurAgent()
                    rapport = redacteur.run_with_corrections(corrections_content)

                    print(f"[Critique] Nouveau rapport recu, re-evaluation...")
                else:
                    print(f"[Critique] Nombre max d'iterations atteint.")

  
        return {
            "valide": False,
            "score": score_global,
            "iterations": iteration,
            "rapport_final": rapport,
            "message": f"Rapport non valide apres {iteration} iterations"
        }
