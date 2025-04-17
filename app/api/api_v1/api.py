# app/api/api_v1/api.py
from fastapi import APIRouter

from app.api.api_v1.endpoints import employes, departements, pointages, evaluations, simulations
# Importez ici les futurs routeurs (departements, pointages, etc.)
# from app.api.api_v1.endpoints import departements
# from app.api.api_v1.endpoints import pointages
# from app.api.api_v1.endpoints import evaluations
# from app.api.api_v1.endpoints import simulations

api_router = APIRouter()

# Inclure le routeur des employés
api_router.include_router(employes.router, prefix="/employes", tags=["Employés"]) # Répéter prefix et tags peut être utiles si on veut les surcharger ici
api_router.include_router(departements.router, prefix="/departements", tags=["Départements"])
api_router.include_router(pointages.router, prefix="/pointages", tags=["Pointages"])
api_router.include_router(evaluations.router, prefix="/evaluations", tags=["Évaluations"])
api_router.include_router(simulations.router, prefix="/simulations", tags=["Simulations"])

# Inclure les autres routeurs quand ils seront prêts
# api_router.include_router(departements.router, prefix="/departements", tags=["Départements"])
# api_router.include_router(pointages.router, prefix="/pointages", tags=["Pointages"])
# api_router.include_router(evaluations.router, prefix="/evaluations", tags=["Évaluations"])
# api_router.include_router(simulations.router, prefix="/simulations", tags=["Simulations"])