SELECT codices.cote, unites_codico.id, unites_codico.loc_init, unites_codico.date_pas_avant, contient.oeuvre, personne.nom, oeuvres.titre
FROM codices, unites_codico, contient, oeuvres, personne
WHERE codices.id = unites_codico.code_id
AND contient.unites_codico = unites_codico.id
AND oeuvres.id = contient.oeuvre
AND personne.id = oeuvres.auteur
ORDER BY codices.id, unites_codico.id;