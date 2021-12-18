import requests
from ..appliMoissac import db
from ..modeles.classes import Codices, Unites_codico, Oeuvres, Contient

def requeteOeuvres(saisie):
    """
    Cette fonction prend comme argument la saisie d'un utilisateur,
    adresse à data.bnf.fr une requête à partir de cette saisie,
    croise les réponses de data.bnf avec les identifiants ark des oeuvres enregistrées
    dans la base libMoissac,
    retourne la liste de clés primaires des codices contenant ces oeuvres.
    """
    
    # Parser la saisie du champ recherche
    motscles = saisie.replace(" ", "+")
    
    # Ecrire la requête
    r = requests.get(f"https://data.bnf.fr/fr/search?term={motscles}")
    
    # Charger les identifiants ark pertinents pour la recherche sur les auteurs
    oeuvres = Oeuvres.query.all()
    ark_oeuvres = []
    for oeuvre in oeuvres:
        if oeuvre.data_bnf:
            ark_oeuvres.append(oeuvre.data_bnf)

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