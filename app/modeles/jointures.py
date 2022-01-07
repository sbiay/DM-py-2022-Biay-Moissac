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
    lieu_conservation = Codices.query.get(code_id).conservation
    if lieu_conservation.label == "Bibliothèque nationale de France":
        lieu_conservation = lieu_conservation.localite + ", BnF"
    else:
        lieu_conservation = lieu_conservation.localite + ", " + lieu_conservation.label
    
    label = f"{lieu_conservation}, {cote}"
    dico[code_id] = label
    return dico


def labelPersonne(idPersonne, forme):
    """
    Cette fonction prend comme argument l'identifiant d'une personne dans la db
    ainsi qu'un paramètre "forme" définissant la forme sous laquelle le nom de la personne est retournée par la fonction
    :param idPersonne: clé primaire d'un objet de la classe Personne
    :type idPersonne: int
    :param forme: prend les valeurs "court" ou "long"
    :type forme: str
    :returns: nom d'une personne assortie ou non de ses dates selon que le paramètre forme est "court" ou "long".
    :rtype: str
    """
    nomPersonne = Personne.query.get(idPersonne).nom
    
    # On retient pour la page le nom sans les parenthèses, sauf si elles contiennent un titre (pape,
    # saint, etc)
    
    # Gestion des cas particuliers (Macer Floridus (auteur prétendu))
    if idPersonne == 16:
        return nomPersonne
    
    if forme == "court":
        if nomPersonne.split("(")[1][0] not in "0123456789":
            """Si le premier caractère après la parenthèse n'est pas un chiffre, c'est un titre
            (on dira "role" pour éviter les confusions avec les titres d'oeuvre) retenir :"""
            role = nomPersonne.split("(")[1].split(",")[0]
            # Le nom sans les dates, suivi du role
            nom = f"{nomPersonne.split('(')[0][:-1]} ({role})"
        else:
            nom = f"{nomPersonne.split('(')[0][:-1]}"
        return nom
    elif forme == "long":
        if nomPersonne.split("(")[1][0] not in "0123456789":
            # Le nom sans les dates, suivi du role
            parenthese = nomPersonne.split('(')[1][:-1]
            role = parenthese.split(", ")[0]
            """Il faudrait traiter deux autres types de caractères :
            - Les '?', à remplacer par un 'v.' avant la date
            - Les '.', à remplacer par des '0' en ajoutant 'apr.' ou 'av.' en tête de la date"""
            dates = parenthese.split(", ")[1]
            dateNaissance = dates.split("-")[0]
            if dateNaissance[0] == "0":
                dateNaissance = dateNaissance[1:]
            dateMort = dates.split("-")[1]
            if dateMort[0] == "0":
                dateMort = dateMort[1:]
            nom = f"{nomPersonne.split('(')[0][:-1]} ({role}, {dateNaissance}-{dateMort})"
        else:
            parenthese = nomPersonne.split('(')[1][:-1]
            dates = parenthese.split("-")
            dateNaissance = dates[0]
            if dateNaissance[0] == "0":
                dateNaissance = dateNaissance[1:]
            dateMort = dates[1]
            if dateMort[0] == "0":
                dateMort = dateMort[1:]
            nom = f"{nomPersonne.split('(')[0][:-1]} ({dateNaissance}-{dateMort})"
            return nom
    else:
        print('''Le paramètre forme n'accepte que les valeurs "long" et "court"''')
        return None

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
    objetsPersonne = Personne.query.order_by(Personne.nom).all()
    for objetPersonne in objetsPersonne:
        personnes[objetPersonne.id] = {"label": objetPersonne.nom, "oeuvres": []}
    
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
