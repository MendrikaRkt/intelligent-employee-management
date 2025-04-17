# app/schemas/departement.py
from pydantic import BaseModel, ConfigDict
from typing import Optional, List

# Schéma de base (pour la création et la mise à jour simple)
class DepartementBase(BaseModel):
    nom: str

# Schéma pour la création (hérite de Base)
class DepartementCreate(DepartementBase):
    pass # Pas de champs supplémentaires pour l'instant

# Schéma pour la mise à jour (nom optionnel)
class DepartementUpdate(BaseModel):
    nom: Optional[str] = None

    model_config = ConfigDict(extra='ignore')

# Schéma pour la lecture (inclut l'ID)
class Departement(DepartementBase):
    id: int

    # Permet de créer le schéma depuis un objet ORM
    model_config = ConfigDict(from_attributes=True)

# Optionnel : Schéma pour lire un département avec la liste de ses employés
# from .employe import Employe # Attention aux imports circulaires potentiels

# class DepartementWithEmployes(Departement):
#    employes: List[Employe] = []