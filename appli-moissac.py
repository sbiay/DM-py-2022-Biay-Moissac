import requests
import csv
from flask import Flask, render_template

app = Flask("Application")


def iiif(ark):
    """A partir d'un identifiant ark, cette fonction donne comme valeur de retour un objet Json
    contenant les métadonnées d'un objet hébergé sur Gallica :

    :param ark: identifiant ark
    :type ark: str
    :returns: objet Json contenant les métadonnées du manuscrit
    :type return: dict
    """
    
    # Requête HTML sur Gallica
    r = requests.get(f"http://gallica.bnf.fr/iiif/{ark}/manifest.json")
    jsonf = r.json()
    # Affichage des métadonnées de l'objet
    for meta in jsonf["metadata"]:
        print("{label} : {value}".format(label=meta["label"], value=meta["value"]))
    
    return jsonf


def concordance(cod_id):
    """A partir d'un identifiant numérique, cette fonction interroge la concordance entre le catalogue
    de Dufour et une liste d'identifiants ark de la BNF et retourne l'objet Json correspondant
    via la fonction iiif"""
    with open("csv/dufour_ark.csv") as f:
        cont_csv = csv.DictReader(f)
        
        # Ecriture d'une liste dont chaque item est un dictionnaire ayant :
        # - Pour clés les intitulés "iduf" et "ark"
        # - Pour valeurs les valeurs correspondantes
        concord_duf_ark = []
        for row in cont_csv:
            concord_duf_ark.append(row)
        
        for enreg in concord_duf_ark:
            if str(cod_id) == enreg["iduf"]:
                json_codex = iiif(enreg["ark"])  # json_codex est le dictionnaire contenant les métadonnées du
                # manuscrit cherché par son identifiant
    return json_codex


@app.route("/")
def conteneur():
    return render_template("conteneur.html", nom="Bibliothèque de Moissac")


@app.route("/pages/")
def accueil():
    return render_template("pages/accueil.html", nom="Bibliothèque de Moissac")


@app.route("/pages/codices/<int:cod_id>")
def notice_codex(cod_id):
    jsonf = concordance(cod_id)
    titre = jsonf["metadata"][4]["value"][62:]
    return render_template("pages/codices.html", titre=titre)


if __name__ == "__main__":
    app.run()
