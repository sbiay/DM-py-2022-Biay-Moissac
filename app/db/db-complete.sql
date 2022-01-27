BEGIN TRANSACTION;
DROP TABLE IF EXISTS "unites_codico";
CREATE TABLE IF NOT EXISTS "unites_codico" (
	"id"	INTEGER,
	"descript"	TEXT,
	"loc_init"	INTEGER DEFAULT NULL,
	"loc_init_v"	BOOLEAN DEFAULT NULL,
	"loc_fin"	INTEGER DEFAULT NULL,
	"loc_fin_v"	BOOLEAN DEFAULT NULL,
	"date_pas_avant"	INTEGER NOT NULL,
	"date_pas_apres"	INTEGER NOT NULL,
	"code_id"	INTEGER,
	FOREIGN KEY("code_id") REFERENCES "codices"("id"),
	PRIMARY KEY("id")
);
DROP TABLE IF EXISTS "oeuvres";
CREATE TABLE IF NOT EXISTS "oeuvres" (
	"id"	INTEGER,
	"titre"	TEXT NOT NULL,
	"data_bnf"	INTEGER,
	"partie_de"	,
	"auteur"	,
	"attr"	INTEGER DEFAULT NULL,
	FOREIGN KEY("partie_de") REFERENCES "oeuvres"("id"),
	FOREIGN KEY("attr") REFERENCES "personnes"("id"),
	FOREIGN KEY("auteur") REFERENCES "personnes"("id"),
	PRIMARY KEY("id")
);
DROP TABLE IF EXISTS "contient";
CREATE TABLE IF NOT EXISTS "contient" (
	"oeuvre"	,
	"unites_codico"	,
	FOREIGN KEY("unites_codico") REFERENCES "unites_codico"("id"),
	FOREIGN KEY("oeuvre") REFERENCES "oeuvres"("id")
);
DROP TABLE IF EXISTS "lieux";
CREATE TABLE IF NOT EXISTS "lieux" (
	"id"	INTEGER,
	"localite"	TEXT NOT NULL,
	"label"	TEXT,
	PRIMARY KEY("id")
);
DROP TABLE IF EXISTS "production";
CREATE TABLE IF NOT EXISTS "production" (
	"codex"	INTEGER NOT NULL,
	"lieu"	INTEGER NOT NULL,
	"cas_particulier"	INTEGER,
	"incertain"	BOOLEAN DEFAULT FALSE,
	"approx"	BOOLEAN DEFAULT FALSE,
	FOREIGN KEY("cas_particulier") REFERENCES "unites_codico"("id"),
	FOREIGN KEY("lieu") REFERENCES "lieux"("id"),
	FOREIGN KEY("codex") REFERENCES "codices"("id")
);
DROP TABLE IF EXISTS "user";
CREATE TABLE IF NOT EXISTS "user" (
	"user_id"	INTEGER NOT NULL,
	"user_nom"	TINYTEXT NOT NULL,
	"user_login"	VARCHAR(45) NOT NULL,
	"user_email"	TINYTEXT NOT NULL,
	"user_password"	VARCHAR(100) NOT NULL,
	PRIMARY KEY("user_id")
);
DROP TABLE IF EXISTS "personnes";
CREATE TABLE IF NOT EXISTS "personnes" (
	"id"	INTEGER,
	"nom"	TEXT,
	"data_bnf"	INTEGER,
	PRIMARY KEY("id")
);
DROP TABLE IF EXISTS "codices";
CREATE TABLE IF NOT EXISTS "codices" (
	"id"	INTEGER,
	"cote"	TEXT NOT NULL,
	"id_technique"	TEXT,
	"descript_materielle"	TEXT,
	"histoire"	TEXT,
	"conservation_id"	INTEGER,
	FOREIGN KEY("conservation_id") REFERENCES "lieux"("id"),
	PRIMARY KEY("id")
);
DROP TABLE IF EXISTS "provenances";
CREATE TABLE IF NOT EXISTS "provenances" (
	"codex"	INTEGER NOT NULL,
	"lieu"	INTEGER NOT NULL,
	"origine"	BOOLEAN NOT NULL DEFAULT 0,
	"remarque"	TEXT,
	"cas_particulier" INTEGER DEFAULT NULL,
	FOREIGN KEY("cas_particulier") REFERENCES "unites_codico"("id"),
	FOREIGN KEY("codex") REFERENCES "codices"("id"),
	FOREIGN KEY("lieu") REFERENCES "lieux"("id")
);
INSERT INTO "unites_codico" ("id","descript","loc_init","loc_init_v","loc_fin","loc_fin_v","date_pas_avant","date_pas_apres","code_id") VALUES (1,'Écriture minuscule caroline d’une main principale.',NULL,NULL,NULL,NULL,975,1000,1),
 (2,NULL,1,1,120,1,981,1020,2),
 (3,'Ecriture régulière de la première moitié du XIe siècle (Dufour, BSM)',121,0,173,0,1001,1050,2),
 (4,NULL,174,0,175,0,1100,1120,2),
 (5,'Les ff. 122 et 123 ont été intercalés.',122,0,123,0,1131,1170,2),
 (6,NULL,NULL,NULL,NULL,NULL,1101,1150,3),
 (7,NULL,NULL,NULL,NULL,NULL,1048,1072,4),
 (8,'Ecrit par une main unique.',NULL,NULL,NULL,NULL,1101,1125,5),
 (9,'Minuscule caroline d’une seule main.',2,1,184,1,1101,1120,6),
 (10,'Deux additions contemporaines au début et à la fin du manuscrit.',1,0,1,0,1201,1220,6),
 (11,NULL,182,0,184,1,1201,1220,6);
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
 (18,'De corpore et sanguine Domini',17908174,NULL,10,NULL),
 (19,'Revelatio quae ostensa est venerabili viro Hispaniensi Eldefonso episcopo',NULL,NULL,NULL,NULL),
 (20,'Epistola ad Elipandum',NULL,NULL,11,NULL),
 (21,'Adversus Elipandum',NULL,NULL,11,NULL),
 (22,'Diadema monachorum',NULL,NULL,12,NULL),
 (23,'De Assumptione beatae Mariae',17814451,NULL,NULL,4),
 (24,'Séquence sans paroles (notation à points superposés).',NULL,NULL,NULL,NULL),
 (25,'Extrait d’un lapidaire (?)',NULL,NULL,NULL,NULL),
 (26,'Opera selecta',NULL,NULL,13,NULL),
 (27,'Apologeticum',12261658,NULL,14,NULL),
 (28,'De viribus herbarum',15605651,NULL,'16',15);
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
 (18,3),
 (19,5),
 (20,6),
 (21,6),
 (22,6),
 (23,6),
 (18,7),
 (22,8),
 (24,10),
 (25,11),
 (26,9),
 (27,9),
 (28,9);
