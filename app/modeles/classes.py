from ..appliMoissac import db
from sqlalchemy import Table, Column, ForeignKey


# La table de relations "provenances" lie les classes "Lieux" et "Codices"
class Provenances(db.Model):
    rowid = db.Column(db.Integer, primary_key=True)
    codex = db.Column(db.Integer, db.ForeignKey("codices.id"))
    lieu = db.Column(db.Integer, db.ForeignKey("lieux.id"))
    origine = db.Column(db.Boolean)
    remarque = db.Column(db.Text)
    cas_particulier = db.Column(db.Integer, db.ForeignKey("unites_codico.id"))
    """On procédera à des jointures à la main en raison des différents attributs portés sur la relation.
    """


class Codices(db.Model):
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    cote = db.Column(db.String)
    id_technique = db.Column(db.String(19))
    descript_materielle = db.Column(db.Text)
    histoire = db.Column(db.Text)
    conservation_id = db.Column(db.Integer, db.ForeignKey("lieux.id"))
    lieu_conservation = db.relationship("Lieux", back_populates="conserve")
    unites_codico = db.relationship("Unites_codico", back_populates="codex")


class Lieux(db.Model):
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    localite = db.Column(db.String(20))
    label = db.Column(db.String(30))
    conserve = db.relationship("Codices", back_populates="lieu_conservation")


# Table de relation "contient"
contient = Table("contient", db.metadata,
                 Column("oeuvre", ForeignKey("oeuvres.id")),
                 Column("unites_codico", ForeignKey("unites_codico.id"))
                 )


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
    code_id = db.Column(db.Integer, db.ForeignKey("codices.id"))
    codex = db.relationship("Codices", back_populates="unites_codico")
    contenu = db.relationship("Oeuvres", secondary=contient, backref="Unites_codico")


class Oeuvres(db.Model):
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    titre = db.Column(db.Text, nullable=False)
    data_bnf = db.Column(db.Integer, nullable=True)
    partie_de = db.Column(db.Boolean, nullable=True)
    unites_codico = db.relationship("Unites_codico", secondary=contient, backref="Oeuvres")
    auteur = db.Column(db.Integer, db.ForeignKey("personnes.id"))
    lien_auteur = db.relationship("Personnes", back_populates="oeuvres_aut", foreign_keys=auteur)
    attr = db.Column(db.Integer, db.ForeignKey("personnes.id"))
    lien_attr = db.relationship("Personnes", back_populates="oeuvres_attr", foreign_keys=attr)


class Personnes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.Text, nullable=False)
    data_bnf = db.Column(db.Integer, nullable=True)
    oeuvres_aut = db.relationship("Oeuvres", back_populates="lien_auteur", foreign_keys=Oeuvres.auteur)
    oeuvres_attr = db.relationship("Oeuvres", back_populates="lien_attr", foreign_keys=Oeuvres.attr)
