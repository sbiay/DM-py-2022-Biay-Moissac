import json
from operator import attrgetter
from ..modeles.classes import Codices, Lieux, Unites_codico, Oeuvres, Personnes, Provenances
from .traitements import labelCodex, labelPersonne, localisationUC


def dicoOeuvre(objetOeuvre):
    """
    Cette fonction prend comme argument un objet de la classe Oeuvres
    et retourne un dictionnaire de forme suivante :
    {
     "oeuvre_id": 1,
     "titre": "Institutions cénobitiques",
     "data.bnf": 13771861,
     "partie_de": null,
     "auteur_id": 1,
     "auteur": "Jean Cassien (saint)",
     "auteur_ark": 12044269,
     "attr": null
    }
    :param objetOeuvre: un objet de la classe Oeuvres
    :type objetOeuvre: dict
    :returns: description des métadonnées d'une oeuvre
    :return type: dict
    """
    # Les métadonnées seront décrites dans le dictionnaire "dico"
    dico = {
        "oeuvre_id": objetOeuvre.id,
        "titre": objetOeuvre.titre,
        "data.bnf": objetOeuvre.data_bnf,
        "partie_de": objetOeuvre.partie_de,
    }
    # Si un auteur est référencé, on ajoute trois types de données (trois clés à "dico")
    if objetOeuvre.lien_auteur:
        dico["auteur_id"] = objetOeuvre.lien_auteur.id
        # On utilise la fonction labelPersonne() pour renseigner la forme courte du nom (sans dates)
        dico["auteur"] = labelPersonne(objetOeuvre.lien_auteur.id, "court")
        dico["auteur_ark"] = objetOeuvre.lien_auteur.data_bnf
    # Sinon, un seul champ est renseigné
    else:
        dico["auteur"] = None
    # Même chose pour les attributions (auteurs apocryphes)
    if objetOeuvre.lien_attr:
        dico["attr_id"] = objetOeuvre.lien_attr.id
        dico["attr"] = labelPersonne(objetOeuvre.lien_attr.id, "court")
        dico["attr_ark"] = objetOeuvre.lien_attr.data_bnf
    else:
        dico["attr"] = None
    return dico

def dicoConservation(codex_id):
    """
    Cette fonction prend comme argument l'identifiant d'un objet de la classe Codices
    et retourne un dictionnaire de forme suivante :
     {
      'lieu_id': 2,
      'localite': 'Paris',
      'label': 'Bibliothèque nationale de France'
     }
    
    :param codex_id: identifiant d'un objet de la classe Codices
    :type codex_id: int
    :returns: métadonnées d'un lieu de conservation
    :return type: dict
    """
    # Charger un objet de la classe Codices à partir de son identifiant
    objetCodex = Codices.query.get(codex_id)
    # Renseigner les couples clé-valeur du dictionnaire à partir de la propriété "lieu_conservation" de l'objet
    dico = {
        "lieu_id": objetCodex.lieu_conservation.id,
        "localite": objetCodex.lieu_conservation.localite,
        "label": objetCodex.lieu_conservation.label
    }
    return dico


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
        "origine": [],
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
        # en faisant appel à la fonction dicoOeuvre
        for objetOeuvre in objetUC.contenu:
            dicoUCcourante = dicoOeuvre(objetOeuvre)
            dicoUC["oeuvres"].append(dicoUCcourante)
        
        # On ajoute le dictionnaire décrivant le contenu de l'unité codicologique courante au dictionnaire description
        description["contenu"].append(dicoUC)
    
    # Pour les provenances et l'origine du manuscrit, on opère des jointures manuelles sur la classe Provenances
    for provenance in Provenances.query.filter(Provenances.codex == codex_id):
        # Pour l'origine du codices, on pose comme condition que l'attirbut booléen "origine" soit True
        if provenance.origine:
            id = Lieux.query.get(provenance.lieu).id
            label = Lieux.query.get(provenance.lieu).label
            localite = Lieux.query.get(provenance.lieu).localite
            # On ajoute les variables précédentes à un dictionnaire
            dicoOrigine = {
                "lieu_id": id,
                "label": label,
                "localite": localite,
                "cas_particulier": provenance.cas_particulier
            }
            # L'attribut remarque, s'il existe, apporte un complément au label (approximation, incertitude) :
            # on les joints dans une chaîne unique.
            if provenance.remarque:
                dicoOrigine["label"] = f"{label} ({provenance.remarque})"
            
            description["origine"].append(dicoOrigine)
        
        # Pour les autres provenances du codex
        else:
            id = Lieux.query.get(provenance.lieu).id
            label = Lieux.query.get(provenance.lieu).label
            localite = Lieux.query.get(provenance.lieu).localite
            dicoProvenance = {
                "lieu_id": id,
                "label": label,
                "localite": localite,
                "cas_particulier": provenance.cas_particulier
            }
            if provenance.remarque:
                dicoProvenance["label"] = f"{label} ({provenance.remarque})"
            description["provenances"].append(dicoProvenance)
    
    # Test : export
    with open("resultats-tests/codex.json", mode="w") as jsonf:
        json.dump(description, jsonf)
    
    # On retourne le dictionnaire description sous la forme d'un fichier Json
    return json.dumps(description)


