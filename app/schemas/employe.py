# app/schemas/employe.py
from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import date

# Propriétés partagées (communes à la lecture et création/update)
class EmployeBase(BaseModel):
    nom: str
    prenom: str
    email: EmailStr # Valide automatiquement le format de l'email
    date_embauche: Optional[date] = None
    position: Optional[str] = None
    departement_id: Optional[int] = None
    is_active: Optional[bool] = True

# Propriétés requises pour la création d'un employé
class EmployeCreate(EmployeBase):
    # Tous les champs de EmployeBase sont requis par défaut,
    # sauf ceux marqués Optional.
    # On pourrait ajouter des champs spécifiques à la création si besoin.
    pass # Pour l'instant, hérite simplement

# Propriétés requises pour la mise à jour (tous les champs optionnels)
class EmployeUpdate(BaseModel):
    nom: Optional[str] = None
    prenom: Optional[str] = None
    email: Optional[EmailStr] = None
    date_embauche: Optional[date] = None
    position: Optional[str] = None
    departement_id: Optional[int] = None
    is_active: Optional[bool] = None

    # Permet d'accepter des champs supplémentaires sans erreur,
    # mais ils ne seront pas utilisés si non définis ci-dessus
    model_config = ConfigDict(extra='ignore')


# Propriétés renvoyées par l'API (lecture d'un employé)
# Inclut l'ID auto-généré
class Employe(EmployeBase):
    id: int

    # Configuration pour permettre le mapping depuis un objet ORM SQLAlchemy
    model_config = ConfigDict(from_attributes=True)

# Optionnel: Si vous voulez renvoyer les informations du département lié
# dans la réponse API pour un employé, vous pouvez définir un schéma
# pour le département et l'inclure ici.
# from .departement import Departement # Assurez-vous d'avoir ce schéma aussi
# class EmployeWithDepartement(Employe):
#     departement: Optional[Departement] = None