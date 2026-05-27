# UFO Sightings — Data Warehouse Dimensional

> Projeto Final da disciplina **CC6IBDDA — Introdução a Big Data e Data Analytics**
> Construção de um Data Warehouse em esquema estrela para análise de avistamentos de UFOs e dos fatores externos que ajudam a explicar picos de relatos.

---

## 🎯 Objetivo

Identificar padrões **temporais, geográficos e contextuais** associados ao aumento de relatos de UFOs, e avaliar a influência de fatores externos conhecidos — clima, proximidade de aeroportos, lançamentos espaciais e interesse cultural — sobre esses avistamentos.

**Pergunta orientadora:** *Quando e onde os relatos de UFO aparecem com maior intensidade, e quais fatores externos ajudam a explicar esses picos?*

## 🧱 Arquitetura — Esquema Estrela

A modelagem segue um esquema estrela clássico, com uma única tabela fato no centro e dimensões descritivas conectadas a ela.

```
                    dim_tempo
                       │
   dim_local ── fato_avistamento ── dim_clima
       │           │     │              │
  dim_formato     ...   ...        dim_aeroporto
       │                                │
   dim_fonte                  dim_evento_espacial
                                        │
                            dim_interesse_cultural
```

### Tabela Fato

| Tabela | Granularidade | Medidas principais |
|---|---|---|
| `fato_avistamento` | um relato por linha | `duracao_segundos`, `lag_reporte_dias`, `latitude`, `longitude`, `quantidade_relato` |

### Dimensões

| Dimensão | Conteúdo |
|---|---|
| `dim_tempo` | ano, mês, dia, hora, dia_semana, trimestre |
| `dim_local` | cidade, estado, país, latitude, longitude, região |
| `dim_formato` | shape_original, shape_normalizado, grupo_formato |
| `dim_fonte` | nome_fonte (NUFORC, GEIPAN, Hugging Face etc.) |
| `dim_clima` | cobertura_nuvens, visibilidade, vento, temperatura, código_clima |
| `dim_aeroporto` | aeroporto_mais_proximo, distancia_km, tipo_aeroporto |
| `dim_evento_espacial` | missão, agência, data_lancamento, distancia_janela |
| `dim_interesse_cultural` | pageviews_mensais, termo, idioma, plataforma |

> O diagrama completo, com chaves primárias, estrangeiras e cardinalidades, está em [`docs/modelo_estrela.png`](docs/modelo_estrela.png).
> O dicionário de dados detalhado está em [`docs/dicionario_dados.md`](docs/dicionario_dados.md).

## 🗂️ Fontes de Dados

| Fonte | Tipo | Uso no DW |
|---|---|---|
| [Kaggle — UFO Sightings](https://www.kaggle.com/datasets/sahityasetu/ufo-sightings) | CSV (NUFORC) | base principal da fato |
| [NUFORC](https://nuforc.org/) | Referência | origem dos dados principais |
| [Open-Meteo Historical Weather](https://open-meteo.com/en/docs/historical-weather-api) | API | popula `dim_clima` |
| [OurAirports](https://ourairports.com/data/) | CSV | popula `dim_aeroporto` |
| [Launch Library 2](https://ll.thespacedevs.com/2.2.0/) | API | popula `dim_evento_espacial` |
| [Wikimedia Pageviews](https://doc.wikimedia.org/generated-data-platform/aqs/analytics-api/reference/page-views.html) | API | popula `dim_interesse_cultural` |
| [GEIPAN/CNES](https://www.cnes-geipan.fr/en/recherche/cas) | CSV | casos oficiais franceses |
| [Hugging Face — Ufo_data_clustered](https://huggingface.co/datasets/cjc0013/Ufo_data_clustered) | JSONL | fonte complementar |

## 🧰 Stack Tecnológica

- **Python 3.11+** — orquestração e ETL
- **DuckDB** — engine analítica local (SQL, colunar, sem servidor)
- **pandas** — manipulação tabular
- **kagglehub** — download do dataset Kaggle
- **requests** — chamadas às APIs externas
- **Jupyter** — notebooks exploratórios

## 📁 Estrutura do Repositório

```
ufo-dw/
├── README.md                       ← este arquivo
├── GUIA_IMPLEMENTACAO.md           ← passo a passo detalhado para a IA seguir
├── requirements.txt
├── .env.example                    ← variáveis (Kaggle, API keys quando necessário)
│
├── data/
│   ├── raw/                        ← arquivos originais baixados
│   ├── processed/                  ← dados limpos e padronizados
│   └── warehouse/                  ← tabelas fato/dim em parquet
│
├── sql/
│   ├── ddl/                        ← CREATE TABLE de cada dimensão e da fato
│   │   ├── 01_dim_tempo.sql
│   │   ├── 02_dim_local.sql
│   │   ├── 03_dim_formato.sql
│   │   ├── 04_dim_fonte.sql
│   │   ├── 05_dim_clima.sql
│   │   ├── 06_dim_aeroporto.sql
│   │   ├── 07_dim_evento_espacial.sql
│   │   ├── 08_dim_interesse_cultural.sql
│   │   └── 09_fato_avistamento.sql
│   └── validacao/                  ← queries de checagem de integridade
│
├── scripts/
│   ├── 01_download/                ← scripts para baixar cada fonte
│   ├── 02_transform/               ← limpeza e padronização
│   ├── 03_load/                    ← carga no DuckDB
│   └── 04_validate/                ← integridade referencial e contagens
│
├── notebooks/
│   └── exploracao_inicial.ipynb
│
└── docs/
    ├── modelo_estrela.png          ← diagrama final do modelo físico
    ├── dicionario_dados.md
    └── decisoes_modelagem.md
```

## 🚀 Como Executar

```bash
# 1. Clonar e entrar no projeto
git clone <repo-url> ufo-dw && cd ufo-dw

# 2. Criar ambiente virtual
python -m venv .venv
source .venv/bin/activate          # Linux/Mac
# .venv\Scripts\activate           # Windows

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Configurar credenciais (Kaggle)
cp .env.example .env
# editar .env com seu KAGGLE_USERNAME e KAGGLE_KEY

# 5. Rodar o pipeline completo
python scripts/run_all.py
```

Para um passo a passo detalhado de cada etapa (download → transformação → modelo físico → carga → validação), consultar [`GUIA_IMPLEMENTACAO.md`](GUIA_IMPLEMENTACAO.md).

## 📊 Entregas do Projeto

| Etapa | Descrição | Status |
|---|---|---|
| 1 | Dataset e descritivo do problema | ✅ |
| 2 | Modelagem física do DW (esquema estrela) | 🔨 em andamento |
| 3 | Carga e enriquecimento dos dados | ⏳ |
| 4 | Análises e dashboards | ⏳ |

## 📝 Licença e Uso

Projeto acadêmico. Bases públicas mantêm suas licenças originais — consultar cada fonte para detalhes de uso.