import json, requests
from flask import flash, Flask, redirect, render_template, request, url_for
from flask_login import login_user, current_user, logout_user
from bs4 import BeautifulSoup

from ..appliMoissac import app, login
from ..modeles.classes import Codices, Lieux, Unites_codico, Oeuvres, Personnes, Provenances
from ..modeles.utilisateurs import User
from ..modeles.jointures import labelCodex, toutes_oeuvres, tous_auteurs, codexJson
from ..modeles.traitements import labelPersonne
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
    # Charger les oeuvres sous la forme d'une liste
    oeuvres = json.loads(toutes_oeuvres())
    # Pour obtenir une liste des noms d'auteurs ordonnée alphabétiquement
    auteurs = json.loads(tous_auteurs())
    codices = "Voici la liste des codices"

    if quel_index == "auteurs":
        return render_template("pages/auteurs.html", auteurs=auteurs, oeuvres=oeuvres)
    elif quel_index == "codices":
        return render_template("pages/codices.html", codices=codices)
    elif quel_index == "oeuvres":
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
    # On récupère la chaîne de requête passée dans l'URL
    motscles = request.args.get("keyword", None)
    
    # Eliminer les caractères inutiles ou potentiellement dangereux
    caracteresInterdits = """,.!<>\;"&#^'`?%{}[]|()"""
    for caractere in caracteresInterdits:
        motscles = motscles.replace(caractere, "")
    # Convertir les mots-clés en liste
    motscles = motscles.split(" ")
    
    # On initie la liste des résultats
    scoresCodices = []
    # On charge les codices de la base en les triant
    codices = Codices.query.all()
    
    # On trie les codices alphanumériquement par Lieu de conservation (localité, puis nom d'institution) puis par cote
    listeLabelCodices = [labelCodex(codex.id)["label"] for codex in codices]
    triLabels = sorted(listeLabelCodices)
    
    # On boucle sur les labels de codices triés pour ensuite traiter chaque codex dans l'ordre alphanumérique
    for label in triLabels:
        for codex in codices:
            if label == labelCodex(codex.id)["label"]:
                # Pour chaque codex, on écrit un dictionnaire
                dicoCodex = {
                    "codex_id": codex.id,
                    "label": labelCodex(codex.id)["label"],
                    "score": 0
                }
                scoresCodices.append(dicoCodex)

    # On boucle sur chaque mot-clé
    for mot in motscles:
        
        # On cherche chaque mot-clé dans une liste de champs pertinents des notices de codices
        # On boucle sur chaque clé du dictionnaire scoresCodices
        for item in scoresCodices:
            # Pour charger les données d'un codex on les récupère grâce à la fonction codexJson()
            # et on les transforme en dictionnaire
            donneesCodex = codexJson(item["codex_id"])
        
            # On cherche une occurrence du mot-clé courant dans les données
            if mot in donneesCodex:
                # Si une ou plusieurs occurrences sont trouvées, le score augmente de 1
                item["score"] += 1
    
    # On cherche chaque mot-clé sur Data-BNF
    
    
    
    # Les résultats sont un dictionnaire dont les codices sont les clés et les valeurs, un score : à chaque
    # match pour un codex, le score augmente de 1.
    
    # PENSER à passer les mots-clés ainsi que le contenu des notices en lower case pour améliorer les chances
    
    return render_template("pages/resultats.html", resultats=scoresCodices)