INSERT INTO "lieux" ("id","localite","label") VALUES (1,'Moissac','abbaye Saint-Pierre'),
 (2,'Paris','Bibliothèque nationale de France'),
 (3,'Layrac','prieuré Saint-Martin'),
 (4,'Agen',NULL),
 (5,'Leiden','Universiteitsbibliotheek'),
 (6,'London','British Library'),
 (7,'Paris','collection Colbert'),
 (8,'Paris','collection Foucault'),
 (9,'London','collection Harley');
INSERT INTO "production" ("codex","lieu","cas_particulier","incertain","approx") VALUES (1,1,NULL,NULL,NULL),
 (2,1,NULL,NULL,NULL),
 (3,3,NULL,1,NULL),
 (3,4,NULL,1,1),
 (4,1,NULL,NULL,NULL),
 (5,1,NULL,NULL,NULL),
 (6,1,NULL,NULL,NULL);
INSERT INTO "user" ("user_id","user_nom","user_login","user_email","user_password") VALUES (2,'Monsieur','mau','mau@mau.com','pbkdf2:sha256:260000$6VVfTtBVWLxvkOk8$cc5269b287968e91c0f746c34be966ad5cc2cea015b8d5b25c1782fd72b765a5'),
 (3,'Barbapapa','bb','barbapapa@gmail.com','pbkdf2:sha256:260000$VdMwwlRdeCOYolak$09a03abb477e2feb8b5986d7fdffed0970c95f4ce425208cb4190512e4941759'),
 (4,'Piccioncina','piccioncina','piccioncina@gmail.com','pbkdf2:sha256:260000$jEfSctJidxhWD7tp$37a94549ceea5d2277b57110bb4c88b0bb42e1e0026e14725a9d0d2f4f43a315');
INSERT INTO "personnes" ("id","nom","data_bnf") VALUES (1,'Jean Cassien (saint, 0360?-0432?)',12044269),
 (2,'Ambroise (saint, 0340?-0397)',11888642),
 (3,'Ambroise Autpert (730?-784)',16708997),
 (4,'Augustin (saint, 0354-0430)',11889551),
 (5,'Evodius Uzaliensis (03..-042.)',12313631),
 (6,'Césaire d''Arles (saint, 0470?-0542)',11894765),
 (7,'Fulgence de Ruspe (saint, 0467-0532)',12127708),
 (8,'Grégoire I (pape, 0540?-0604)',11886472),
 (9,'Halitgaire (07..-0831?)',16844039),
 (10,'Paschase Radbert (saint, 0790?-0865?)',11929840),
 (11,'Alcuin (0732?-0804)',12030679),
 (12,'Smaragde de Saint Mihiel (0750?-0825?)',11989580),
 (13,'Cyprien (saint, 02..-0258)',11886041),
 (14,'Tertullien (0155?-0222?)',11926244),
 (15,'Odon de Meung (10..-10..)',16685825),
 (16,'Macer Floridus (auteur prétendu)',12515583);
