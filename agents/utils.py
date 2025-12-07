import os
import json

def save_history_to_file(history: list, filename: str, folder: str = "logs") -> str:
    """
    Sauvegarde une liste (comme conversation_history) dans un fichier JSON structuré.
    
    :param history: La liste des messages à sauvegarder.
    :param filename: Le nom du fichier (ex: 'history_agent1.json').
    :param folder: Le dossier de destination.
    """
    try:
        if not os.path.exists(folder):
            os.makedirs(folder)

        # On s'assure que le fichier a bien l'extension .json
        if not filename.endswith('.json'):
            filename += '.json'
            
        file_path = os.path.join(folder, filename)

        # indent=4 permet de créer un fichier "joli" et lisible (pas tout sur une ligne)
        # ensure_ascii=False permet de garder les accents (é, à, etc.) lisibles
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=4, ensure_ascii=False)

        print(f"Historique sauvegardé dans : {file_path}")

    except Exception as e:
        print(f"Erreur sauvegarde JSON : {e}")


def load_history_from_file(filename: str, folder: str = "logs"):
        """
        Charge l'historique depuis un fichier JSON et le remet dans la mémoire de l'agent.
        """
        import os
        import json
        
        # Gestion de l'extension .json
        if not filename.endswith('.json'):
            filename += '.json'
            
        file_path = os.path.join(folder, filename)
        
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    conversation_history = json.load(f)
                print(f"Mémoire rechargée depuis {filename} ({len(conversation_history)} messages)")
            except Exception as e:
                print(f"Erreur lecture JSON : {e}")
        else:
            print(f"Fichier {filename} introuvable dans {folder}. On part de zéro.")
        
        return conversation_history