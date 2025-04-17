# app/models/employe.py
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func # Pour les fonctions SQL comme now()

from .base import Base
# Importation pour la relation ForeignKey et la définition du type de relation
from .departement import Departement

class Employe(Base):
    __tablename__ = "employes"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False) # Email doit être unique
    date_embauche = Column(Date, nullable=True) # Peut être null si non connu immédiatement
    position = Column(String(100), nullable=True) # Poste occupé
    is_active = Column(Boolean, default=True) # Pour désactiver un employé sans le supprimer

    # Clé étrangère vers le département
    departement_id = Column(Integer, ForeignKey("departements.id"), nullable=True) # Peut être null si l'employé n'est pas encore affecté

    # Relation Many-to-One : Plusieurs employés appartiennent à un département
    departement = relationship("Departement", back_populates="employes")

    # Relations One-to-Many inverses
    pointages = relationship("Pointage", back_populates="employe", cascade="all, delete-orphan") # Si on supprime un employé, ses pointages sont supprimés
    evaluations = relationship("Evaluation", back_populates="employe", cascade="all, delete-orphan")
    simulations = relationship("Simulation", back_populates="employe", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Employe(id={self.id}, nom='{self.nom}', prenom='{self.prenom}', email='{self.email}')>"