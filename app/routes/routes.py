import json, requests, time
from flask import flash, Flask, redirect, render_template, request, url_for
from flask_login import login_user, current_user, logout_user
from bs4 import BeautifulSoup

from ..appliMoissac import app, login
from ..constantes import ROWS_PER_PAGE
from ..modeles.classes import Codices, Lieux, Unites_codico, Oeuvres, Personnes, Provenances
from ..modeles.utilisateurs import User
from ..modeles.traitements import auteursListDict, codexJson, codicesListDict, conservationDict, personneLabel, \
    codexLabel, tousAuteursJson, tousArkDict, toutesOeuvresJson, traitntMotsCles, oeuvreDict, oeuvresListDict
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


@app.route("/pages/auteurs")
def indexAuteurs():
    # On définit de la variable "page"
    page = request.args.get('page', 1, type=int)
    
    # On charge les auteurs sous la forme d'un objet paginé
    classAuteurs = Personnes.query.order_by(Personnes.nom).paginate(page=page, per_page=ROWS_PER_PAGE)
    # On charge les métadonnées et données liées aux auteurs sous la forme d'une liste
    donneesAuteurs = json.loads(tousAuteursJson())
    
    return render_template("pages/auteurs.html", auteurs=donneesAuteurs, classAuteurs=classAuteurs)


@app.route("/pages/oeuvres")
def indexOeuvres():
    # On définit de la variable "page"
    page = request.args.get('page', 1, type=int)
    
    # On charge les métadonnées et données liées aux oeuvres sous la forme d'une liste
    donneesOeuvres = json.loads(toutesOeuvresJson())
    
    # On charge les oeuvres sous la forme d'un objet paginé
    classOeuvres = Oeuvres.query.order_by(Oeuvres.titre).paginate(page=page, per_page=ROWS_PER_PAGE)
    
    return render_template("pages/oeuvres.html", oeuvres=donneesOeuvres, classOeuvres=classOeuvres)


@app.route("/pages/auteur/<int:id>")
def noticePersonne(id):
    """Cette route prend pour argument l'identifiant d'un auteur et retourne le template de sa notice"""
    # On charge les données de tous les auteurs
    toutesPersonnes = json.loads(tousAuteursJson())
    
    # On récupère les données de l'auteur concerné
    for item in toutesPersonnes:
        if item["personne_id"] == id:
            dictPersonne = item
    
    return render_template("pages/auteur.html", dictPersonne=dictPersonne, titre=dictPersonne["label"])


@app.route("/pages/oeuvre/<int:id>")
def noticeOeuvre(id):
    """Cette route prend pour argument l'identifiant d'une oeuvre et retourne le template de sa notice"""
    # On charge les données de toutes les oeuvres
    toutesOeuvres = json.loads(toutesOeuvresJson())
    
    # On récupère les données de l'oeuvre concernée
    for item in toutesOeuvres:
        if item["oeuvre_id"] == id:
            dictOeuvre = item
    
    return render_template("pages/oeuvre.html", dictOeuvre=dictOeuvre, titre=dictOeuvre["titre"])


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


