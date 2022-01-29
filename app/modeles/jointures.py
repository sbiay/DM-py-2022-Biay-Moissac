import json
from ..modeles.classes import Codices, Lieux, Unites_codico, Oeuvres, Personnes, Provenances
from .traitements import labelCodex, labelPersonne, localisationUC


def codexJson(codex_id):
    """
    Cette fonction prend pour argument l'identifiant d'un objet de la classe Codices
    et retourne un objet Json décrivant toutes les métadonnées du codex.
    :params codex_id: identifiant d'un objet de la classe Codices
    :codex_id type: int
    :returns: description des métadonnées d'un codex
    :return type: Json
    
    Modèle de contenu du Json retourné : {
     "codex_id": 1,
     "lieu_conservation": "Paris, Biblioth\u00e8que nationale de France",
     "label": "Paris, BnF, Latin 2989",
     "id_technique": "ark:/12148/cc60815j",
     "description_materielle": "Reliure du XVIIIe…",
     "histoire": "Produit dans le Sud-Ouest de la France…",
     "contenu": [
        {
            "uc_id": 1,
            "localisation": null,
            "description": "\u00c9criture minuscule caroline d\u2019une main principale.",
            "date": "entre 975 et 1000",
            "oeuvres": [
                {
                    "oeuvre_id": 1,
                    "titre": "Institutions c\u00e9nobitiques",
                    "data.bnf": 13771861,
                    "partie_de": null,
                    "auteur": "Jean Cassien (saint)",
                    "auteur_ark": 12044269, "attr": null
                }
            ]
        }
    ],
    "provenances": [
        {
            "lieu_id": 7,
            "label": "collection Colbert",
            "localite": "Paris",
            "remarque": null,
            "cas_particulier": null
        }
    ],
    "origine": {
        "lieu_id": 1,
        "label": "abbaye Saint-Pierre",
        "localite": "Moissac",
        "cas_particulier": null
        }
    }
    """
    
    codex = Codices.query.get_or_404(codex_id)
    
    description = {
        "codex_id": codex.id,
        "lieu_conservation": f"{codex.lieu_conservation.localite}, {codex.lieu_conservation.label}",
        "label": f"{labelCodex(codex_id)['label']}",
        "id_technique": codex.id_technique,
        "description_materielle": codex.descript_materielle,
        "histoire": codex.histoire,
        "contenu": [],
        "provenances": []
    }
    
    listObjetsUC = codex.unites_codico
    # Pour écrire un dictionnaire contenant les informations relatives à chaque UC
    for objetUC in listObjetsUC:
        dicoUC = {}
        dicoUC["uc_id"] = objetUC.id
        dicoUC["localisation"] = localisationUC(objetUC.id)
        dicoUC["description"] = objetUC.descript
        dicoUC["date"] = f"entre {objetUC.date_pas_avant} et {objetUC.date_pas_apres}"
        dicoUC["oeuvres"] = []
        
        # Pour chaque oeuvre contenue dans l'objet UC courant, on ajoutera un dictionnaire décrivant ses métadonnées
        for objetOeuvre in objetUC.contenu:
            dicoUCcourante = {
                    "oeuvre_id": objetOeuvre.id,
                    "titre": objetOeuvre.titre,
                    "data.bnf": objetOeuvre.data_bnf,
                    "partie_de": objetOeuvre.partie_de,
                }
            if objetOeuvre.lien_auteur:
                dicoUCcourante["auteur"] = labelPersonne(objetOeuvre.lien_auteur.id, "court")
                dicoUCcourante["auteur_ark"] = objetOeuvre.lien_auteur.data_bnf
            else:
                dicoUCcourante["auteur"] = None
            if objetOeuvre.lien_attr:
                dicoUCcourante["attr"] = labelPersonne(objetOeuvre.lien_attr.id, "court")
                dicoUCcourante["attr_ark"] = objetOeuvre.lien_attr.data_bnf
            else:
                dicoUCcourante["attr"] = None
            
            dicoUC["oeuvres"].append(dicoUCcourante)
        description["contenu"].append(dicoUC)
    
    # Pour les provenances et l'origine du manuscrit, on opère des jointures manuelles sur la classe Provenances
    for provenance in Provenances.query.filter(Provenances.codex == codex_id):
        if provenance.origine:
            id = Lieux.query.get(provenance.lieu).id
            label = Lieux.query.get(provenance.lieu).label
            localite = Lieux.query.get(provenance.lieu).localite
            description["origine"] = {
                "lieu_id": id,
                "label": label,
                "localite": f"{localite} ({provenance.remarque})",
                "cas_particulier": provenance.cas_particulier
            }
        else:
            id = Lieux.query.get(provenance.lieu).id
            label = Lieux.query.get(provenance.lieu).label
            localite = Lieux.query.get(provenance.lieu).localite
            dicoProvenance = {
                "lieu_id": id,
                "label": label,
                "localite": f"{localite} ({provenance.remarque})",
                "cas_particulier": provenance.cas_particulier
            }
            description["provenances"].append(dicoProvenance)

    # Test : export
    with open("resultats-tests/codex.json", mode="w") as jsonf:
        json.dump(description, jsonf)
    
    return json.dumps(description)

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
