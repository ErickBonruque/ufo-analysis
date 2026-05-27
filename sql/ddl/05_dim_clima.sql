CREATE TABLE IF NOT EXISTS dim_clima (
    sk_clima          INTEGER       PRIMARY KEY,
    cobertura_nuvens  DOUBLE,
    visibilidade      DOUBLE,
    vento             DOUBLE,
    temperatura       DOUBLE,
    codigo_clima      VARCHAR(20)
);
