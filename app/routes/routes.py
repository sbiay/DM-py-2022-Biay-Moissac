import json, requests, time
from flask import flash, Flask, redirect, render_template, request, url_for
from flask_login import login_user, current_user, logout_user
from sqlalchemy import delete, update, or_, and_
from bs4 import BeautifulSoup
import urllib.parse
import requests
import json

from ..appliMoissac import app, login, db
from ..constantes import ROWS_PER_PAGE
from ..modeles.classes import Codices, Lieux, Unites_codico, Oeuvres, Personnes, Provenances, Contient
from ..modeles.utilisateurs import User
from ..modeles.traitements import auteursListDict, codexJson, codicesListDict, conservationDict, personneLabel, \
    codexLabel, tousAuteursJson, tousArkDict, toutesOeuvresJson, saisieRecherche, saisieTexte, \
    oeuvreDict, oeuvresListDict
from ..modeles.requetes import rechercheArk, rechercheCote


@app.route("/")
def accueil():
    """
    La page d'accueil affiche la liste des codices enregistrés dans la base
    alphanumériquement par lieu de conservation (localité, puis nom d'institution) puis par cote
    """
    # Pour pouvoir trier les codices alphanumériquement par labels et cote,
    # on récupère la liste des dictionnaires ordonnés contenant les id et les labels
    # grâce à la fonction codicesListDict()
    listeDictCodices = codicesListDict()
    # On crée une liste ordonnée des codices
    idOrdonnés = [codex["codex_id"] for codex in listeDictCodices]
    
    # On initie la pagination
    page = request.args.get('page', 1, type=int)
    # On récupère les codex selon l'ordre prédéfini en paginant les réponses
    codicesPagines = Codices.query.filter(Codices.id.in_(idOrdonnés)).paginate(page=page, per_page=ROWS_PER_PAGE)
    
    return render_template("pages/accueil.html", resultats=listeDictCodices, codicesPagines=codicesPagines)


@app.route("/pages/inscription", methods=["GET", "POST"])
def inscription():
    if request.method == "POST":
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
    return redirect(url_for("accueil"))


# TODO factoriser les routes des index
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


