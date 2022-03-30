import json, requests
from flask import request, url_for, jsonify, Response
from urllib.parse import urlencode

from ..appliMoissac import app
from ..constantes import ROWS_PER_PAGE
from ..modeles.classes import Codices
from ..modeles.traitements import codexJson, codicesListDict, saisieRecherche, tousArkDict
from ..modeles.requetes import rechercheArk


@app.route("/404")
def erreur_404():
    """
    Cette route gère les requêtes sur l'API ne renvoyant aucune réponse.
    """
    response = Response("Il y a eu une erreur")
    response.headers["content-type"] = "text/plain"
    response.status_code = 404
    return response


@app.route("/api/codex/<int:num>")
def codex(num):
    # Test d'existence de l'identifiant cherché
    codexGet = Codices.query.get(num)
    if codexGet:
        codex = json.loads(codexJson(num))
        
        return jsonify(codex)
    else:
        return erreur_404()

@app.route("/api/codices")
def codices():
    """
    Cette route retourne de manière paginée tous les codices de la base avec leurs métadonnées au format Json.
    """
    # On récupère tous les codices pour dresser la liste de leurs id
    codices = Codices.query.all()
    tousId = [codex.id for codex in codices]
    # On initie la pagination et on pagine tous les codices
    page = request.args.get('page', 1, type=int)
    codicesPagines = Codices.query.filter(Codices.id.in_(tousId)).paginate(page=page, per_page=ROWS_PER_PAGE)
    
    # On initie le dictionnaire des résultats:
    resultats = {
        "results": [
            # On charge dans le dict resultats les données json de chaque codex
            json.loads(codexJson(codex.id)) for codex in codicesPagines.items
        ],
        "total": len(codices),
        "links": {}
    }
    # On créé les liens de la navigation entre les pages de la réponse
    if codicesPagines.has_next:
        arguments = {
            "page": codicesPagines.next_num
        }
        resultats["links"]["next"] = url_for("codices", _external=True) + "?" + urlencode(arguments)
    
    if codicesPagines.has_prev:
        arguments = {
            "page": codicesPagines.prev_num
        }
        resultats["links"]["prev"] = url_for("codices", _external=True) + "?" + urlencode(arguments)
    
    return jsonify(resultats)


@app.route("/api/recherche-codex")
def recherche_codex():
    """
    Cette route retourne de manière paginée tous les codices répondant à une liste d'arguments
    saisis par un utilisateur.
    Elle fonctionne selon les mêmes modalités que la recherche simple de l'application avec interface.
    """
    
    # On récupère la chaîne de requête passée dans l'URL
    motscles = request.args.get("q", None)
    page = request.args.get("page", 1)
    
    # On récupère les mots-clés traités grâce à la fonction saisieRecherche()
    # La recherche simple est à priori inclusive
    motscles, exclusive = saisieRecherche(motscles, exclusive=False)
    
    if isinstance(page, str) and page.isdigit():
        page = int(page)
    else:
        page = 1
    
    if motscles:
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
            listeDictCodices = codicesListDict()
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
                        # Si l'id courant parmi les résulats de la requête DataBNF correspond à l'id du codex
                        # en cours de traitement, la pertinence est établie
                        if codex["codex_id"] == id:
                            pertinent = True
                if pertinent:
                    codex["score"] += 1
        
        # On initie une liste d'id des codices résultats
        idResultats = []
        
        # On définit un booléen pour indiquer le succès ou non de la recherche
        bredouille = True
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
        
        try:
            resultats = Codices.query.filter(Codices.id.in_(idResultats)).paginate(page=page, per_page=ROWS_PER_PAGE)
        except Exception:
            return erreur_404()

        dict_resultats = {
            "links": {
                "self": request.url
            },
            "results": [
                json.loads(codexJson(codex.id))
                for codex in resultats.items
            ]
        }
        if resultats.has_next:
            arguments = {
                "page": resultats.next_num
            }
            if motscles:
                arguments["q"] = motscles
            dict_resultats["links"]["next"] = url_for("recherche_codex", _external=True) + "?" + urlencode(
                arguments)

        if resultats.has_prev:
            arguments = {
                "page": resultats.prev_num
            }
            if motscles:
                arguments["q"] = motscles
            dict_resultats["links"]["prev"] = url_for("recherche_codex", _external=True) + "?" + urlencode(
                arguments)

    reponse = jsonify(dict_resultats)
    return reponse