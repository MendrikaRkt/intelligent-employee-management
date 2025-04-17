# app/crud/crud_simulation.py
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.models.simulation import Simulation as SimulationModel
from app.schemas.simulation import SimulationParams # Utilisé pour le type hinting peut-être

def get_simulation(db: Session, simulation_id: int) -> Optional[SimulationModel]:
    return db.query(SimulationModel).filter(SimulationModel.id == simulation_id).first()

def get_simulations_by_employe(
    db: Session, employe_id: int, skip: int = 0, limit: int = 100
) -> List[SimulationModel]:
    # Vérifier si l'employé existe peut être fait ici ou dans l'endpoint
    return db.query(SimulationModel)\
             .filter(SimulationModel.employe_id == employe_id)\
             .order_by(SimulationModel.date_simulation.desc())\
             .offset(skip).limit(limit).all()

def create_simulation_record(
    db: Session,
    employe_id: int,
    parametres: Dict[str, Any],
    resultats: Dict[str, Any]
) -> SimulationModel:
    """
    Enregistre le résultat d'une simulation dans la base de données.
    Appelé APRÈS l'exécution de la simulation par le service.

    Args:
        db: Session de base de données.
        employe_id: ID de l'employé concerné.
        parametres: Dictionnaire des paramètres utilisés pour la simulation.
        resultats: Dictionnaire des résultats de la simulation.

    Returns:
        L'enregistrement SimulationModel créé.
    """
    # Note: date_simulation est gérée par server_default=func.now() dans le modèle
    db_simulation = SimulationModel(
        employe_id=employe_id,
        parametres_entree=parametres,
        resultats_simulation=resultats
    )
    db.add(db_simulation)
    db.commit()
    db.refresh(db_simulation)
    return db_simulation

def delete_simulation(db: Session, simulation_id: int) -> Optional[SimulationModel]:
    db_simulation = get_simulation(db, simulation_id=simulation_id)
    if db_simulation is None:
        return None
    db.delete(db_simulation)
    db.commit()
    return db_simulation