# TODO factoriser les routes des notices
@app.route("/pages/codex/<int:num>", methods=["GET", "POST"])
def notice_codex(num, idUC=None):
    # Test d'existence de l'identifiant cherché
    codexGet = Codices.query.get_or_404(num)
    
    # Réassignation de la variable codex par l'objet Json retourné par la fonction codexJson()
    codex = json.loads(codexJson(num))
    
    if request.method == "GET":
        # On définit un booléen pour savoir si l'on affiche les champs en mode mise à jour ou en mode consultation
        maj = False
        return render_template("pages/codex.html",
                               id=codex["codex_id"],
                               titre=codex["label"],
                               descript_materielle=codex["description_materielle"],
                               histoire=codex["histoire"],
                               provenances=codex["provenances"],
                               origine=codex["origine"],
                               descUCs=codex["contenu"],
                               maj=maj)
    
    # Pour mettre à jour un codex
    elif request.method == "POST":
        maj = True
        # On définit l'ancre pour la redirection consécutive à la mise à jour
        ancre = ""
        # On récupère la liste des provenances existantes
        provenances = Lieux.query.filter(Lieux.est_provenance_de).order_by(Lieux.localite).order_by(Lieux.label).all()
        # On récupère la liste des provenances qui sont marquées comme origine
        origines = Provenances.query.filter(Provenances.origine).all()
        lieuxOrigine = []
        for item in origines:
            if item.a_pour_lieu not in lieuxOrigine:
                lieuxOrigine.append(item.a_pour_lieu)
        # On récupère les données sur les oeuvres
        toutesOeuvres = json.loads(toutesOeuvresJson())
        
        # Pour mettre à jour les champs textes de la première zone
        modifZ1 = False
        if request.form.get("id_technique", "").strip():
            # On modifie les propriétés de l'objet codex courant après les avoir traitées avec la fonction saisieTexte()
            codexGet.id_technique = saisieTexte(request.form["id_technique"])
            modifZ1 = True
        if request.form.get("histoire", "").strip():
            # On modifie les propriétés de l'objet codex courant après les avoir traitées avec la fonction saisieTexte()
            codexGet.histoire = saisieTexte(request.form["histoire"])
            modifZ1 = True
        if request.form.get("descript_materielle", "").strip():
            # On modifie les propriétés de l'objet codex courant après les avoir traitées avec la fonction saisieTexte()
            codexGet.descript_materielle = saisieTexte(request.form["descript_materielle"])
            modifZ1 = True
        if modifZ1:
            try:
                db.session.add(codexGet)
                db.session.commit()
                flash("Mise à jour correctement effectuée.", "success")
            except Exception as erreur:
                flash("La mise à jour a rencontré un problème.", "error")
                print(erreur)
        
        # Si l'utilisateur veut supprimer une origine
        if request.form.get("originesuppr", "").strip():
            idAsupprimer = request.form["originesuppr"]
            injection = Provenances.query.filter(
                and_(Provenances.codex == num, Provenances.lieu == idAsupprimer)).first()
            try:
                db.session.delete(injection)
                db.session.commit()
                flash("Enregistrement correctement supprimé.", "success")
            except Exception as erreur:
                flash("La suppression a rencontré un problème.", "error")
                print(erreur)
        
        # Pour ajouter une origine
        if request.form.get("origineAjout", "").strip():
            origineAjout = request.form["origineAjout"]
            injection = Provenances.creer(
                codex=num,
                lieu=origineAjout,
                origine=True,
                remarque=None,
                cas_particulier=None)
            if injection[0]:
                flash("La nouvelle origine a été créée avec succès", "success")
            else:
                flash("La création de la nouvelle origine a rencontré un problème", "error")
        
        # Pour ajouter une provenance
        if request.form.get("provenanceAjout", "").strip():
            provenanceAjout = request.form["provenanceAjout"]
            injection = Provenances.creer(
                codex=num,
                lieu=provenanceAjout,
                origine=False,
                remarque=None,
                cas_particulier=None)
            if injection[0]:
                flash("La nouvelle provenance a été créée avec succès", "success")
            else:
                flash("La création de la nouvelle provenance a rencontré un problème", "error")
        
        # Pour mettre à jour les champs textes de la deuxième zone
        # On récupère l'identifiant de l'UC courante
        idUC = request.args.get("idUC", None)
        if idUC:
            ucGet = Unites_codico.query.get(int(idUC))
        modifZ2 = False
        
        if request.form.get("paleographie", "").strip():
            ucGet.descript = saisieTexte(request.form["paleographie"])
            modifZ2 = True
        if request.form.get("date_pas_avant", "").strip():
            ucGet.date_pas_avant = saisieTexte(request.form["date_pas_avant"])
            modifZ2 = True
        if request.form.get("date_pas_apres", "").strip():
            # On modifie les propriétés de l'objet codex courant après les avoir traitées avec la fonction saisieTexte()
            ucGet.descript_materielle = saisieTexte(request.form["date_pas_apres"])
            modifZ2 = True
        if modifZ2:
            try:
                db.session.add(ucGet)
                db.session.commit()
                flash("Mise à jour correctement effectuée.", "success")
            except Exception as erreur:
                flash("La mise à jour a rencontré un problème.", "error")
                print(erreur)
        
        # Si l'utilisateur veut supprimer une oeuvre dans une unité codicologique
        if request.form.get("oeuvreSuppr", "").strip():
            idAsupprimer = request.form["oeuvreSuppr"]
            # La requête suivante retourne une liste d'un seul item
            injection = Contient.query.filter(
                and_(Contient.unites_codico == int(idUC), Contient.oeuvre == int(idAsupprimer))).all()
            try:
                db.session.delete(injection[0])
                db.session.commit()
                flash("Enregistrement correctement supprimé.", "success")
            except Exception as erreur:
                flash("La suppression a rencontré un problème.", "error")
                print(erreur)
        
        # Pour ajouter une oeuvre à l'unité codicologique courante
        if request.form.get("oeuvreAjout", "").strip():
            oeuvreAjout = request.form["oeuvreAjout"]
            injection = Contient.creer(int(oeuvreAjout), int(idUC))
            if injection[0]:
                flash("L'oeuvre a été associée avec succès", "success")
            else:
                flash("L'association de l'oeuvre a rencontré un problème", "error")
        
        # On recharge les données du codex
        codex = json.loads(codexJson(num))
        
        return render_template(f"pages/codex.html",
                               id=codex["codex_id"],
                               id_technique=codex["id_technique"],
                               titre=codex["label"],
                               descript_materielle=codex["description_materielle"],
                               histoire=codex["histoire"],
                               provenances=codex["provenances"],
                               origine=codex["origine"],
                               descUCs=codex["contenu"],
                               toutesProvenances=provenances,
                               toutesOrigines=lieuxOrigine,
                               toutesOeuvres=toutesOeuvres,
                               maj=maj)


@app.route("/pages/auteur/<int:id>")
def noticePersonne(id):
    """Cette route prend pour argument l'identifiant d'un auteur et retourne le template de sa notice"""
    # Test d'existence de l'identifiant cherché
    personne = Personnes.query.get_or_404(id)
    
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
    # Test d'existence de l'identifiant cherché
    oeuvre = Oeuvres.query.get_or_404(id)
    
    # On charge les données de toutes les oeuvres
    toutesOeuvres = json.loads(toutesOeuvresJson())
    
    # On récupère les données de l'oeuvre concernée
    for item in toutesOeuvres:
        if item["oeuvre_id"] == id:
            dictOeuvre = item
    
    return render_template("pages/oeuvre.html", dictOeuvre=dictOeuvre, titre=dictOeuvre["titre"])


