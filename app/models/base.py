# app/models/base.py
from sqlalchemy.orm import declarative_base
from sqlalchemy import MetaData

# Définir une convention de nommage pour les contraintes (FK, PK, Index, etc.)
metadata = MetaData(naming_convention={
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
})

# Créer la classe de base
Base = declarative_base(metadata=metadata)