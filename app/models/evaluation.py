# app/models/evaluation.py
from sqlalchemy import Column, Integer, String, Text, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base
from .employe import Employe # Importation pour ForeignKey

class Evaluation(Base):
    __tablename__ = "evaluations"

    id = Column(Integer, primary_key=True, index=True)
    date_evaluation = Column(Date, nullable=False, default=func.current_date(), index=True) # Date de l'évaluation
    evaluateur = Column(String(100), nullable=True) # Nom ou ID de la personne qui évalue
    score_global = Column(Float, nullable=True) # Un score numérique global
    commentaires = Column(Text, nullable=True) # Commentaires textuels libres

    # On pourrait ajouter des champs plus spécifiques si nécessaire (ex: score_communication, score_technique...)
    # Pour plus de flexibilité, on pourrait utiliser un champ JSON pour stocker des critères variables :
    # criteres_scores = Column(JSON, nullable=True)

    # Clé étrangère vers l'employé évalué
    employe_id = Column(Integer, ForeignKey("employes.id"), nullable=False, index=True)

    # Relation Many-to-One
    employe = relationship("Employe", back_populates="evaluations")

    def __repr__(self):
        return f"<Evaluation(id={self.id}, employe_id={self.employe_id}, date='{self.date_evaluation}', score={self.score_global})>"