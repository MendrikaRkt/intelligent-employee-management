# app/crud/crud_employe.py
from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.employe import Employe as EmployeModel # Renommer pour éviter conflit de nom
from app.schemas.employe import EmployeCreate, EmployeUpdate

def get_employe(db: Session, employe_id: int) -> Optional[EmployeModel]:
    """
    Récupère un employé par son ID.

    Args:
        db: Session de base de données SQLAlchemy.
        employe_id: ID de l'employé à récupérer.

    Returns:
        L'objet EmployeModel s'il est trouvé, sinon None.
    """
    return db.query(EmployeModel).filter(EmployeModel.id == employe_id).first()

def get_employe_by_email(db: Session, email: str) -> Optional[EmployeModel]:
    """
    Récupère un employé par son adresse email.

    Args:
        db: Session de base de données SQLAlchemy.
        email: Email de l'employé à récupérer.

    Returns:
        L'objet EmployeModel s'il est trouvé, sinon None.
    """
    return db.query(EmployeModel).filter(EmployeModel.email == email).first()

def get_employes(db: Session, skip: int = 0, limit: int = 100) -> List[EmployeModel]:
    """
    Récupère une liste d'employés avec pagination.

    Args:
        db: Session de base de données SQLAlchemy.
        skip: Nombre d'enregistrements à sauter (pour pagination).
        limit: Nombre maximum d'enregistrements à retourner.

    Returns:
        Une liste d'objets EmployeModel.
    """
    return db.query(EmployeModel).offset(skip).limit(limit).all()

def create_employe(db: Session, employe: EmployeCreate) -> EmployeModel:
    """
    Crée un nouvel employé dans la base de données.

    Args :
        db : Session de base de données SQLAlchemy.
        Employe: Objet EmployeCreate contenant les données du nouvel employé.

    Returns :
        L'objet EmployeModel nouvellement créé.
    """
    # Créer une instance du modèle SQLAlchemy à partir des données du schéma Pydantic
    db_employe = EmployeModel(**employe.model_dump())
    db.add(db_employe) # Ajoute l'objet à la session
    db.commit()      # Valide la transaction (sauvegarde en BDD)
    db.refresh(db_employe) # Rafraîchit l'objet avec les données de la BDD (ex: l'ID généré)
    return db_employe

def update_employe(
    db: Session,
    employe_id: int,
    employe_update: EmployeUpdate
) -> Optional[EmployeModel]:
    """
    Met à jour un employé existant.

    Args:
        db: Session de base de données SQLAlchemy.
        employe_id: ID de l'employé à mettre à jour.
        employe_update: Objet EmployeUpdate contenant les champs à mettre à jour.

    Returns:
        L'objet EmployeModel mis à jour s'il existe, sinon None.
    """
    db_employe = get_employe(db, employe_id=employe_id)
    if db_employe is None:
        return None # Ou lever une exception si préféré

    # Récupérer les données à mettre à jour sous forme de dictionnaire
    # exclude_unset=True ne prend que les champs explicitement fournis dans la requête
    update_data = employe_update.model_dump(exclude_unset=True)

    # Mettre à jour les champs du modèle SQLAlchemy
    for key, value in update_data.items():
        setattr(db_employe, key, value)

    db.add(db_employe) # Peut être implicite si l'objet est déjà dans la session, mais ne nuit pas
    db.commit()
    db.refresh(db_employe)
    return db_employe

def delete_employe(db: Session, employe_id: int) -> Optional[EmployeModel]:
    """
    Supprime un employé de la base de données.

    Args:
        db: Session de base de données SQLAlchemy.
        employe_id: ID de l'employé à supprimer.

    Returns:
        L'objet EmployeModel qui vient d'être supprimé s'il existait, sinon None.
    """
    db_employe = get_employe(db, employe_id=employe_id)
    if db_employe is None:
        return None

    db.delete(db_employe)
    db.commit()
    return db_employe

# --- Potentiellement d'autres fonctions CRUD ---
# Par exemple, rechercher des employés par nom, par département, etc.
def get_employes_by_departement(db: Session, departement_id: int, skip: int = 0, limit: int = 100) -> List[EmployeModel]:
    """Récupère les employés d'un département spécifique."""
    return db.query(EmployeModel).filter(EmployeModel.departement_id == departement_id).offset(skip).limit(limit).all()