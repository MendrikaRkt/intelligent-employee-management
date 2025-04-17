# app/api/api_v1/endpoints/employes.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Any

from app import crud, models, schemas # Utilise les __init__.py pour importer
from app.db.session import get_db # Importe la dépendance de session

router = APIRouter(
    # prefix="/employes", # Préfixe pour toutes les routes de ce routeur
    tags=["Employés"]    # Tag pour la documentation Swagger UI
)

@router.post("/", response_model=schemas.Employe, status_code=status.HTTP_201_CREATED)
async def create_new_employe(
    employe: schemas.EmployeCreate,
    db: Session = Depends(get_db)
):
    """
    Crée un nouvel employé.

    - **nom**: Nom de l'employé (requis)
    - **prenom**: Prénom de l'employé (requis)
    - **email**: Email unique de l'employé (requis)
    - **date_embauche**: Date d'embauche (optionnel)
    - **position**: Poste de l'employé (optionnel)
    - **departement_id**: ID du département associé (optionnel)
    - **is_active**: Statut actif (défaut: true)
    """
    # Vérification optionnelle: l'email existe-t-il déjà ?
    db_employe = crud.get_employe_by_email(db, email=employe.email)
    if db_employe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"L'email '{employe.email}' est déjà enregistré."
        )
    # Vérification optionnelle: le département existe-t-il ?
    if employe.departement_id:
         # Note: Vous devrez créer crud.departement.get_departement
         db_departement = crud.departement.get_departement(db, departement_id=employe.departement_id)
         if not db_departement:
             raise HTTPException(
                 status_code=status.HTTP_404_NOT_FOUND,
                 detail=f"Le département avec l'ID {employe.departement_id} n'existe pas."
             )

    created_employe = crud.create_employe(db=db, employe=employe)
    return created_employe

@router.get("/", response_model=List[schemas.Employe])
async def read_all_employes(
    skip: int = 0,
    limit: int = Query(default=100, ge=1, le=500), # Limite avec validation
    db: Session = Depends(get_db)
):
    """
    Récupère la liste de tous les employés avec pagination.

    - **skip**: Nombre d'employés à sauter.
    - **limit**: Nombre maximum d'employés à retourner (entre 1 et 500).
    """
    employes = crud.get_employes(db, skip=skip, limit=limit)
    return employes

@router.get("/{employe_id}", response_model=schemas.Employe)
async def read_single_employe(
    employe_id: int,
    db: Session = Depends(get_db)
):
    """
    Récupère un employé spécifique par son ID.
    """
    db_employe = crud.get_employe(db, employe_id=employe_id)
    if db_employe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"L'employé avec l'ID {employe_id} n'a pas été trouvé."
        )
    return db_employe

@router.put("/{employe_id}", response_model=schemas.Employe)
async def update_existing_employe(
    employe_id: int,
    employe_in: schemas.EmployeUpdate,
    db: Session = Depends(get_db)
):
    """
    Met à jour un employé existant.
    Seuls les champs fournis dans le corps de la requête seront mis à jour.
    """
    db_employe = crud.get_employe(db, employe_id=employe_id)
    if db_employe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"L'employé avec l'ID {employe_id} n'a pas été trouvé."
        )

    # Vérification si l'email est changé et s'il existe déjà pour un AUTRE employé
    if employe_in.email and employe_in.email != db_employe.email:
        existing_employe = crud.get_employe_by_email(db, email=employe_in.email)
        if existing_employe and existing_employe.id != employe_id:
             raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"L'email '{employe_in.email}' est déjà utilisé par un autre employé."
            )

    # Vérification si le département est changé et s'il existe
    if employe_in.departement_id and employe_in.departement_id != db_employe.departement_id:
         db_departement = crud.departement.get_departement(db, departement_id=employe_in.departement_id)
         if not db_departement:
             raise HTTPException(
                 status_code=status.HTTP_404_NOT_FOUND,
                 detail=f"Le département avec l'ID {employe_in.departement_id} n'existe pas."
             )

    updated_employe = crud.update_employe(db=db, employe_id=employe_id, employe_update=employe_in)
    # update_employe devrait renvoyer None si l'employé n'est pas trouvé, mais nous l'avons déjà vérifié.
    # Si pour une raison quelconque l'update échoue autrement, `updated_employe` pourrait être None ou une erreur serait levée.
    if updated_employe is None:
         raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, # Ou autre code approprié
            detail="La mise à jour de l'employé a échoué."
        )
    return updated_employe

@router.delete("/{employe_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_employe(
    employe_id: int,
    db: Session = Depends(get_db)
) -> None:
    """
    Supprime un employé existant par son ID.
    Retourne un statut 204 No Content en cas de succès.
    """
    deleted_employe = crud.delete_employe(db=db, employe_id=employe_id)
    if deleted_employe is None:
         raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"L'employé avec l'ID {employe_id} n'a pas été trouvé pour suppression."
        )
    # Pas de return car le status code est 204
    return None

# --- Ajouter d'autres endpoints si nécessaire ---
# Par exemple, pour lister les employés d'un département spécifique

@router.get("/by_departement/{departement_id}", response_model=List[schemas.Employe])
async def read_employes_by_departement(
    departement_id: int,
    skip: int = 0,
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """
    Récupère la liste des employés pour un département spécifique.
    """
    # Vérifier d'abord si le département existe (nécessite crud.departement.get_departement)
    db_departement = crud.departement.get_departement(db, departement_id=departement_id)
    if not db_departement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Le département avec l'ID {departement_id} n'existe pas."
        )

    employes = crud.get_employes_by_departement(db, departement_id=departement_id, skip=skip, limit=limit)
    return employes