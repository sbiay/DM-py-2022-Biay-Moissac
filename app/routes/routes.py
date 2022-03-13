import json, requests
from flask import flash, Flask, redirect, render_template, request, url_for
from flask_login import login_user, current_user, logout_user
from bs4 import BeautifulSoup

from ..appliMoissac import app, login
from ..modeles.classes import Codices, Lieux, Unites_codico, Oeuvres, Personnes, Provenances
from ..modeles.utilisateurs import User
from ..modeles.traitements import codexJson, codicesListDict, personneLabel, codexLabel, tousAuteursJson, tousArkDict, \
    toutesOeuvresJson
from ..modeles.requetes import rechercheArk
from ..comutTest import test


@app.route("/")
def accueil():
    """
    La page d'accueil affiche la liste des codices enregistrés dans la base
    alphanumériquement par lieu de conservation (localité, puis nom d'institution) puis par cote
    """
    # On récupère la liste des dictionnaires contenant les id, les labels et les scores initiés à 0 des codices
    # triés alphanumériquement par labels grâce à la fonction codicesListDict()
    listeDictCodices = codicesListDict()
    
    return render_template("pages/accueil.html", resultats=listeDictCodices)


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
    oeuvres = json.loads(toutesOeuvresJson())
    # Pour obtenir une liste des noms d'auteurs ordonnée alphabétiquement
    auteurs = json.loads(tousAuteursJson())
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
    """
    Cette route traite les mots-clés envoyés via le formulaire de recherche simple de la barre de navigation.
    Elle fonctionne selon un opérateur OU par défaut entre les différents mots-clés de la saisie.
    L'opérateur ET peut être saisi par l'utilisateur ce qui rend la recherche exclusive et non inclusive.
    Afin de bénéficier des multiples formes de titres d'oeuvre et de noms d'auteurs décrits sur data.bnf.fr,
    cette recherche croise les identifiants ark d'auteurs et d'oeuvres contenus dans la base locale
    avec les ark répondant aux mêmes mots-clés interrogés sur data.bnf.fr.
    """
    # On récupère la chaîne de requête passée dans l'URL
    motscles = request.args.get("keyword", None)
    # Si la conjonction ET est présente dans la requête, on définit la recherche comme exclusive
    rechercheIntersection = False
    if " ET " in motscles:
        rechercheIntersection = True
    
    # On élimine les caractères inutiles ou potentiellement dangereux
    caracteresInterdits = """,.!<>\;"&#^'`?%{}[]|()"""
    for caractere in caracteresInterdits:
        # On passe également les mots en bas de casse
        motscles = motscles.replace(caractere, "").lower()
    # On convertit les mots-clés en liste
    motscles = motscles.split(" ")
    
    # On récupère la liste des dictionnaires contenant les id, les labels et les scores initiés à 0 des codices
    # triés alphanumériquement par labels grâce à la fonction codicesListDict()
    listeDictCodices = codicesListDict()
    
    # On charge les arks de la base de donnée
    tousArk = tousArkDict()
    
    # On boucle sur chaque mot-clé
    for mot in motscles:
        # On cherche chaque mot-clé sur Data-BNF au moyen de la fonction requeteDataBNF()
        # qui retourne un set d'id de codices
        resultatsDataBNF = rechercheArk(mot, tousArk)
        
        # On boucle sur chaque codex via de scoresCodices
        for codex in listeDictCodices:
            # On initie un booléen qui détermine si le codex courant est pertinent vis-à-vis du mot-clé courant
            pertinent = False
            
            # Pour charger les données d'un codex on les récupère grâce à la fonction codexJson()
            donneesCodex = codexJson(codex["codex_id"])
            # On passe tous les mots en bas de casse
            donneesCodex = donneesCodex.lower()
            
            # On cherche une occurrence du mot-clé courant dans les données
            if mot in donneesCodex:
                # Si une ou plusieurs occurrences sont trouvées, la pertinence est vraie
                pertinent = True
            # A défaut, on cherche les résulats parmis ceux retournés par la requête sur Data-BNF
            else:
                for id in resultatsDataBNF:
                    # Si l'id courant parmi les résulats de la requête DataBNF correspond à l'id du codex en cours de
                    # traitement, la pertinence est établie
                    if codex["codex_id"] == id:
                        pertinent = True
            if pertinent:
                codex["score"] += 1
    
    # On définit un booléen pour indiquer le succès ou non de la recherche
    bredouille = True  # Ou plutôt "broucouille", comme on dit dans le Bouchonnois
    for codex in listeDictCodices:
        # Si l'on recherche une intersection entre les mots-clés,
        # seuls les codices ayant un score égal au nombre de mots-clés sont des résultats positifs,
        # sinon, leur score est annulé
        if rechercheIntersection:
            if codex["score"] < len(motscles):
                codex["score"] = 0
        if codex["score"] != 0:
            bredouille = False
    
    return render_template("pages/resultats.html", resultats=listeDictCodices, bredouille=bredouille)


@app.route("/recherche-avancee")
def rechercheAvancee():
    # On récupère la chaîne de requête passée dans l'URL
    saisieAuteur = request.args.get("auteur", None)
    saisieOeuvre = request.args.get("oeuvre", None)
    saisieOeuvre = request.args.get("lieu", None)
    checkProvenance = request.args.get("provenances", None)
    print(checkProvenance)
    
    return render_template("pages/recherche-avancee.html")