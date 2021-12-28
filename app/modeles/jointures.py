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
