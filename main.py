# main.py (Version 1)
from agents.agent0_controler import ControlerAgent
from agents.agent1_chercheur import ChercheurAgent
import sys
import time

def main():
    # 1. Initialisation des Agents
    print("🤖 Initialisation du système Multi-Agents...")
    controleur = ControlerAgent()
    chercheur = ChercheurAgent() 

    # 2. Boucle d'interaction
    while True:
        try:
            print("\n" + "-"*50)
            user_input = input("🗣️  Pose ta question (ou 'q' pour quitter) : ")
            
            if user_input.lower() in ['q', 'quit', 'exit']:
                print("Au revoir !")
                break

            # --- ÉTAPE 1 : LE FILTRE (Contrôleur) ---
            print("⏳ Analyse de la pertinence...")
            resultat_controle = controleur.run(user_input)
            
            # --- ÉTAPE 2 : LA DÉCISION ---
            if resultat_controle.get("decision") == "OUI":
                print("✅ Sujet financier détecté.")
                
                # Pour l'instant, on demande le Ticker manuellement à l'utilisateur
                # (Dans la version finale, un LLM pourrait l'extraire tout seul de la phrase)
                ticker = input("   Quel est le ticker de l'entreprise (ex: NVDA, TSLA, MC.PA) ? : ").strip().upper()
                
                if ticker:
                    # --- ÉTAPE 3 : L'ACTION (Chercheur) ---
                    print(f"🚀 Lancement de l'Agent Chercheur sur {ticker}...")
                    start_time = time.time()
                    
                    # L'agent récupère les données, réfléchit et SAUVEGARDE dans contexte.txt
                    rapport_synthese = chercheur.run(ticker)
                    
                    end_time = time.time()
                    
                    # Affichage du résultat dans le terminal
                    print("\n" + "="*20 + f" RAPPORT {ticker} " + "="*20)
                    print(rapport_synthese)
                    print("="*50)
                    print(f"⏱️ Temps de recherche : {round(end_time - start_time, 2)} secondes")
                    print("💾 Le rapport a été sauvegardé dans 'data/contexte.txt'")
                    
                else:
                    print("⚠️ Aucun ticker fourni, annulation.")

            else:
                # Si le contrôleur dit NON
                print(f"⛔ REFUSÉ : {resultat_controle.get('raison')}")
                
        except KeyboardInterrupt:
            print("\nArrêt du programme.")
            break
        except Exception as e:
            print(f"❌ Une erreur est survenue : {e}")

if __name__ == "__main__":
    main()