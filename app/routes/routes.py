from flask import Flask, render_template
from ..appliMoissac import app
from ..modeles.classes import Codices, Lieux, Unites_codico, Oeuvres, Contient, Personne


@app.route("/")
def accueil():
    return render_template("pages/accueil.html", nom="Bibliothèque de Moissac")


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