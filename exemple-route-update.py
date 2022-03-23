from flask import render_template, request, flash, redirect
from flask_login import current_user, login_user, logout_user, login_required

@app.route("/place/<int:place_id>/update", methods=["GET", "POST"])
@login_required
def lieu_update(place_id):
    """ Route permettant l'affichage des données d'un lieu

    :param place_id: Identifiant numérique du lieu
    """
    # On a bien sûr aussi modifié le template pour refléter le changement
    mon_lieu = Place.query.get_or_404(place_id)
    place_types = PlaceType.query.all()

    erreurs = []
    updated = False

    if request.method == "POST":
        # J"ai un formulaire
        if not request.form.get("placeNom", "").strip():
            erreurs.append("placeNom")
        if not request.form.get("placeLongitude", "").strip():
            erreurs.append("placeLongitude")
        if not request.form.get("placeLatitude", "").strip():
            erreurs.append("placeLatitude")
        if not request.form.get("placeDescription", "").strip():
            erreurs.append("placeDescription")
            
        if not request.form.get("placeType", "").strip():
            erreurs.append("placeType")
        elif not PlaceType.query.get(request.form["placeType"]):
            erreurs.append("placeType")

        if not erreurs:
            print("Faire ma modifications")
            mon_lieu.place_nom = request.form["placeNom"]
            mon_lieu.place_longitude = request.form["placeLongitude"]
            mon_lieu.place_latitude = request.form["placeLatitude"]
            mon_lieu.place_description = request.form["placeDescription"]
            
            # Soit je passe toujours par ce code :
            #mon_lieu.place_type = request.form["placeType"]
            # Soit j'utilise la relationship
            mon_lieu.has_type = PlaceType.query.get(request.form["placeType"])

            db.session.add(mon_lieu)
            db.session.add(Authorship(place=mon_lieu, user=current_user))
            db.session.commit()
            updated = True
    return render_template(
        "pages/place_form_update.html", 
        nom="Gazetteer",
        lieu=mon_lieu,
        placeTypes=place_types,
        erreurs=erreurs,
        updated=updated
    )

