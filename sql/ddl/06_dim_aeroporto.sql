CREATE TABLE IF NOT EXISTS dim_aeroporto (
    sk_aeroporto            INTEGER       PRIMARY KEY,
    aeroporto_mais_proximo  VARCHAR(100)  NOT NULL,
    distancia_km            DOUBLE        NOT NULL,
    tipo_aeroporto          VARCHAR(30)
);
