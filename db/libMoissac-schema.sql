CREATE TABLE IF NOT EXISTS codices (
    id INTEGER PRIMARY KEY,     --? Identifiant unique de chaque codex dans la base
    cote TEXT NOT NULL,         --? Cote du codex dans la collection où il est conservé
    id_technique TEXT,          --? Identifiant de type ark, ou autre
    reliure_descript TEXT,      --? Description de la reliure du codex
    histoire TEXT               --? Description de l'histoire du codex et de sa conservation
);

CREATE TABLE IF NOT EXISTS unites_codico (
    id INTEGER PRIMARY KEY,     --? Identifiant unique de l'unité codicologique (UC) dans la base
    descript TEXT,              --? Description physique de l'unité codicologique et des mains
    loc TEXT,                   --? Dans le cas de plusieurs unités codicologiques par codex, indique la localisation de l'unité courante dans le codex
    date_pas_avant INTEGER NOT NULL, --? Borne chronologique de début pour la fabrication de l'UC
    date_pas_apres INTEGER NOT NULL, --? Borne chronologique de fin pour la fabrication de l'UC
    date_circa BOOLEAN NOT NULL --? Précise si la date porte la mention circa.
);

CREATE TABLE IF NOT EXISTS oeuvres (
    id INTEGER PRIMARY KEY,     --? Identifiant unique d'une oeuvre littéraire dans la base
    titre TEXT NOT NULL,        --? Titre de l'oeuvre dans sa forme d'autorité selon Data-BNF
    data_bnf INTEGER,           --? Identifiant Data-BNF de l'oeuvre
    partie_de REFERENCES oeuvres(id), --? Lien entre une partie d'oeuvre et l'oeuvre complète
    auteur REFERENCES personne(id) --? Lien entre l'oeuvre et son auteur
);

CREATE TABLE IF NOT EXISTS contient (
    oeuvre REFERENCES oeuvres(id),
    unites_codico REFERENCES unites_codico(id)  
);

CREATE TABLE IF NOT EXISTS personne (
    id INTEGER PRIMARY KEY,     --? Identifiant unique d'une personne physique dans la base
    nom TEXT,                   --? Nom de la personne dans sa forme d'autorité selon Data-BNF
    data_bnf INTEGER           --? Identifiant Data-BNF de la personne
);

