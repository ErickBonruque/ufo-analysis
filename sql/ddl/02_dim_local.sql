CREATE TABLE IF NOT EXISTS dim_local (
    sk_local        INTEGER       PRIMARY KEY,
    cidade          VARCHAR(100),
    estado          VARCHAR(50),
    pais            VARCHAR(50),
    latitude        DOUBLE,
    longitude       DOUBLE,
    regiao          VARCHAR(30),
    UNIQUE (cidade, estado, pais)
);
