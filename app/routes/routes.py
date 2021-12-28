from flask import Flask, render_template
from ..appliMoissac import app
from ..modeles.classes import Codices, Lieux, Unites_codico, Oeuvres, Contient, Personne


@app.route("/")
def accueil():
    return render_template("pages/accueil.html")

@app.route("/pages/<quel_index>")
def index(quel_index):
    indexes = ["auteurs", "codices", "oeuvres"]
    
    # auteurs est un dictionnaire de dictionnaire
    # Les clés de premier niveau sont des noms d'auteurs
    # Les valeurs sont des dictionnaires, dont les clés sont des oeuvres et les valeurs sont
    classOeuvres = Oeuvres.query.all()
    auteurs = {}
    
    for item in classOeuvres:
        if item.auteur:
            auteur = Personne.query.get(item.auteur)
            # auteur.nom est le nom de l'auteur
            # item.titre est le titre de l'oeuvre en question
            
            # Si l'auteur n'existe pas, l'ajoute comme clé (sous la forme d'un tuple contenant son id et son nom)
            # avec comme valeur une liste d'une seule oeuvre (sous la forme d'un tuple contenant son id et son titre)
            if not auteurs.get((auteur.rowid, auteur.nom)):
                auteurs[(auteur.rowid, auteur.nom)] = [(item.id, item.titre)]
            # Si l'auteur existe, ajoute l'oeuvre à la liste des valeurs
            else:
                auteurs[(auteur.rowid, auteur.nom)].append((item.id, item.titre))
        # Même traitement si l'oeuvre est simplement attribuée (on ajoute une simple mention en fin de titre)
        elif item.attr:
            auteur = Personne.query.get(item.attr)
            # auteur.nom est le nom de l'auteur
            # item.titre est le titre de l'oeuvre en question
    
            # Si l'auteur n'existe pas, l'ajoute comme clé avec comme valeur une liste d'une seule oeuvre
            if not auteurs.get((auteur.rowid, auteur.nom)):
                auteurs[(auteur.rowid, auteur.nom)] = [(item.id, item.titre + " (attribution douteuse")]
            # Si l'auteur existe, ajoute l'oeuvre à la liste des valeurs
            else:
                auteurs[(auteur.rowid, auteur.nom)].append((item.id, item.titre + " (attribution douteuse"))
                
    # Ajoute au dictionnaire auteurs les codices qui contiennent chaque oeuvre :
    auteurs_liste_avec_codex = {}
    for auteur in auteurs:
        auteurs_liste_avec_codex[auteur] = []
        for oeuvre in auteurs[auteur]:
            oeuvre_id = oeuvre[0]
            UCs = Contient.query.filter(Contient.oeuvre == oeuvre_id).all()
            oeuvre_avec_codex = {oeuvre: []}
            for UC in UCs:
                req = Unites_codico.query.filter(Unites_codico.id == UC.unites_codico).one()
                code_id = req.code_id
                cote = Codices.query.get(code_id).cote
                if cote[:5] == "Latin":
                    lieu_conserv = "Paris, BnF"
                else:
                    lieu_conserv = "Attention ! règle à créer"
                codex_label = (code_id, f"{lieu_conserv}, {cote}")
                
                # Ajout du codex au dictionnaire des auteurs, pour chaque oeuvre
                # d'une liste de tuples contenant l'id du codex et son label
                
                # Pour ne pas ajouter deux fois le codex d'une oeuvre qui y serait conservée en plusieurs fragments
                if codex_label not in oeuvre_avec_codex[oeuvre]:
                    oeuvre_avec_codex[oeuvre].append(codex_label)
            auteurs_liste_avec_codex[auteur].append(oeuvre_avec_codex)
    
    auteurs = auteurs_liste_avec_codex
    codices = "Voici la liste des codices"
    oeuvres = "Voici la liste des oeuvres"
    
    if quel_index == indexes[0]:
        return render_template("pages/index.html", auteurs=auteurs)
    elif quel_index == indexes[1]:
        return render_template("pages/index.html", codices=codices)
    elif quel_index == indexes[2]:
        return render_template("pages/index.html", oeuvres=oeuvres)
    

@app.route("/pages/codices/<int:num>")
def notice_codex(num):
    codex = Codices.query.get(num)
    
    # Pour le lieu de conservation du codex
    id_lieu_cons = Codices.query.get(num).lieu_conservation
    lieu_conservation = Lieux.query.get(id_lieu_cons)
    if lieu_conservation.label == "Bibliothèque nationale de France":
        lieu_conservation = lieu_conservation.localite + ", BnF"
    else:
        lieu_conservation = lieu_conservation.localite + ", " + lieu_conservation.label
    
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
                               titre= f"{lieu_conservation}, {codex.cote}",
                               reliure=codex.reliure_descript,
                               histoire=codex.histoire,
                               descUCs=descUCs)
    else:
        return render_template("pages/codices.html", message_erreur="Cette adresse ne correspond à aucune notice !")