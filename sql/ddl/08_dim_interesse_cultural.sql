CREATE TABLE IF NOT EXISTS dim_interesse_cultural (
    sk_interesse_cultural  INTEGER       PRIMARY KEY,
    ano_mes                VARCHAR(6)    NOT NULL,
    pageviews_mensais      INTEGER       NOT NULL,
    termo                  VARCHAR(50)   NOT NULL,
    idioma                 VARCHAR(10)   NOT NULL,
    plataforma             VARCHAR(30)   NOT NULL
);