@app.route("/recherche/<typeRecherche>")
def recherche(typeRecherche=["simple", "avancee"]):
    """
    Cette route traite les mots-clés envoyés via le formulaire de recherche simple de la barre de navigation,
    ou via le formulaire de saisie de la recherche avancée :
        - La recherche simple fonctionne selon un opérateur OU par défaut entre les différents mots-clés de la saisie.
        L'opérateur ET peut être saisi par l'utilisateur ce qui rend la recherche exclusive et non inclusive.
        Afin de bénéficier des multiples formes de titres d'oeuvre et de noms d'auteurs décrits sur data.bnf.fr,
        cette recherche croise les identifiants ark d'auteurs et d'oeuvres contenus dans la base locale
        avec les ark répondant aux mêmes mots-clés interrogés sur data.bnf.fr.
        - La recherche avancée : de même que la recherche simple, toutes les formes de noms d'auteurs ou de titres
        d'oeuvres existant sur data.bnf.fr sont moissonnés par la recherche avancée
        et croisés avec les données de la base locale. La recherche avancée est à la fois exclusive et inclusive :
            - Elle ne renvoie que les *codices* pertinents par rapport à tous les mots-clés saisis ;
            - Elle renvoie les oeuvres répondant à tous les mots-clés saisis dans le champ "oeuvre"
            (indépendamment des mots-clés saisis dans le champ "auteur") ;
            - Elle renvoie les auteurs répondant à tous les mots-clés saisis dans le champ "auteur"
            (indépendamment des mots-clés saisis dans le champ "oeuvre") ;
        Enfin, l'opérateur "OU" peut être saisi dans les champs "oeuvre" et "auteur",
        ce qui rend la recherche inclusive pour ces types de données respectifs.
    """
    # Si la recherche est vide, les variables suivantes sont inchangées
    motscles = []
    exclusive = False
    vide = True  # Pour la recherche avancée, si aucun champ n'est complété
    
    # On récupère la requête de l'utilisateur
    if typeRecherche == "simple":
        # On récupère la chaîne de requête passée dans l'URL
        motscles = request.args.get("keyword", None)
        # On récupère les mots-clés traités grâce à la fonction saisieRecherche()
        # La recherche simple est à priori inclusive
        motscles, exclusive = saisieRecherche(motscles, exclusive=False)
    
    # Si la recherche est de type "avancée"
    else:
        # On récupère les mots-clés de la recherche pour chaque champ
        motscles = {
            "cote": request.args.get("cote", None),
            "auteur": request.args.get("auteur", None),
            "oeuvre": request.args.get("oeuvre", None)
        }
        # On initie un dictionnaire pour récupérer les saisies après traitement
        motsclesNets = {}
        # On initie des booléens pour savoir quel champs ont été remplis
        rechAuteur = False
        rechCote = False
        rechOeuvre = False
        # On effectue le traitement des mots-clés sur chaque champ saisi grâce à la fonction saisieRecherche()
        if motscles["cote"]:
            motsclesNets["cote"] = saisieRecherche(motscles["cote"], exclusive=True)
            vide = False
            rechCote = True
        if motscles["auteur"]:
            motsclesNets["auteur"] = saisieRecherche(motscles["auteur"], True)
            vide = False
            rechAuteur = True
        if motscles["oeuvre"]:
            motsclesNets["oeuvre"] = saisieRecherche(motscles["oeuvre"], True)
            vide = False
            rechOeuvre = True
    
    # On récupère les listes de dictionnaires contenant les id, les labels et les scores initiés à 0 des codices
    # triés alphanumériquement par labels grâce à la fonction codicesListDict()
    listeDictCodices = codicesListDict()
    
    # On définit une liste de mots vides à éliminer pour optimiser les requêtes sur Data-BNF
    motsVides = [
        "ad", "à", "au", "aux",
        "de", "du", "des",
        "et",
        "in",
        "l", "le", "la", "les",
        "un", "une",
        "sur",
        "saint", "sainte"
    ]
    
    # Si des mots-clés ont été envoyés à la recherche simple
    if typeRecherche == "simple" and motscles:
        # On boucle sur chaque mot-clé
        for mot in motscles:
            # On charge les arks de la base de donnée
            arks = tousArkDict(idSortie="codices")
            # Si le mot n'est pas de type vide, on cherche chaque mot-clé sur Data-BNF au moyen de la fonction
            # rechercheArk() qui retourne un set d'id de codices
            resultatsDataBNF = {}
            # On ne requête que les mots qui ne sont pas parmi les mots vides
            if mot not in motsVides:
                try:
                    resultatsDataBNF = rechercheArk(mot, arks)
                except requests.exceptions.SSLError:
                    resultatsDataBNF = {}
            
            # On boucle sur chaque codex via listeDictCodices
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
            if exclusive:
                if codex["score"] < len(motscles):
                    codex["score"] = 0
            if codex["score"] != 0:
                bredouille = False
                # On ajoute les objets Codices aux résultats paginés
                idResultats.append(codex["codex_id"])
        
        resultats = Codices.query.filter(Codices.id.in_(idResultats)).paginate(page=page, per_page=ROWS_PER_PAGE)
        
        return render_template("pages/resultats.html", type="simple", resultats=resultats, donnees=listeDictCodices,
                               bredouille=bredouille)
    
    # Si la recherche est de type avancé et que des mots-clés ont été inscrits dans au moins un champ
    elif typeRecherche == "avancee" and not vide:
        # On charge les dictionnaires destinées à recevoir, par type de donnée, les scores de la recherche
        listeDictAuteurs = auteursListDict()
        listeDictOeuvres = oeuvresListDict()
        listeDictCodices = codicesListDict()
        
        # On boucle sur chaque champ de la saisie traitée
        for champ in motsclesNets:
            # On pose comme condition l'existence de mot-clé
            if motsclesNets[champ][0]:
                # On boucle sur chaque mot-clé
                for mot in motsclesNets[champ][0]:
                    
                    # Pour une recherche sur les cotes
                    if champ == "cote":
                        for codex in listeDictCodices:
                            # On initie un booléen qui détermine si le codex courant est pertinent vis-à-vis du mot-clé
                            pertinent = False
                            # La recherche d'un codex porte sur son label,
                            # on fait pour cela appel à la fonction codexLabel(code_id)
                            if mot in codexLabel(codex["codex_id"])["label"].lower():
                                pertinent = True
                            if pertinent:
                                codex["score"] += 1
                    
                    # Pour une recherche sur les auteurs
                    elif champ == "auteur":
                        tousArks = tousArkDict(idSortie="personnes")
                        arks = {
                            "arkPersonnes": tousArks["arkPersonnes"]
                        }
                        # Si le mot n'est pas de type vide, on le cherche sur Data-BNF au moyen de la fonction
                        # rechercheArk() qui retourne un set d'id de codices pertinents
                        # On initie les résultats de la recherche
                        resultatsDataBNF = {}
                        if mot not in motsVides:
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
                            else:
                                if auteur["personne_id"] in resultatsDataBNF:
                                    pertinent = True
                            if pertinent:
                                auteur["score"] += 1
                    
                    # Pour une recherche sur les oeuvres
                    elif champ == "oeuvre":
                        tousArks = tousArkDict(idSortie="oeuvres")
                        arks = {
                            "arkOeuvres": tousArks["arkOeuvres"]
                        }
                        resultatsDataBNF = {}
                        if mot not in motsVides:
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
                            else:
                                if oeuvre["oeuvre_id"] in resultatsDataBNF:
                                    pertinent = True
                            if pertinent:
                                oeuvre["score"] += 1
        
        # On initie les listes de dictionnaires pour les résultats positifs
        cotesPositives = []
        auteursPositifs = []
        oeuvresPositives = []
        
        # On initie un booléen pour déterminer si la recherche sur les auteurs n'a donné aucun résultat
        boolPasAuteur = True
        if rechAuteur:
            for auteur in listeDictAuteurs:
                # On récupère le booléen propre à la saisie du champ courant
                # afin de déterminer si la recherche doit être inclusive ou exclusive
                exclusive = motsclesNets["auteur"][1]
                if exclusive:
                    # Si le score de l'auteur courant est inférieur au nombre de mots-clés, son score est annulé
                    if auteur["score"] < len(motsclesNets["auteur"][0]):
                        auteur["score"] = 0
                # S'il reste un auteur dont le score n'est pas nul, la recherche est fructueuse
                if auteur["score"] != 0:
                    auteursPositifs.append(auteur)
                    boolPasAuteur = False
        
        # De même pour les oeuvres
        boolPasOeuvre = True
        if rechOeuvre:
            for oeuvre in listeDictOeuvres:
                exclusive = motsclesNets["oeuvre"][1]
                if exclusive:
                    if oeuvre["score"] < len(motsclesNets["oeuvre"][0]):
                        oeuvre["score"] = 0
                if oeuvre["score"] != 0:
                    boolPasOeuvre = False
                    # On ajoute alors des métadonnées sur l'oeuvre
                    oeuvresPositives.append(oeuvre)
                    oeuvre["donnees"] = oeuvreDict(oeuvre["oeuvre_id"])
        
        # De même pour les cotes
        boolPasCote = True
        if rechCote:
            for codex in listeDictCodices:
                exclusive = motsclesNets["cote"][1]
                if exclusive:
                    if codex["score"] < len(motsclesNets["cote"][0]):
                        codex["score"] = 0
                if codex["score"] != 0:
                    boolPasCote = False
                    cotesPositives.append(codex)
        
        # Pour croiser les résultats des différents champs et retourner les codices pertinents
        # On initie la liste des id des dictionnaires pertients
        idCodicesPertinents = []
        codices = Codices.query.all()
        for codex in codices:
            donneesCodex = json.loads(codexJson(codex.id))
            scoreCodex = 0
            # On boucle sur les dict des oeuvres s'il y en a parmi les résultats
            if oeuvresPositives:
                for oeuvrePositive in oeuvresPositives:
                    # On initie un booléen pour établir la pertinence de la comparaison
                    pertinent = False
                    for UC in donneesCodex["contenu"]:
                        for oeuvre in UC["oeuvres"]:
                            if oeuvre["oeuvre_id"] == oeuvrePositive["oeuvre_id"]:
                                pertinent = True
                    if pertinent:
                        scoreCodex += 1
            if auteursPositifs:
                for auteurPositif in auteursPositifs:
                    pertinent = False
                    for UC in donneesCodex["contenu"]:
                        for oeuvre in UC["oeuvres"]:
                            if oeuvre.get("auteur_id") == auteurPositif["personne_id"] \
                                or oeuvre.get("attr_id") == auteurPositif["personne_id"]:
                                pertinent = True
                    if pertinent:
                        scoreCodex += 1
            if len(oeuvresPositives) \
                + len(auteursPositifs) \
                <= scoreCodex and scoreCodex != 0:
                idCodicesPertinents.append(donneesCodex["codex_id"])
        
        # Pour croiser ces résultats avec les résultats de la recherche sur les cotes
        # et récupérer leur label à afficher dans une liste
        listeCodicesPertinents = []
        # Si les recherches des autres champs ont des résultats, on les croise avec celui sur les cotes
        if rechOeuvre or rechAuteur and idCodicesPertinents:
            if cotesPositives:
                for cote in cotesPositives:
                    for id in idCodicesPertinents:
                        if cote["codex_id"] == id:
                            listeCodicesPertinents.append(codexLabel(id))
            else:
                listeCodicesPertinents = [codexLabel(id) for id in idCodicesPertinents]
        
        # S'il n'y a pas de recherche sur les autres champs
        elif rechCote and not rechAuteur and not rechOeuvre:
            listeCodicesPertinents = [codexLabel(cote["codex_id"]) for cote in cotesPositives]
        
        return render_template("pages/resultats.html",
                               type="avancee",
                               codices=listeCodicesPertinents,
                               rechAuteur=rechAuteur,
                               boolPasAuteur=boolPasAuteur,
                               resultatsAuteurs=auteursPositifs,
                               rechOeuvre=rechOeuvre,
                               boolPasOeuvre=boolPasOeuvre,
                               resultatsOeuvres=oeuvresPositives
                               )
    
    elif typeRecherche == "avancee" and vide:
        return render_template("pages/recherche-avancee.html")


