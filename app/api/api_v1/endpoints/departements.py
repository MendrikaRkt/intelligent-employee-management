# app/api/api_v1/endpoints/departements.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Any

from app import crud, schemas # Utilise-les __init__.py
from app.db.session import get_db

router = APIRouter(
    tags=["Départements"] # Tag pour Swagger UI
)

@router.post("/", response_model=schemas.Departement, status_code=status.HTTP_201_CREATED)
async def create_new_departement(
    departement: schemas.DepartementCreate,
    db: Session = Depends(get_db)
):
    """
    Crée un nouveau département.
    Vérifie si le nom existe déjà.
    """
    existing_departement = crud.departement.get_departement_by_nom(db, nom=departement.nom)
    if existing_departement:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Un département nommé '{departement.nom}' existe déjà."
        )
    try:
        created_dept = crud.departement.create_departement(db=db, departement=departement)
        return created_dept
    except ValueError as e: # Attrape l'erreur du CRUD si la vérification initiale a échoué (race condition?)
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/", response_model=List[schemas.Departement])
async def read_all_departements(
    skip: int = 0,
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """
    Récupère la liste de tous les départements avec pagination.
    """
    departements = crud.departement.get_departements(db, skip=skip, limit=limit)
    return departements

@router.get("/{departement_id}", response_model=schemas.Departement)
async def read_single_departement(
    departement_id: int,
    db: Session = Depends(get_db)
):
    """
    Récupère un département spécifique par son ID.
    """
    db_departement = crud.departement.get_departement(db, departement_id=departement_id)
    if db_departement is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Le département avec l'ID {departement_id} n'a pas été trouvé."
        )
    return db_departement

@router.put("/{departement_id}", response_model=schemas.Departement)
async def update_existing_departement(
    departement_id: int,
    departement_in: schemas.DepartementUpdate,
    db: Session = Depends(get_db)
):
    """
    Met à jour un département existant.
    Vérifie si le nouveau nom est déjà pris par un autre département.
    """
    db_departement = crud.departement.get_departement(db, departement_id=departement_id)
    if db_departement is None:
         raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Le département avec l'ID {departement_id} n'a pas été trouvé."
        )

    try:
        updated_dept = crud.departement.update_departement(
            db=db, departement_id=departement_id, departement_update=departement_in
        )
        return updated_dept
    except ValueError as e: # Attrape l'erreur d'unicité du nom du CRUD
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e: # Autres erreurs potentielles
        # Logguer l'erreur e
         raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la mise à jour du département."
        )


@router.delete("/{departement_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_departement(
    departement_id: int,
    db: Session = Depends(get_db)
) -> None:
    """
    Supprime un département existant par son ID.
    Retourne 409 Conflict si le département ne peut pas être supprimé (ex: employés liés).
    """
    db_departement = crud.departement.get_departement(db, departement_id=departement_id)
    if db_departement is None:
        # Ou retourner 204 directement car la ressource n'existe plus (idempotent)
         raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Le département avec l'ID {departement_id} n'a pas été trouvé."
        )

    try:
        crud.departement.delete_departement(db=db, departement_id=departement_id)
    except Exception as e: # Attrape les erreurs d'intégrité (FK) ou ValueError du CRUD
        # Logguer l'erreur e
        # On pourrait vérifier le type d'erreur pour être plus précis
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Impossible de supprimer le département {departement_id}. Il est peut-être lié à des employés. Erreur: {e}"
        )
    return None # Retourne 204 No Content si succès