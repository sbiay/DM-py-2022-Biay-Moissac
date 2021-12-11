BEGIN TRANSACTION;
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
    loc_init INTEGER DEFAULT NULL,  --? Indique le début de la foliotation de l'unité courante dans le codex
    loc_init_v BOOLEAN DEFAULT NULL, --? Est vrai si l'unité codicologique commence sur un verso
    loc_fin INTEGER DEFAULT NULL,     --? Indique la fin de la foliotation de l'unité courante dans le codex
    loc_fin_v BOOLEAN DEFAULT NULL,  --? Est vrai si l'unité codicologique commence sur un verso
    date_pas_avant INTEGER NOT NULL, --? Borne chronologique de début pour la fabrication de l'UC
    date_pas_apres INTEGER NOT NULL, --? Borne chronologique de fin pour la fabrication de l'UC
    code_id INTEGER REFERENCES codices(id) --? Identifiant du codex auquel l'unité codico. appartient
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
INSERT INTO "codices" ("id","cote","id_technique","reliure_descript","histoire") VALUES (1,'Latin 2989','ark:/12148/cc60815j','Reliure du XVIIIe siècle sur ais de carton en maroquin rouge aux armes royales ; dos décoré par des poinçons, au chiffre royal ; titre au dos en lettres dorées : « Cassianus de monachis ». Contregardes et gardes en parchemin.','Produit dans le Sud-Ouest de la France, le ms. a fait partie de la bibliothèque de l’abbaye de Saint-Pierre de Moissac : il est recensé dans le catalogue de 1678 parmi les livres que Colbert fit venir de Moissac à Paris, mais il est absent du catalogue de Moissac rédigé peu avant cette date (cf. Dufour, « La composition », p. 210). Le volume est donc entré dans la collection de Jean-Baptiste Colbert (1619-1683) (cf. cote ancienne au f. 3r, « Codex Colber. 6156 ») et il entra dans la Bibliothèque du roi en 1732, avec d’autres manuscrits colbertins.'),
 (2,'Latin 2077','ark:/12148/cc599714','Reliure maroquin rouge aux armes de Colbert.','Provient de l''abbaye de Moissac, cf. Delisle, Cab. des mss ., I, 519.');
INSERT INTO "unites_codico" (
"id",
"descript",
"loc_init",
"loc_init_v",
"loc_fin",
"loc_fin_v",
"date_pas_avant",
"date_pas_apres",
"code_id"
)
VALUES
       (1,
        'Parchemin. 154 ff., précédés et suivis d’une garde en parchemin. 180 x 123 mm (justif. 130 x 80 mm). Écriture minuscule caroline d’une main principale.',
        NULL,
        NULL,
        NULL,
        NULL,
        975,
        1000,
        1)
       ;
INSERT INTO "oeuvres" ("id","titre","data_bnf","partie_de","auteur") VALUES
 (1,'Institutions cénobitiques',13771861,NULL,1),
 (2,'De officiis ministrorum',NULL,NULL,2),
 (3,'De conflictu vitiorum et virtutum',16746816,NULL,3),
 (4,'Conlatio cum Maximino Arrianorum episcopo',12076565,NULL,4),
 (5,'Contra Maximinum haereticum Arianorum episcopum',12076556,NULL,4),
 (6,'Quatre-vingt trois questions différentes',13620219,NULL,4);
INSERT INTO "personne" ("id","nom","data_bnf") VALUES (1,'Jean Cassien (saint, 0360?-0432?)',12044269),
 (2,'Ambroise (saint, 0340?-0397)',11888642),
 (3,'Ambroise Autpert (730?-784)',16708997),
 (4,'Augustin (saint, 0354-0430)',11889551);
INSERT INTO "contient" ("oeuvre","unites_codico") VALUES
 (1,1),
 (2,2),
 (3,2),
 (4,2),
 (5,2),
 (6,2);
COMMIT;
