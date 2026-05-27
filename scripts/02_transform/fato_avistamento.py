"""Monta fato_avistamento fazendo joins entre staging e dimensões via DuckDB."""
import os
from pathlib import Path
import duckdb
from dotenv import load_dotenv

load_dotenv()
con = duckdb.connect(os.getenv("DW_PATH", "data/warehouse/ufo_dw.duckdb"))

con.execute("CREATE OR REPLACE VIEW staging     AS SELECT * FROM read_parquet('data/processed/ufo_staging.parquet')")
con.execute("CREATE OR REPLACE VIEW v_aeroporto AS SELECT * FROM read_parquet('data/processed/dim_aeroporto.parquet')")

# Join com clima_lookup se disponível
tem_clima = Path("data/processed/clima_lookup.parquet").exists()
if tem_clima:
    con.execute("CREATE OR REPLACE VIEW v_clima_lkp AS SELECT * FROM read_parquet('data/processed/clima_lookup.parquet')")
    join_clima = """
LEFT JOIN v_clima_lkp cl ON cl.lat_r = ROUND(src.latitude, 0)
                         AND cl.lon_r = ROUND(src.longitude, 0)
                         AND cl.mes   = MONTH(src.data_completa)
LEFT JOIN dim_clima   c  ON c.sk_clima = cl.sk_clima"""
    col_clima = "cl.sk_clima"
else:
    join_clima = ""
    col_clima  = "NULL::INTEGER"
    print("  [info] clima_lookup.parquet não encontrado — sk_clima será NULL")

print("Montando fato_avistamento...")
con.execute("DELETE FROM fato_avistamento")

con.execute(f"""
INSERT INTO fato_avistamento
SELECT
    row_number() OVER ()                        AS sk_avistamento,
    t.sk_tempo,
    l.sk_local,
    f.sk_formato,
    s.sk_fonte,
    {col_clima}                                 AS sk_clima,
    a.sk_aeroporto,
    ev.sk_evento_espacial,
    ic.sk_interesse_cultural,
    src.duracao_segundos,
    src.duracao_suspeita,
    src.lag_reporte_dias,
    src.latitude,
    src.longitude,
    1                                           AS quantidade_relato
FROM staging src
JOIN  dim_tempo               t  ON t.data_completa = src.data_completa
JOIN  dim_local               l  ON l.cidade  = src.cidade
                                AND l.estado  = src.estado
                                AND l.pais    = src.pais
JOIN  dim_formato             f  ON f.shape_original = src.shape
JOIN  dim_fonte               s  ON s.nome_fonte = src.fonte
LEFT JOIN v_aeroporto         av ON av.cidade = src.cidade
                                AND av.estado = src.estado
                                AND av.pais   = src.pais
LEFT JOIN dim_aeroporto       a  ON a.sk_aeroporto = av.sk_aeroporto
LEFT JOIN dim_interesse_cultural ic ON ic.plataforma = 'wikipedia'
                                   AND ic.idioma     = 'en'
                                   AND ic.termo      = 'UFO'
                                   AND CAST(YEAR(src.data_completa) AS VARCHAR)
                                       || LPAD(CAST(MONTH(src.data_completa) AS VARCHAR),2,'0')
                                       = ic.ano_mes
LEFT JOIN LATERAL (
    SELECT sk_evento_espacial
    FROM dim_evento_espacial
    WHERE data_lancamento BETWEEN (src.data_completa::DATE - INTERVAL '30' DAY)
                              AND (src.data_completa::DATE + INTERVAL '30' DAY)
    ORDER BY ABS(DATEDIFF('day', data_lancamento, src.data_completa::DATE))
    LIMIT 1
) ev ON true
{join_clima}
""")

qtd          = con.execute("SELECT COUNT(*)                FROM fato_avistamento").fetchone()[0]
tem_clima    = con.execute("SELECT COUNT(sk_clima)         FROM fato_avistamento").fetchone()[0]
tem_espacial = con.execute("SELECT COUNT(sk_evento_espacial)   FROM fato_avistamento").fetchone()[0]
tem_cultural = con.execute("SELECT COUNT(sk_interesse_cultural) FROM fato_avistamento").fetchone()[0]
print(f"fato_avistamento: {qtd:,} linhas")
print(f"  com sk_clima:             {tem_clima:,}")
print(f"  com sk_evento_espacial:   {tem_espacial:,}")
print(f"  com sk_interesse_cultural:{tem_cultural:,}")
con.close()
