CREATE TABLE IF NOT EXISTS dim_formato (
    sk_formato        INTEGER       PRIMARY KEY,
    shape_original    VARCHAR(50)   NOT NULL,
    shape_normalizado VARCHAR(50)   NOT NULL,
    grupo_formato     VARCHAR(30)   NOT NULL,
    UNIQUE (shape_original)
);
