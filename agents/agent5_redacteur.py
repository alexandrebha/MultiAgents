from agents.base_agent import Agent
from agents.utils import save_to_file, load_history_from_file
import json
import datetime
import os

class RedacteurAgent(Agent):
    """
    Agent Redacteur - Genere le rapport final en repondant a la question utilisateur.

    - Voie A (investissement): Utilise contexte + avis Bull/Bear/Score
    - Voie B (renseignement): Utilise uniquement le contexte
    """

    def __init__(self):
        super().__init__(
            name="Redacteur",
            description="Expert en redaction de rapports financiers clairs et structures.",
            modelName="mistral-nemo"
        )

    def _get_user_question(self) -> str:
        """Recupere la derniere question de l'utilisateur depuis l'historique du Controlleur."""
        try:
            history = load_history_from_file("history_Controlleur.json")
          
            for entry in reversed(history):
                if entry.get("role") == "user":
                    content = entry.get("content", "")
                 
                    if "Voici la demande :" in content:
                        return content.split("Voici la demande :")[1].strip()
                    elif "Voici la demande:" in content:
                        return content.split("Voici la demande:")[1].strip()
                    return content
            return "Question non trouvee"
        except Exception as e:
            return f"Erreur lecture historique: {e}"

    def _load_file_safe(self, filepath: str) -> str:
        """Charge un fichier de maniere securisee."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return None
        except Exception as e:
            return f"Erreur: {e}"

    def run(self, voie: str = "A") -> str:
        """
        Execute l'agent redacteur.

        Args:
            voie: "A" pour investissement (avec Bull/Bear/Score), "B" pour renseignement (contexte seul)
        """
        print(f"[Redacteur] Redaction du rapport final (Voie {voie})...")

        question = self._get_user_question()
        print(f"[Redacteur] Question detectee: {question[:80]}...")

     
        contexte = self._load_file_safe("data/contexte.txt")
        if not contexte:
            return "ERREUR: Le fichier contexte.txt est introuvable."

    
        avis_bull = None
        avis_bear = None
        avis_score = None

        if voie.upper() == "A":
            avis_bull = self._load_file_safe("data/avis_bull.txt")
            avis_bear = self._load_file_safe("data/avis_bear.txt")
            avis_score = self._load_file_safe("data/avis_score.txt")

            if not all([avis_bull, avis_bear, avis_score]):
                print("[Redacteur] Attention: Certains avis sont manquants, passage en mode renseignement.")
                voie = "B"

        
        if voie.upper() == "A":
            system_prompt = self._build_prompt_voie_a()
            user_content = self._build_content_voie_a(question, contexte, avis_bull, avis_bear, avis_score)
        else:
            system_prompt = self._build_prompt_voie_b()
            user_content = self._build_content_voie_b(question, contexte)

        
        rapport = self.callLlm(
            systemPromptInput=system_prompt,
            userPromptInput=user_content,
            formatJson=False,
            useHistory=False
        )

      
        current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        final_rapport = f"""# RAPPORT FINAL

**Question de l'utilisateur:** {question}
**Type d'analyse:** {"Investissement (Voie A)" if voie.upper() == "A" else "Renseignement (Voie B)"}
**Date:** {current_date}

---

{rapport}

---
*Rapport genere automatiquement par l'Agent Redacteur*
"""

    
        save_to_file(final_rapport, "rapport_final.txt", "data")
        print(f"[Redacteur] Rapport sauvegarde dans data/rapport_final.txt")

        return final_rapport

    def run_with_corrections(self, corrections: str) -> str:
        """
        Regenere le rapport en tenant compte des corrections de l'Agent Critique.

        Args:
            corrections: Contenu du fichier corrections.txt

        Returns:
            Nouveau rapport corrige
        """
        print(f"[Redacteur] Regeneration avec corrections...")

     
        question = self._get_user_question()

    
        contexte = self._load_file_safe("data/contexte.txt")
        avis_bull = self._load_file_safe("data/avis_bull.txt")
        avis_bear = self._load_file_safe("data/avis_bear.txt")
        avis_score = self._load_file_safe("data/avis_score.txt")
        ancien_rapport = self._load_file_safe("data/rapport_final.txt")

        if not contexte:
            return "ERREUR: Contexte non trouve."

        # 3. Construire le prompt avec corrections
        system_prompt = self._build_prompt_with_corrections()

        # Extraire les infos
        chiffres_cles = self._extract_key_numbers(contexte)
        actualites = self._extract_news_section(contexte)
        infos_entreprise = self._extract_company_info(contexte)

        user_content = f"""
QUESTION ORIGINALE:
"{question}"

============================================================
CORRECTIONS DEMANDEES PAR L'AGENT CRITIQUE
(Tu DOIS corriger ces problemes dans le nouveau rapport)
============================================================
{corrections}

