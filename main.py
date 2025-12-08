# main.py (Version 1)
from agents.agent0_controler import ControlerAgent

def main():
    # 1. Initialisation
    print("🤖 Initialisation du système...")
    controleur = ControlerAgent()

    # 2. Boucle d'interaction
    while True:
        user_input = input("\n🗣️  Pose ta question (ou 'q' pour quitter) : ")
        if user_input.lower() == 'q':
            break

        # 3. L'Agent 0 filtre
        resultat = controleur.run(user_input)
        
        # 4. Logique d'Orchestration (Le Losange de décision)
        if resultat.get("decision") == "OUI":
            print("✅ SUJET VALIDE. (Ici, on lancera bientôt l'Agent Chercheur)")
        else:
            print(f"⛔ REFUSÉ : {resultat.get('raison')}")

if __name__ == "__main__":
    main()