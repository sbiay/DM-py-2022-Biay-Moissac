import requests
from bs4 import BeautifulSoup
from ..appliMoissac import db
from ..modeles.classes import Codices, Unites_codico, Oeuvres, Contient

def rechercheSimple(motscles):
    """
    :param motscles: saisie du champ recherche nettoyée
    :type motscles: list
    """
    # Charger les identifiants ark pertinents pour la recherche sur les auteurs et sur les oeuvres
    # J'ai pour cela besoin de tous les ark intéressants de ma base

def requeteOeuvres(motscles):
    """
    Cette fonction prend comme argument la saisie d'un utilisateur,
    adresse à data.bnf.fr une requête get à partir de cette saisie,
    croise les réponses de data.bnf avec les identifiants ark des oeuvres enregistrées dans la base libMoissac,
    retourne la liste de clés primaires des codices contenant ces oeuvres.
    """
    
    
    # Charger les identifiants ark pertinents pour la recherche sur les auteurs
    oeuvres = Oeuvres.query.all()
    ark_oeuvres = []
    for oeuvre in oeuvres:
        if oeuvre.data_bnf:
            ark_oeuvres.append(oeuvre.data_bnf)
    
    # Ecrire la requête
    r = requests.get(f"https://data.bnf.fr/fr/search?term={motscles}")

    # Parser la réponse
    reponses = []  # Contient une liste d'identifiants ark
    for ligne in r.text.split("\n"):
        for ark in ark_oeuvres:
            if str(f"=https://data.bnf.fr/fr/{ark}/") in ligne:
                reponses.append(ark)
    
    # Requête sur les codices concernés
    # Liste des oeuvres
    oeuvres = []
    for ark in reponses:
        r = Oeuvres.query.filter(Oeuvres.data_bnf == int(ark)).one()
        oeuvres.append(r)
    
    # Liste des codices qui les contiennent
    codices = []
    for oeuvre in oeuvres:
        # Toutes les UC contenant chaque oeuvre
        r = Contient.query.filter(Contient.oeuvre == oeuvre.id).all()
        for conteneur in r:
            r_uc = Unites_codico.query.filter(Unites_codico.id == conteneur.unites_codico).all()
            for uc in r_uc:
                r_cod = Codices.query.filter(Codices.id == uc.code_id).all()
                for codex in r_cod:
                    codices.append(codex.id)
    print(codices)
    return codices


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
    soup = BeautifulSoup(r.text, features="lxml")
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