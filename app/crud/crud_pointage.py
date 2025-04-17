# app/crud/crud_pointage.py
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.models.pointage import Pointage as PointageModel
from app.schemas.pointage import PointageCreate, PointageUpdate
from app.models.employe import Employe as EmployeModel # Pour vérifier l'existence de l'employé

def get_pointage(db: Session, pointage_id: int) -> Optional[PointageModel]:
    return db.query(PointageModel).filter(PointageModel.id == pointage_id).first()

def get_pointages(db: Session, skip: int = 0, limit: int = 100) -> List[PointageModel]:
    return db.query(PointageModel).order_by(PointageModel.date_pointage.desc(), PointageModel.heure_arrivee.desc()).offset(skip).limit(limit).all()

def get_pointages_by_employe(
    db: Session, employe_id: int, start_date: Optional[date] = None, end_date: Optional[date] = None, skip: int = 0, limit: int = 100
) -> List[PointageModel]:
    query = db.query(PointageModel).filter(PointageModel.employe_id == employe_id)
    if start_date:
        query = query.filter(PointageModel.date_pointage >= start_date)
    if end_date:
        query = query.filter(PointageModel.date_pointage <= end_date)
    return query.order_by(PointageModel.date_pointage.desc(), PointageModel.heure_arrivee.desc()).offset(skip).limit(limit).all()

def get_pointage_by_employe_and_date(db: Session, employe_id: int, date_pointage: date) -> Optional[PointageModel]:
    """Trouve un pointage pour un employé à une date donnée (peut y en avoir plusieurs si entrées/sorties multiples non gérées)."""
    # Attention: peut retourner le premier trouvé s'il y a plusieurs pointages par jour
    return db.query(PointageModel).filter(
        PointageModel.employe_id == employe_id,
        PointageModel.date_pointage == date_pointage
    ).first()


def create_pointage(db: Session, pointage: PointageCreate) -> PointageModel:
    # Vérifier si l'employé existe
    db_employe = db.query(EmployeModel).filter(EmployeModel.id == pointage.employe_id).first()
    if not db_employe:
        raise ValueError(f"L'employé avec l'ID {pointage.employe_id} n'existe pas.")
    # Ajouter d'autres logiques si nécessaire (ex: vérifier si déjà un pointage pour ce jour)

    db_pointage = PointageModel(**pointage.model_dump())
    db.add(db_pointage)
    db.commit()
    db.refresh(db_pointage)
    return db_pointage

def update_pointage(
    db: Session,
    pointage_id: int,
    pointage_update: PointageUpdate
) -> Optional[PointageModel]:
    db_pointage = get_pointage(db, pointage_id=pointage_id)
    if db_pointage is None:
        return None

    update_data = pointage_update.model_dump(exclude_unset=True)

    # Valider heure_depart vs heure_arrivee existante
    if 'heure_depart' in update_data and update_data['heure_depart'] is not None:
        if update_data['heure_depart'] <= db_pointage.heure_arrivee:
             raise ValueError("L'heure de départ doit être postérieure à l'heure d'arrivée existante.")
        db_pointage.heure_depart = update_data['heure_depart']

    # Mettre à jour d'autres champs si présents dans update_data et autorisés

    db.add(db_pointage)
    db.commit()
    db.refresh(db_pointage)
    return db_pointage

def delete_pointage(db: Session, pointage_id: int) -> Optional[PointageModel]:
    db_pointage = get_pointage(db, pointage_id=pointage_id)
    if db_pointage is None:
        return None
    db.delete(db_pointage)
    db.commit()
    return db_pointage