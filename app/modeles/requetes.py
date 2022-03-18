import requests, time
from bs4 import BeautifulSoup

from ..modeles.classes import Codices
from ..modeles.traitements import saisieRecherche

def rechercheCote(saisie, id_conservation):
    """
    Cette fonction prend comme argument la saisie d'un utilisateur
    et cherche parmi les cotes des manuscrits de la base une cote correspondante.
    :param saisie: Saisie d'un utilisateur
    :type saisie: str
    :param id_conservation: identifiant du lieu de conservation associé au codex dont on analyse la cote
    :type id_conservation: int
    :returns: False si la saisie ne correspond à aucune cote, True si la saisie correspond à une cote
    :return type: bool
    """
    
    # On charge les codices de la base pour récupérer leur cote
    
    codices = Codices.query.filter(Codices.conservation_id == id_conservation).all()
    # On écrit une liste de dictionnaires pour récupérer les scores de la recherche
    listeCotes = []
    for codex in codices:
        # On initie un score
        dictCote = {
            "cote": codex.cote,
            "score": 0
        }
        listeCotes.append(dictCote)
    
    # On nettoie et découpe la saisie
    motscles = saisieRecherche(saisie, False)
    
    cotePertinentes = []
    # On boucle sur chaque codex via listeDictCodices
    for cote in listeCotes:
        # On procède par élimination des cotes qui ne sont pas pertinentes, vis-à-vis des mots
        pertinent = True
        # On boucle sur chaque mot-clé
        for mot in motscles[0]:
            # On cherche une occurrence du mot-clé courant dans les données
            chaine = cote["cote"].lower()
            chaine = chaine.split()
            if mot not in chaine:
                pertinent = False
        # Si tous les mots sont présents dans la cote, alors on ajoute la cote aux résultats
        if pertinent:
            cotePertinentes.append(cote)
    
    if cotePertinentes:
        return True
    # Si la condition n'a jamais été remplie : aucun match, on retourne False
    return False


def rechercheArk(motcle, arks, reponse=["codices", "oeuvres", "personnes"]):
    """
    Cette fonction prend comme argument un mot-clé traité à partir d'une saisie d'utilisateur
    ainsi qu'une liste d'identifiants ark,
    adresse à data.bnf.fr une requête get à partir de cette saisie,
    croise les réponses de data.bnf avec les identifiants ark enregistrés dans la base libMoissac,
    retourne un set des clés primaires des codices contenant ark.
    :param motcle: mot-clé traité à partir d'une saisie d'utilisateur
    :motcle type: str
    :param arks: dictionnaire où sont renseignés les arks des objets de la base locale, par type de classe
    :arks type: dict
    :return type: set
    """
    
    # On écrit la requête
    r = requests.get(f"https://data.bnf.fr/fr/search?term={motcle}", time.sleep(3))
    
    # Si la requête rencontre un problème, on retourne un set vide
    if r.status_code == 200:
        # On transforme la réponse HTML de data.bnf en objet BeautifulSoup afin de pouvoir le parser
        soup = BeautifulSoup(r.text, "html.parser")
        reponses = []
        
        # Parser la réponse : les identifiants ark potentiellement intéressants apparaissent dans les éléments "a"
        liens = soup.find_all("a")
        for lien in liens:
            if lien.get("href")[25:28] == "ark":
                reponses.append(lien["href"][25:])
        
        # Si l'un des ark de la réponse est dans les ark de notre base de données, on retourne l'id du codex concerné
        idCodicesPertinents = []
        # On boucle sur les arks de la base de données
        for typeArk in arks:
            for ark in arks[typeArk]:
                if ark in reponses:
                    for idCodex in arks[typeArk][ark]:
                        idCodicesPertinents.append(idCodex)
        
        return set(idCodicesPertinents)
    
    else:
        return {}

def creationDataBNF(motscles, objet=["auteur", "oeuvre"]):
    """
    Cette fonction prend comme paramètre des mots-clés et un paramètre auteur ou oeuvre
    et retourne, selon ce dernier, une liste d'auteurs ou une liste d'oeuvres répondant à ces mots-clés
    sur le site Data-BnF.
    """
    # Parser la saisie du champ recherche
    motscles = motscles.replace(" ", "+")
    
    # Faire une requête data.bnf à partir des mots-clés
    r = requests.get(f"https://data.bnf.fr/fr/search?term={motscles}")
    
    # Transformer la réponse HTML de data.bnf en objet BeautifulSoup afin de pouvoir le parser
    soup = BeautifulSoup(r.text, "html.parser")
    reponses = []
    for index, span in enumerate(soup.find_all('span')):
        # Les label que l'on souhaite récupérer sont contenus dans des spans dépourvus de class, sauf le premier
        if span.get("class") == None:
            reponses.append(span.string)
            # La réponse est une liste où s'intercalent 'Auteurs', 'Œuvres' et 'Thèmes' : on récupère les index
            if span.string == 'Auteurs':
                premierAuteur = index + 1
            elif span.string == 'Œuvres':
                premiereOeuvre = index + 1
            elif span.string == 'Thèmes':
                premierTheme = index + 1
    
    # Liste des catégories de tri des réponses par défaut dans data.bnf
    categories = ["Auteurs", "Organisations", "Œuvres", "Thèmes", "Lieux", "Spectacles", "Périodiques"]
    categories_presentes = []
    # Pour déterminer la liste des catégories présentes parmi les réponses
    for item in categories:
        if item in reponses:
            categories_presentes.append(item)
    # Pour établir les index de début de ces catégories sous forme d'une liste de tuples
    index_categories_presentes = []
    for categorie in categories_presentes:
        index_categories_presentes.append((categorie, reponses.index(categorie) + 1))
    
    # Pour établir dans quels tuples se trouvent l'index initial des auteurs et celui des oeuvres
    index_auteurs = categories_presentes.index("Auteurs")
    index_oeuvres = categories_presentes.index("Œuvres")
    
    # Pour la liste propre des noms d'auteurs
    # Attention : si la catégorie est en dernière position : IndexError
    auteurs = reponses[
              index_categories_presentes[index_auteurs][1]
              :
              (index_categories_presentes[index_auteurs + 1][1]) - 1]
    
    # Pour la liste propre des noms d'oeuvres
    oeuvres = reponses[
              index_categories_presentes[index_oeuvres][1]
              :
              (index_categories_presentes[index_oeuvres + 1][1]) - 1]
    
    if objet == "auteur":
        return auteurs
    else:
        return oeuvres
