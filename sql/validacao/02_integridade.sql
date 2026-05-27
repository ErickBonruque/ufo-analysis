-- Verifica órfãos: nenhuma sk_ da fato pode estar fora da dimensão correspondente
SELECT 'tempo'    AS dim, COUNT(*) AS orfaos FROM fato_avistamento f
  LEFT JOIN dim_tempo   d ON d.sk_tempo   = f.sk_tempo
  WHERE d.sk_tempo IS NULL
UNION ALL
SELECT 'local',   COUNT(*) FROM fato_avistamento f
  LEFT JOIN dim_local   d ON d.sk_local   = f.sk_local
  WHERE d.sk_local IS NULL
UNION ALL
SELECT 'formato', COUNT(*) FROM fato_avistamento f
  LEFT JOIN dim_formato d ON d.sk_formato = f.sk_formato
  WHERE d.sk_formato IS NULL
UNION ALL
SELECT 'fonte',   COUNT(*) FROM fato_avistamento f
  LEFT JOIN dim_fonte   d ON d.sk_fonte   = f.sk_fonte
  WHERE d.sk_fonte IS NULL;
-- (Não verificar as 4 opcionais — podem ter NULL legítimo.)
