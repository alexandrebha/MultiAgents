"""
Module de collecte et gestion des métriques pour le système Multi-Agents.
Permet de comparer les performances entre le système multi-agents et mono-agent.
"""

import time
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, field, asdict


@dataclass
class AgentMetrics:
    """Métriques pour un agent individuel."""
    name: str
    execution_time: float = 0.0
    llm_calls: int = 0
    success: bool = True
    error_message: Optional[str] = None


@dataclass
class AnalysisMetrics:
    """Métriques pour une analyse complète."""
    # Identifiant
    timestamp: str = ""
    mode: str = "multi-agent"  # "multi-agent" ou "mono-agent"
    ticker: str = ""
    question: str = ""

    # Performance du système
    total_execution_time: float = 0.0
    agents_metrics: List[Dict] = field(default_factory=list)

    # Métriques du Critique (multi-agent uniquement)
    critique_iterations: int = 0
    critique_final_score: float = 0.0
    validated_first_pass: bool = False

    # Qualité de l'extraction ticker
    ticker_extracted: Optional[str] = None
    ticker_validated_by_user: bool = True
    ticker_extraction_correct: bool = True

    # Métriques de qualité du rapport
    voie_choisie: str = ""  # "ANALYSE_COMPLETE" ou "INFO_SIMPLE"
    rapport_genere: bool = False

    # Arguments Bull/Bear (pour comparaison)
    nb_arguments_bull: int = 0
    nb_arguments_bear: int = 0
    score_final: float = 0.0
    recommandation: str = ""