def toutes_oeuvres():
    """
    Cette fonction retourne un objet Json de toutes les oeuvres de la base,
    avec les métadonnées de leurs auteurs et des codices qui les contiennent.
    :return type: Json
    Exemple :
    [
     {
        "oeuvre_id": 14,
        "titre": "Ad Trasimundum",
        "data.bnf": null,
        "partie_de": null,
        "auteur_id": 7,
        "auteur": "Fulgence de Ruspe (saint)",
        "auteur_ark": 12127708,
        "attr": null,
        "contenue_dans": [
            {
                "codex_id": 2,
                "lieu_conservation": {
                    "lieu_id": 2,
                    "localite": "Paris",
                    "label": "Biblioth\u00e8que nationale de France"
                },
                "label": "Paris, BnF, Latin 2077",
                "id_technique": "ark:/12148/cc599714"
            }
        ]
     },
     {
        "oeuvre_id": 21,
        "titre": "Adversus Elipandum",
        "data.bnf": null,
        "partie_de": null,
        "auteur_id": 11,
        "auteur": "Alcuin",
        "auteur_ark": 12030679,
        "attr": null,
        "contenue_dans": [
            {
                "codex_id": 3,
                "lieu_conservation": {
                    "lieu_id": 2,
                    "localite": "Paris",
                    "label": "Biblioth\u00e8que nationale de France"
                },
                "label": "Paris, BnF, Latin 2388",
                "id_technique": "ark:/12148/cc60220h"
            }
        ]
     }
    ]
    """
    # On initie une liste vide, puis on assigne l'ensemble des objets de la classe Oeuvres à classOeuvres
    oeuvres = []
    classOeuvres = Oeuvres.query.order_by(Oeuvres.titre).all()
    
    # On boucle sur chaque objet
    for objetOeuvre in classOeuvres:
        # On décrit les métadonnées d'une oeuvre grâce à la fonction dicoOeuvre()
        oeuvre = dicoOeuvre(objetOeuvre)
        
        # Pour renseigner les codices contenant l'oeuvre
        oeuvre["contenue_dans"] = []
        for objetUC in Oeuvres.query.get(objetOeuvre.id).unites_codico:
            objetCodex = objetUC.codex
            dicoCodex = {
                "codex_id": objetCodex.id,
                # Pour le lieu de conservation, on fait appel à la fonction dicoConservation
                "lieu_conservation": dicoConservation(objetCodex.id),
                # Pour le label du codex, on fait appel à la fonction labelCodex
                "label": labelCodex(objetCodex.id)["label"],
                "id_technique": objetCodex.id_technique,
            }
            oeuvre["contenue_dans"].append(dicoCodex)
        oeuvres.append(oeuvre)
        
    # test
    with open("resultats-tests/oeuvres.json", mode="w") as jsonf:
        json.dump(oeuvres, jsonf)
    
    # On retourne la liste des oeuvres sous la forme d'un objet Json
    return json.dumps(oeuvres)


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
    personnes = []
    objetsPersonne = Personnes.query.order_by(Personnes.nom).all()
    for objetPersonne in objetsPersonne:
        # On crée un dictionnaire pour renseigner les métadonnées de chaque personne
        dicoPersonne = {
                "personne_id": objetPersonne.id,
                "personne_ark": objetPersonne.data_bnf,
                # On appelle la fonction labelPersonne pour écrire le nom complet de la personne
                "label": labelPersonne(objetPersonne.id, "long"),
                "oeuvres": []
            }
        # On récupère toutes les oeuvres attribuées à un auteur
        oeuvres = []
        if objetPersonne.oeuvres_attr:
            for oeuvre in objetPersonne.oeuvres_attr:
                oeuvres.append(oeuvre)
        if objetPersonne.oeuvres_aut:
            for oeuvre in objetPersonne.oeuvres_aut:
                oeuvres.append(oeuvre)
        # On trie les oeuvres alphabétiquement selon l'attribut "titre"
        oeuvres.sort(key=attrgetter('titre'))
        
        # On récupère les attributs des objets de la classe Oeuvres contenus dans la liste "oeuvres"
        # et on les organise dans un dictionnaire sur le modèle de la fonction toutes_oeuvres()
        for oeuvre in oeuvres:
            # On applique la fonction dicoOeuvre() à nos objets
            donneesOeuvre = dicoOeuvre(oeuvre)
            # On créé une nouvelle donnée si l'oeuvre possède un auteur
            if donneesOeuvre["auteur"]:
                donneesOeuvre["relation"] = "a pour auteur"
            # Si une oeuvre possède une attribution
            elif donneesOeuvre["attr"]:
                donneesOeuvre["relation"] = "a pour attribution"
                
            # On retire à présent les clés redondantes par rapport au dictionnaire dicoPersonne
            if donneesOeuvre["attr"]:
                print(donneesOeuvre["attr"])
            """
                donneesOeuvre.pop("auteur_ark")
                donneesOeuvre.pop("auteur_id")
                donneesOeuvre.pop("auteur")
                donneesOeuvre.pop("attr_ark")
                donneesOeuvre.pop("attr_id")
                donneesOeuvre.pop("attr")
            """
            # On renseigne les codices qui contiennent l'oeuvre en mobilisant la fonction toutes_oeuvres()
            corpus = json.loads(toutes_oeuvres())
            for item in corpus:
                if item["oeuvre_id"] == donneesOeuvre["oeuvre_id"]:
                    donneesOeuvre["contenue_dans"] = item["contenue_dans"]
            dicoPersonne["oeuvres"].append(donneesOeuvre)
        
        # On ajout le dictionnaire complet à la liste
        personnes.append(dicoPersonne)
        
    with open("resultats-tests/auteurs.json", mode="w") as f:
        json.dump(personnes, f)
        
    #return auteurs
