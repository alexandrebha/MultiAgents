# Système Multi-Agents pour l'Analyse Financière

Alexandre BOUHARIRA--THELLIEZ,
Samuel SILVA,
Yanis ZIDI,
Ilyes OUBBEA

Projet académique (ING3 - NLP) démontrant l'utilisation de systèmes multi-agents pour l'analyse financière intelligente et équilibrée.

## Table des matières

- [Dataset](#dataset)
- [Problématique](#problématique)
- [Solution Appliquée](#solution-appliquée)
- [Architecture Multi-Agents](#architecture-multi-agents)
- [Résultats](#résultats)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Comparaison Mono-Agent vs Multi-Agents](#comparaison-mono-agent-vs-multi-agents)

---

## Dataset

### Source de données : Yahoo Finance API

Le projet utilise l'API **Yahoo Finance** via la librairie `yfinance` pour récupérer des données financières en temps réel.

**Types de données collectées :**
- **Prix et valorisation** : Prix actuel, variations 52 semaines, moyennes mobiles
- **Métriques de valorisation** : P/E ratio, Forward P/E, PEG, Price-to-Sales, EV/EBITDA
- **Santé financière** : Revenus, EBITDA, EPS, marges opérationnelles, ROE, ratios d'endettement
- **Informations entreprise** : Secteur, industrie, nombre d'employés, site web
- **Consensus analystes** : Objectifs de prix, recommandations
- **Actualités** : Jusqu'à 5 articles récents avec contenu complet

**Exemple de données récupérées (NVIDIA) :**
```
- Prix : $191.13
- Capitalisation : $4.65 trillions
- P/E Ratio : 47.66
- Croissance revenus : 62.5%
- Marge opérationnelle : 63.17%
```

---

## Problématique

### Objectif principal
Fournir une **analyse d'investissement intelligente et équilibrée** sur des actions en bourse à partir de questions en langage naturel.

### Défis identifiés

1. **Biais cognitifs** : Les analyses financières humaines sont souvent biaisées (optimisme/pessimisme)
2. **Surcharge informationnelle** : Trop de données financières rendent la décision difficile
3. **Manque de transparence** : Les recommandations sans explication ne sont pas fiables
4. **Rigidité des systèmes** : Les outils classiques ne comprennent pas le langage naturel

### Approche proposée

Utiliser un **système multi-agents** où chaque agent a un rôle spécialisé :
- Validation et extraction d'informations
- Recherche de données
- Analyses contradictoires (Bull/Bear)
- Scoring multi-critères
- Génération de rapports
- Contrôle qualité

---

## Solution Appliquée

### Technologies et librairies

| Technologie | Version/Type | Usage |
|-------------|--------------|-------|
| **Python** | 3.x | Langage principal |
| **LangChain** | `langchain_ollama`, `langchain_core` | Framework multi-agents |
| **Ollama** | Local LLMs | Moteur d'inférence (mistral, mistral-nemo) |
| **yfinance** | - | Récupération données Yahoo Finance |
| **Regex** | Built-in | Parsing des sorties LLM |

### Modèles Ollama utilisés

- **mistral** : Agents de contrôle et coordination (Contrôleur, Chercheur, Planificateur)
- **mistral-nemo** : Agents d'analyse et rédaction (Bull, Bear, Score, Rédacteur, Critique)

### Techniques implémentées

1. **Architecture multi-agents** : 8 agents spécialisés avec responsabilités uniques (SRP)
2. **Mémoire conversationnelle** : Historique de conversation persistant (JSON)
3. **Boucle de feedback** : Système de critique et correction itérative (max 3 itérations)
4. **Routing intelligent** : Deux modes opératoires (INFO_SIMPLE vs ANALYSE_COMPLETE)
5. **Scoring pondéré** : 7 critères avec poids définis
6. **Analyses contradictoires** : Agents Bull et Bear pour équilibrer les biais

---

### Système de scoring (Agent 4)

Le système évalue 7 dimensions avec pondération :

| Critère | Poids | Description |
|---------|-------|-------------|
| Valorisation | 20% | P/E, PEG, Price-to-Sales, etc. |
| Croissance | 20% | Croissance revenus, EPS, perspectives |
| Rentabilité | 15% | Marges, ROE, génération de cash |
| Santé Financière | 15% | Ratios d'endettement, liquidités |
| Sentiment Analystes | 10% | Consensus, objectifs de prix |
| Momentum | 10% | Performance récente du titre |
| Risques Identifiés | 10% | Facteurs de risque identifiés |

**Score final** : /10 avec recommandation (ACHAT FORT, ACHAT MODÉRÉ, CONSERVER, VENDRE, etc.)

---

## Résultats

### Exemple d'analyse : NVIDIA (NVDA)

**Question utilisateur :** "faut il investir sur nvidia ?"

**Output système :**

```markdown
RAPPORT D'ANALYSE FINANCIÈRE : NVIDIA

==================================================
RECOMMANDATION : ACHAT MODÉRÉ
SCORE GLOBAL : 7.4/10
==================================================

POINTS FORTS (Bull) :
✓ Croissance exceptionnelle des revenus : +62.5% YoY
✓ Marge opérationnelle élevée : 63.17%
✓ Position de trésorerie solide : $60B
✓ Leader du marché des GPU pour l'IA
✓ Adoption massive de l'architecture CUDA

POINTS DE VIGILANCE (Bear) :
 Valorisation élevée : P/E ratio à 47.66
 Concurrence intense (AMD, Intel, startups)
 Incertitude sur l'accord OpenAI
 Dépendance au marché des datacenters

DÉTAIL DU SCORING :
┌────────────────────────┬───────┬──────────┐
│ Critère                │ Score │ Poids    │
├────────────────────────┼───────┼──────────┤
│ Valorisation           │ 6/10  │ 20%      │
│ Croissance             │ 9/10  │ 20%      │
│ Rentabilité            │ 8/10  │ 15%      │
│ Santé Financière       │ 8/10  │ 15%      │
│ Sentiment Analystes    │ 7/10  │ 10%      │
│ Momentum               │ 7/10  │ 10%      │
│ Risques Identifiés     │ 6/10  │ 10%      │
└────────────────────────┴───────┴──────────┘

VALIDATION QUALITÉ :
Rapport validé après 1 itération (Score qualité : 74/100)
```

### Métriques de performance

> **Note :** Cette section sera complétée avec les métriques suivantes lors de l'évaluation finale :

#### Métriques prévues

**Performance du système :**
- Temps d'exécution moyen par analyse complète
- Temps d'exécution par agent
- Nombre moyen d'itérations de correction (Agent Critique)
- Taux de validation au premier passage

**Qualité des analyses :**
- Précision de l'extraction de ticker (Agent 0)
- Cohérence des scores Bull/Bear avec les fondamentaux
- Corrélation entre score système et performance réelle des titres (backtesting)
- Taux de complétude des rapports

**Comparaison Mono-Agent vs Multi-Agents :**
- Différence de qualité des rapports (évaluation humaine)
- Différence de temps d'exécution
- Richesse argumentative (nombre de points abordés)
- Équilibre Bull/Bear

**Exemples de métriques à collecter :**
```
Temps moyen d'exécution : [À COMPLÉTER]
Nombre d'analyses réalisées : [À COMPLÉTER]
Précision extraction ticker : [À COMPLÉTER]
Score qualité moyen (Critique) : [À COMPLÉTER]
```

### Exemples de sorties générées

Tous les fichiers sont sauvegardés dans le dossier [data/](data/) :

- [contexte.txt](data/contexte.txt) : Données brutes récupérées par le Chercheur
- [avis_bull.txt](data/avis_bull.txt) : Arguments optimistes
- [avis_bear.txt](data/avis_bear.txt) : Arguments pessimistes
- [avis_score.txt](data/avis_score.txt) : Scoring détaillé
- [rapport_final.txt](data/rapport_final.txt) : Rapport complet validé
- [corrections.txt](data/corrections.txt) : Feedback du Critique
- [metriques.txt](data/metriques.txt) : Métriques d'exécution

---

## Installation

### Prérequis

- **Python** 3.8 ou supérieur
- **Ollama** installé et fonctionnel ([ollama.ai](https://ollama.ai))
- Connexion internet (pour l'API Yahoo Finance)

### Étape 1 : Installation d'Ollama

#### Sur Ubuntu/Linux
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

#### Sur Windows
1. Télécharger l'installeur depuis [ollama.ai/download](https://ollama.ai/download)
2. Exécuter l'installeur et suivre les instructions

#### Sur macOS
```bash
brew install ollama
```

### Étape 2 : Téléchargement des modèles Ollama

Une fois Ollama installé, télécharger les modèles requis :

```bash
# Modèle principal (Contrôleur, Chercheur, Planificateur)
ollama pull mistral

# Modèle secondaire (Bull, Bear, Score, Rédacteur, Critique)
ollama pull mistral-nemo
```

**Vérification :**
```bash
ollama list
```

Vous devriez voir :
```
NAME            ID              SIZE
mistral:latest  ...             4.1 GB
mistral-nemo:latest ...         5.2 GB
```

### Étape 3 : Installation des dépendances Python

```bash
# Cloner ou télécharger le projet
cd MultiAgents

# Installer les dépendances
pip install -r requirements.txt
```

**Contenu de requirements.txt :**
```
langchain
langchain-ollama
langchain-core
yfinance
```

> **Note importante :** Le projet nécessite également le module `tools.yfinance_fetch` qui doit être disponible dans votre environnement. Assurez-vous que ce module est accessible dans le PYTHONPATH.

### Étape 4 : Vérification de l'installation

```bash
# Vérifier qu'Ollama fonctionne
ollama run mistral "Bonjour"

# Vérifier les imports Python
python -c "import langchain_ollama; import yfinance; print('OK')"
```

---

## Utilisation

### Lancer l'analyse multi-agents

```bash
python main.py
```

**Interaction typique :**

```
=== Système Multi-Agents - Analyse Financière ===

Posez votre question (ou 'quit' pour quitter) :
> faut il investir sur nvidia

Ticker détecté : NVDA
Voulez-vous utiliser ce ticker ? (oui/non ou nouveau ticker) :
> oui

[Agent Chercheur] Récupération des données financières pour NVDA...
[Agent Planificateur] Route sélectionnée : ANALYSE_COMPLETE
[Agent Bull] Génération des arguments optimistes...
[Agent Bear] Génération des arguments pessimistes...
[Agent Score] Calcul du score pondéré...
[Agent Rédacteur] Rédaction du rapport final...
[Agent Critique] Validation qualité...

✓ Rapport validé (Score qualité : 74/100)

[RAPPORT FINAL AFFICHÉ ICI]

Temps d'exécution : 45.2 secondes

Posez votre question (ou 'quit' pour quitter) :
>
```

### Lancer l'analyse mono-agent (baseline)

Pour comparaison, vous pouvez lancer la version mono-agent :

```bash
python mono_agent.py
```

**Différences clés :**
- Analyse réalisée en un seul appel LLM
- Pas de contrôle qualité itératif
- Rapport plus simple
- Plus rapide mais moins nuancé

### Exemples de questions supportées

**Voie A (Analyse complète) :**
- "faut il investir sur nvidia ?"
- "est-ce que TSLA est un bon investissement ?"
- "analyse de l'action Apple"
- "recommandation pour Microsoft"

**Voie B (Info simple) :**
- "c'est quoi LVMH ?"
- "présente-moi l'entreprise Tesla"
- "que fait Amazon ?"

**Questions rejetées (non financières) :**
- "quelle est la météo ?"
- "comment faire une pizza ?"

---

## Comparaison Mono-Agent vs Multi-Agents

### Mono-Agent (`mono_agent.py`)

**Avantages :**
- Plus rapide (1 seul appel LLM)
- Implémentation simple
- Consommation mémoire réduite

**Inconvénients :**
- Pas de séparation des préoccupations (Bull/Bear)
- Risque de biais dans l'analyse
- Pas de contrôle qualité automatique
- Rapport moins structuré

### Multi-Agents (`main.py`)

**Avantages :**
- Analyses contradictoires équilibrées (Bull vs Bear)
- Contrôle qualité avec boucle de feedback
- Modularité et maintenabilité
- Scoring transparent et explicable
- Historique conversationnel
- Routing intelligent selon l'intention

**Inconvénients :**
- Temps d'exécution plus long (8 agents)
- Complexité accrue
- Plus de consommation mémoire
- Dépendance entre agents

### Tableau comparatif

| Critère | Mono-Agent | Multi-Agents |
|---------|-----------|--------------|
| Temps d'exécution | ~10-15s | ~40-60s |
| Nombre d'appels LLM | 1 | 8-12 (avec corrections) |
| Qualité argumentation | Moyenne | Élevée |
| Équilibre Bull/Bear | Non garanti | Garanti |
| Contrôle qualité | Aucun | Automatique (Agent 6) |
| Scoring transparent | Non | Oui (7 critères pondérés) |
| Historique conversation | Non | Oui (persistant) |
| Routing intelligent | Non | Oui (Voie A/B) |

---

## Structure du projet

```
MultiAgents/
├── README.md                       # Ce fichier
├── requirements.txt                # Dépendances Python
│
├── main.py                         # Point d'entrée multi-agents
├── mono_agent.py                   # Baseline mono-agent
│
├── agents/                         # Système multi-agents
│   ├── base_agent.py              # Classe de base Agent
│   ├── agent0_controler.py        # Validation & extraction ticker
│   ├── agent1_chercheur.py        # Récupération données Yahoo Finance
│   ├── agent2_planificateur.py    # Routing Voie A/B
│   ├── agent3_bull.py             # Analyse optimiste
│   ├── agent3_bear.py             # Analyse pessimiste
│   ├── agent4_score.py            # Scoring pondéré
│   ├── agent5_redacteur.py        # Génération rapport
│   ├── agent6_critique.py         # Contrôle qualité
│   ├── utils.py                   # Utilitaires
│   └── logs/                      # Historiques conversations (JSON)
│
└── data/                          # Outputs générés
    ├── contexte.txt               # Données brutes
    ├── avis_bull.txt              # Arguments optimistes
    ├── avis_bear.txt              # Arguments pessimistes
    ├── avis_score.txt             # Scoring détaillé
    ├── rapport_final.txt          # Rapport validé (multi-agents)
    ├── rapport_mono_agent.txt     # Rapport baseline (mono-agent)
    ├── corrections.txt            # Feedback Critique
    └── metriques.txt              # Métriques d'exécution
```

---

## Auteurs

Projet académique ING3 - NLP

---

## Licence

Ce projet est à usage éducatif uniquement.

---

## Notes techniques

### Modèles Ollama requis

| Modèle | Taille | Usage |
|--------|--------|-------|
| mistral | ~4.1 GB | Agents de coordination |
| mistral-nemo | ~5.2 GB | Agents d'analyse |

### Dépendances externes

- **Yahoo Finance API** : Gratuite, pas de clé API requise
- **Ollama Server** : Doit être en cours d'exécution (port par défaut 11434)

### Limites connues

1. **Données Yahoo Finance** : Parfois incomplètes pour certains tickers
2. **Tickers internationaux** : Nécessitent le suffixe (ex: MC.PA pour LVMH Paris)
3. **Latence** : Dépend de la vitesse de votre machine (LLMs locaux)
4. **Langue** : Optimisé pour le français, questions en anglais possibles mais rapport en français

### Troubleshooting

**Erreur : "Ollama server not running"**
```bash
# Démarrer Ollama
ollama serve
```

**Erreur : "Model not found"**
```bash
# Re-télécharger les modèles
ollama pull mistral
ollama pull mistral-nemo
```

**Erreur : "Ticker invalide"**
- Vérifier le ticker sur Yahoo Finance
- Pour les actions européennes, ajouter le suffixe (.PA pour Paris, .L pour Londres, etc.)

**Performances lentes**
- Utiliser un GPU si disponible
- Réduire le nombre d'itérations max du Critique (paramètre dans agent6_critique.py)
- Passer au mode mono-agent pour des résultats rapides

---

## Améliorations futures

- [ ] Support de l'analyse multi-actions (portfolios)
- [ ] Ajout de graphiques de visualisation
- [ ] Export PDF des rapports
- [ ] Interface web (Streamlit/Gradio)
- [ ] Intégration d'autres sources de données (Bloomberg, Alpha Vantage)
- [ ] Backtesting automatique des recommandations
- [ ] Support multilingue complet


### Lien Vidéos

- Vidéo Présentation du WorkFlow : 
  https://www.youtube.com/watch?v=avi9Pp75ps0
- Vidéo Démo : 
  https://youtu.be/R1Fsayh--yI