============================================================
ANCIEN RAPPORT A CORRIGER
============================================================
{ancien_rapport[:2000] if ancien_rapport else "Non disponible"}

============================================================
DONNEES SOURCES (utiliser ces chiffres EXACTS)
============================================================

--- CHIFFRES CLES ---
{chiffres_cles}

--- INFORMATIONS ENTREPRISE ---
{infos_entreprise}

--- ARGUMENTS BULL ---
{avis_bull[:800] if avis_bull else "Non disponible"}

--- ARGUMENTS BEAR ---
{avis_bear[:800] if avis_bear else "Non disponible"}

--- SCORING ---
{avis_score[:800] if avis_score else "Non disponible"}

--- ACTUALITES ---
{actualites}

============================================================
INSTRUCTIONS
============================================================
1. Lis attentivement les CORRECTIONS DEMANDEES
2. Corrige TOUS les problemes identifies
3. Utilise les CHIFFRES EXACTS du contexte
4. Garde la meme structure mais ameliore le contenu
"""

        
        rapport = self.callLlm(
            systemPromptInput=system_prompt,
            userPromptInput=user_content,
            formatJson=False,
            useHistory=False
        )

        # 5. Ajouter l'en-tete
        current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        final_rapport = f"""# RAPPORT FINAL (Version Corrigee)

**Question de l'utilisateur:** {question}
**Type d'analyse:** Investissement (Voie A)
**Date:** {current_date}
**Statut:** Corrige suite aux remarques de l'Agent Critique

---

{rapport}

---
*Rapport corrige automatiquement par l'Agent Redacteur*
"""

     
        save_to_file(final_rapport, "rapport_final.txt", "data")
        print(f"[Redacteur] Rapport corrige sauvegarde")

        return final_rapport

    def _build_prompt_with_corrections(self) -> str:
        """Prompt pour la regeneration avec corrections."""
        return """Tu es un conseiller financier expert qui CORRIGE un rapport d'investissement.

MISSION: Regenerer un rapport AMELIORE en corrigeant les problemes identifies.

REGLES STRICTES:
1. CORRIGE tous les problemes mentionnes dans les corrections
2. Utilise les CHIFFRES EXACTS fournis (ne pas inventer)
3. Ajoute les sections manquantes si demande
4. Ameliore l'argumentation avec des donnees concretes
5. Garde le meme format de rapport

FORMAT OBLIGATOIRE DU RAPPORT:

## REPONSE DIRECTE

[RECOMMANDATION] - Score: [X.X]/10

[Conclusion en 2-3 phrases]

---

## ARGUMENTS POUR L'INVESTISSEMENT (THESE BULL)

- [Argument 1 avec chiffres EXACTS]
- [Argument 2 avec chiffres EXACTS]
- [Argument 3 avec chiffres EXACTS]

---

## RISQUES IDENTIFIES (THESE BEAR)

- [Risque 1 avec chiffres EXACTS]
- [Risque 2 avec chiffres EXACTS]
- [Risque 3 avec chiffres EXACTS]

---

## CHIFFRES CLES

