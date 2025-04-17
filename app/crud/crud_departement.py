# app/crud/crud_departement.py
from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.departement import Departement as DepartementModel # Renommer pour clarté
from app.schemas.departement import DepartementCreate, DepartementUpdate

def get_departement(db: Session, departement_id: int) -> Optional[DepartementModel]:
    """
    Récupère un département par son ID.

    Args:
        db: Session de base de données SQLAlchemy.
        departement_id: ID du département à récupérer.

    Returns:
        L'objet DepartementModel s'il est trouvé, sinon None.
    """
    return db.query(DepartementModel).filter(DepartementModel.id == departement_id).first()

def get_departement_by_nom(db: Session, nom: str) -> Optional[DepartementModel]:
    """
    Récupère un département par son nom (qui doit être unique).

    Args:
        db: Session de base de données SQLAlchemy.
        nom: Nom du département à récupérer.

    Returns:
        L'objet DepartementModel s'il est trouvé, sinon None.
    """
    return db.query(DepartementModel).filter(DepartementModel.nom == nom).first()

def get_departements(db: Session, skip: int = 0, limit: int = 100) -> List[DepartementModel]:
    """
    Récupère une liste de départements avec pagination.

    Args:
        db: Session de base de données SQLAlchemy.
        skip: Nombre d'enregistrements à sauter.
        limit: Nombre maximum d'enregistrements à retourner.

    Returns:
        Une liste d'objets DepartementModel.
    """
    return db.query(DepartementModel).offset(skip).limit(limit).all()

def create_departement(db: Session, departement: DepartementCreate) -> DepartementModel:
    """
    Crée un nouveau département dans la base de données.
    Vérifie d'abord si un département avec le même nom existe déjà.

    Args:
        db: Session de base de données SQLAlchemy.
        departement: Objet DepartementCreate contenant les données.

    Returns:
        L'objet DepartementModel nouvellement créé.

    Raises:
        ValueError: Si un département avec le même nom existe déjà.
    """
    # Vérification de l'unicité du nom avant la création
    existing_departement = get_departement_by_nom(db, nom=departement.nom)
    if existing_departement:
        # Il est souvent préférable de gérer cette logique (lever une HTTPException)
        # au niveau de l'endpoint API plutôt que dans le CRUD.
        # Mais une vérification ici peut être utile.
        # On peut aussi simplement retourner l'existant ou lever une exception simple.
        raise ValueError(f"Un département nommé '{departement.nom}' existe déjà.")

    db_departement = DepartementModel(**departement.model_dump())
    db.add(db_departement)
    db.commit()
    db.refresh(db_departement)
    return db_departement

def update_departement(
    db: Session,
    departement_id: int,
    departement_update: DepartementUpdate
) -> Optional[DepartementModel]:
    """
    Met à jour un département existant.

    Args:
        db: Session de base de données SQLAlchemy.
        departement_id: ID du département à mettre à jour.
        departement_update: Objet DepartementUpdate contenant le champ à mettre à jour.

    Returns:
        L'objet DepartementModel mis à jour s'il existe, sinon None.

    Raises:
        ValueError: Si le nouveau nom est déjà pris par un autre département.
    """
    db_departement = get_departement(db, departement_id=departement_id)
    if db_departement is None:
        return None

    update_data = departement_update.model_dump(exclude_unset=True)

    # Vérification si le nom est changé et s'il est déjà pris
    if "nom" in update_data and update_data["nom"] != db_departement.nom:
        existing_departement = get_departement_by_nom(db, nom=update_data["nom"])
        if existing_departement and existing_departement.id != departement_id:
            raise ValueError(f"Un autre département nommé '{update_data['nom']}' existe déjà.")
        db_departement.nom = update_data["nom"] # Mettre à jour le nom

    # Potentiellement d'autres champs à mettre à jour si ajoutés au modèle/schéma

    db.add(db_departement)
    db.commit()
    db.refresh(db_departement)
    return db_departement

def delete_departement(db: Session, departement_id: int) -> Optional[DepartementModel]:
    """
    Supprime un département.
    Attention: Gérer les employés liés à ce département avant suppression
              (par exemple, les mettre à NULL ou empêcher la suppression).
              La logique actuelle ne gère pas ce cas explicitement,
              cela dépendra des contraintes de clé étrangère et de la stratégie souhaitée.

    Args:
        db: Session de base de données SQLAlchemy.
        departement_id: ID du département à supprimer.

    Returns:
        L'objet DepartementModel supprimé s'il existait, sinon None.
    """
    db_departement = get_departement(db, departement_id=departement_id)
    if db_departement is None:
        return None

    # --- Logique de gestion des employés liés (Exemple) ---
    # Option 1: Vérifier s'il y a des employés et empêcher la suppression
    # if db_departement.employes: # Accès via la relation définie dans le modèle
    #    raise ValueError(f"Impossible de supprimer le département '{db_departement.nom}' car il contient des employés.")

    # Option 2: Mettre departement_id à NULL pour les employés liés (si FK le permet)
    # for employe in db_departement.employes:
    #     employe.departement_id = None
    #     db.add(employe)
    # Note: Ceci nécessite un commit séparé ou doit être géré dans la même transaction.

    # Option 3: Compter sur la cascade ou la configuration FK (SET NULL, RESTRICT)
    # C'est souvent géré au niveau de la base de données ou de SQLAlchemy.
    # Par défaut, si des employés existent, une erreur d'intégrité sera levée au commit.
    # -------------------------------------------------------

    db.delete(db_departement)
    try:
        db.commit()
    except Exception as e:
        db.rollback() # Annuler la transaction en cas d'erreur (ex: violation FK)
        # Renvoyer l'erreur ou la logger
        print(f"Erreur lors de la suppression du département {departement_id}: {e}")
        # Vous pourriez vouloir lever une exception spécifique ici
        raise e # Ou retourner None ou un message d'erreur

    return db_departement