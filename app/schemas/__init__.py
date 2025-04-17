# app/schemas/__init__.py

# Importer les classes spécifiques depuis chaque fichier de schéma
from .employe import Employe, EmployeCreate, EmployeUpdate, EmployeBase
from .departement import Departement, DepartementCreate, DepartementUpdate, DepartementBase
from .evaluation import Evaluation, EvaluationCreate, EvaluationUpdate, EvaluationBase
from .simulation import Simulation, SimulationParams, SimulationRun, SimulationBase
from .pointage import Pointage, PointageCreate, PointageUpdate
# Ajoutez ici les imports pour les futurs schémas (Pointage, Evaluation, Simulation)
# quand vous les créerez. Par exemple :
# from .pointage import Pointage, PointageCreate, PointageBase
# from .evaluation import Evaluation, EvaluationCreate, EvaluationBase
# from .simulation import Simulation, SimulationCreate, SimulationBase

# Optionnel: Définir __all__ pour contrôler ce qui est importé avec "from app.schemas import *"
# Cela n'est pas strictement nécessaire pour que l'import direct fonctionne,
# mais c'est une bonne pratique si d'autres parties du code utilisaient "import *".
__all__ = [
    # Employe schemas
    "Employe",
    "EmployeCreate",
    "EmployeUpdate",
    "EmployeBase",
    # Departement schemas
    "Departement",
    "DepartementCreate",
    "DepartementUpdate",
    "DepartementBase",
    # Evaluation schemas
    "Evaluation",
    "EvaluationCreate",
    "EvaluationUpdate",
    "EvaluationBase",
    # Simualation schemas
    "Simulation",
    "SimulationParams",
    "SimulationRun",
    "SimulationBase",
    # Departement schemas
    "Pointage",
    "PointageCreate",
    "PointageUpdate",
]