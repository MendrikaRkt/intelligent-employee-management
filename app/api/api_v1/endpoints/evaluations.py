# app/api/api_v1/endpoints/evaluations.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app import crud, schemas
from app.db.session import get_db

router = APIRouter(
    tags=["Évaluations"]
)

@router.post("/", response_model=schemas.Evaluation, status_code=status.HTTP_201_CREATED)
async def create_new_evaluation(
    evaluation: schemas.EvaluationCreate,
    db: Session = Depends(get_db)
):
    """
    Crée une nouvelle évaluation pour un employé.
    Vérifie l'existence de l'employé.
    """
    try:
        # La validation de l'employé est dans le CRUD
        created_evaluation = crud.evaluation.create_evaluation(db=db, evaluation=evaluation)
        return created_evaluation
    except ValueError as e: # Erreur si employé non trouvé
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) # 404 car la ressource liée (employé) n'existe pas
    except Exception as e:
        # Log error e
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erreur interne lors de la création de l'évaluation.")

@router.get("/", response_model=List[schemas.Evaluation])
async def read_all_evaluations(
    skip: int = 0,
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """
    Récupère la liste de toutes les évaluations.
    """
    evaluations = crud.evaluation.get_evaluations(db, skip=skip, limit=limit)
    return evaluations

@router.get("/by_employe/{employe_id}", response_model=List[schemas.Evaluation])
async def read_evaluations_for_employe(
    employe_id: int,
    skip: int = 0,
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """
    Récupère les évaluations pour un employé spécifique.
    """
    # Vérifier si l'employé existe
    db_employe = crud.employe.get_employe(db, employe_id=employe_id)
    if not db_employe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Employé avec ID {employe_id} non trouvé.")

    evaluations = crud.evaluation.get_evaluations_by_employe(
        db, employe_id=employe_id, skip=skip, limit=limit
    )
    return evaluations

@router.get("/{evaluation_id}", response_model=schemas.Evaluation)
async def read_single_evaluation(
    evaluation_id: int,
    db: Session = Depends(get_db)
):
    """
    Récupère une évaluation spécifique par son ID.
    """
    db_evaluation = crud.evaluation.get_evaluation(db, evaluation_id=evaluation_id)
    if db_evaluation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Évaluation avec ID {evaluation_id} non trouvée.")
    return db_evaluation

@router.put("/{evaluation_id}", response_model=schemas.Evaluation)
async def update_existing_evaluation(
    evaluation_id: int,
    evaluation_in: schemas.EvaluationUpdate,
    db: Session = Depends(get_db)
):
    """
    Met à jour une évaluation existante.
    """
    updated_evaluation = crud.evaluation.update_evaluation(db, evaluation_id=evaluation_id, evaluation_update=evaluation_in)
    if updated_evaluation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Évaluation avec ID {evaluation_id} non trouvée.")
    return updated_evaluation

@router.delete("/{evaluation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_evaluation(
    evaluation_id: int,
    db: Session = Depends(get_db)
) -> None:
    """
    Supprime une évaluation existante par son ID.
    """
    deleted = crud.evaluation.delete_evaluation(db, evaluation_id=evaluation_id)
    if deleted is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Évaluation avec ID {evaluation_id} non trouvée.")
    return None