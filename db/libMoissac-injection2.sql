/* Pour Latin 2077 : incomplet */
INSERT INTO codices(id, cote, id_technique, reliure_descript, histoire)
VALUES (2, 'Latin 2077', 'ark:/12148/cc599714', 'Reliure maroquin rouge aux armes de Colbert.', "Provient de l'abbaye de Moissac, cf. Delisle, Cab. des mss ., I, 519.");

INSERT INTO unites_codico(id, descript, loc, date_pas_avant, date_pas_apres, date_circa) 
VALUES (2, "Parchemin.179 ff.350 × 230 mm.", NULL, 1001, 1100, NULL);

INSERT INTO personne(id, nom, data_bnf)
VALUES
(2, 'Ambroise (saint, 0340?-0397)', 11888642),
(3, 'Ambroise Autpert (730?-784)', 16708997),
(4, 'Augustin (saint, 0354-0430)', 11889551);

INSERT INTO oeuvres(id, titre, data_bnf, partie_de, auteur)
VALUES
(2, 'De officiis ministrorum', NULL, NULL, 2),
(3, 'De conflictu vitiorum et virtutum', 16746816, NULL, 3),
(4, 'Conlatio cum Maximino Arrianorum episcopo', 12076565, NULL, 4),
(5, 'Contra Maximinum haereticum Arianorum episcopum', 12076556, 4),
(6, 'Quatre-vingt trois questions différentes', 13620219, 4);