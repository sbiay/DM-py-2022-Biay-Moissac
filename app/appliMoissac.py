import requests
import csv
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import os

# Gestion des chemins
chemin_actuel = os.path.dirname(os.path.abspath(__file__))
templates = os.path.join(chemin_actuel, "templates")
statics = os.path.join(chemin_actuel, "static")

# Définition de mon application
app = Flask("lib-moissac", template_folder=templates,
            static_folder=statics)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{chemin_actuel}/db/libMoissac.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Définition de mes classes d'objets (ATTENTION, il faudra veiller à bien appliquer le modèle logique)
class Codices(db.Model):
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    cote = db.Column(db.String)
    id_technique = db.Column(db.String(19))
    reliure_descript = db.Column(db.Text)
    histoire = db.Column(db.Text)


class Unites_codico(db.Model):
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    # Description physique
    descript = db.Column(db.Text)
    # Localisation d'une unité dans un codex (f. n-f. m)
    loc_init = db.Column(db.Integer, default=None)
    loc_init_v = db.Column(db.Boolean, default=None)
    loc_fin = db.Column(db.Integer, default=None)
    loc_fin_v = db.Column(db.Boolean, default=None)
    date_pas_avant = db.Column(db.Integer, nullable=False)
    date_pas_apres = db.Column(db.Integer, nullable=False)
    code_id = db.Column(db.Integer, nullable=False)


class Oeuvres(db.Model):
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    titre = db.Column(db.Text)
    data_bnf = db.Column(db.Integer)
    partie_de = db.Column(db.Boolean)
    auteur = db.Column(db.Integer)


@app.route("/")
def conteneur():
    return render_template("conteneur.html", nom="Bibliothèque de Moissac")


@app.route("/pages/")
def accueil():
    return render_template("pages/accueil.html", nom="Bibliothèque de Moissac")


@app.route("/pages/codices/<int:num>")
def notice_codex(num):
    codex = Codices.query.get(num)
    
    # Requête portant sur les unités codicologiques enfants d'un codex désigné par son identifiant
    # A mettre dans un script à part "contenu_notice_codex"
    listUC_enfants = Unites_codico.query.filter(Unites_codico.code_id == num).all()
    paramsUCs = []
    for UC in listUC_enfants:
        paramsUC = {}
        paramsUC["description"] = UC.descript
        
        # Conditions portant sur le booléen relatif aux recto/verso au début et à la fin de l'UC
        if UC.loc_init_v:
            rvdebut = "v"
        else:
            rvdebut = ""
        if UC.loc_fin_v:
            rvfin = "v"
        else:
            rvfin = ""
        paramsUC["localisation"] = f"f. {str(UC.loc_init)}{rvdebut}-{str(UC.loc_fin)}{rvfin}"
        
        paramsUC["date"] = f"entre {UC.date_pas_avant} et {UC.date_pas_apres}"
        
        # Il faut à présent boucler sur les contenus de chaque UC, et requêter leurs auteurs
        
    # Test d'existence d'un index dans la liste des prem_codices :
    codices = Codices.query.all()
    if num <= len(codices):
        # Si l'id passé dans l'URL n'est pas plus grand que la liste 
        # de tous les codices, alors :
        return render_template("pages/codices.html",
                               titre=codex.cote,
                               reliure=codex.reliure_descript,
                               histoire=codex.histoire,
                               paramsUCs=paramsUCs)
    else:
        return render_template("pages/codices.html", message_erreur="Cette adresse ne correspond à aucune notice !")
