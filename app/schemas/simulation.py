# app/schemas/simulation.py
from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime

# Schéma pour les paramètres d'entrée de la simulation (ce que l'utilisateur fournit)
class SimulationParams(BaseModel):
    scenario: str = "standard" # Ex: "standard", "augmentation_charge", "formation"
    duree_mois: int = 6
    # Ajoutez d'autres paramètres spécifiques que votre modèle Runge-Kutta pourrait utiliser
    facteur_stress: Optional[float] = None
    impact_formation: Optional[float] = None
    # ... autres paramètres ...

    model_config = ConfigDict(extra='allow') # Permet des paramètres non définis explicitement

# Schéma pour lancer une simulation (via l'API)
class SimulationRun(BaseModel):
    employe_id: int
    parametres: SimulationParams

# Schéma de base pour représenter une simulation enregistrée en BDD
class SimulationBase(BaseModel):
    employe_id: int
    date_simulation: datetime
    parametres_entree: Optional[Dict[str, Any]] = None # Stockage des paramètres utilisés
    resultats_simulation: Optional[Dict[str, Any]] = None # Stockage des résultats (ex: {'temps': [], 'performance': []})

# Pas de schéma Create spécifique car la création se fait via le lancement (SimulationRun)
# Pas de schéma Update typique, on ne modifie généralement pas une simulation passée

# Schéma pour lire une simulation depuis la BDD
class Simulation(SimulationBase):
    id: int

    model_config = ConfigDict(from_attributes=True)