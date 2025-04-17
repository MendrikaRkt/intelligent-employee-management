# app/schemas/evaluation.py
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Dict, Any
from datetime import date

class EvaluationBase(BaseModel):
    date_evaluation: Optional[date] = Field(default_factory=date.today) # Par défaut à aujourd'hui si non fourni
    evaluateur: Optional[str] = None
    score_global: Optional[float] = Field(None, ge=0, le=100) # Score entre 0 et 100 (exemple)
    commentaires: Optional[str] = None
    employe_id: int
    # Si vous utilisez un champ JSON pour des critères flexibles:
    # criteres_scores: Optional[Dict[str, Any]] = None

class EvaluationCreate(EvaluationBase):
    # score_global: float = Field(..., ge=0, le=100) # Rendre le score requis à la création?
    pass # Hérite tels quels pour l'instant

class EvaluationUpdate(BaseModel):
    # Tous les champs sont optionnels pour la mise à jour
    date_evaluation: Optional[date] = None
    evaluateur: Optional[str] = None
    score_global: Optional[float] = Field(None, ge=0, le=100)
    commentaires: Optional[str] = None
    # Peut-on changer l'employé évalué ? Probablement pas. employe_id n'est pas inclus.
    # criteres_scores: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(extra='ignore')

class Evaluation(EvaluationBase):
    id: int
    # Remplacer date_evaluation optionnelle de Base par une requise ici
    date_evaluation: date

    model_config = ConfigDict(from_attributes=True)