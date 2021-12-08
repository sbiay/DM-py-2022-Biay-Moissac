from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask("lib-moissac")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/libMoissac.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

query = db.engine.execute('SELECT * FROM codices')


# for x in query.fetchall():  # Problème avec fetchone() et fetchmany()
#    print(x.fetch[1]())

class Codices(db.Model):
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    cote = db.Column(db.String)
    id_technique = db.Column(db.String(19))
    reliure_descript = db.Column(db.Text)
    histoire = db.Column(db.Text)


ts_codices = Codices.query.all()  # Assigne tous les enregistrements sous forme de liste

print('\n# Les descriptions des reliures')
for codex in ts_codices:
    print('- ' + codex.reliure_descript)

codex1 = Codices.query.get(
    1)  # Recherche un enregistrement par sa clé prim. et l'assigne en tant que classe d'objet (<class '__main__.Codices'>)


# Pour poser un filtre (clause Where)
class Oeuvres(db.Model):
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    titre = db.Column(db.Text)
    data_bnf = db.Column(db.Integer)
    partie_de = db.Column(db.Boolean)
    auteur = db.Column(db.Integer)


print("\n\n# Les oeuvres d'Augustin")
oeuvres_Augustin = Oeuvres.query.filter(
    Oeuvres.auteur == 4).all()  # Assigne l'enregistrement sous forme d'une liste (ici d'un seul item)
for oeuvre in oeuvres_Augustin:
    print('- ' + oeuvre.titre)

print("\n## Leur nombre")
nb_ops_Aug = Oeuvres.query.filter(Oeuvres.auteur == 4).count()
print(nb_ops_Aug)

print("\n## La première oeuvre de la liste")
ops_Aug_1 = Oeuvres.query.filter(Oeuvres.auteur == 4).first().titre
print(ops_Aug_1)

print("\n\n# Récupérer une requête pour la déboguer")
requete = Oeuvres.query.filter(Oeuvres.auteur == 4).order_by(Oeuvres.id.desc())
# En SQL :
print(requete)
# Attention, on ne peut pas afficher la syntaxe de requête SQL si on lui applique d'emblée une clé (.titre) ou une méthode (count())
