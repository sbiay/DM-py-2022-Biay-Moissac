import requests
import json
import csv

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
    with open("json/notice_gallica.json", mode="w") as f:
        json.dump(jsonf, f)
    return jsonf


def concordance(id):
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
            if str(id) == enreg["iduf"]:
                json_codex = iiif(enreg["ark"])  # json_codex est le dictionnaire contenant les métadonnées du
                # manuscrit cherché par son identifiant
                
        print(json_codex.keys())
    return json_codex


def notice_codex(cod_id):
    print("yez")
    return "Notice " + str(cod_id) + " du catalogue de Jean Dufour"


concordance(56)
