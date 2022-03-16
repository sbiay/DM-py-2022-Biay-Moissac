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
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    cote = db.Column(db.String)
    id_technique = db.Column(db.String(19), nullable=True)
    descript_materielle = db.Column(db.Text, nullable=True)
    histoire = db.Column(db.Text, nullable=True)
    conservation_id = db.Column(db.Integer, db.ForeignKey("lieux.id"))
    lieu_conservation = db.relationship("Lieux", back_populates="conserve")
    unites_codico = db.relationship("Unites_codico", back_populates="codex")
    
    @staticmethod
    def creer(cote, id_technique, descript_materielle, histoire, conservation_id):
        """
        Création d'un codex dans la base de données.
        """
        # On vérifie la qualité des données
        erreurs = []
        if not cote:
            erreurs.append("Une cote doit être renseignée.")
        if not conservation_id:
            erreurs.append("Un lieu de conservation doit être renseigné.")
        
        # Si on a au moins une erreur
        if len(erreurs) > 0:
            return False, erreurs
        
        # La création d'une première unité-codicologique doit être automatique
        unites_codico = []
        
        # On crée les données du codex
        nouveauCodex = Codices(
            cote=cote,
            id_technique=id_technique,
            descript_materielle=descript_materielle,
            histoire=histoire,
            conservation_id=conservation_id,
            unites_codico=unites_codico
        )
        # On tente d'écrire le nouveau codex dans la base
        try:
            db.session.add(nouveauCodex)
            # On envoie le paquet
            db.session.commit()
            
            # On renvoie l'utilisateur
            return True, nouveauCodex
        except Exception as erreur:
            return False, [str(erreur)]


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
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    # Description physique
    descript = db.Column(db.Text, nullable=True)
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
    
    @staticmethod
    def creer(code_id, date_pas_avant, date_pas_apres,
              descript=None, loc_init=None, loc_init_v=None, loc_fin=None, loc_fin_v=None):
        """
        Création d'une unité codicologique dans la base de données.
        """
        # TODO ajouter un test des valeurs entrantes
        
        # On crée les données de la nouvelle unité codicologique
        nouvelleUC = Unites_codico(
            descript=descript,
            loc_init=loc_init,
            loc_init_v=loc_init_v,
            loc_fin=loc_fin,
            loc_fin_v=loc_fin_v,
            date_pas_avant=date_pas_avant,
            date_pas_apres=date_pas_apres,
            code_id=code_id,
        )
        # On tente d'écrire le nouveau codex dans la base
        try:
            db.session.add(nouvelleUC)
            # On envoie le paquet
            db.session.commit()
            
            # On renvoie l'UC créée
            return True, nouvelleUC
        except Exception as erreur:
            return False, [str(erreur)]


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
