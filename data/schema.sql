PRAGMA foreign_keys = ON;
PRAGMA encoding = 'UTF-8';


DROP TABLE IF EXISTS identidades;


CREATE TABLE IF NOT EXISTS identidades (
    nome        TEXT      NOT NULL,
    idade       INTEGER   NOT NULL,
    pronomes    TEXT      NOT NULL,
    profissao   TEXT      NOT NULL,

    PRIMARY KEY (nome)
) STRICT;
