import requests
import csv
from flask import Flask, render_template

app = Flask("Application")

prem_codices = [
    {
        'cote': "Paris, BNF, Latin 2077",
        'format': '''Initiales en couleur, grandes initiales peintes à entrelacs (32v, 38, 45v, 59v, 96, 113,
        119).
        Rubriques en capitale rustique.
        Croquis dans les marges inférieures (55v, 66, 87v, 98v, 106, 108) et 10 dessins (162v-173).
        — Les ff. 122 et 123 ont été intercalés.
        Les ff. 123v et 161 sont blancs.
        Parchemin.179 ff.350 × 230 mm.
        Reliure maroquin rouge aux armes de Colbert.''',
        'partLoc': '',
        'date': 'Fin du IXe siècle',
        'contenu': [
            {
                'auteur': 'S. Augustinus',
                'titre': ''
            },
            {
                'auteur': 'Paschasius Radbertus',
                'titre': ''
            },
            {
                'auteur': 'S. Leodegarius',
                'titre': ''
            },
            {
                'auteur': 'Halitgarius Cameracensis',
                'titre': ''
            },
            {
                'auteur': 'Ambrosius Autpertus',
                'titre': ''
            },
        ]
    },
    {
        'cote': "Paris, BNF, Latin 2989",
        'format': '''Écriture minuscule caroline d’une main principale.
        Initiales décorées à entrelacs, motifs végétaux et palmettes, tracées à l’encre brune et colorées en rose, vert,
        jaune et mauve : f. 3v Veteris (9 lignes) ; f. 6v De (6 lignes) ; f. 12v Duplici (7 lignes) ;
        f. 24r De (7 lignes) ; f. 33r De (7 lignes) ; f. 56r Quintus (7 lignes) ; f. 78v Secundum (6 lignes) ;
        f. 87v Tercius (11 lignes) ; f. 101r Quarto (6 lignes) ; f. 111v Quintum (5 lignes) ;
        f. 115r Sextum (5 lignes) ; f. 129r Septimum (8 lignes) ; f. 136v Octavum (7 lignes) ;
        f. 154v Propagatori (7 lignes).
        Petites initiales anthropomorphes et zoomorphes : f. 31v Cuius (3 lignes) ; f. 34v Quam (3 lignes) ;
        f. 47v Cuius (3 lignes) ; f. 83v Haec (4 lignes).
        Initiales de couleur à l’encre rouge, verte et jaune ; capitales rehaussées de rouge, rose, vert et jaune.
        Premiers mots de chaque chapitre en lettres mixtes de capitales et minuscules, rehaussées de rouge.
        Rubriques en capitales rustiques à l’encre rouge, numéros de chapitre à l’encre rouge.''',
        'partLoc': '',
        'date': 'Xe siècle (dernier quart)',
        'contenu': [
            {
                'auteur': 'Iohannes Cassianus',
                'titre': 'De institutis coenobiorum'
            },
        ]
    }
]


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
    # Test d'existence d'un index dans la liste des prem_codices :
    if cod_id <= len(prem_codices) - 1:
        codex = prem_codices[cod_id]
        return render_template("pages/codices.html", titre=codex['cote'])
    else:
        return render_template("pages/codices.html", message_erreur="Cette adresse ne correspond à aucune notice !")


if __name__ == "__main__":
    app.run()
