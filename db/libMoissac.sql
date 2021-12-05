BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "codices" (
	"id"	INTEGER,
	"cote"	TEXT NOT NULL,
	"id_technique"	TEXT,
	"reliure_descript"	TEXT,
	"histoire"	TEXT,
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "unites_codico" (
	"id"	INTEGER,
	"descript"	TEXT,
	"loc"	TEXT,
	"date_pas_avant"	INTEGER NOT NULL,
	"date_pas_apres"	INTEGER NOT NULL,
	"date_circa"	BOOLEAN NOT NULL,
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "oeuvres" (
	"id"	INTEGER,
	"titre"	TEXT NOT NULL,
	"data_bnf"	INTEGER,
	"partie_de"	,
	"auteur"	,
	PRIMARY KEY("id"),
	FOREIGN KEY("partie_de") REFERENCES "oeuvres"("id"),
	FOREIGN KEY("auteur") REFERENCES "personne"("id")
);
CREATE TABLE IF NOT EXISTS "personne" (
	"id"	INTEGER,
	"nom"	TEXT,
	"data_bnf"	INTEGER,
	PRIMARY KEY("id")
);
INSERT INTO "codices" ("id","cote","id_technique","reliure_descript","histoire") VALUES (1,'Latin 2989','ark:/12148/cc60815j','Reliure du XVIIIe siècle sur ais de carton en maroquin rouge aux armes royales ; dos décoré par des poinçons, au chiffre royal ; titre au dos en lettres dorées : « Cassianus de monachis ». Contregardes et gardes en parchemin.','Produit dans le Sud-Ouest de la France, le ms. a fait partie de la bibliothèque de l’abbaye de Saint-Pierre de Moissac : il est recensé dans le catalogue de 1678 parmi les livres que Colbert fit venir de Moissac à Paris, mais il est absent du catalogue de Moissac rédigé peu avant cette date (cf. Dufour, « La composition », p. 210). Le volume est donc entré dans la collection de Jean-Baptiste Colbert (1619-1683) (cf. cote ancienne au f. 3r, « Codex Colber. 6156 ») et il entra dans la Bibliothèque du roi en 1732, avec d’autres manuscrits colbertins.');
INSERT INTO "unites_codico" ("id","descript","loc","date_pas_avant","date_pas_apres","date_circa") VALUES (1,'Parchemin. 154 ff., précédés et suivis d’une garde en parchemin. 180 x 123 mm (justif. 130 x 80 mm). Écriture minuscule caroline d’une main principale.',NULL,975,1000,0);
INSERT INTO "oeuvres" ("id","titre","data_bnf","partie_de","auteur") VALUES (1,'Institutions cénobitiques',13771861,NULL,1);
INSERT INTO "personne" ("id","nom","data_bnf") VALUES (1,'Jean Cassien (saint, 0360?-0432?)',12044269);
COMMIT;