@app.route("/recherche/<typeRecherche>")
def recherche(typeRecherche=["simple", "avancee"]):
    """
    Cette route traite les mots-clés envoyés via le formulaire de recherche simple de la barre de navigation.
    Elle fonctionne selon un opérateur OU par défaut entre les différents mots-clés de la saisie.
    L'opérateur ET peut être saisi par l'utilisateur ce qui rend la recherche exclusive et non inclusive.
    Afin de bénéficier des multiples formes de titres d'oeuvre et de noms d'auteurs décrits sur data.bnf.fr,
    cette recherche croise les identifiants ark d'auteurs et d'oeuvres contenus dans la base locale
    avec les ark répondant aux mêmes mots-clés interrogés sur data.bnf.fr.
    """
    # Si la recherche est vide, les variables suivantes sont inchangées
    motscles = []
    rechercheIntersection = False
    # On initie un booléen pour savoir si la recherche avancée est vide
    vide = True
    
    if typeRecherche == "simple":
        # On récupère la chaîne de requête passée dans l'URL
        motscles = request.args.get("keyword", None)
        # On récupère les mots-clés traités grâce à la fonction traitntMotsCles
        # La recherche simple est à priori inclusive (argument False)
        motscles, rechercheIntersection = traitntMotsCles(motscles, False)
    
    # Si la recherche est de type "avancée"
    else:
        # On récupère les mots-clés de la recherche pour chaque champ
        dictMotsCles = {
            "motsClesCote": request.args.get("cote", None),
            "motsClesAuteur": request.args.get("auteur", None),
            "motsClesOeuvre": request.args.get("oeuvre", None),
            "motsClesLieu": request.args.get("lieu", None)
        }
        # On initie un dictionnaire pour récupérer les saisies à traiter
        dictMotsClesNets = {}
        # On initie des booléens pour savoir quel champs ont été remplis
        rechAuteur = False
        rechCote = False
        rechLieu = False
        rechOeuvre = False
        # On effectue le traitement des mots-clés sur chaque champ saisi
        if dictMotsCles["motsClesCote"]:
            dictMotsClesNets["motsClesCote"] = traitntMotsCles(dictMotsCles["motsClesCote"], True)
            vide = False
            rechCote = True
        if dictMotsCles["motsClesAuteur"]:
            dictMotsClesNets["motsClesAuteur"] = traitntMotsCles(dictMotsCles["motsClesAuteur"], True)
            vide = False
            rechAuteur = True
        if dictMotsCles["motsClesOeuvre"]:
            dictMotsClesNets["motsClesOeuvre"] = traitntMotsCles(dictMotsCles["motsClesOeuvre"], True)
            vide = False
            rechOeuvre = True
        if dictMotsCles["motsClesLieu"]:
            dictMotsClesNets["motsClesLieu"] = traitntMotsCles(dictMotsCles["motsClesLieu"], True)
            vide = False
            rechLieu = True
        print(dictMotsClesNets)
    # On récupère les listes de dictionnaires contenant les id, les labels et les scores initiés à 0 des codices
    # triés alphanumériquement par labels grâce à la fonction codicesListDict()
    listeDictCodices = codicesListDict()
    
    if typeRecherche == "simple" and motscles:
        # On boucle sur chaque mot-clé
        for mot in motscles:
            # On charge les arks de la base de donnée
            arks = tousArkDict()
            # On cherche chaque mot-clé sur Data-BNF au moyen de la fonction requeteDataBNF()
            # qui retourne un set d'id de codices
            try:
                resultatsDataBNF = rechercheArk(mot, arks)
            except requests.exceptions.SSLError:
                resultatsDataBNF = {}
            
            # On boucle sur chaque codex via scoresCodices
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
        
        
        # On prépare la pagination des résultats
        page = request.args.get('page', 1, type=int)
        
        # On initie une liste d'id des codices résultats
        idResultats = []
        
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
                # On ajoute les objets Codices aux résultats paginés
                idResultats.append(codex["codex_id"])
        
        resultats = Codices.query.filter(Codices.id.in_(idResultats)).paginate(page=page, per_page=ROWS_PER_PAGE)
        
        return render_template("pages/resultats.html", type="simple", resultats=resultats, donnees=listeDictCodices,
                               bredouille=bredouille)
    
    # Si la recherche est de type avancé
    elif typeRecherche == "avancee" and not vide:
        # On charge les dictionnaires destinées à recevoir, par type de donnée, les scores de la recherche
        listeDictAuteurs = auteursListDict()
        listeDictOeuvres = oeuvresListDict()
        
        # On boucle sur chaque champ de la saisie traitée
        for champ in dictMotsClesNets:
            # On pose comme condition l'existence de mot-clé
            if dictMotsClesNets[champ][0]:
                for mot in dictMotsClesNets[champ][0]:
                    # Pour une recherche sur les auteurs
                    if champ == "motsClesAuteur":
                        tousArks = tousArkDict()
                        arks = {
                            "arkPersonnes": tousArks["arkPersonnes"]
                        }
                        try:
                            resultatsDataBNF = rechercheArk(mot, arks)
                        except requests.exceptions.SSLError:
                            resultatsDataBNF = {}
                        
                        # Pour la recherche sur les données locales
                        # on boucle sur les auteurs chargés dans listeDictAuteurs
                        for auteur in listeDictAuteurs:
                            # On initie un booléen qui détermine si l'auteur courant est pertinent vis-à-vis du mot-clé
                            pertinent = False
                            # La recherche d'un auteur porte sur son nom
                            if mot in auteur["nom"].lower():
                                pertinent = True
                            if pertinent:
                                auteur["score"] += 1
                    
                    # Pour une recherche sur les oeuvres
                    elif champ == "motsClesOeuvre":
                        tousArks = tousArkDict()
                        arks = {
                            "arkOeuvres": tousArks["arkOeuvres"]
                        }
                        try:
                            resultatsDataBNF = rechercheArk(mot, arks)
                        except requests.exceptions.SSLError:
                            resultatsDataBNF = {}
                        
                        # Pour la recherche sur les données locales
                        # on boucle sur les oeuvres chargées dans listeDictOeuvres
                        for oeuvre in listeDictOeuvres:
                            # On initie un booléen qui détermine si l'oeuvre courant est pertinente vis-à-vis du mot-clé
                            pertinent = False
                            # La recherche d'une oeuvre porte sur son titre
                            if mot in oeuvre["titre"].lower():
                                pertinent = True
                            if pertinent:
                                oeuvre["score"] += 1
        
        # On initie un booléen pour déterminer si la recherche sur les auteurs n'a donné aucun résultat
        boolPasAuteur = True
        
        for auteur in listeDictAuteurs:
            # On récupère le booléen propre à la saisie du champ courant
            # afin de déterminer si la recherche doit être inclusive ou exclusive
            rechercheIntersection = dictMotsClesNets["motsClesAuteur"][1]
            if rechercheIntersection:
                # Si le score de l'auteur courant est inférieur au nombre de mots-clés, son score est annulé
                if auteur["score"] < len(dictMotsClesNets["motsClesAuteur"][0]):
                    auteur["score"] = 0
            # S'il reste un auteur dont le score n'est pas nul, la recherche est fructueuse
            if auteur["score"] != 0:
                boolPasAuteur = False
        
        # De même pour les oeuvres
        boolPasOeuvre = True
        for oeuvre in listeDictOeuvres:
            if oeuvre["score"] != 0:
                boolPasOeuvre = False
                # On ajoute alors des métadonnées sur l'oeuvre
                oeuvre["donnees"] = oeuvreDict(oeuvre["oeuvre_id"])
        
        return render_template("pages/resultats.html",
                               type="avancee",
                               rechAuteur=rechAuteur,
                               boolPasAuteur=boolPasAuteur,
                               resultatsAuteurs=listeDictAuteurs,
                               rechOeuvre=rechOeuvre,
                               boolPasOeuvre=boolPasOeuvre,
                               resultatsOeuvres=listeDictOeuvres
                               )
    
    elif typeRecherche == "avancee" and vide:
        return render_template("pages/recherche-avancee.html")