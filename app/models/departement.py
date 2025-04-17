# app/models/departement.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from .base import Base # Importation relative

class Departement(Base):
    __tablename__ = "departements" # Nom de la table dans la BDD

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), unique=True, index=True, nullable=False) # Longueur max 100, unique, indexé, requis

    # Relation inverse : Un département peut avoir plusieurs employés
    employes = relationship("Employe", back_populates="departement") # "Employe" est le nom de la classe, "departement" est le nom de l'attribut de relation dans la classe Employe

    def __repr__(self):
        return f"<Departement(id={self.id}, nom='{self.nom}')>"