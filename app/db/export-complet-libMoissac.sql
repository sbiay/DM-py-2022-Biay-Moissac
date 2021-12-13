BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "codices" (
	"id"	INTEGER PRIMARY KEY,
	"cote"	TEXT NOT NULL,
	"id_technique"	TEXT,
	"reliure_descript"	TEXT,
	"histoire"	TEXT
	
);
CREATE TABLE IF NOT EXISTS "unites_codico" (
	"id"	INTEGER PRIMARY KEY,
	"descript"	TEXT,
	"loc_init"	INTEGER DEFAULT NULL,
	"loc_init_v"	BOOLEAN DEFAULT NULL,
	"loc_fin"	INTEGER DEFAULT NULL,
	"loc_fin_v"	BOOLEAN DEFAULT NULL,
	"date_pas_avant"	INTEGER NOT NULL,
	"date_pas_apres"	INTEGER NOT NULL,
	"code_id"	INTEGER FOREIGN KEY REFERENCES "codices"("id")
);
CREATE TABLE IF NOT EXISTS "oeuvres" (
	"id"	INTEGER PRIMARY KEY,
	"titre"	TEXT NOT NULL,
	"data_bnf"	INTEGER,
	"partie_de"	FOREIGN KEY REFERENCES "oeuvres"("id"),
	"auteur" FOREIGN KEY REFERENCES "personne"("id"),
	"attr"	INTEGER DEFAULT NULL FOREIGN KEY REFERENCES "personne"("id")
);
CREATE TABLE IF NOT EXISTS "contient" (
	"oeuvre"	FOREIGN KEY REFERENCES "unites_codico"("id"),
	"unites_codico"	FOREIGN KEY REFERENCES "oeuvres"("id"),
);
CREATE TABLE IF NOT EXISTS "personne" (
	"id"	INTEGER PRIMARY KEY,
	"nom"	TEXT,
	"data_bnf"	INTEGER
);
INSERT INTO "codices" ("id","cote","id_technique","reliure_descript","histoire") VALUES (1,'Latin 2989','ark:/12148/cc60815j','Reliure du XVIIIe siècle sur ais de carton en maroquin rouge aux armes royales ; dos décoré par des poinçons, au chiffre royal ; titre au dos en lettres dorées : « Cassianus de monachis ». Contregardes et gardes en parchemin.','Produit dans le Sud-Ouest de la France, le ms. a fait partie de la bibliothèque de l’abbaye de Saint-Pierre de Moissac : il est recensé dans le catalogue de 1678 parmi les livres que Colbert fit venir de Moissac à Paris, mais il est absent du catalogue de Moissac rédigé peu avant cette date (cf. Dufour, « La composition », p. 210). Le volume est donc entré dans la collection de Jean-Baptiste Colbert (1619-1683) (cf. cote ancienne au f. 3r, « Codex Colber. 6156 ») et il entra dans la Bibliothèque du roi en 1732, avec d’autres manuscrits colbertins.'),
 (2,'Latin 2077','ark:/12148/cc599714','Reliure maroquin rouge aux armes de Colbert.','Provient de l''abbaye de Moissac, cf. Delisle, Cab. des mss ., I, 519.');
INSERT INTO "unites_codico" ("id","descript","loc_init","loc_init_v","loc_fin","loc_fin_v","date_pas_avant","date_pas_apres","code_id") VALUES (1,'Parchemin. 154 ff., précédés et suivis d’une garde en parchemin. 180 x 123 mm (justif. 130 x 80 mm). Écriture minuscule caroline d’une main principale.',NULL,NULL,NULL,NULL,975,1000,1),
 (2,NULL,1,1,120,1,981,1020,2),
 (3,'Ecriture régulière de la première moitié du XIe siècle (Dufour, BSM)',121,0,173,0,1001,1050,2),
 (4,NULL,174,0,175,0,1100,1120,2),
 (5,NULL,122,0,123,0,1131,1170,2);
INSERT INTO "oeuvres" ("id","titre","data_bnf","partie_de","auteur","attr") VALUES (1,'Institutions cénobitiques',13771861,NULL,1,NULL),
 (2,'De officiis ministrorum',NULL,NULL,2,NULL),
 (3,'De conflictu vitiorum et virtutum',16746816,NULL,3,NULL),
 (4,'Conlatio cum Maximino Arrianorum episcopo',12076565,NULL,4,NULL),
 (5,'Contra Maximinum haereticum Arianorum episcopum',12076556,NULL,4,NULL),
 (6,'Quatre-vingt trois questions différentes',13620219,NULL,4,NULL),
 (7,'De fide et symbolo',15127117,NULL,4,NULL),
 (8,'De Genesi contra Manichaeos',12489317,NULL,4,NULL),
 (9,'Sermones',11983905,NULL,4,NULL),
 (10,'Adversus haereses',12009584,NULL,4,NULL),
 (11,'Collatio cum Pascentio ariano',16182204,NULL,4,NULL),
 (12,'De fide contra Manichaeos',NULL,NULL,5,4),
 (13,'Sermones',13541232,NULL,6,NULL),
 (14,'Ad Trasimundum',NULL,NULL,7,NULL),
 (15,'Decreta',NULL,NULL,8,NULL),
 (16,'Moralia in Job',12043707,NULL,8,NULL),
 (17,'De vitiis et virtutibus',NULL,NULL,9,NULL),
 (18,'De corpore et sanguine Domini',17908174,NULL,10,NULL);
INSERT INTO "contient" ("oeuvre","unites_codico") VALUES (1,1),
 (2,3),
 (3,3),
 (4,2),
 (5,2),
 (6,2),
 (7,2),
 (8,2),
 (9,3),
 (6,3),
 (10,2),
 (11,2),
 (12,2),
 (13,3),
 (14,2),
 (15,4),
 (16,2),
 (17,3),
 (18,3);
INSERT INTO "personne" ("id","nom","data_bnf") VALUES (1,'Jean Cassien (saint, 0360?-0432?)',12044269),
 (2,'Ambroise (saint, 0340?-0397)',11888642),
 (3,'Ambroise Autpert (730?-784)',16708997),
 (4,'Augustin (saint, 0354-0430)',11889551),
 (5,'Evodius Uzaliensis (03..-042.)',12313631),
 (6,'Césaire d''Arles (saint, 0470?-0542)',11894765),
 (7,'Fulgence de Ruspe (saint, 0467-0532)',12127708),
 (8,'Grégoire I (pape, 0540?-0604)',11886472),
 (9,'Halitgaire (07..-0831?)',16844039),
 (10,'Paschase Radbert (saint, 0790?-0865?)',11929840);
COMMIT;
