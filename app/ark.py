import requests
from bs4 import BeautifulSoup

def arkModif(numero):
    """Cette fonction prend comme argument un numéro de la db et requête son ark complet"""
    # Ecrire la requête
    r = requests.get(f"https://data.bnf.fr/{numero}")

    # Transformer le résultat en objet BeautifulSoup
    soup = BeautifulSoup(r.text, 'html.parser')
    
    # Chercher tous les éléments 'meta'
    meta = soup.find_all("meta")
    for item in meta:
        # Chercher la valeur de l'attribut @content
        contenu = item.get('content')
        # Attention, certains @content sont None
        if type(contenu) is str and "ark" in contenu[:3]:
            ark = contenu
    
    return ark