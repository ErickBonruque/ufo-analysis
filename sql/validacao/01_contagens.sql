-- Contagens por tabela
SELECT 'dim_tempo'              AS tabela, COUNT(*) AS qtd FROM dim_tempo
UNION ALL SELECT 'dim_local',              COUNT(*) FROM dim_local
UNION ALL SELECT 'dim_formato',            COUNT(*) FROM dim_formato
UNION ALL SELECT 'dim_fonte',              COUNT(*) FROM dim_fonte
UNION ALL SELECT 'dim_clima',              COUNT(*) FROM dim_clima
UNION ALL SELECT 'dim_aeroporto',          COUNT(*) FROM dim_aeroporto
UNION ALL SELECT 'dim_evento_espacial',    COUNT(*) FROM dim_evento_espacial
UNION ALL SELECT 'dim_interesse_cultural', COUNT(*) FROM dim_interesse_cultural
UNION ALL SELECT 'fato_avistamento',       COUNT(*) FROM fato_avistamento;