- **Prix actuel:** [COPIE le prix exact] $
- **Objectif analystes:** [COPIE l'objectif exact] $ (Potentiel: +X%)
- **Capitalisation:** [COPIE la capitalisation exacte]
- **P/E Ratio:** [COPIE le P/E exact]
- **Marge Operationnelle:** [COPIE la marge exacte]%

---

## DETAIL DES SCORES (Systeme Multi-Agents)

| Critere | Note | Coefficient | Contribution |
|---------|------|-------------|--------------|
| Valorisation | X/10 | 20% | X.X |
| Croissance | X/10 | 20% | X.X |
| Rentabilite | X/10 | 15% | X.X |
| Sante Financiere | X/10 | 15% | X.X |
| Sentiment Analystes | X/10 | 10% | X.X |
| Momentum | X/10 | 10% | X.X |
| Risques | X/10 | 10% | X.X |
| **TOTAL** | | 100% | **X.X/10** |

---

## ACTUALITES RECENTES

[Resume des actualites avec liens]

---

## INFORMATIONS ENTREPRISE

- **Secteur:** [secteur]
- **Industrie:** [industrie]
- **Description:** [description]

---

## CONSEIL FINAL

[Recommandation detaillee et actionnable]

IMPORTANT: Assure-toi que TOUTES les corrections demandees sont appliquees!
"""

    def _build_prompt_voie_a(self) -> str:
        """Prompt pour la voie A (investissement avec Bull/Bear/Score)."""
        return """Tu es un conseiller financier expert qui redige un rapport d'investissement COMPLET et PROFESSIONNEL.

MISSION: Generer un rapport detaille et structure repondant a la question d'investissement.

REGLES:
- Redige en FRANCAIS
- Utilise les donnees fournies pour construire le rapport
- Sois PRECIS avec les chiffres (copie les exactement)
- Fournis une analyse COMPLETE

FORMAT OBLIGATOIRE DU RAPPORT:

## REPONSE DIRECTE

[RECOMMANDATION] - Score: [X.X]/10

[Conclusion en 2-3 phrases]

---

## ARGUMENTS POUR L'INVESTISSEMENT (THESE BULL)

- [Argument 1 avec chiffres]
- [Argument 2 avec chiffres]
- [Argument 3 avec chiffres]

---

## RISQUES IDENTIFIES (THESE BEAR)

- [Risque 1 avec chiffres]
- [Risque 2 avec chiffres]
- [Risque 3 avec chiffres]

---

## CHIFFRES CLES

- **Prix actuel:** [prix] $ | **Objectif analystes:** [target] $ (Potentiel: [+X%])
- **Capitalisation:** [market_cap]
- **P/E Ratio:** [pe_ratio]
- **Marge Operationnelle:** [marge]%
- **Croissance Revenus:** [croissance]%
- **ROE:** [roe]%

---

## DETAIL DES SCORES (Systeme Multi-Agents)

| Critere | Note | Coefficient | Contribution |
|---------|------|-------------|--------------|
| Valorisation | X/10 | 20% | X.X |
| Croissance | X/10 | 20% | X.X |
| Rentabilite | X/10 | 15% | X.X |
| Sante Financiere | X/10 | 15% | X.X |
| Sentiment Analystes | X/10 | 10% | X.X |
| Momentum | X/10 | 10% | X.X |
| Risques | X/10 | 10% | X.X |
| **TOTAL** | | 100% | **X.X/10** |

---

## ACTUALITES RECENTES

[Resume des 3-5 dernieres actualites importantes]

---

## INFORMATIONS ENTREPRISE

- **Secteur:** [secteur]
- **Industrie:** [industrie]
- **Description:** [description courte de l'activite]

---

## CONSEIL FINAL

[Paragraphe de synthese avec recommandation actionnable basee sur la question posee]
"""

    def _build_prompt_voie_b(self) -> str:
        """Prompt pour la voie B (renseignement sans analyse d'investissement)."""
        return """Tu es un analyste qui presente une entreprise.

REGLE ABSOLUE: Utilise UNIQUEMENT les chiffres fournis dans les donnees ci-dessous.
NE JAMAIS inventer ou utiliser tes connaissances pour les chiffres. Si un chiffre n'est pas dans les donnees, ecris "Non disponible".

MISSION: Reponds a la question avec les informations EXACTES du contexte.

FORMAT OBLIGATOIRE:

## En resume
[2-3 phrases repondant a la question]

## L'entreprise en bref
[Description basee sur le contexte fourni]

## Situation actuelle (CHIFFRES EXACTS DU CONTEXTE)
- Capitalisation: [COPIE le chiffre exact de market_cap]
- Prix actuel: [COPIE le chiffre exact de current_price] $
- Objectif analystes: [COPIE target_price_mean] $

## Ce qu'il faut retenir
[3-4 points cles]

## Actualites recentes
[Resume des news du contexte]
"""

    def _build_content_voie_a(self, question: str, contexte: str, bull: str, bear: str, score: str) -> str:
        """Construit le contenu utilisateur pour la voie A."""
  
        chiffres_cles = self._extract_key_numbers(contexte)
      
        actualites = self._extract_news_section(contexte)
       
        infos_entreprise = self._extract_company_info(contexte)

        return f"""
QUESTION A LAQUELLE TU DOIS REPONDRE:
"{question}"

============================================================
DONNEES FINANCIERES (A UTILISER DANS LE RAPPORT)
============================================================

--- CHIFFRES CLES (utiliser ces valeurs exactes) ---
{chiffres_cles}

--- INFORMATIONS ENTREPRISE ---
{infos_entreprise}

============================================================
ANALYSES DES AGENTS SPECIALISES
============================================================

--- THESE BULL (Arguments positifs - Agent Bull) ---
{bull if bull else "Non disponible"}

--- THESE BEAR (Risques identifies - Agent Bear) ---
{bear if bear else "Non disponible"}

--- SCORING DETAILLE (Agent Score) ---
{score if score else "Non disponible"}

============================================================
ACTUALITES RECENTES
============================================================
{actualites}

============================================================
CONTEXTE COMPLET (pour reference)
============================================================
{contexte[:3000]}

INSTRUCTIONS: Genere un rapport COMPLET et STRUCTURE en utilisant TOUTES les donnees ci-dessus.
Remplis CHAQUE section du format demande avec les vraies donnees.
"""

    def _extract_key_numbers(self, contexte: str) -> str:
        """Extrait les chiffres cles du contexte pour les mettre en evidence."""
        import re

      
        prix = re.search(r'\*\*Prix actuel:\*\*\s*([\d.,]+)\s*\$', contexte)
     
        cap = re.search(r'\*\*Capitalisation:\*\*\s*([\d.,\s]+[TBMtbm]?)', contexte)
        target = re.search(r'\*\*Cible Moyenne:\*\*\s*([\d.,]+)\s*\$', contexte)
        pe = re.search(r'\*\*P/E \(Actuel\):\*\*\s*([\d.,]+)', contexte)
      
        var_52 = re.search(r'\*\*Var\. 52 semaines:\*\*\s*([^\n]+)', contexte)
        marge_op = re.search(r'\*\*Marge Operationnelle:\*\*\s*([\d.,]+%)', contexte)
        revenus = re.search(r'\*\*Revenus Totaux:\*\*\s*([\d.,\s]+)', contexte)

        chiffres = []
        if prix:
            chiffres.append(f"- Prix actuel: {prix.group(1)} $")
        if cap:
            cap_value = cap.group(1).strip()
            chiffres.append(f"- Capitalisation: {cap_value}")
        if target:
            chiffres.append(f"- Objectif analystes: {target.group(1)} $")
        if pe:
            chiffres.append(f"- P/E ratio: {pe.group(1)}")
        if var_52:
            chiffres.append(f"- Variation 52 semaines: {var_52.group(1).strip()}")
        if marge_op:
            chiffres.append(f"- Marge operationnelle: {marge_op.group(1)}")
        if revenus:
            chiffres.append(f"- Revenus totaux: {revenus.group(1).strip()}")

        return "\n".join(chiffres) if chiffres else "Chiffres non extraits"

    def _extract_news_section(self, contexte: str) -> str:
        """Extrait la section actualites du contexte."""
        import re

       
        match = re.search(r'## 9\. ACTUALITES RECENTES ET ANALYSE\n(.*?)(?=\n---|\n### Liens|$)', contexte, re.DOTALL)
        if match:
            news_content = match.group(1).strip()
            if news_content and len(news_content) > 20:
                return news_content

    
        links_match = re.search(r'### Liens des articles sources\n(.*?)(?=\n---|$)', contexte, re.DOTALL)
        if links_match:
            return f"Liens disponibles:\n{links_match.group(1).strip()}"

        return "Actualites non trouvees dans le contexte"

    def _extract_company_info(self, contexte: str) -> str:
        """Extrait les informations sur l'entreprise du contexte."""
        import re

        nom = re.search(r'\*\*Nom:\*\*\s*(.+)', contexte)
        secteur = re.search(r'\*\*Secteur:\*\*\s*(.+)', contexte)
        industrie = re.search(r'\*\*Industrie:\*\*\s*(.+)', contexte)
        pays = re.search(r'\*\*Pays:\*\*\s*(.+)', contexte)
        employes = re.search(r'\*\*Employes:\*\*\s*(.+)', contexte)

       
        desc_match = re.search(r'## 1\. PRESENTATION DE L\'ENTREPRISE\n(.*?)(?=\n## 2\.)', contexte, re.DOTALL)
        description = ""
        if desc_match:
            description = desc_match.group(1).strip()[:500]

        infos = []
        if nom:
            infos.append(f"- Nom: {nom.group(1).strip()}")
        if secteur:
            infos.append(f"- Secteur: {secteur.group(1).strip()}")
        if industrie:
            infos.append(f"- Industrie: {industrie.group(1).strip()}")
        if pays:
            infos.append(f"- Pays: {pays.group(1).strip()}")
        if employes:
            infos.append(f"- Employes: {employes.group(1).strip()}")
        if description:
            infos.append(f"\nDescription:\n{description}")

        return "\n".join(infos) if infos else "Informations entreprise non trouvees"

    def _build_content_voie_b(self, question: str, contexte: str) -> str:
        """Construit le contenu utilisateur pour la voie B."""
       
        chiffres_cles = self._extract_key_numbers(contexte)
       
        actualites = self._extract_news_section(contexte)

        return f"""
QUESTION A LAQUELLE TU DOIS REPONDRE:
"{question}"

=== CHIFFRES CLES A UTILISER (NE PAS INVENTER) ===
{chiffres_cles}

=== ACTUALITES RECENTES ===
{actualites}

=== CONTEXTE COMPLET (informations entreprise) ===
{contexte[:2500]}

RAPPEL IMPORTANT: Utilise UNIQUEMENT les chiffres ci-dessus. Ne jamais inventer de chiffres.
"""



