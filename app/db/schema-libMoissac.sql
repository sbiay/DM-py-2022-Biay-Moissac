BEGIN TRANSACTION;
CREATE TABLE "codices" (
	"id"	INTEGER,
	"cote"	TEXT NOT NULL,
	"id_technique"	TEXT,
	"reliure_descript"	TEXT,
	"histoire"	TEXT,
	PRIMARY KEY("id")
);
CREATE TABLE "unites_codico" (
	"id"	INTEGER,
	"descript"	TEXT,
	"loc_init"	INTEGER DEFAULT NULL,
	"loc_init_v"	BOOLEAN DEFAULT NULL,
	"loc_fin"	INTEGER DEFAULT NULL,
	"loc_fin_v"	BOOLEAN DEFAULT NULL,
	"date_pas_avant"	INTEGER NOT NULL,
	"date_pas_apres"	INTEGER NOT NULL,
	"code_id"	INTEGER FOREIGN KEY("code_id") REFERENCES "codices"("id"),
	PRIMARY KEY("id")
);
CREATE TABLE "oeuvres" (
	"id"	INTEGER,
	"titre"	TEXT NOT NULL,
	"data_bnf"	INTEGER,
	"partie_de"	FOREIGN KEY("partie_de") REFERENCES "oeuvres"("id"),
	"auteur"	FOREIGN KEY("auteur") REFERENCES "personne"("id"),
	"attr"	INTEGER DEFAULT NULL FOREIGN KEY("attr") REFERENCES "personne"("id"),
	PRIMARY KEY("id")
);
CREATE TABLE "contient" (
	"oeuvre"	FOREIGN KEY("unites_codico") REFERENCES "unites_codico"("id"),
	"unites_codico"	FOREIGN KEY("oeuvre") REFERENCES "oeuvres"("id")
	
	
);
CREATE TABLE "personne" (
	"id"	INTEGER,
	"nom"	TEXT,
	"data_bnf"	INTEGER,
	PRIMARY KEY("id")
);
COMMIT;
