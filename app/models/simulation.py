# app/models/simulation.py
from sqlalchemy import Column, Integer, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base
from .employe import Employe # Importation pour ForeignKey

class Simulation(Base):
    __tablename__ = "simulations"

    id = Column(Integer, primary_key=True, index=True)
    date_simulation = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True) # Quand la simulation a été lancée

    # Clé étrangère vers l'employé concerné par la simulation
    employe_id = Column(Integer, ForeignKey("employes.id"), nullable=False, index=True)

    # Paramètres utilisés pour lancer la simulation (sous forme de JSON)
    parametres_entree = Column(JSON, nullable=True)
    # Exemple: {'scenario': 'augmentation_charge', 'duree_mois': 6, 'facteur_stress': 1.2}

    # Résultats de la simulation (probablement une série temporelle, stockée en JSON)
    resultats_simulation = Column(JSON, nullable=True)
    # Exemple: {'temps': [0, 1, 2, 3, 4, 5, 6], 'performance_predite': [75, 76, 74, 70, 68, 69, 71]}

    # Relation Many-to-One
    employe = relationship("Employe", back_populates="simulations")

    def __repr__(self):
        return f"<Simulation(id={self.id}, employe_id={self.employe_id}, date='{self.date_simulation}')>"