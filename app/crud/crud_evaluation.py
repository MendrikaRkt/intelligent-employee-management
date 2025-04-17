# app/crud/crud_evaluation.py
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.models.evaluation import Evaluation as EvaluationModel
from app.schemas.evaluation import EvaluationCreate, EvaluationUpdate
from app.models.employe import Employe as EmployeModel # Pour vérifier l'employé

def get_evaluation(db: Session, evaluation_id: int) -> Optional[EvaluationModel]:
    return db.query(EvaluationModel).filter(EvaluationModel.id == evaluation_id).first()

def get_evaluations(db: Session, skip: int = 0, limit: int = 100) -> List[EvaluationModel]:
    # Ordonner par date décroissante par défaut
    return db.query(EvaluationModel).order_by(EvaluationModel.date_evaluation.desc()).offset(skip).limit(limit).all()

def get_evaluations_by_employe(
    db: Session, employe_id: int, skip: int = 0, limit: int = 100
) -> List[EvaluationModel]:
    # Vérifier si l'employé existe pourrait être fait ici ou dans l'endpoint
    return db.query(EvaluationModel)\
             .filter(EvaluationModel.employe_id == employe_id)\
             .order_by(EvaluationModel.date_evaluation.desc())\
             .offset(skip).limit(limit).all()

def create_evaluation(db: Session, evaluation: EvaluationCreate) -> EvaluationModel:
    # Vérifier si l'employé existe
    db_employe = db.query(EmployeModel).filter(EmployeModel.id == evaluation.employe_id).first()
    if not db_employe:
        raise ValueError(f"L'employé avec l'ID {evaluation.employe_id} n'existe pas.")

    # Créer l'objet EvaluationModel
    # Si date_evaluation n'est pas fournie dans le schéma, la valeur par défaut du modèle sera utilisée.
    # Pydantic utilise sa propre valeur par défaut (default_factory) si défini.
    db_evaluation = EvaluationModel(**evaluation.model_dump())

    # Si date_evaluation n'est pas dans le schéma et que le modèle a server_default=func.current_date()
    # il faudra peut-être ne pas l'inclure dans model_dump() pour laisser la BDD la générer.
    # Mais ici, Pydantic la génère via default_factory.

    db.add(db_evaluation)
    db.commit()
    db.refresh(db_evaluation)
    return db_evaluation

def update_evaluation(
    db: Session,
    evaluation_id: int,
    evaluation_update: EvaluationUpdate
) -> Optional[EvaluationModel]:
    db_evaluation = get_evaluation(db, evaluation_id=evaluation_id)
    if db_evaluation is None:
        return None

    update_data = evaluation_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        # On ne permet généralement pas de changer employe_id après création
        if key != "employe_id":
             setattr(db_evaluation, key, value)

    db.add(db_evaluation) # Marque l'objet comme modifié
    db.commit()
    db.refresh(db_evaluation)
    return db_evaluation

def delete_evaluation(db: Session, evaluation_id: int) -> Optional[EvaluationModel]:
    db_evaluation = get_evaluation(db, evaluation_id=evaluation_id)
    if db_evaluation is None:
        return None
    db.delete(db_evaluation)
    db.commit()
    return db_evaluation