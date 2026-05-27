CREATE TABLE IF NOT EXISTS dim_fonte (
    sk_fonte    INTEGER       PRIMARY KEY,
    nome_fonte  VARCHAR(50)   NOT NULL UNIQUE
);
