from agents.agent0_controler import ControlerAgent
from agents.agent1_chercheur import ChercheurAgent
from agents.agent2_planificateur import PlanificateurAgent
from agents.agent3_bull import BullAgent
from agents.agent3_bear import BearAgent
from agents.agent4_score import ScoreAgent
from agents.agent5_redacteur import RedacteurAgent
from agents.agent6_critique import CritiqueAgent
from agents.utils import save_to_file
from agents.metrics import get_collector
import sys
import time
import re

def main():

    print("Initialisation du systeme Multi-Agents...")
    controleur = ControlerAgent()
    chercheur = ChercheurAgent()
    planificateur = PlanificateurAgent()
    bull = BullAgent()
    bear = BearAgent()
    score_agent = ScoreAgent()
    redacteur = RedacteurAgent()
    critique = CritiqueAgent()

    # Initialisation du collecteur de métriques
    metrics = get_collector()

    while True:
        try:
            print("\n" + "-"*50)
            user_input = input("Pose ta question (ou 'q' pour quitter) : ")

            if user_input.lower() in ['q', 'quit', 'exit']:
                print("Au revoir !")
                break


            print("[1/6] Analyse de la pertinence et identification...")
            metrics.start_agent("Controleur")
            resultat_controle = controleur.run(user_input)
            metrics.end_agent("Controleur")

            if resultat_controle.get("decision") == "OUI":
                print("Sujet financier valide.")


                ticker_ia = resultat_controle.get("ticker")
                ticker = None
                ticker_validated_by_user = True
                ticker_extraction_correct = True


                if ticker_ia:
                    print(f"Ticker identifie par l'IA : {ticker_ia}")
                    validation = input("   Est-ce le bon ticker ? (Tapez 'Entree' pour Oui, ou 'n' pour Non) : ").strip().lower()

                    if validation in ['n', 'non', 'no']:

                        ticker = input("   Entrez le ticker correct (ex: NVDA, MC.PA) : ").strip().upper()
                        ticker_validated_by_user = False
                        ticker_extraction_correct = False
                    else:

                        ticker = ticker_ia
                else:

                    print("Aucun ticker identifie automatiquement.")
                    ticker = input("   Quel est le ticker (ex: NVDA, TSLA) ? : ").strip().upper()
                    ticker_extraction_correct = False


                if ticker:
                    # Démarrer la collecte de métriques pour cette analyse
                    metrics.start_analysis("multi-agent", ticker, user_input)
                    metrics.set_ticker_info(ticker_ia, ticker_validated_by_user, ticker_extraction_correct)

                    print(f"[2/6] Lancement de l'Agent Chercheur sur {ticker}...")
                    start_time = time.time()

                    metrics.start_agent("Chercheur")
                    resultat_recherche = chercheur.run(ticker)
                    metrics.end_agent("Chercheur")


                    if "Impossible de recuperer" in resultat_recherche or "Erreur critique" in resultat_recherche:
                        print(f"Arret : Donnees introuvables pour {ticker}.")
                        metrics.end_agent("Chercheur", success=False, error_message="Données introuvables")
                        continue


                    print(f"[3/6] Planification de la strategie...")
                    metrics.start_agent("Planificateur")
                    strategie = planificateur.run(user_input)
                    metrics.end_agent("Planificateur")
                    metrics.set_voie(strategie)


                    if strategie == "ANALYSE_COMPLETE":
                        print(f"\nVOIE A : Analyse Investissement ({ticker})")


                        print("   [Bull] Analyse des opportunites de croissance...")
                        metrics.start_agent("Bull")
                        avis_bull = bull.run()
                        metrics.end_agent("Bull")
                        save_to_file(avis_bull, "avis_bull.txt", "data")


                        print("   [Bear] Analyse des risques et faiblesses...")
                        metrics.start_agent("Bear")
                        avis_bear = bear.run()
                        metrics.end_agent("Bear")
                        save_to_file(avis_bear, "avis_bear.txt", "data")


                        print("   [Score] Arbitrage et notation finale...")
                        metrics.start_agent("Score")
                        avis_score = score_agent.run()
                        metrics.end_agent("Score")


                        print("   [Redacteur] Generation du rapport final...")
                        metrics.start_agent("Redacteur")
                        rapport_final = redacteur.run(voie="A")
                        metrics.end_agent("Redacteur")


                        print("   [Critique] Evaluation du rapport...")
                        metrics.start_agent("Critique")
                        resultat_critique = critique.run(max_iterations=3)
                        metrics.end_agent("Critique")

                        # Enregistrer les métriques du Critique
                        validated_first = resultat_critique.get("iterations", 0) == 1 and resultat_critique.get("valide", False)
                        metrics.set_critique_info(
                            iterations=resultat_critique.get("iterations", 0),
                            final_score=resultat_critique.get("score", 0),
                            validated_first_pass=validated_first
                        )

                        # Compter les arguments Bull/Bear
                        nb_bull = len(re.findall(r'^[-•]\s', avis_bull, re.MULTILINE))
                        nb_bear = len(re.findall(r'^[-•]\s', avis_bear, re.MULTILINE))

                        # Extraire le score et la recommandation
                        score_match = re.search(r'(\d+(?:[.,]\d+)?)\s*/\s*10', avis_score)
                        score_val = float(score_match.group(1).replace(',', '.')) if score_match else 0
                        reco_match = re.search(r'(ACHAT|VENTE|CONSERVER|NEUTRE|HOLD|BUY|SELL)', avis_score, re.IGNORECASE)
                        reco = reco_match.group(1).upper() if reco_match else "N/A"

                        metrics.set_report_quality(nb_bull, nb_bear, score_val, reco)

                        if resultat_critique.get("valide"):
                            print(f"   [Critique] RAPPORT VALIDE (Score: {resultat_critique['score']}/100)")
                            print(f"   [Critique] Iterations necessaires: {resultat_critique['iterations']}")
                        else:
                            print(f"   [Critique] Rapport non optimal apres {resultat_critique['iterations']} iterations")
                            print(f"   [Critique] Score final: {resultat_critique.get('score', 'N/A')}/100")

                     
                        try:
                            with open("data/rapport_final.txt", "r", encoding="utf-8") as f:
                                rapport_final = f.read()
                        except:
                            pass

                       
                        print("\n" + "="*15 + " RAPPORT FINAL " + "="*15)
                        print(rapport_final)
                        print("="*45)

                    else:  # INFO_SIMPLE
                        print(f"\nVOIE B : Rapport Factuel ({ticker})")


                        print("   [Redacteur] Generation du rapport informatif...")
                        metrics.start_agent("Redacteur")
                        rapport_final = redacteur.run(voie="B")
                        metrics.end_agent("Redacteur")

                        # Appel du Critique pour valider le rapport informatif
                        print("   [Critique] Evaluation du rapport...")
                        metrics.start_agent("Critique")
                        resultat_critique = critique.run(max_iterations=3)
                        metrics.end_agent("Critique")

                        # Enregistrer les métriques du Critique
                        validated_first = resultat_critique.get("iterations", 0) == 1 and resultat_critique.get("valide", False)
                        metrics.set_critique_info(
                            iterations=resultat_critique.get("iterations", 0),
                            final_score=resultat_critique.get("score", 0),
                            validated_first_pass=validated_first
                        )

                        metrics.set_report_quality(0, 0, 0, "INFO_SIMPLE")

                        if resultat_critique.get("valide"):
                            print(f"   [Critique] RAPPORT VALIDE (Score: {resultat_critique['score']}/100)")
                            print(f"   [Critique] Iterations necessaires: {resultat_critique['iterations']}")
                        else:
                            print(f"   [Critique] Rapport non optimal apres {resultat_critique['iterations']} iterations")
                            print(f"   [Critique] Score final: {resultat_critique.get('score', 'N/A')}/100")

                        # Recharger le rapport corrigé si disponible
                        try:
                            with open("data/rapport_final.txt", "r", encoding="utf-8") as f:
                                rapport_final = f.read()
                        except:
                            pass

                        print("\n" + "="*15 + " RAPPORT " + "="*15)
                        print(rapport_final)
                        print("="*40)

                    end_time = time.time()
                    execution_time = round(end_time - start_time, 2)
                    print(f"\nCycle termine en {execution_time}s")

                    # Finaliser et sauvegarder les métriques
                    metrics.end_analysis()
                    metrics.save_report()
                    print("[Metrics] Métriques sauvegardées dans data/metriques.txt")

                else:
                    print("Annulation : Pas de ticker fourni.")

            else:
                print(f"REFUSE : {resultat_controle.get('raison')}")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Erreur critique dans le main : {e}")

if __name__ == "__main__":
    main()
