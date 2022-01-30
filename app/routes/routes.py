import json, requests
from flask import flash, Flask, redirect, render_template, request, url_for
from flask_login import login_user, current_user, logout_user
from bs4 import BeautifulSoup

from ..appliMoissac import app, login
from ..modeles.classes import Codices, Lieux, Unites_codico, Oeuvres, Personnes, Provenances
from ..modeles.utilisateurs import User
from ..modeles.jointures import labelCodex, toutes_oeuvres, tous_auteurs, codexJson
from ..comutTest import test


@app.route("/")
def accueil():
    return render_template("pages/accueil.html")


@app.route("/pages/connexion", methods=["POST", "GET"])
def connexion():
    """ Route gérant les connexions
    """
    if current_user.is_authenticated is True:
        flash("Vous êtes déjà connecté !", "info")
        return redirect(url_for('accueil'))
    # Si on est en POST, cela veut dire que le formulaire a été envoyé
    if request.method == "POST":
        utilisateur = User.identification(
            login=request.form.get("login", None),
            motdepasse=request.form.get("motdepasse", None)
        )
        if utilisateur:
            flash("Connexion effectuée.", "success")
            login_user(utilisateur)
            return redirect(url_for('accueil'))
        else:
            flash("Les identifiants n'ont pas été reconnus", "error")
    
    return render_template("pages/connexion.html")


# On définit que la page de connexion est celle définie par connexion() :
# c'est un renvoi pour les users souhaitant effectuer une opération
# nécessitant une connexion.
login.login_view = 'connexion'


@app.route("/deconnexion", methods=["POST", "GET"])
def deconnexion():
    if current_user.is_authenticated is True:
        logout_user()
    flash("Vous êtes bien déconnecté.", "info")
    return render_template("pages/accueil.html")


@app.route("/pages/<quel_index>")
def index(quel_index=["auteurs", "codices", "oeuvres"]):
    oeuvres = toutes_oeuvres()
    auteurs = tous_auteurs()
    codices = "Voici la liste des codices"
    
    if quel_index == indexes[0]:
        return render_template("pages/auteurs.html", auteurs=auteurs)
    elif quel_index == indexes[1]:
        return render_template("pages/codices.html", codices=codices)
    elif quel_index == indexes[2]:
        return render_template("pages/oeuvres.html", oeuvres=oeuvres)


@app.route("/pages/inscription", methods=["GET", "POST"])
def inscription():
    if request.method == "POST":
        print("Formulaire envoyé !")
        statut, donnees = User.creer(
            login=request.form.get("login", None),
            email=request.form.get("email", None),
            nom=request.form.get("nom", None),
            motdepasse=request.form.get("motdepasse", None)
        )
        if statut is True:
            flash("Enregistrement effectué. Identifiez-vous maintenant", "success")
            return render_template("pages/connexion.html")
        else:
            flash("Les erreurs suivantes ont été rencontrées : " + ",".join(donnees), "error")
            return render_template("pages/inscription.html")
    else:
        return render_template("pages/inscription.html")


@app.route("/pages/codices/<int:num>")
def notice_codex(num):
    # Test d'existence de l'identifiant cherché
    codex = Codices.query.get_or_404(num)
    
    # Réassignation de la variable codex par l'objet Json retourné par la fonction codexJson()
    codex = json.loads(codexJson(num))
    print(codex["origine"])
    
    if not test:
        return render_template("pages/codices.html",
                               titre=codex["label"],
                               materielle=codex["description_materielle"],
                               histoire=codex["histoire"],
                               provenances=codex["provenances"],
                               origine=codex["origine"],
                               descUCs=codex["contenu"])


@app.route("/recherche")
def recherche():
    motscles = request.args.get("keyword", None)
    
    # Eliminer les caractères inutiles
    caracteresInutiles = ",.!"
    for caractere in caracteresInutiles:
        motscles = motscles.replace(caractere, "")
    # Eliminer les caractères potentiellements dangereux
    caracteresInterdits = """<>\;"&#^'`?%{}[]|()"""
    for caractere in caracteresInterdits:
        motscles = motscles.replace(caractere, "")
    # Convertir les mots-clés en liste
    motscles = motscles.split(" ")
    print(motscles)
    return render_template("pages/resultats.html")