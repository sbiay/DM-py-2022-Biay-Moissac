from ..appliMoissac import db

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
    titre = db.Column(db.Text, nullable=False)
    data_bnf = db.Column(db.Integer, nullable=True)
    partie_de = db.Column(db.Boolean, nullable=True)
    auteur = db.Column(db.Integer, nullable=True)
    
class Contient(db.Model):
    rowid = db.Column(db.Integer, primary_key=True)
    oeuvre = db.Column(db.Integer, nullable=False)
    unites_codico = db.Column(db.Integer, nullable=False)
    
class Personne(db.Model):
    rowid = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.Text, nullable=False)
    data_bnf = db.Column(db.Integer, nullable=True)