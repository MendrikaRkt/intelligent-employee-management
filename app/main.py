# app/main.py
from fastapi import FastAPI

from app.api.api_v1.api import api_router # Importez le routeur de l'API v1
# from app.core.config import settings # Si vous avez un fichier de config centralisé

# Initialiser l'application FastAPI
app = FastAPI(
    title="Système de Gestion Intelligente des Employés API",
    # description="Description détaillée de l'API...", # Optionnel
    version="1.0.0", # Version de l'API
    openapi_url="/api/v1/openapi.json" # Chemin pour le schéma OpenAPI
)

# Inclure le routeur principal de l'API v1
app.include_router(api_router, prefix="/api/v1") # Toutes les routes d'api_router seront préfixées par /api/v1

# Route racine simple (optionnel)
@app.get("/")
async def read_root():
    return {"message": "Bienvenue sur l'API de Gestion Intelligente des Employés"}

# Ping pour vérifier si l'API est en ligne (optionnel)
@app.get("/ping")
async def ping():
    return {"ping": "pong"}

# --- Ici, vous pourriez ajouter d'autres configurations ---
# Par exemple, des gestionnaires d'événements au démarrage/arrêt,
# des middlewares, la configuration CORS, etc.