# Changelog - Système Multi-Agents

## [2026-01-31] - Restructuration des rapports finaux

### Ajouté
- **Nouveau dossier `rapport_final/`** : Dossier dédié pour les rapports finaux
- **Génération PDF automatique** : Les rapports sont maintenant générés en TXT et PDF
  - `rapport_multi_agent.txt` et `.pdf`
  - `rapport_mono_agent.txt` et `.pdf`
- **Fonction `save_to_pdf()`** dans `agents/utils.py` : Génération de PDF avec support UTF-8
- **Fonction `save_report_both_formats()`** dans `agents/utils.py` : Sauvegarde simultanée TXT + PDF
- **README** dans `rapport_final/` : Documentation du contenu du dossier
- **`.gitignore`** : Exclusion des fichiers générés du versioning

### Modifié
- **requirements.txt** : Ajout de `fpdf2` pour la génération de PDF
- **main.py** :
  - Import de `save_report_both_formats`
  - Sauvegarde automatique en TXT + PDF après validation du Critique (Voie A)
  - Sauvegarde automatique en TXT + PDF pour les rapports informatifs (Voie B)
- **mono_agent.py** :
  - Import de `save_report_both_formats`
  - Sauvegarde automatique en TXT + PDF à la fin de l'analyse
  - Maintien de la compatibilité avec `data/rapport_mono_agent.txt`
- **README.md** :
  - Mise à jour de la structure du projet
  - Documentation de la génération PDF
  - Mise à jour des exemples d'utilisation

### Structure des fichiers

```
MultiAgents/
├── rapport_final/          # NOUVEAU : Rapports finaux
│   ├── README.md
│   ├── rapport_multi_agent.txt
│   ├── rapport_multi_agent.pdf
│   ├── rapport_mono_agent.txt
│   └── rapport_mono_agent.pdf
├── data/                   # Fichiers intermédiaires (inchangé)
│   ├── contexte.txt
│   ├── avis_bull.txt
│   ├── avis_bear.txt
│   ├── avis_score.txt
│   └── ...
└── ...
```

### Technique

**Génération PDF :**
- Utilisation de `fpdf2` avec police DejaVu pour support UTF-8
- Fallback sur Arial si DejaVu non disponible
- Gestion des titres markdown (# et ##)
- Mise en page automatique avec sauts de ligne

**Compatibilité :**
- Les fichiers TXT sont toujours sauvegardés dans `data/` pour la compatibilité
- Les nouveaux rapports finaux sont dans `rapport_final/` pour une meilleure organisation
- Pas de breaking changes : l'ancien code fonctionne toujours

### Installation

Pour mettre à jour les dépendances :

```bash
pip install -r requirements.txt
```

Cela installera notamment `fpdf2` pour la génération de PDF.

### Note pour le prof

Les rapports finaux à évaluer se trouvent maintenant dans le dossier `rapport_final/` au format TXT et PDF, pour les deux versions (multi-agent et mono-agent).

Le dossier `data/` contient les fichiers intermédiaires utilisés par le système (avis des agents Bull/Bear, contexte, etc.).
