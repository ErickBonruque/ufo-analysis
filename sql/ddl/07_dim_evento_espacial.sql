CREATE TABLE IF NOT EXISTS dim_evento_espacial (
    sk_evento_espacial  INTEGER       PRIMARY KEY,
    missao              VARCHAR(150),
    agencia             VARCHAR(50),
    data_lancamento     DATE,
    distancia_janela    DOUBLE
);
