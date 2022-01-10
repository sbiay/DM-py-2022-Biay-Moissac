import json
from ..modeles.classes import Codices, Lieux, Unites_codico, Oeuvres, Contient, Personnes
from .traitements import labelCodex, labelPersonne

def toutes_oeuvres():
    """
    Cette fonction retourne un dictionnaire de toutes les oeuvres,
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
            objetAuteur = Personnes.query.get(objetOeuvre.auteur)
            oeuvres[objetOeuvre.id]["auteur"][objetAuteur.id] = labelPersonne(objetAuteur.id, "court")
        
        # Pour renseigner les attributions apocryphes à des auteurs
        if objetOeuvre.attr:
            objetAuteur = Personnes.query.get(objetOeuvre.attr)
            oeuvres[objetOeuvre.id]["auteur"][objetAuteur.id] = str(
                labelPersonne(objetAuteur.id, "court")) + " (attribué à)"
        
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


def tous_auteurs():
    """
    Cette fonction retourne un dictionnaire destiné contenant pour chaque auteur de la classe Oeuvres
    les informations relatives aux oeuvres qu'il a écrites et aux codices qui les conservent
    Il se structure de la façon suivante :
    auteurs = {
        "ID AUTEUR": {
            "label": "NOM AUTEUR",
            "oeuvres": [
                {
                "ID OEUVRE": {
                    "label": "TITRE OEUVRE",
                    "codices": [
                        {
                            "ID LIEU": "LIEU CONSERVATION"}]}}]}
        }
    """
    
    # On procède dans un premier temps à la création d'un dictionnaire sur le modèle précédemment décrit
    # contenant toutes les personnes de la db.
    personnes = {}
    objetsPersonne = Personnes.query.order_by(Personnes.nom).all()
    for objetPersonne in objetsPersonne:
        personnes[objetPersonne.id] = {"label": labelPersonne(objetPersonne.id, "long"), "oeuvres": []}
    
    """
    On appelle la fonction toutes_oeuvres() dont on va parser le contenu et injecter certaines parties
    dans le dictionnaire personnes.
    Pour cela on compare :
    - L'identifiant de chaque personne du dict personnes : 'clePersonne' ;
    - avec l'identifiant de chaque auteur du dict oeuvres : 'cleAuteur'.
    """
    oeuvres = toutes_oeuvres()
    for clePersonne in personnes:
        for cleOeuvre in oeuvres:
            for cleAuteur in oeuvres[cleOeuvre].get("auteur"):
                if clePersonne == cleAuteur:
                    # Une condition permet de distinguer les oeuvres dont les auteurs sont apocryphes
                    if not oeuvres[cleOeuvre]["auteur"][cleAuteur][-13:] == " (attribué à)":
                        personnes[clePersonne]["oeuvres"].append({
                            cleOeuvre: {
                                "label": oeuvres[cleOeuvre]["label"],
                                "codices": oeuvres[cleOeuvre]["codices"]
                            }
                        })
                    # La mention "attribué à", signe d'autorité apocryphe, est reportée dans le label de l'oeuvre
                    else:
                        personnes[clePersonne]["oeuvres"].append({
                            cleOeuvre: {
                                "label": oeuvres[cleOeuvre]["label"] + " (attribué à)",
                                "codices": oeuvres[cleOeuvre]["codices"]
                            }
                        })
    # On crée un dictionnaire des auteurs ne comprenant que des personnes qui ont des oeuvres :
    auteurs = {}
    for clePersonne in personnes:
        if personnes[clePersonne]["oeuvres"]:
            auteurs[clePersonne] = personnes[clePersonne]
    
    with open("resultats-tests/auteurs.json", mode="w") as jsonf:
        json.dump(auteurs, jsonf)
    
    return auteurs
