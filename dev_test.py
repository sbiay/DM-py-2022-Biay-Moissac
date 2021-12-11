import requests
import csv
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy


# Définition de mon application
app = Flask("lib-moissac")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/libMoissac.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Définition de mes classes d'objets
# ATTENTION, il faudra veiller à bien appliquer le modèle logique
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



def notice_codex(num):
    codex = Codices.query.get(num)
    
    # Requête portant sur les unités codicologiques enfants d'un codex désigné par son identifiant
    listUC_enfants = Unites_codico.query.filter(Unites_codico.code_id == num).all()
    for UC in listUC_enfants:
        description = UC.descript
        print(description)
        # Conditions portant sur le booléen relatif aux recto/verso au début et à la fin de l'UC
        if UC.loc_init_v:
            rvdebut = "v"
        else:
            rvdebut = ""
        if UC.loc_fin_v:
            rvfin = "v"
        else:
            rvfin = ""
        localisation = f"f. {str(UC.loc_init)}{rvdebut}-{str(UC.loc_fin)}{rvfin}"
    
    # REPRENDRE ICI : assigner les paramètres de date
    
    # Test d'existence d'un index dans la liste des prem_codices :
    codices = Codices.query.all()
    if num <= len(codices):
        # Si l'id passé dans l'URL n'est pas plus grand que la liste
        # de tous les codices, alors :
        print(codex.cote)
        print(codex.reliure_descript)
    else:
        print("Cette adresse ne correspond à aucune notice !")


from app import test.bot
bot()