-- ============================================================
-- PREPARAÇÃO PARA RECARGA DOS DADOS CORRIGIDOS
-- Correr no pgAdmin ANTES de executar o script Python de carga
-- ============================================================

-- 1. Adicionar coluna duracao_suspeita (nova — marcador de outlier)
ALTER TABLE fato_avistamento
    ADD COLUMN IF NOT EXISTS duracao_suspeita BOOLEAN NOT NULL DEFAULT FALSE;

-- 2. Limpar fato primeiro (respeita FK constraints)
TRUNCATE TABLE fato_avistamento;

-- 3. Limpar dimensões na ordem correcta (FK: fato depende de dims)
TRUNCATE TABLE dim_interesse_cultural;
TRUNCATE TABLE dim_evento_espacial;
TRUNCATE TABLE dim_aeroporto;
TRUNCATE TABLE dim_clima;
TRUNCATE TABLE dim_fonte;
TRUNCATE TABLE dim_formato;
TRUNCATE TABLE dim_local;
TRUNCATE TABLE dim_tempo;

-- 4. Confirmar que está tudo vazio
SELECT 'fato_avistamento'       AS tabela, COUNT(*) AS linhas FROM fato_avistamento UNION ALL
SELECT 'dim_tempo',                         COUNT(*) FROM dim_tempo             UNION ALL
SELECT 'dim_local',                         COUNT(*) FROM dim_local             UNION ALL
SELECT 'dim_formato',                       COUNT(*) FROM dim_formato           UNION ALL
SELECT 'dim_fonte',                         COUNT(*) FROM dim_fonte             UNION ALL
SELECT 'dim_clima',                         COUNT(*) FROM dim_clima             UNION ALL
SELECT 'dim_aeroporto',                     COUNT(*) FROM dim_aeroporto         UNION ALL
SELECT 'dim_evento_espacial',               COUNT(*) FROM dim_evento_espacial   UNION ALL
SELECT 'dim_interesse_cultural',            COUNT(*) FROM dim_interesse_cultural
ORDER BY tabela;
