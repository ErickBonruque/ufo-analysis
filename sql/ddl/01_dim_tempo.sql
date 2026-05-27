CREATE TABLE IF NOT EXISTS dim_tempo (
    sk_tempo        INTEGER       PRIMARY KEY,
    data_completa   TIMESTAMP     NOT NULL,
    ano             INTEGER       NOT NULL,
    mes             INTEGER       NOT NULL,
    dia             INTEGER       NOT NULL,
    hora            INTEGER,
    dia_semana      VARCHAR(15)   NOT NULL,
    trimestre       INTEGER       NOT NULL,
    UNIQUE (data_completa)
);
