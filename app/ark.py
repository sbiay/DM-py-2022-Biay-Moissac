import requests
from bs4 import BeautifulSoup
from app.modeles.classes import Oeuvres, Personnes
from sqlalchemy import update

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

def modificationArk(classe):
    """
    :tables type: list
    """
    tous_objets = classe.query.all()
    with open("app/db/injection.sql", mode="w") as f:
        for objet in tous_objets:
            if objet.data_bnf:
                modifier = objet.data_bnf
                """stmt = (
                    update(classe).
                        where(classe.data_bnf == modifier).
                        values(data_bnf=f'{arkModif(modifier)}')
                    )
                """
                f.write(f'''UPDATE {classe.__tablename__} SET data_bnf = "{arkModif(modifier)}" WHERE data_bnf = "{modifier}";\n''')
