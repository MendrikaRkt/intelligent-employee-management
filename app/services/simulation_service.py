# app/services/simulation_service.py

import time
import random
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime, timedelta

# --- Imports for Runge-Kutta ---
import numpy as np
from scipy.integrate import solve_ivp
# --------------------------------

from app import crud, models # crud n'est plus utilisé directement ici si on passe l'état initial
from sqlalchemy.orm import Session
from app.schemas.simulation import SimulationParams
from app.models.evaluation import Evaluation as EvaluationModel # Pour chercher la dernière éval

# ==============================================
# ==      MODÈLE DE PERFORMANCE (Exemple)     ==
# ==============================================
def performance_differential_equation(
    t: float,
    P: np.ndarray,
    base_growth: float,
    base_decay: float,
    scenario_impact: float,
    stress_factor: float
) -> List[float]:
    """
    Définit l'équation différentielle pour la performance P.
    dP/dt = f(t, P, params...)

    Args:
        t: Temps (en mois dans notre cas). Non utilisé dans ce modèle simple, mais requis par solve_ivp.
        P: État actuel [performance]. P[0] est la performance.
        base_growth: Taux de croissance de base.
        base_decay: Taux de déclin/fatigue de base.
        scenario_impact: Impact direct du scénario (+ pour formation, - pour stress).
        stress_factor: Multiplicateur appliqué au déclin dû au stress.

    Returns:
        Liste contenant [dP/dt].
    """
    current_performance = P[0]

    # Limiter la performance entre 0 et 100 pour éviter divergence dans le modèle
    current_performance = max(0, min(100, current_performance))

    # Calcul du taux de croissance (diminue quand P approche 100)
    # Le facteur (100 - P)/100 normalise la distance au max
    growth_term = base_growth * (100 - current_performance) / 50 # facteur 50 pour ajuster l'échelle

    # Calcul du taux de déclin (augmenté par le stress)
    # Le facteur P/100 normalise
    decay_term = (base_decay * (1 + stress_factor)) * current_performance / 50 # facteur 50 pour ajuster

    # Calcul de la dérivée (taux de changement)
    dPdt = growth_term - decay_term + scenario_impact

    # Assurer que si P est déjà à 100, il ne peut pas augmenter, et s'il est à 0, il ne peut pas diminuer négativement
    if current_performance >= 100 and dPdt > 0:
        dPdt = 0
    if current_performance <= 0 and dPdt < 0:
        dPdt = 0

    return [dPdt]

