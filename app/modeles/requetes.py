import requests, time
from bs4 import BeautifulSoup


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
