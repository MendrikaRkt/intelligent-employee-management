# app/crud/__init__.py
from .crud_employe import (
    get_employe,
    get_employe_by_email,
    get_employes,
    create_employe,
    update_employe,
    delete_employe,
    get_employes_by_departement
)

from .import crud_employe as employe

# Ajouter les imports pour le CRUD département
from .crud_departement import (
    get_departement,
    get_departement_by_nom,
    get_departements,
    create_departement,
    update_departement,
    delete_departement
)

# Import de l'objet 'departement' pour pouvoir faire crud.departement.get_departement
from . import crud_departement as departement

# ... futurs imports ...
from .crud_pointage import (
    get_pointage,
    get_pointages,
    get_pointages_by_employe,
    get_pointage_by_employe_and_date,
    create_pointage,
    update_pointage,
    delete_pointage
)
from . import crud_pointage as pointage

from .crud_evaluation import (
    get_evaluation,
    get_evaluations,
    get_evaluations_by_employe,
    create_evaluation,
    update_evaluation,
    delete_evaluation
)
from . import crud_evaluation as evaluation

from .crud_simulation import (
    get_simulation,
    get_simulations_by_employe,
    create_simulation_record,
    delete_simulation
)
from . import crud_simulation as simulation