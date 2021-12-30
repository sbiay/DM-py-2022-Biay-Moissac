import json
from flask import Flask, render_template, request, url_for
from ..appliMoissac import app
from ..modeles.classes import Codices, Lieux, Unites_codico, Oeuvres, Contient, Personne
from ..modeles.jointures import labelCodex


@app.route("/")
def accueil():
    return render_template("pages/accueil.html")

@app.route("/pages/<quel_index>")
def index(quel_index):
    indexes = ["auteurs", "codices", "oeuvres"]

    auteurs = {}
    """
    auteurs est un dictionnaire destiné à accueillir, pour chaque auteur de la classe Oeuvres
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
    classOeuvres = Oeuvres.query.all()
    for item in classOeuvres:
        if item.auteur:
            auteur = Personne.query.get(item.auteur)
            
            """
            Si l'auteur n'existe pas dans le dictionnaire auteurs,
            on ajoute comme clé son id et comme valeur un dictionnaire comprenant
            - label : (son nom)
            - oeuvres : une liste de dictionnaires, avec :
                - clé : id des oeuvres
                - valeurs :
                    - label : titre de l'oeuvre
                    - codices : une liste vide qui acceuillera les codices qui le contiennent
            """
            if not auteurs.get(auteur.id):
                auteurs[auteur.id] = {
                    "label": auteur.nom,
                    "oeuvres": [
                        {item.id: {
                            "label": item.titre,
                            "codices": []
                            }
                        }
                    ]
                }
            # Si l'auteur existe, ajoute l'oeuvre (item) à la liste des valeurs
            else:
                auteurs[auteur.id]["oeuvres"].append(
                    {item.id: {
                        "label": item.titre,
                        "codices": []
                        }
                    }
                )
        # Même traitement si l'oeuvre est simplement attribuée (on ajoute une simple mention en fin de titre)
        if item.attr:
            auteur = Personne.query.get(item.attr)
    
            # Si l'auteur n'existe pas dans le dictionnaire auteurs,
            # l'ajoute comme clé (sous la forme d'un tuple)
            # avec comme valeur une liste d'un seul tuple contenant son id et son titre)
            if not auteurs.get(auteur.id):
                auteurs[auteur.id] = {
                    "label": auteur.nom,
                    "oeuvres": [
                        {item.id: {
                            "label": f"{item.titre} (attribué à)",
                            "codices": []
                        }
                        }
                    ]
                }
            # Si l'auteur existe, ajoute l'oeuvre à la liste des valeurs
            else:
                auteurs[auteur.id]["oeuvres"].append(
                    {item.id: {
                        "label": f"{item.titre} (attribué à)",
                        "codices": []
                    }
                    }
                )
           
    # On ajoute ici le contenu de la liste qui est la valeur de la clé codices dans le dictionnaire auteurs
    for id_auteur in auteurs:
        for dict_oeuvre in auteurs[id_auteur]["oeuvres"]:
            for id_oeuvre in dict_oeuvre:
                UCs = Contient.query.filter(Contient.oeuvre == id_oeuvre).all()
                for UC in UCs:
                    req = Unites_codico.query.filter(Unites_codico.id == UC.unites_codico).one()
                    code_id = req.code_id
                    codex = labelCodex(code_id)
                    # Si l'oeuvre est présente dans le même codex sous plusieurs fragments
                    # le codex n'est ajouté qu'une seule fois
                    if not codex in dict_oeuvre[id_oeuvre]["codices"]:
                        dict_oeuvre[id_oeuvre]["codices"].append(codex)

    with open("resultats-tests/auteurs.json", mode="w") as jsonf:
        json.dump(auteurs, jsonf)
    
    codices = "Voici la liste des codices"
    oeuvres = "Voici la liste des oeuvres"
    url_site = url_for("accueil")

    if quel_index == indexes[0]:
        return render_template(
            "pages/auteurs.html", auteurs=auteurs, url_site=url_site
        )
    elif quel_index == indexes[1]:
        return render_template("pages/codices.html", codices=codices, url_site=url_site)
    elif quel_index == indexes[2]:
        return render_template("pages/oeuvres.html", oeuvres=oeuvres, url_site=url_site)
    

@app.route("/pages/codices/<int:num>")
def notice_codex(num):
    codex = Codices.query.get(num)
    
    # Pour le lieu de conservation et la cote du codex
    label = labelCodex(num)[num]
    
    # Liste des unités codicologiques enfants du codex
    listUC_enfants = Unites_codico.query.filter(Unites_codico.code_id == num).order_by(Unites_codico.loc_init).all()
    
    # Eléments descriptifs de chaque unité codicologique
    descUCs = []
    for UC in listUC_enfants:
        descUC = {}
        descUC["description"] = UC.descript
        
        # Conditions portant sur le booléen relatif aux recto/verso au début et à la fin de l'UC
        if UC.loc_init_v:
            rvdebut = "v"
        else:
            rvdebut = ""
        if UC.loc_fin_v:
            rvfin = "v"
        else:
            rvfin = ""
        descUC["localisation"] = f"f. {str(UC.loc_init)}{rvdebut}-{str(UC.loc_fin)}{rvfin}"
        
        descUC["date"] = f"entre {UC.date_pas_avant} et {UC.date_pas_apres}"
        
        # Il faut à présent boucler sur les contenus de chaque UC
        requ_contenu = Contient.query.filter(Contient.unites_codico == UC.id).all()
        # requ_contenu est une liste de mapping possédant comme propriétés .oeuvre et .unites_codico
        # et ce d'après la table de relation "contient"
        
        # On peut donc initier une liste dont les valeurs seront les résultats des requêtes sur
        # la classe Oeuvres en fonction du mapping assigné précédemment
        contenu = []
        # En bouclant sur les items de cette requête, je requête la classe Oeuvres pour obtenir
        # les données relatives à chaque oeuvre de l'unité codicologique présente
        for items in requ_contenu:
            auteur = Oeuvres.query.get(items.oeuvre).auteur
            titre = Oeuvres.query.get(items.oeuvre).titre
            if auteur:
                # Le nom sous la forme d'autorité (avec fonction et dates entre parenthèses)
                nom = Personne.query.get(auteur).nom
                
                # On retient pour la page le nom sans les parenthèses, sauf si elles contiennent un titre (pape,
                # saint, etc)
                # Si le premier caractère après la parenthèse n'est pas un chiffre, c'est un titre (on dira "role"
                # pour éviter les confusions avec les titres d'oeuvre)
                # retenir :
                if nom.split("(")[1][0] not in "0123456789":
                    role = nom.split("(")[1].split(",")[0]
                    # Le nom sans les dates, suivi du role
                    nom = f"{nom.split('(')[0][:-1]} ({role})"
                else:
                    nom = f"{nom.split('(')[0][:-1]}"
            else:
                nom = "Anonyme"
            contenu.append((nom, titre))
        
        descUC["contenu"] = contenu
        
        # Après avoir bouclé sur les items du contenu, on ajoute le dictionnaire à la liste descUCs
        descUCs.append(descUC)
    
    # A la fin de ma boucle sur les unités codicologiques, la liste descUCs contient les données
    # relatives à chacune.
    
    # Test d'existence d'un index dans la liste codices :
    codices = Codices.query.all()
    
    if num <= len(codices) and num !=0:
        # Si l'id passé dans l'URL n'est pas plus grand que la liste
        # de tous les codices, alors :
        return render_template("pages/codices.html",
                               titre= f"{label}",
                               reliure=codex.reliure_descript,
                               histoire=codex.histoire,
                               descUCs=descUCs)
    else:
        return render_template("pages/codices.html", message_erreur="Cette adresse ne correspond à aucune notice !")
    
@app.route("/recherche")
def recherche():
    motclef = request.args.get("keyword", None)
    with open("resultats-tests/test.txt" , mode="w") as f:
        f.write(motclef)