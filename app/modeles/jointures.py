import json
from ..modeles.classes import Codices, Lieux, Unites_codico, Oeuvres, Contient, Personne

def labelCodex(code_id):
    """Cette fonction prend comme argument l'identifiant d'un codex
    et retourne un dictionnaire :
    :param code_id: identifiant d'un codex selon la classe Codices
    :type code_id: int
    :returns: dictionnaire dont :
       - la clé est l'id du codex (int)
       - la valeur est le label (str) composé de son lieu de conservation et de sa cote.
    :rtype: dict
    """
    dico = {}
    cote = Codices.query.get(code_id).cote
    id_lieu_cons = Codices.query.get(code_id).lieu_conservation
    lieu_conservation = Lieux.query.get(id_lieu_cons)
    if lieu_conservation.label == "Bibliothèque nationale de France":
        lieu_conservation = lieu_conservation.localite + ", BnF"
    else:
        lieu_conservation = lieu_conservation.localite + ", " + lieu_conservation.label
    
    label = f"{lieu_conservation}, {cote}"
    dico[code_id] = label
    return dico

def toutes_oeuvres():
    """
    Cette fonction retourne un fichier Json de toutes les oeuvres,
    avec leur auteur et les codices qui les contiennent.
    """
    oeuvres = {}
    classOeuvres = Oeuvres.query.order_by(Oeuvres.titre).all()
    for objetOeuvre in classOeuvres:
        oeuvres[objetOeuvre.id] = {
            "label": objetOeuvre.titre,
            "auteur": {},
            "codices": []
        }
        # Pour renseigner les auteurs
        if objetOeuvre.auteur:
            objetAuteur = Personne.query.get(objetOeuvre.auteur)
            oeuvres[objetOeuvre.id]["auteur"][objetAuteur.id] = objetAuteur.nom

        # Pour renseigner les attributions apocryphes à des auteurs
        if objetOeuvre.attr:
            objetAuteur = Personne.query.get(objetOeuvre.attr)
            oeuvres[objetOeuvre.id]["auteur"][objetAuteur.id] = str(objetAuteur.nom) + " (attribué à)"
        
        # Pour renseigner les codices
        objetsContenu = Contient.query.filter(Contient.oeuvre == objetOeuvre.id).all()
        for objetContenu in objetsContenu:
            objetUC = Unites_codico.query.filter(Unites_codico.id == objetContenu.unites_codico).one()
            code_id = objetUC.code_id
            dictCodex = labelCodex(code_id)
            oeuvres[objetOeuvre.id]["codices"].append(dictCodex)
            
    # test
    with open("resultats-tests/oeuvres.json", mode="w") as jsonf:
        json.dump(oeuvres, jsonf)
    
    return oeuvres
    