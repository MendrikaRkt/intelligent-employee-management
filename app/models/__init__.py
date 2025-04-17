# app/models/__init__.py
from .base import Base
from .departement import Departement
from .employe import Employe
from .pointage import Pointage
from .evaluation import Evaluation
from .simulation import Simulation

# Optionnel: Définir __all__ pour contrôler ce qui est importé avec "from .models import *"
__all__ = [
    "Base",
    "Departement",
    "Employe",
    "Pointage",
    "Evaluation",
    "Simulation",
]