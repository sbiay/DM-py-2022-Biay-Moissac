from flask import Flask, render_template
from ..appliMoissac import app
from ..modeles.classes import Codices, Unites_codico, Oeuvres


@app.route("/")
def conteneur():
    return render_template("conteneur.html", nom="Bibliothèque de Moissac")


@app.route("/pages/")
def accueil():
    return render_template("pages/accueil.html", nom="Bibliothèque de Moissac")


@app.route("/pages/codices/<int:num>")
def notice_codex(num):
    codex = Codices.query.get(num)
    
    # Requête portant sur les unités codicologiques enfants d'un codex désigné par son identifiant
    # A mettre dans un script à part "contenu_notice_codex"
    listUC_enfants = Unites_codico.query.filter(Unites_codico.code_id == num).all()
    paramsUCs = []
    for UC in listUC_enfants:
        paramsUC = {}
        paramsUC["description"] = UC.descript
        
        # Conditions portant sur le booléen relatif aux recto/verso au début et à la fin de l'UC
        if UC.loc_init_v:
            rvdebut = "v"
        else:
            rvdebut = ""
        if UC.loc_fin_v:
            rvfin = "v"
        else:
            rvfin = ""
        paramsUC["localisation"] = f"f. {str(UC.loc_init)}{rvdebut}-{str(UC.loc_fin)}{rvfin}"
        
        paramsUC["date"] = f"entre {UC.date_pas_avant} et {UC.date_pas_apres}"
        
        # Il faut à présent boucler sur les contenus de chaque UC, et requêter leurs auteurs
    
    # Test d'existence d'un index dans la liste des prem_codices :
    codices = Codices.query.all()
    if num <= len(codices):
        # Si l'id passé dans l'URL n'est pas plus grand que la liste
        # de tous les codices, alors :
        return render_template("pages/codices.html",
                               titre=codex.cote,
                               reliure=codex.reliure_descript,
                               histoire=codex.histoire,
                               paramsUCs=paramsUCs)
    else:
        return render_template("pages/codices.html", message_erreur="Cette adresse ne correspond à aucune notice !")
