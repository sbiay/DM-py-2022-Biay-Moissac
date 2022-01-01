from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os
from .constantes import SECRET_KEY

# Gestion des chemins
chemin_actuel = os.path.dirname(os.path.abspath(__file__))
templates = os.path.join(chemin_actuel, "templates")
statics = os.path.join(chemin_actuel, "static")

# Définition de mon application
app = Flask("lib-moissac", template_folder=templates,
            static_folder=statics)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{chemin_actuel}/db/libMoissac.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = SECRET_KEY
db = SQLAlchemy(app)
login_manager = LoginManager(app)


from app.comutTest import test
if not test:
    # Import des classes
    from app.modeles.classes import Codices, Unites_codico, Oeuvres
    from app.modeles.utilisateurs import User
    # Import des routes
    from app.routes import routes
