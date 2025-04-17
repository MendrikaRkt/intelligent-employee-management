# app/models/pointage.py
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base
from .employe import Employe # Importation pour ForeignKey

class Pointage(Base):
    __tablename__ = "pointages"

    id = Column(Integer, primary_key=True, index=True)
    date_pointage = Column(Date, nullable=False, index=True) # Date du pointage
    heure_arrivee = Column(DateTime(timezone=True), nullable=False) # Heure d'arrivée exacte avec timezone
    heure_depart = Column(DateTime(timezone=True), nullable=True) # Heure de départ, peut être null si l'employé est toujours présent ou oubli

    # Clé étrangère vers l'employé
    employe_id = Column(Integer, ForeignKey("employes.id"), nullable=False, index=True)

    # Relation Many-to-One : Plusieurs pointages appartiennent à un employé
    employe = relationship("Employe", back_populates="pointages")

    def __repr__(self):
        return f"<Pointage(id={self.id}, employe_id={self.employe_id}, date='{self.date_pointage}', arrivee='{self.heure_arrivee}')>"