BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "codices" (
	"id"	INTEGER,
	"cote"	TEXT NOT NULL,
	"id_technique"	TEXT,
	"reliure_descript"	TEXT,
	"histoire"	TEXT,
	"lieu_conservation"	INTEGER,
	FOREIGN KEY("lieu_conservation") REFERENCES "lieux"("id"),
	PRIMARY KEY("id")
);
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
CREATE TABLE IF NOT EXISTS "oeuvres" (
	"id"	INTEGER,
	"titre"	TEXT NOT NULL,
	"data_bnf"	INTEGER,
	"partie_de"	,
	"auteur"	,
	"attr"	INTEGER DEFAULT NULL,
	FOREIGN KEY("attr") REFERENCES "personne"("id"),
	FOREIGN KEY("partie_de") REFERENCES "oeuvres"("id"),
	FOREIGN KEY("auteur") REFERENCES "personne"("id"),
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "contient" (
	"oeuvre"	,
	"unites_codico"	,
	FOREIGN KEY("oeuvre") REFERENCES "oeuvres"("id"),
	FOREIGN KEY("unites_codico") REFERENCES "unites_codico"("id")
);
CREATE TABLE IF NOT EXISTS "personne" (
	"id"	INTEGER,
	"nom"	TEXT,
	"data_bnf"	INTEGER,
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "lieux" (
	"id"	INTEGER,
	"localite"	TEXT NOT NULL,
	"label"	TEXT,
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "provenances" (
	"codex"	INTEGER NOT NULL,
	"lieu"	INTEGER NOT NULL,
	"cas_particulier"	INTEGER NOT NULL,
	FOREIGN KEY("lieu") REFERENCES "lieux"("id"),
	FOREIGN KEY("codex") REFERENCES "codices"("id"),
	FOREIGN KEY("cas_particulier") REFERENCES "unites_codico"("id")
);
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
CREATE TABLE IF NOT EXISTS "user" (
	"user_id"	INTEGER NOT NULL,
	"user_nom"	TINYTEXT NOT NULL,
	"user_login"	VARCHAR(45) NOT NULL,
	"user_email"	TINYTEXT NOT NULL,
	"user_password"	VARCHAR(100) NOT NULL,
	PRIMARY KEY("user_id")
);
COMMIT;
