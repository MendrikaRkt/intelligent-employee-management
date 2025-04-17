# app/schemas/pointage.py
from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional
from datetime import date, datetime

class PointageBase(BaseModel):
    date_pointage: date
    heure_arrivee: datetime # Supposant que le modèle utilise timezone=True
    heure_depart: Optional[datetime] = None
    employe_id: int

    @field_validator('heure_depart')
    def check_departure_after_arrival(cls, v, values):
        # Assurez-vous que 'heure_arrivee' est déjà validé et présent
        if v is not None and 'heure_arrivee' in values.data and v <= values.data['heure_arrivee']:
            raise ValueError("L'heure de départ doit être postérieure à l'heure d'arrivée")
        return v

    # Assurez-vous que les objets datetime sont conscients du fuseau horaire si nécessaire
    # model_config = ConfigDict(arbitrary_types_allowed=True) # Si vous utilisez des types non std

class PointageCreate(PointageBase):
    pass

class PointageUpdate(BaseModel):
    # Principalement pour mettre à jour l'heure de départ
    heure_depart: Optional[datetime] = None
    # On pourrait autoriser la modification d'autres champs si nécessaire

    # model_config = ConfigDict(extra='ignore') # Si vous voulez ignorer les champs non définis

class Pointage(PointageBase):
    id: int
    model_config = ConfigDict(from_attributes=True)