INSERT INTO "codices" ("id","cote","id_technique","descript_materielle","histoire","conservation_id") VALUES (1,'Latin 2989','ark:/12148/cc60815j','Reliure du XVIIIe siècle sur ais de carton en maroquin rouge aux armes royales ; dos décoré par des poinçons, au chiffre royal ; titre au dos en lettres dorées : « Cassianus de monachis ». Contregardes et gardes en parchemin. Parchemin. 154 ff., précédés et suivis d’une garde en parchemin. 180 x 123 mm (justif. 130 x 80 mm). ','Produit dans le Sud-Ouest de la France, le ms. a fait partie de la bibliothèque de l’abbaye de Saint-Pierre de Moissac : il est recensé dans le catalogue de 1678 parmi les livres que Colbert fit venir de Moissac à Paris, mais il est absent du catalogue de Moissac rédigé peu avant cette date (cf. Dufour, « La composition », p. 210). Le volume est donc entré dans la collection de Jean-Baptiste Colbert (1619-1683) (cf. cote ancienne au f. 3r, « Codex Colber. 6156 ») et il entra dans la Bibliothèque du roi en 1732, avec d’autres manuscrits colbertins.',2),
 (2,'Latin 2077','ark:/12148/cc599714','Reliure maroquin rouge aux armes de Colbert.','Provient de l''abbaye de Moissac, cf. Delisle, Cab. des mss ., I, 519.',2),
 (3,'Latin 2388','ark:/12148/cc60220h','Reliure de maroquin rouge, aux armes et au chiffre de Jean-Baptiste Colbert, XVIIe siècle. Estampille de la Bibliothèque royale avant 1735 (modèle Josserand-Bruno, n° 4). Parchemin (certains feuillets sont coupés), 77 ff., 310 x 215 mm (just. 230 x 160 mm). 10 cahiers : 1 cahier de 7 ff. (1-7 ; f. 7 monté), 3 cahiers de 8 ff. (8-31), 1 cahier de 9 ff. (32-40 ; le 10e f. est coupé), 4 cahiers de 8 ff. (41-72), 1 cahier de 5 ff. (73-77 ; montages multiples, présence de talons), précédés et suivis d''une garde de papier et de deux gardes de parchemin. Réclames. Signatures. Piqures.','Ce manuscrit n''a vraisemblablement pas été réalisé à Moissac. La présence d''une charte en langue vulgaire (f. 7), datée de 1248, concernant Layrac, dépendance de Moissac, incite à penser que le manuscrit fut écrit et décoré dans les environs d''Agen, peut-être à Layrac même. La copie de cette charte indique dans tous les cas que le manuscrit se trouvait à Layrac au milieu du XIIIe siècle.',2),
 (4,'BPL 1822',NULL,NULL,'Ce manuscrit peut être daté de l''abbatiat de Durand (1048-1072) : son écriture est archaïque mais l''emploi du signe tironien pour ''et'' est fréquent. A la fin du XIe siècle, un copiste combla une lacune du texte (f. 111). Il appartint à Foucault, fut vendu à La Haye en 1721, entra à la bibliothèque universitaire de Leyde en 1905 lors de la vente de la collection de Vroom à Deventer (JD, BSM).',5),
 (5,'Harley 3078',NULL,'Après 1600. Couvrure de cuir aux armes de Nicolas Joseph Foucault.','Une main moderne a inscrit la mention ''Ex Abbatia Moissiacensi''. Après avoir été la propriété de Foucault, il est vendu par le libraire Thomas Ballard à Edward Harley le 20 février 1720/21. La collection Harley, formée par Robert Harley (1661-1724), 1er comte d’Oxford et Mortimer, homme politique, et Edward Harley (1689-1741), 2e comte d’Oxford et Mortimer, collectionneur de livres et mécène, a enregistré l''entrée du codex par la main de leur bibliothécaire, Humfrey Wanley, le 23 février 1720/21 [sic]. Edward Harley légua la bibliothèque à sa veuve, Henrietta Cavendish, née Holles (1694-1755), puis elle fut transmise à leur fille, Margaret Cavendish Bentinck (1715-1785), duchesse de Portland. Les manuscrits ont été vendus par elle en 1753 à la nation britannique pour £10000 en vertu de la loi du Parlement qui a également établi le British Museum ; les manuscrits de Harley forment l’une des collections fondatrices de la British Library.',6),
 (6,'Latin 1656A','ark:/12148/cc59616k','Reliure du XVIIe s. sur ais de carton couverts de maroquin rouge, plats décorés à encadrement doré de triple filet et médaillon central en or aux armes de Colbert ; dos à six nerfs, au chiffre de Colbert et titre en lettres dorées « OPERA / SANCTI / CYPRIANI ». Contre-gardes et gardes en papier, gardes en parchemin. Aux f. 2r et 184v, estampille de la « Bibliotheca regia » identique au modèle Josserand-Bruno n° 5 (Ancien Régime) en usage avant 1735.',NULL,2);
INSERT INTO "provenances" ("codex","lieu","origine","remarque") VALUES (1,1,1,NULL),
 (1,7,0,NULL),
 (3,7,0,NULL),
 (2,1,1,NULL),
 (3,3,1,'?'),
 (3,4,1,'région de'),
 (4,1,1,NULL),
 (4,8,0,NULL),
 (5,1,1,NULL),
 (5,8,0,NULL),
 (6,1,1,NULL),
 (6,9,0,NULL);
COMMIT;