@app.route("/creer/<typeCreation>", methods=["GET", "POST"])
def creer(typeCreation=["codex", "oeuvre"],
          idUC=None, oeuvreAvecAuteur=None, oeuvreAnonyme=None, auteurAbsent=None, oeuvreChoisie=None, idAuteur=None):
    """
    Selon le paramètre "typeCreation", cette route permet la création d'un codex ou d'une oeuvre dans la base.
    La création d'une oeuvre est strictement conditionnée à son rattachement à une unité codicologique déterminée :
    elle ne peut se faire que par le formulaire de mise à jour d'un codex, au niveau d'une unité codicologique
    particulière.
    """
    
    if typeCreation == "codex":
        # On récupère les données nécessaires au chargement des menus :
        # On récupère la liste des lieux de conservations existants
        lieuxConservation = Lieux.query.filter(Lieux.conserve).order_by(Lieux.localite).order_by(Lieux.label).all()
        # On définit la BNF comme lieu par défaut pour la saisie
        lieuParDefaut = Lieux.query.get(2)
        # On récupère la liste des provenances existantes
        provenances = Lieux.query.filter(Lieux.est_provenance_de).order_by(Lieux.localite).order_by(Lieux.label).all()
        # On récupère la liste des provenances qui sont marquées comme origine
        origines = Provenances.query.filter(Provenances.origine).all()
        lieuxOrigine = []
        for item in origines:
            if item.a_pour_lieu not in lieuxOrigine:
                lieuxOrigine.append(item.a_pour_lieu)
        
        if request.method == "GET":
            return render_template(
                "pages/creer.html",
                titre="codex",
                lieuxConservation=lieuxConservation,
                lieuParDefaut=lieuParDefaut,
                provenances=provenances,
                origines=lieuxOrigine
            )
        
        # L'accès au formulaire de création d'un codex se fait par la méthode POST
        elif request.method == "POST":
            # On contrôle la saisie des données
            erreurs = []
            
            if not request.form.get("conservation_id", "").strip():
                erreurs.append("Un lieu de conservation doit être renseigné. ")
            if not request.form.get("cote", "").strip():
                erreurs.append("Une cote doit être renseignée. ")
            else:
                # Si une cote a été saisie, on vérifie qu'elle ne soit pas déjà renseignée dans la base
                # en relation avec le même lieu de conservation, et ce au moyen de la fonction rechercheCote()
                if request.form.get("conservation_id", "").strip():
                    if rechercheCote(request.form["cote"], request.form["conservation_id"]):
                        erreurs.append("Cette cote est déjà présente dans la base. ")
            if not request.form.get("date_pas_avant", "").strip():
                erreurs.append("Une date de début doit être renseignée. ")
            if not request.form.get("date_pas_apres", "").strip():
                erreurs.append("Une date de fin doit être renseignée. ")
            
            # Si on a au moins une erreur
            if len(erreurs) > 0:
                for erreur in erreurs:
                    flash(erreur, "error")
                return render_template("pages/creer.html",
                                       titre="codex",
                                       lieuxConservation=lieuxConservation,
                                       lieuParDefaut=lieuParDefaut,
                                       provenances=provenances,
                                       origines=lieuxOrigine,
                                       saisieCote=request.form.get("cote", ""),
                                       saisieIdentifiant=request.form.get("identifiant_technique", ""),
                                       saisieDescription=request.form.get("descript_materielle", ""),
                                       saisieHistoire=request.form.get("histoire", ""),
                                       saisieDatepasavant=request.form.get("date_pas_avant", ""),
                                       saisieDatepasapres=request.form.get("date_pas_apres", ""),
                                       )
            
            # S'il n'y a pas d'erreur, on récupère les valeurs en les nettoyant grâce à la fonction saisieTexte()
            cote = saisieTexte(request.form["cote"])
            id_technique = saisieTexte(request.form["id_technique"])
            descript_materielle = saisieTexte(request.form["descript_materielle"])
            histoire = saisieTexte(request.form["histoire"])
            date_pas_avant = int(request.form.get("date_pas_avant", ""))
            date_pas_apres = int(request.form.get("date_pas_apres", ""))
            conservation_id = request.form["conservation_id"]
            unites_codico = []
            
            # Créer une première unité codicologique par défaut
            # Déterminer l'identifiant du codex en cours de création, dont l'UC sera enfant
            idFuturCodex = len(Codices.query.all()) + 1
            nouvelle_uc = Unites_codico.creer(
                code_id=idFuturCodex,
                date_pas_avant=date_pas_avant,
                date_pas_apres=date_pas_apres,
                descript=None, loc_init=None, loc_init_v=None, loc_fin=None, loc_fin_v=None
            )
            # Si la création de la nouvelle UC est un succès
            if nouvelle_uc[0]:
                unites_codico.append(nouvelle_uc[1].id)
            else:
                print(
                    f"L'unité codicologique par défaut du codex {idFuturCodex}"
                    f" en cours de création a rencontré un problème."
                )
            
            # On crée le codex dans la base
            if Codices.creer(cote,
                             id_technique,
                             descript_materielle,
                             histoire,
                             conservation_id,
                             unites_codico
                             )[0]:
                return redirect(url_for("notice_codex", num=idFuturCodex)), flash("Le codex a bien été créé", "success")
            else:
                return render_template("pages/creer.html",
                                       titre="codex",
                                       lieuxConservation=lieuxConservation,
                                       lieuParDefaut=lieuParDefaut,
                                       provenances=provenances,
                                       origines=lieuxOrigine,
                                       saisieCote=request.form.get("cote", ""),
                                       saisieIdentifiant=request.form.get("identifiant_technique", ""),
                                       saisieDescription=request.form.get("descript_materielle", ""),
                                       saisieHistoire=request.form.get("histoire", ""),
                                       saisieDatepasavant=request.form.get("date_pas_avant", ""),
                                       saisieDatepasapres=request.form.get("date_pas_apres", ""),
                                       ), flash("La création du codex a rencontré un problème.", "error")
    if typeCreation == "oeuvre":
        # On récupère les booléens définissant si l'oeuvre à créer possède un auteur ou est anonyme
        oeuvreAvecAuteur = request.args.get("oeuvreAvecAuteur", None)
        oeuvreAnonyme = request.args.get("oeuvreAnonyme", None)
        idUC = request.args.get("idUC", None)
        # Si l'oeuvre à créer possède un auteur
        if oeuvreAvecAuteur:
            # On doit proposer la liste des auteurs
            tousAuteurs = json.loads(tousAuteursJson())
            
            # Si la case "l'auteur n'est pas dans la liste" a été cochée
            if request.args.get("auteurAbsent", None):
                auteurAbsent = True
                
                # Si des mots clés ont été saisis par l'utilisateur
                if request.form.get("auteur", "").strip():
                    # On récupère la saisie et on en élimine les caracètes dangereux
                    motscles = saisieRecherche(request.form["auteur"])
                    # Les mots-clés sont une list en index 0 du retour de la fonction saisieRecherche()
                    motscles = motscles[0]
                    # On écrit un filtre sparql pour chaque mot-clé,
                    # à la fois pour la recherche de la forme d'autorité du nom
                    # et pour la recherche des formes alternatives
                    listeFiltres = [f'filter contains(lcase(?nom), "{mot}").' for mot in motscles]
                    listeFiltresAutres = [f'filter contains(lcase(?nomAutre), "{mot}").' for mot in motscles]
                    # On écrit ces filtres dans une str :
                    chaineFiltres = ""
                    for index, filtre in enumerate(listeFiltres):
                        # On n'ajoutera pas de saut de ligne pour le dernier filtre de la liste
                        if index == len(listeFiltres) - 1:
                            chaineFiltres += "\n" + filtre
                        else:
                            chaineFiltres += filtre
                    chaineFiltresAutres = ""
                    for index, filtre in enumerate(listeFiltresAutres):
                        # On n'ajoutera pas de saut de ligne pour le dernier filtre de la liste
                        if index == len(listeFiltres) - 1:
                            chaineFiltresAutres += "\n" + filtre
                        else:
                            chaineFiltresAutres += filtre
                    # On écrit une requête sparql pour l'adresser à DataBNF
                    requete = '''PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
                    SELECT DISTINCT ?uri ?nomFr ?uriAbout
                    WHERE {
                        ?uri skos:prefLabel ?nom.
                        ?uri <http://www.w3.org/2004/02/skos/core#prefLabel> ?nomFr.
                        ?uri <http://xmlns.com/foaf/0.1/focus> ?uriAbout.
                        ?uriAbout <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://xmlns.com/foaf/0.1/Person>.
                        ''' + chaineFiltres +'''
                        OPTIONAL {
                        ?uri skos:altLabel ?nomAutre.
                        ''' + chaineFiltresAutres +'''
                        }
                    } LIMIT 100
                    '''
                    requHTTP = requests.get("https://data.bnf.fr/sparql?format=json&query=" + urllib.parse.quote(requete))
                    # On récupère les données au format Json
                    try:
                        resultat = requHTTP.json()
                        if not resultat["results"]["bindings"]:
                            flash("La requête n'a donné aucun résultat.", "info")
                            return render_template(
                                "pages/creer.html",
                                titre="oeuvre",
                                idUC=idUC,
                                auteurAbsent=True,
                                personnes=None
                            )
                        
                        else:
                            resultats = []
                            for resultat in resultat["results"]["bindings"]:
                                resultats.append(resultat)
                            return render_template(
                                "pages/creer.html",
                                titre="oeuvre",
                                idUC=idUC,
                                resultats=resultats
                            )
                    except json.decoder.JSONDecodeError:
                        flash("La requête à rencontré un problème, veuillez réessayer plus tard.", "error")
                        
                        return render_template(
                            "pages/creer.html",
                            titre="oeuvre",
                            idUC=idUC,
                            auteurAbsent=True,
                            personnes=None
                        )
                
                # Si un auteur a été choisi dans la liste des résultats
                elif request.form.get("auteurChoisiNom", "").strip():
                    # On récupère l'URI de l'auteur et son nom
                    nom = request.form["auteurChoisiNom"]
                    uri = request.form["auteurChoisiUriAbout"]
                    
                    # On récupère le numéro ark dans l'uri
                    ark = uri[19:-6]
                    # On vérifie que l'ark ne soit finalement pas déjà présent dans la base
                    tousArksPersonnes = tousArkDict("personnes")["arkPersonnes"]
                    # Si c'est le cas, on est renvoé à la liste de sélection des auteurs
                    if tousArksPersonnes.get(ark):
                        flash("L'auteur est déjà présent dans la liste.", "info")
                        return render_template(
                            "pages/creer.html",
                            titre="oeuvre",
                            idUC=idUC,
                            personnes=tousAuteurs
                        )
                    # Si l'auteur est effectivement nouveau, on ajoute l'auteur à la base
                    # puis on revient à la liste des auteurs
                    else:
                        statut, nouvelAuteur = Personnes.creer(nom=nom, data_bnf=ark)
                        if statut:
                            flash("L'auteur a été ajouté avec succès.", "success")
                            # On recharge la liste des auteurs
                            tousAuteurs = json.loads(tousAuteursJson())
                            
                            return render_template(
                                "pages/creer.html",
                                titre="oeuvre",
                                idUC=idUC,
                                personnes=tousAuteurs
                            )
                        else:
                            flash("La création de l'auteur a rencontré un problème.", "error")
                            return render_template(
                                "pages/creer.html",
                                titre="oeuvre",
                                idUC=idUC,
                                personnes=tousAuteurs
                            )
                
                # Si aucun nom n'a été saisi pour la recherche d'un auteur, on reste sur le formulaire
                else:
                    return render_template(
                        "pages/creer.html",
                        titre="oeuvre",
                        idUC=idUC,
                        auteurAbsent=True,
                        personnes=None
                    )
            
            # Si on a sélectionné un auteur dans la liste des auteurs existants
            elif request.form.get("auteurChoisi", None):
                idAuteurChoisi = request.form["auteurChoisi"]
                # On récupère l'ark de cet auteur
                ark = Personnes.query.get(int(idAuteurChoisi)).data_bnf
                # On recompose l'URI Data-BNF de l'auteur
                uriAuteurAbout = f"http://data.bnf.fr/{ark}#about"
                
                # On écrit une requête sparql pour aller chercher les oeuvres de cet auteur
                requete = '''SELECT DISTINCT ?uriOeuvre ?titre
                WHERE {
                    ?uriOeuvre <http://purl.org/dc/terms/creator> <''' + uriAuteurAbout +'''>.
                    ?uriOeuvre <http://www.w3.org/2000/01/rdf-schema#label> ?titre.
                    } LIMIT 100'''
                requHTTP = requests.get("https://data.bnf.fr/sparql?format=json&query=" + urllib.parse.quote(requete))
                # On procède comme ci-dessus pour la récupération des résultats
                try:
                    resultat = requHTTP.json()
                    if not resultat["results"]["bindings"]:
                        flash("Aucune oeuvre n'est associée à cet auteur sur Data-BNF.", "info")
                        return render_template(
                            "pages/creer.html",
                            titre="oeuvre",
                            idUC=idUC,
                            idAuteur=idAuteurChoisi,
                            auteurAbsent=True,
                            personnes=None
                        )
                    
                    else:
                        resultats = []
                        for resultat in resultat["results"]["bindings"]:
                            resultats.append(resultat)
                        return render_template(
                            "pages/creer.html",
                            titre="oeuvre",
                            idUC=idUC,
                            resultatsOeuvres=resultats,
                            idAuteurChoisi=idAuteurChoisi
                        )
                except json.decoder.JSONDecodeError:
                    flash("La requête à rencontré un problème, veuillez réessayer plus tard.", "error")
            
            if request.args.get("oeuvreChoisie", None):
                oeuvreChoisie = True
                # On récupère les données du formulaire de sélection de l'oeuvre
                titre = request.form["oeuvreChoisieTitre"]
                idAuteur = request.form["idAuteur"]
                URIdataBNF = request.form["oeuvreChoisieURIabout"]
                ark = URIdataBNF[19:-6]
                # On récupère l'id du codex concerné pour la redirection
                idcodex = Unites_codico.query.get(int(idUC)).code_id
                
                # On vérifie que l'oeuvre ne soit pas déjà dans la base
                tousArksOeuvres = tousArkDict("oeuvres")["arkOeuvres"]
                # Si c'est le cas, on est renvoyé à la liste de sélection des auteurs
                if tousArksOeuvres.get(ark):
                    flash("L'oeuvre est déjà présente dans la base.", "info")
                    return redirect(url_for("notice_codex", num=idcodex))
                
                # Si l'oeuvre n'est pas présente dans la base, on doit la créer
                else:
                    reussi, nouvelleOeuvre = Oeuvres.creer(
                        titre=titre,
                        data_bnf=ark,
                        lien_auteur=int(idAuteur))
                    if reussi:
                        # Puis on doit l'associer à l'unité codicologique courante
                        reussi, nouvelleAssociation = Contient.creer(nouvelleOeuvre.id, int(idUC))
                        if reussi:
                            flash("L'oeuvre a été correctement créée et ajoutée à l'unité codicologique", "success")
                            return redirect(url_for("notice_codex", num=idcodex))
                        else:
                            flash("L'association de l'oeuvre à l'l'unité codicologique a rencontré un problème.",
                                  "error")
                            return redirect(url_for("notice_codex", num=idcodex))
                    else:
                        flash("La création de l'oeuvre a rencontré un problème.",
                              "error")
                        return redirect(url_for("notice_codex", num=idcodex))
            
            
            
            
            # Accès au menu d'une création avec auteur
            else:
                return render_template(
                    "pages/creer.html",
                    titre="oeuvre",
                    idUC=idUC,
                    personnes=tousAuteurs
                )
        elif oeuvreAnonyme:
            # S'il y a une saisie
            if request.form.get("titre", "").strip():
                # On récupère la saisie et on en élimine les caracètes dangereux
                motscles = saisieRecherche(request.form["titre"])
                # Les mots-clés sont une list en index 0 du retour de la fonction saisieRecherche()
                motscles = motscles[0]
                # On écrit un filtre sparql pour chaque mot-clé,
                # à la fois pour la recherche de la forme d'autorité du titre
                # et pour la recherche des formes alternatives
                listeFiltres = [f'filter contains(lcase(?titre), "{mot}").' for mot in motscles]
                listeFiltresAutres = [f'filter contains(lcase(?titreAutre), "{mot}").' for mot in motscles]
                # On écrit ces filtres dans une str :
                chaineFiltres = ""
                for index, filtre in enumerate(listeFiltres):
                    # On n'ajoutera pas de saut de ligne pour le dernier filtre de la liste
                    if index == len(listeFiltres) - 1:
                        chaineFiltres += "\n" + filtre
                    else:
                        chaineFiltres += filtre
                chaineFiltresAutres = ""
                for index, filtre in enumerate(listeFiltresAutres):
                    # On n'ajoutera pas de saut de ligne pour le dernier filtre de la liste
                    if index == len(listeFiltres) - 1:
                        chaineFiltresAutres += "\n" + filtre
                    else:
                        chaineFiltresAutres += filtre
                # On écrit une requête sparql pour l'adresser à DataBNF
                requete = '''
                            PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
                            PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
                            SELECT DISTINCT ?uri ?titre ?uriAbout
                            WHERE {
                              ?uri skos:prefLabel ?titre.
                              ?uri skos:altLabel ?titreAutre.
                              ?uri <http://xmlns.com/foaf/0.1/focus> ?uriAbout.
                              ?uriAbout <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>
                             <http://rdvocab.info/uri/schema/FRBRentitiesRDA/Work>.
                              ''' + chaineFiltres + '''
                              OPTIONAL {?uri skos:altLabel ?titreAutre.
                              ''' + chaineFiltresAutres + '''
                              }
                              } LIMIT 100'''
                requHTTP = requests.get(
                    "https://data.bnf.fr/sparql?format=json&query=" + urllib.parse.quote(requete))
                if requHTTP.status_code == 200:
                    try:
                        resultat = requHTTP.json()
                        if not resultat["results"]["bindings"]:
                            flash("La requête n'a donné aucun résultat.", "info")
                            return render_template(
                                "pages/creer.html",
                                titre="oeuvre",
                                idUC=idUC,
                                oeuvreAnonyme=True
                            )
                        else:
                            resultats = []
                            for resultat in resultat["results"]["bindings"]:
                                resultats.append(resultat)
                            return render_template(
                                "pages/creer.html",
                                titre="oeuvre",
                                idUC=idUC,
                                oeuvreAnonyme=True,
                                resultatsOeuvres=resultats
                            )
                    except json.decoder.JSONDecodeError:
                        flash("La requête à rencontré un problème, veuillez réessayer plus tard.", "error")
                        
                        return render_template(
                            "pages/creer.html",
                            titre="oeuvre",
                            idUC=idUC,
                            oeuvreAnonyme=True
                        )

            if request.args.get("oeuvreChoisie", None):
                # On récupère les données du formulaire de sélection de l'oeuvre
                titre = request.form["oeuvreChoisieTitre"]
                URIdataBNF = request.form["oeuvreChoisieURIabout"]
                ark = URIdataBNF[19:-6]
                idUC = request.args.get("idUC", None)
                # On récupère l'id du codex concerné pour la redirection
                idcodex = Unites_codico.query.get(int(idUC)).code_id

                # On vérifie que l'oeuvre ne soit pas déjà dans la base
                tousArksOeuvres = tousArkDict("oeuvres")["arkOeuvres"]
                # Si c'est le cas, on est renvoyé à la liste de sélection des auteurs
                if tousArksOeuvres.get(ark):
                    flash("L'oeuvre est déjà présente dans la base.", "info")
                    return redirect(url_for("notice_codex", num=idcodex))

                # Si l'oeuvre n'est pas présente dans la base, on doit la créer
                else:
                    reussi, nouvelleOeuvre = Oeuvres.creer(
                        titre=titre,
                        data_bnf=ark,
                        auteur=idAuteur)
                    if reussi:
                        # Puis on doit l'associer à l'unité codicologique courante
                        reussi, nouvelleAssociation = Contient.creer(nouvelleOeuvre.id, int(idUC))
                        if reussi:
                            flash("L'oeuvre a été correctement créée et ajoutée à l'unité codicologique", "success")
                            return redirect(url_for("notice_codex", num=idcodex))
                        else:
                            flash("L'association de l'oeuvre à l'l'unité codicologique a rencontré un problème.",
                                  "error")
                            return redirect(url_for("notice_codex", num=idcodex))
                    else:
                        flash("La création de l'oeuvre a rencontré un problème.",
                              "error")
                        return redirect(url_for("notice_codex", num=idcodex))
                    
            return render_template(
                    "pages/creer.html",
                    titre="oeuvre",
                    idUC=idUC,
                    oeuvreAnonyme=True
                )
        
        # Accès au menu générale de la création avec ou sans auteur
        return render_template(
            "pages/creer.html",
            titre="oeuvre",
            idUC=idUC,
            oeuvreAnonyme=False
        )
        