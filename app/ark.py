import requests
from bs4 import BeautifulSoup

def arkModif(numero):
    """Cette fonction prend comme argument un numéro de la db et requête son ark complet"""
    # Ecrire la requête
    r = requests.get(f"https://data.bnf.fr/{numero}")

    soup = BeautifulSoup(r.text, 'html.parser')
    
    meta = soup.find_all("meta")
    for item in meta:
        contenu = item.get('content')
        if "ark" in contenu[:3]:
            print(contenu)