# ==============================================
# ==      SERVICE DE SIMULATION PRINCIPAL     ==
# ==============================================
def run_performance_simulation(
    db: Session, # Gardé si on veut chercher plus de données historiques
    employe_id: int,
    params: SimulationParams
) -> Dict[str, Any]:
    """
    Exécute la simulation de performance pour un employé donné en utilisant Runge-Kutta.

    Args:
        db: Session de base de données.
        employe_id: ID de l'employé.
        params: Paramètres de la simulation (scenario, duree_mois, etc.).

    Returns:
        Un dictionnaire contenant les résultats.
        Ex: {'temps_relatif_mois': [0, 1, ..., N], 'performance_predite': [p0, p1, ..., pN]}

    Raises:
        ValueError: Si la simulation échoue ou si l'employé/évaluation initiale manque.
    """
    print(f"Lancement de la simulation RK pour l'employé {employe_id} avec params: {params.model_dump()}")

    # --- 1. Obtenir la condition initiale (Performance de départ) ---
    # Chercher la dernière évaluation valide de l'employé
    latest_evaluation = db.query(EvaluationModel)\
                          .filter(EvaluationModel.employe_id == employe_id)\
                          .filter(EvaluationModel.score_global.isnot(None))\
                          .order_by(EvaluationModel.date_evaluation.desc())\
                          .first()

    if latest_evaluation and latest_evaluation.score_global is not None:
        initial_performance = float(latest_evaluation.score_global)
        # S'assurer qu'elle est dans les bornes 0-100
        initial_performance = max(0.0, min(100.0, initial_performance))
        print(f"Performance initiale basée sur l'évaluation du {latest_evaluation.date_evaluation}: {initial_performance:.1f}")
    else:
        # Pas d'évaluation ou score nul, utiliser une valeur par défaut raisonnable
        initial_performance = 70.0 # Valeur par défaut (à ajuster)
        print(f"Aucune évaluation trouvée ou score invalide, utilisation de la performance initiale par défaut: {initial_performance:.1f}")

    y0 = [initial_performance] # Condition initiale pour solve_ivp (doit être une liste/array)

    # --- 2. Définir les paramètres du modèle basés sur le scénario ---
    # !!! VALEURS À AJUSTER / CALIBRER EN FONCTION DES DONNÉES RÉELLES !!!
    base_growth_rate = 0.2   # Taux d'apprentissage/motivation de base
    base_decay_rate = 0.1    # Taux de fatigue/déclin de base
    scenario_impact_value = 0.0 # Impact direct du scénario
    stress_multiplier = 0.0   # Facteur additionnel de stress impactant le déclin

    if params.scenario == "formation":
        # Augmentation temporaire de la croissance ou impact direct positif
        scenario_impact_value = params.impact_formation if params.impact_formation else 2.0 # Boost direct mensuel
        print("Scénario: Formation appliqué.")
    elif params.scenario == "augmentation_charge":
        # Augmentation du stress et potentiellement un léger impact négatif direct
        stress_multiplier = params.facteur_stress if params.facteur_stress else 0.5 # Augmente le déclin de 50%
        scenario_impact_value = -1.0 # Léger impact négatif direct
        print("Scénario: Augmentation de charge appliquée.")
    # Ajouter d'autres scénarios ici si nécessaire ("promotion", "standard", etc.)
    else: # Scénario standard
        print("Scénario: Standard appliqué.")
        pass # Utilise les valeurs de base

    # --- 3. Définir l'intervalle et les points d'évaluation ---
    simulation_duration_months = params.duree_mois
    t_span = (0, simulation_duration_months) # Intervalle de temps [début, fin] en mois

    # Points où l'on veut connaître la valeur de la performance (ex: chaque mois)
    t_eval = np.linspace(t_span[0], t_span[1], simulation_duration_months + 1)

    # --- 4. Exécuter la simulation avec solve_ivp (méthode RK45 par défaut) ---
    print("Appel de solve_ivp...")
    try:
        sol = solve_ivp(
            fun=performance_differential_equation, # Notre fonction dP/dt
            t_span=t_span,                      # Intervalle de temps
            y0=y0,                              # Condition initiale [P(0)]
            method='RK45',                      # Méthode Runge-Kutta (ou autre: 'LSODA', 'BDF'...)
            t_eval=t_eval,                      # Points où évaluer la solution
            args=(base_growth_rate,             # Arguments additionnels pour notre fonction dP/dt
                  base_decay_rate,
                  scenario_impact_value,
                  stress_multiplier)
        )
    except Exception as e:
        print(f"Erreur durant l'exécution de solve_ivp: {e}")
        raise ValueError(f"La simulation numérique a échoué: {e}")

    # --- 5. Traiter et retourner les résultats ---
    if sol.success:
        print("Simulation solve_ivp réussie.")
        # Extraire les temps et les valeurs de performance prédites
        times = sol.t.tolist()
        # sol.y est un array 2D (même si une seule variable), prendre la première ligne
        performance_predicted = sol.y[0]

        # S'assurer que les valeurs restent dans les bornes [0, 100] et arrondir
        performance_predicted = np.clip(performance_predicted, 0, 100)
        performance_list = [round(p, 1) for p in performance_predicted.tolist()]

        resultats = {
            "temps_relatif_mois": times,
            "performance_predite": performance_list
        }
        print(f"Résultats de la simulation (RK): {resultats}")
        return resultats
    else:
        print(f"La simulation solve_ivp a échoué: {sol.message}")
        raise ValueError(f"La simulation n'a pas convergé ou a échoué: {sol.message}")