class MetricsCollector:
    """
    Collecteur centralisé de métriques pour le système.

    Usage:
        collector = MetricsCollector()
        collector.start_analysis("multi-agent", "AAPL", "Faut-il investir sur Apple?")

        # Pour chaque agent
        collector.start_agent("Chercheur")
        # ... exécution de l'agent ...
        collector.end_agent("Chercheur", success=True)

        # À la fin
        collector.end_analysis()
        collector.save_to_file()
    """

    def __init__(self):
        self.current_analysis: Optional[AnalysisMetrics] = None
        self._agent_start_times: Dict[str, float] = {}
        self._analysis_start_time: float = 0.0
        self.history: List[AnalysisMetrics] = []
        self._load_history()

    def _load_history(self):
        """Charge l'historique des métriques depuis le fichier JSON."""
        history_file = "data/metriques_history.json"
        if os.path.exists(history_file):
            try:
                with open(history_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.history = [AnalysisMetrics(**m) for m in data]
            except (json.JSONDecodeError, Exception):
                self.history = []

    def _save_history(self):
        """Sauvegarde l'historique des métriques."""
        os.makedirs("data", exist_ok=True)
        history_file = "data/metriques_history.json"
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump([asdict(m) for m in self.history], f, indent=2, ensure_ascii=False)

    def start_analysis(self, mode: str, ticker: str, question: str):
        """Démarre la collecte pour une nouvelle analyse."""
        self.current_analysis = AnalysisMetrics(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            mode=mode,
            ticker=ticker,
            question=question[:100]  # Tronquer si trop long
        )
        self._analysis_start_time = time.time()
        self._agent_start_times = {}

    def start_agent(self, agent_name: str):
        """Marque le début de l'exécution d'un agent."""
        self._agent_start_times[agent_name] = time.time()

    def end_agent(self, agent_name: str, success: bool = True, error_message: str = None):
        """Marque la fin de l'exécution d'un agent."""
        if agent_name not in self._agent_start_times:
            return

        execution_time = time.time() - self._agent_start_times[agent_name]

        agent_metrics = AgentMetrics(
            name=agent_name,
            execution_time=round(execution_time, 2),
            success=success,
            error_message=error_message
        )

        if self.current_analysis:
            self.current_analysis.agents_metrics.append(asdict(agent_metrics))

    def set_ticker_info(self, extracted: str, validated_by_user: bool, correct: bool):
        """Enregistre les infos sur l'extraction du ticker."""
        if self.current_analysis:
            self.current_analysis.ticker_extracted = extracted
            self.current_analysis.ticker_validated_by_user = validated_by_user
            self.current_analysis.ticker_extraction_correct = correct

    def set_critique_info(self, iterations: int, final_score: float, validated_first_pass: bool):
        """Enregistre les infos du Critique."""
        if self.current_analysis:
            self.current_analysis.critique_iterations = iterations
            self.current_analysis.critique_final_score = final_score
            self.current_analysis.validated_first_pass = validated_first_pass

    def set_voie(self, voie: str):
        """Enregistre la voie choisie par le Planificateur."""
        if self.current_analysis:
            self.current_analysis.voie_choisie = voie

    def set_report_quality(self, nb_bull: int, nb_bear: int, score: float, recommandation: str):
        """Enregistre les métriques de qualité du rapport."""
        if self.current_analysis:
            self.current_analysis.nb_arguments_bull = nb_bull
            self.current_analysis.nb_arguments_bear = nb_bear
            self.current_analysis.score_final = score
            self.current_analysis.recommandation = recommandation
            self.current_analysis.rapport_genere = True

    def end_analysis(self):
        """Termine la collecte et calcule les métriques finales."""
        if self.current_analysis:
            self.current_analysis.total_execution_time = round(
                time.time() - self._analysis_start_time, 2
            )
            self.history.append(self.current_analysis)
            self._save_history()

    def get_current_metrics(self) -> Optional[AnalysisMetrics]:
        """Retourne les métriques de l'analyse en cours."""
        return self.current_analysis

    def get_summary_stats(self) -> Dict:
        """
        Calcule les statistiques résumées pour le rapport.
        Sépare les métriques multi-agent et mono-agent.
        """
        multi_agent_analyses = [m for m in self.history if m.mode == "multi-agent"]
        mono_agent_analyses = [m for m in self.history if m.mode == "mono-agent"]

        def calc_stats(analyses: List[AnalysisMetrics]) -> Dict:
            if not analyses:
                return {
                    "nb_analyses": 0,
                    "temps_moyen": 0.0,
                    "temps_min": 0.0,
                    "temps_max": 0.0,
                    "taux_validation_premier_passage": 0.0,
                    "iterations_correction_moyenne": 0.0,
                    "precision_ticker": 0.0,
                    "score_qualite_moyen": 0.0,
                    "nb_args_bull_moyen": 0.0,
                    "nb_args_bear_moyen": 0.0,
                    "temps_par_agent": {}
                }

            times = [m.total_execution_time for m in analyses]

            # Taux validation premier passage
            first_pass_validated = sum(1 for m in analyses if m.validated_first_pass)

            # Précision ticker
            ticker_correct = sum(1 for m in analyses if m.ticker_extraction_correct)

            # Temps moyen par agent
            agent_times: Dict[str, List[float]] = {}
            for analysis in analyses:
                for agent in analysis.agents_metrics:
                    name = agent.get("name", "Unknown")
                    t = agent.get("execution_time", 0.0)
                    if name not in agent_times:
                        agent_times[name] = []
                    agent_times[name].append(t)

            avg_agent_times = {
                name: round(sum(times) / len(times), 2)
                for name, times in agent_times.items()
            }

            return {
                "nb_analyses": len(analyses),
                "temps_moyen": round(sum(times) / len(times), 2),
                "temps_min": round(min(times), 2),
                "temps_max": round(max(times), 2),
                "taux_validation_premier_passage": round(first_pass_validated / len(analyses) * 100, 1),
                "iterations_correction_moyenne": round(
                    sum(m.critique_iterations for m in analyses) / len(analyses), 2
                ),
                "precision_ticker": round(ticker_correct / len(analyses) * 100, 1),
                "score_qualite_moyen": round(
                    sum(m.critique_final_score for m in analyses) / len(analyses), 1
                ),
                "nb_args_bull_moyen": round(
                    sum(m.nb_arguments_bull for m in analyses) / len(analyses), 1
                ),
                "nb_args_bear_moyen": round(
                    sum(m.nb_arguments_bear for m in analyses) / len(analyses), 1
                ),
                "temps_par_agent": avg_agent_times
            }

        return {
            "multi_agent": calc_stats(multi_agent_analyses),
            "mono_agent": calc_stats(mono_agent_analyses)
        }

    def generate_report(self) -> str:
        """Génère le rapport de métriques formaté pour metriques.txt."""
        stats = self.get_summary_stats()
        ma = stats["multi_agent"]
        mo = stats["mono_agent"]

        current_date = datetime.now().strftime("%Y-%m-%d %H:%M")

        report = f"""# RAPPORT DE MÉTRIQUES - SYSTÈME MULTI-AGENTS VS MONO-AGENT
Date de génération: {current_date}

================================================================================
                           RÉSUMÉ DES PERFORMANCES
================================================================================

## 1. PERFORMANCE DU SYSTÈME

### Multi-Agents
- Nombre d'analyses réalisées: {ma['nb_analyses']}
- Temps d'exécution moyen: {ma['temps_moyen']}s
- Temps minimum: {ma['temps_min']}s
- Temps maximum: {ma['temps_max']}s

### Mono-Agent
- Nombre d'analyses réalisées: {mo['nb_analyses']}
- Temps d'exécution moyen: {mo['temps_moyen']}s
- Temps minimum: {mo['temps_min']}s
- Temps maximum: {mo['temps_max']}s

### Temps par Agent (Multi-Agents)
"""
        # Ajouter temps par agent
        for agent_name, avg_time in ma.get("temps_par_agent", {}).items():
            report += f"- {agent_name}: {avg_time}s (moyenne)\n"

        report += f"""
--------------------------------------------------------------------------------

## 2. QUALITÉ DES ANALYSES

### Multi-Agents
- Précision extraction ticker: {ma['precision_ticker']}%
- Score qualité moyen (Critique): {ma['score_qualite_moyen']}/100
- Taux de validation au premier passage: {ma['taux_validation_premier_passage']}%
- Nombre moyen d'itérations de correction: {ma['iterations_correction_moyenne']}

### Mono-Agent
- Précision extraction ticker: {mo['precision_ticker']}%
- Score qualité moyen: N/A (pas de Critique)

--------------------------------------------------------------------------------

## 3. RICHESSE ARGUMENTATIVE

### Multi-Agents
- Nombre moyen d'arguments Bull: {ma['nb_args_bull_moyen']}
- Nombre moyen d'arguments Bear: {ma['nb_args_bear_moyen']}
- Équilibre Bull/Bear: {'Équilibré' if abs(ma['nb_args_bull_moyen'] - ma['nb_args_bear_moyen']) < 1 else 'Déséquilibré'}

### Mono-Agent
- Nombre moyen d'arguments Bull: {mo['nb_args_bull_moyen']}
- Nombre moyen d'arguments Bear: {mo['nb_args_bear_moyen']}
- Équilibre Bull/Bear: {'Équilibré' if abs(mo['nb_args_bull_moyen'] - mo['nb_args_bear_moyen']) < 1 else 'Déséquilibré'}

--------------------------------------------------------------------------------

## 4. COMPARAISON MULTI-AGENT VS MONO-AGENT

"""
        # Calcul des différences
        if ma['nb_analyses'] > 0 and mo['nb_analyses'] > 0:
            time_diff = ma['temps_moyen'] - mo['temps_moyen']
            args_diff = (ma['nb_args_bull_moyen'] + ma['nb_args_bear_moyen']) - \
                       (mo['nb_args_bull_moyen'] + mo['nb_args_bear_moyen'])

            report += f"""| Métrique                    | Multi-Agent | Mono-Agent | Différence |
|-----------------------------|-------------|------------|------------|
| Temps d'exécution moyen     | {ma['temps_moyen']}s       | {mo['temps_moyen']}s       | {time_diff:+.2f}s      |
| Précision ticker            | {ma['precision_ticker']}%      | {mo['precision_ticker']}%      | {ma['precision_ticker'] - mo['precision_ticker']:+.1f}%     |
| Arguments Bull (moy)        | {ma['nb_args_bull_moyen']}        | {mo['nb_args_bull_moyen']}        | {ma['nb_args_bull_moyen'] - mo['nb_args_bull_moyen']:+.1f}       |
| Arguments Bear (moy)        | {ma['nb_args_bear_moyen']}        | {mo['nb_args_bear_moyen']}        | {ma['nb_args_bear_moyen'] - mo['nb_args_bear_moyen']:+.1f}       |
| Total arguments             | {ma['nb_args_bull_moyen'] + ma['nb_args_bear_moyen']:.1f}        | {mo['nb_args_bull_moyen'] + mo['nb_args_bear_moyen']:.1f}        | {args_diff:+.1f}       |

### Analyse
"""
            if time_diff > 0:
                report += f"- Le système Multi-Agents est plus lent de {time_diff:.1f}s en moyenne.\n"
            else:
                report += f"- Le système Multi-Agents est plus rapide de {abs(time_diff):.1f}s en moyenne.\n"

            if args_diff > 0:
                report += f"- Le système Multi-Agents produit {args_diff:.1f} arguments de plus en moyenne.\n"
            else:
                report += f"- Le système Mono-Agent produit {abs(args_diff):.1f} arguments de plus en moyenne.\n"
        else:
            report += "Données insuffisantes pour la comparaison. Exécutez plus d'analyses.\n"

        report += """
================================================================================
                           HISTORIQUE DES ANALYSES
================================================================================

"""
        # Ajouter les 10 dernières analyses
        recent = self.history[-10:] if len(self.history) > 10 else self.history
        for i, analysis in enumerate(reversed(recent), 1):
            report += f"""### Analyse #{len(self.history) - i + 1}
- Date: {analysis.timestamp}
- Mode: {analysis.mode}
- Ticker: {analysis.ticker}
- Temps: {analysis.total_execution_time}s
- Score: {analysis.critique_final_score}/100
- Recommandation: {analysis.recommandation or 'N/A'}

"""

        report += """================================================================================
                                    FIN DU RAPPORT
================================================================================
"""

        return report

    def save_report(self):
        """Sauvegarde le rapport de métriques dans data/metriques.txt."""
        os.makedirs("data", exist_ok=True)
        report = self.generate_report()
        with open("data/metriques.txt", "w", encoding="utf-8") as f:
            f.write(report)
        print("[Metrics] Rapport sauvegardé dans data/metriques.txt")


# Instance globale pour faciliter l'utilisation
_collector: Optional[MetricsCollector] = None


def get_collector() -> MetricsCollector:
    """Retourne l'instance globale du collecteur de métriques."""
    global _collector
    if _collector is None:
        _collector = MetricsCollector()
    return _collector
