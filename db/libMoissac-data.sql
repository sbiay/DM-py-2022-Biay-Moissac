BEGIN TRANSACTION;
INSERT INTO "codices" ("id","cote","id_technique","reliure_descript","histoire") VALUES (1,'Latin 2989','ark:/12148/cc60815j','Reliure du XVIIIe siècle sur ais de carton en maroquin rouge aux armes royales ; dos décoré par des poinçons, au chiffre royal ; titre au dos en lettres dorées : « Cassianus de monachis ». Contregardes et gardes en parchemin.','Produit dans le Sud-Ouest de la France, le ms. a fait partie de la bibliothèque de l’abbaye de Saint-Pierre de Moissac : il est recensé dans le catalogue de 1678 parmi les livres que Colbert fit venir de Moissac à Paris, mais il est absent du catalogue de Moissac rédigé peu avant cette date (cf. Dufour, « La composition », p. 210). Le volume est donc entré dans la collection de Jean-Baptiste Colbert (1619-1683) (cf. cote ancienne au f. 3r, « Codex Colber. 6156 ») et il entra dans la Bibliothèque du roi en 1732, avec d’autres manuscrits colbertins.'),
 (2,'Latin 2077','ark:/12148/cc599714','Reliure maroquin rouge aux armes de Colbert.','Provient de l''abbaye de Moissac, cf. Delisle, Cab. des mss ., I, 519.');
INSERT INTO "unites_codico" ("id","descript","loc","date_pas_avant","date_pas_apres","date_circa") VALUES (1,'Parchemin. 154 ff., précédés et suivis d’une garde en parchemin. 180 x 123 mm (justif. 130 x 80 mm). Écriture minuscule caroline d’une main principale.',NULL,975,1000,0),
 (2,'Parchemin.179 ff.350 × 230 mm.',NULL,1001,1100,0);
INSERT INTO "oeuvres" ("id","titre","data_bnf","partie_de","auteur") VALUES (1,'Institutions cénobitiques',13771861,NULL,1),
 (2,'De officiis ministrorum',NULL,NULL,2),
 (3,'De conflictu vitiorum et virtutum',16746816,NULL,3),
 (4,'Conlatio cum Maximino Arrianorum episcopo',12076565,NULL,4),
 (5,'Contra Maximinum haereticum Arianorum episcopum',12076556,NULL,4),
 (6,'Quatre-vingt trois questions différentes',13620219,NULL,4);
INSERT INTO "personne" ("id","nom","data_bnf") VALUES (1,'Jean Cassien (saint, 0360?-0432?)',12044269),
 (2,'Ambroise (saint, 0340?-0397)',11888642),
 (3,'Ambroise Autpert (730?-784)',16708997),
 (4,'Augustin (saint, 0354-0430)',11889551);
INSERT INTO "contient" ("oeuvre","unites_codico") VALUES (1,1),
 (2,2),
 (3,2),
 (4,2),
 (5,2),
 (6,2);
COMMIT;
