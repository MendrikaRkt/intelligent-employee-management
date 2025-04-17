# migrations/env.py
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# --- Ajout 1: Importations pour lire .env et trouver les modèles ---
from dotenv import load_dotenv
# Assurez-vous que le chemin vers 'app' est correct par rapport à la racine du projet
# Si vous lancez alembic depuis la racine, 'app' devrait être accessible.
# Si vous avez des problèmes d'importation, vous devrez peut-être ajuster sys.path
# import sys
# sys.path.append(os.path.join(os.path.dirname(__file__), '..')) # Ajoute le dossier parent (racine) au path
from app.models.base import Base # Importez votre Base déclarative
# Importez tous vos modèles pour que Base.metadata les connaisse
# (Souvent, il suffit d'importer Base si vos modèles sont bien importés dans app/models/__init__.py)
import app.models # Assurez-vous que cet import charge bien tous vos modèles

load_dotenv() # Charger .env pour accéder à DATABASE_URL
# ----------------------------------------------------------------

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# --- Ajout 2: Configurer sqlalchemy.url à partir de .env (si Option 2 choisie pour alembic.ini) ---
# Récupérer l'URL de la BDD depuis l'environnement
db_url = os.getenv("DATABASE_URL")
if db_url:
    # Définir l'option 'sqlalchemy.url' dans la configuration Alembic
    # Ceci remplace ou fournit la valeur si elle n'est pas dans alembic.ini
    config.set_main_option("sqlalchemy.url", db_url)
elif not config.get_main_option("sqlalchemy.url"):
    # Si l'URL n'est ni dans .env ni dans alembic.ini, lever une erreur
     raise ValueError("L'URL de la base de données doit être définie dans .env (DATABASE_URL) ou dans alembic.ini (sqlalchemy.url)")
# -----------------------------------------------------------------------------

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
# --- Ajout 3: Définir target_metadata ---
target_metadata = Base.metadata # Indiquer à Alembic les métadonnées de vos modèles
# ----------------------------------------

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    # ... (le reste de cette fonction est généralement laissé tel quel)
    """Run migrations in 'offline' mode.
    ...
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata, # S'assurer que target_metadata est passé ici aussi
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    # ... (le reste de cette fonction est généralement laissé tel quel)
    """Run migrations in 'online' mode.
    ...
    """
    # --- Modification: Utiliser engine_from_config avec les options lues ---
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}), # Lire la section [alembic]
        prefix="sqlalchemy.", # Préfixe pour les options de BDD (comme sqlalchemy.url)
        poolclass=pool.NullPool,
    )
    # --------------------------------------------------------------------

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata # S'assurer que target_metadata est passé ici aussi
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()