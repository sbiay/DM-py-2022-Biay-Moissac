import json
from flask import request, url_for, jsonify
from urllib.parse import urlencode

from ..appliMoissac import app
from ..constantes import ROWS_PER_PAGE
from ..modeles.classes import Codices
from ..modeles.traitements import codexJson

@app.route("/api/codex/<int:num>")
def codex(num):
    codex = json.loads(codexJson(num))

    return jsonify(codex)

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
        "items": [
            # On charge dans le dict resultats les données json de chaque codex
            json.loads(codexJson(codex.id)) for codex in codicesPagines.items
        ],
        "total": len(codices),
        "navigation": {}
     }
    # On créé les liens de la navigation entre les pages de la réponse
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