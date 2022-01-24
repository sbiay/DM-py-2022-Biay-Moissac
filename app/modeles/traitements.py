from .classes import Codices, Personnes

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


def labelDate(chaine):
    """Cette fonction prend une chaîne de caractère contenant une date et traite les informations
    de type approximatif et les retourne mises en forme :
    :param chaine: chaine de caractère à traiter
    :type chaine: str
    :returns: chaine exprimant une éventuelle approximation de date de la façon suivante : v. 1550, ou av./apr. 1550.
    :returns type: str
    """
    if chaine[0] == "0":
        chaine = chaine[1:]
    if chaine[-1] == "?":
        chaine = "v. " + chaine[:-1]
    elif "." in chaine:
        chaine = "apr. " + chaine.replace(".", "0")
    return chaine


def labelPersonne(idPersonne, forme=["court", "long"]):
    """
    Cette fonction prend comme argument l'identifiant d'une personne dans la db
    (correspondant à sa typographie selon Data-BNF)
    ainsi qu'un paramètre "forme" définissant la forme courte ou longue (sans dates ou avec dates)
    sous laquelle le nom de la personne est retourné par la fonction.
    :param idPersonne: clé primaire d'un objet de la classe Personne
    :type idPersonne: int
    :param forme: prend les valeurs "court" ou "long"
    :type forme: str
    :returns: nom d'une personne assortie ou non de ses dates selon que le paramètre forme est "court" ou "long".
    :rtype: str
    """
    nomPersonne = Personnes.query.get(idPersonne).nom
    
    # On retient pour la page le nom sans les parenthèses, sauf si elles contiennent un titre (pape,
    # saint, etc)
    
    # Gestion des cas particuliers
    if idPersonne == 16:
        # Macer Floridus (auteur prétendu)
        return nomPersonne
    elif idPersonne == 15:
        # Odon de Meung (10..-10..)
        if forme == "long":
            return "Odon de Meung (XIe siècle)"
    
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
        # Si l'on veut obtenir un label de nom avec les dates de la personne
        if nomPersonne.split("(")[1][0] not in "0123456789":
            # Si la forme d'autorité DataBNF place en tête de parenthèse non une date (chiffre) mais un rôle (lettre)
            parenthese = nomPersonne.split('(')[1][:-1]
            role = parenthese.split(", ")[0]
            dates = parenthese.split(", ")[1]
            dateNaissance = dates.split("-")[0]
            dateNaissance = labelDate(dateNaissance)
            dateMort = dates.split("-")[1]
            dateMort = labelDate(dateMort)
            nom = f"{nomPersonne.split('(')[0][:-1]} ({role}, {dateNaissance}-{dateMort})"
            return nom
        else:
            # Si les parenthèses ne contiennent que des dates
            parenthese = nomPersonne.split('(')[1][:-1]
            dates = parenthese.split("-")
            dateNaissance = dates[0]
            dateNaissance = labelDate(dateNaissance)
            dateMort = dates[1]
            dateMort = labelDate(dateMort)
            nom = f"{nomPersonne.split('(')[0][:-1]} ({dateNaissance}-{dateMort})"
            return nom
    else:
        print('''Le paramètre forme n'accepte que les valeurs "long" et "court"''')
        return None
