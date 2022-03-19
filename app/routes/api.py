import json, requests, time
from flask import flash, Flask, redirect, render_template, request, url_for, jsonify
from urllib.parse import urlencode
from flask_login import login_user, current_user, logout_user
from sqlalchemy import delete, update, or_, and_
from bs4 import BeautifulSoup

from ..appliMoissac import app, login, db
from ..constantes import ROWS_PER_PAGE
from ..modeles.classes import Codices, Lieux, Unites_codico, Oeuvres, Personnes, Provenances, Contient
from ..modeles.utilisateurs import User
from ..modeles.traitements import auteursListDict, codexJson, codicesListDict, conservationDict, personneLabel, \
    codexLabel, tousAuteursJson, tousArkDict, toutesOeuvresJson, saisieRecherche, saisieTexte, \
    oeuvreDict, oeuvresListDict
from ..modeles.requetes import rechercheArk, rechercheCote
from ..comutTest import test

@app.route("/api/codex/<int:num>")
def codex(num):
    codex = json.loads(codexJson(num))

    return jsonify(codex)

@app.route("/api/codices")
def codices():
    # On récupère tous les codices
    codices = Codices.query.all()
    tousId = [codex.id for codex in codices]
    # On initie la pagination
    page = request.args.get('page', 1, type=int)
    codicesPagines = Codices.query.filter(Codices.id.in_(tousId)).paginate(page=page, per_page=ROWS_PER_PAGE)
    print(codicesPagines)
    
    # On initie le code Json des résultats:
    resultats = {
        "items": [
            # On charge dans le dict resultats les données json de chaque codex
            json.loads(codexJson(codex.id)) for codex in codicesPagines.items
        ],
        "total": len(codices),
        "navigation": {}
     }

    if codicesPagines.has_next:
        arguments = {
            "page": codicesPagines.next_num
        }
        resultats["navigation"]["suivant"] = url_for("codices", _external=True) + "?" + urlencode(arguments)

    if codicesPagines.has_prev:
        arguments = {
            "page": codicesPagines.prev_num
        }
        resultats["navigation"]["precedent"] = url_for("codices", _external=True) + "?" + urlencode(arguments)
    

    return jsonify(resultats)