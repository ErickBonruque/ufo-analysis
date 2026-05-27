CREATE TABLE IF NOT EXISTS fato_avistamento (
    sk_avistamento          BIGINT        PRIMARY KEY,
    -- chaves estrangeiras
    sk_tempo                INTEGER       NOT NULL,
    sk_local                INTEGER       NOT NULL,
    sk_formato              INTEGER       NOT NULL,
    sk_fonte                INTEGER       NOT NULL,
    sk_clima                INTEGER,
    sk_aeroporto            INTEGER,
    sk_evento_espacial      INTEGER,
    sk_interesse_cultural   INTEGER,
    -- medidas
    duracao_segundos        DOUBLE,
    duracao_suspeita        BOOLEAN       NOT NULL DEFAULT FALSE,
    lag_reporte_dias        INTEGER,
    latitude                DOUBLE,
    longitude               DOUBLE,
    quantidade_relato       INTEGER       NOT NULL DEFAULT 1
    -- Nota: DuckDB não suporta FOREIGN KEY REFERENCES na DDL.
    -- A integridade referencial é garantida pela lógica do pipeline ETL.
);
