# app/api/api_v1/endpoints/pointages.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app import crud, schemas
from app.db.session import get_db

router = APIRouter(
    tags=["Pointages"]
)

@router.post("/", response_model=schemas.Pointage, status_code=status.HTTP_201_CREATED)
async def create_new_pointage(
    pointage: schemas.PointageCreate,
    db: Session = Depends(get_db)
):
    """
    Crée un nouvel enregistrement de pointage pour un employé.
    Vérifie l'existence de l'employé.
    """
    try:
        # La validation de l'employé est maintenant dans le CRUD
        # La validation heure_depart vs heure_arrivee est dans le schéma Pydantic
        created_pointage = crud.pointage.create_pointage(db=db, pointage=pointage)
        return created_pointage
    except ValueError as e:
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
         # Log error e
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erreur interne lors de la création du pointage.")

@router.get("/", response_model=List[schemas.Pointage])
async def read_all_pointages(
    skip: int = 0,
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """
    Récupère la liste de tous les pointages (peut être volumineux).
    """
    pointages = crud.pointage.get_pointages(db, skip=skip, limit=limit)
    return pointages

@router.get("/by_employe/{employe_id}", response_model=List[schemas.Pointage])
async def read_pointages_for_employe(
    employe_id: int,
    start_date: Optional[date] = Query(None, description="Date de début (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="Date de fin (YYYY-MM-DD)"),
    skip: int = 0,
    limit: int = Query(default=100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Récupère les pointages pour un employé spécifique, avec filtre de date optionnel.
    """
    # Vérifier si l'employé existe
    db_employe = crud.employe.get_employe(db, employe_id=employe_id)
    if not db_employe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Employé avec ID {employe_id} non trouvé.")

    pointages = crud.pointage.get_pointages_by_employe(
        db, employe_id=employe_id, start_date=start_date, end_date=end_date, skip=skip, limit=limit
    )
    return pointages

@router.get("/{pointage_id}", response_model=schemas.Pointage)
async def read_single_pointage(
    pointage_id: int,
    db: Session = Depends(get_db)
):
    """
    Récupère un pointage spécifique par son ID.
    """
    db_pointage = crud.pointage.get_pointage(db, pointage_id=pointage_id)
    if db_pointage is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Pointage avec ID {pointage_id} non trouvé.")
    return db_pointage

@router.put("/{pointage_id}", response_model=schemas.Pointage)
async def update_existing_pointage(
    pointage_id: int,
    pointage_in: schemas.PointageUpdate,
    db: Session = Depends(get_db)
):
    """
    Met à jour un pointage existant (typiquement l'heure de départ).
    """
    try:
        updated_pointage = crud.pointage.update_pointage(db, pointage_id=pointage_id, pointage_update=pointage_in)
        if updated_pointage is None:
             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Pointage avec ID {pointage_id} non trouvé.")
        return updated_pointage
    except ValueError as e: # Erreur de validation (ex: heure départ <= arrivée)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        # Log error e
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erreur interne lors de la mise à jour du pointage.")


@router.delete("/{pointage_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_pointage(
    pointage_id: int,
    db: Session = Depends(get_db)
) -> None:
    """
    Supprime un pointage existant par son ID.
    """
    deleted = crud.pointage.delete_pointage(db, pointage_id=pointage_id)
    if deleted is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Pointage avec ID {pointage_id} non trouvé.")
    return None