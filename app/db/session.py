# app/db/session.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Charger les variables d'environnement du fichier .env
load_dotenv()

# Récupérer l'URL de la base de données depuis les variables d'environnement
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL is None:
    raise ValueError("La variable d'environnement DATABASE_URL n'est pas définie.")

# Créer l'engine SQLAlchemy
# Pour SQLite, il faut ajouter connect_args pour autoriser l'utilisation dans plusieurs threads (nécessaire avec FastAPI)
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(DATABASE_URL) # Pas besoin de connect_args pour PostgreSQL/MySQL par défaut

# Créer une factory de session configurée
# autocommit=False: Les transactions ne sont pas automatiquement validées.
# autoflush=False: Les changements ne sont pas automatiquement envoyés à la BDD avant une requête.
# bind=engine: Associe cette factory de session à notre engine.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Fonction de dépendance pour FastAPI
def get_db():
    """
    Générateur de session de base de données pour les dépendances FastAPI.
    Assure que la session est correctement fermée après chaque requête.
    """
    db = SessionLocal()
    try:
        yield db # Fournit la session à la fonction de l'endpoint
    finally:
        db.close() # Ferme la session après utilisation