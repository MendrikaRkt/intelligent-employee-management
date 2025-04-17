# app/api/api_v1/endpoints/simulations.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app import crud, schemas
from app.db.session import get_db
from app.services import simulation_service # Importer le service

router = APIRouter(
    tags=["Simulations"]
)

@router.post("/run", response_model=schemas.Simulation)
async def run_and_save_simulation(
    simulation_input: schemas.SimulationRun,
    db: Session = Depends(get_db)
):
    """
    Lance une nouvelle simulation de performance pour un employé,
    enregistre les résultats et retourne l'enregistrement de simulation.
    """
    # 1. Vérifier si l'employé existe
    db_employe = crud.employe.get_employe(db, employe_id=simulation_input.employe_id)
    if not db_employe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employé avec ID {simulation_input.employe_id} non trouvé."
        )

    # 2. Exécuter la simulation via le service
    try:
        print(f"Appel du service de simulation pour employe_id={simulation_input.employe_id}")
        simulation_results = simulation_service.run_performance_simulation(
            db=db,
            employe_id=simulation_input.employe_id,
            params=simulation_input.parametres
        )
        print(f"Résultats reçus du service: {simulation_results}")
    except ValueError as e: # Capturer les erreurs potentielles de la simulation elle-même
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Erreur lors de l'exécution de la simulation: {e}")
    except Exception as e:
        # Log l'erreur e de manière plus détaillée côté serveur
        print(f"Erreur inattendue dans le service de simulation: {e}") # Log temporaire
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erreur interne du serveur lors de la simulation.")

    # 3. Enregistrer les résultats dans la base de données via le CRUD
    try:
        # Convertir les paramètres Pydantic en dict pour le stockage JSON
        params_dict = simulation_input.parametres.model_dump()
        created_simulation_record = crud.simulation.create_simulation_record(
            db=db,
            employe_id=simulation_input.employe_id,
            parametres=params_dict,
            resultats=simulation_results
        )
        print(f"Enregistrement de simulation créé avec ID: {created_simulation_record.id}")
        return created_simulation_record
    except Exception as e:
        # Log l'erreur e
        print(f"Erreur lors de l'enregistrement de la simulation: {e}") # Log temporaire
        # Si la simulation a réussi mais l'enregistrement échoue, que faire?
        # On pourrait retourner les résultats sans les avoir sauvegardés, ou lever une erreur 500.
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erreur lors de l'enregistrement des résultats de la simulation.")


@router.get("/by_employe/{employe_id}", response_model=List[schemas.Simulation])
async def read_simulations_for_employe(
    employe_id: int,
    skip: int = 0,
    limit: int = Query(default=10, ge=1, le=100), # Moins par défaut car potentiellement volumineux
    db: Session = Depends(get_db)
):
    """
    Récupère l'historique des simulations enregistrées pour un employé spécifique.
    """
    # Vérifier si l'employé existe
    db_employe = crud.employe.get_employe(db, employe_id=employe_id)
    if not db_employe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Employé avec ID {employe_id} non trouvé.")

    simulations = crud.simulation.get_simulations_by_employe(
        db, employe_id=employe_id, skip=skip, limit=limit
    )
    return simulations

@router.get("/{simulation_id}", response_model=schemas.Simulation)
async def read_single_simulation(
    simulation_id: int,
    db: Session = Depends(get_db)
):
    """
    Récupère un enregistrement de simulation spécifique par son ID.
    """
    db_simulation = crud.simulation.get_simulation(db, simulation_id=simulation_id)
    if db_simulation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Simulation avec ID {simulation_id} non trouvée.")
    return db_simulation

@router.delete("/{simulation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_simulation(
    simulation_id: int,
    db: Session = Depends(get_db)
) -> None:
    """
    Supprime un enregistrement de simulation existant par son ID.
    """
    deleted = crud.simulation.delete_simulation(db, simulation_id=simulation_id)
    if deleted is None:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Simulation avec ID {simulation_id} non trouvée.")
    return None