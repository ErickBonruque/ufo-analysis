# Pipeline de Dados — Avistamentos de UFO

## Fontes de Dados

| Fonte | Formato | Descrição |
|---|---|---|
| **NUFORC via Kaggle** | CSV | 80.332 relatos de avistamentos de UFO (1906–2014) |
| **OurAirports** | CSV | Cadastro global de aeroportos com coordenadas geográficas |
| **Space Devs API** (`ll.thespacedevs.com`) | JSON (API REST) | Histórico de lançamentos espaciais (1957–2020) |
| **Wikimedia Pageviews API** | JSON (API REST) | Visualizações mensais de artigos de UFO/OVNI na Wikipedia (2015–2024) |
| **Modelo climático estimado** | Gerado em código | Normais climáticas calculadas por latitude e mês |

---

## Staging — Limpeza Inicial

A partir do CSV bruto do Kaggle (`ufo_sightings_scrubbed.csv`):

- Renomeação de colunas para snake_case em português
- Conversão de `datetime` e `date posted` para tipo `datetime`, descartando linhas com data inválida
- Conversão de `duration (seconds)` para numérico; erros silenciados como `NaN`
- Coordenadas (`latitude`, `longitude`) convertidas para float; erros silenciados
- Cálculo de **lag de reporte**: diferença em dias entre a data do avistamento e a data de postagem no site
- Data arredondada para **hora cheia** para viabilizar o join com `dim_tempo`
- Padronização de strings: `strip()` + `lower()` em cidade, estado, país e shape
- Valores ausentes: `shape` preenchido com `"unknown"`, `pais` preenchido com `"us"`
- Coluna `fonte` adicionada com valor fixo `"NUFORC"`

**Resultado:** 74.535 registros no staging (descarte de ~7% por data inválida ou dados incompletos)

---

## Dimensões

### `dim_tempo`
- Gerada programaticamente cobrindo **1900 a 2026** com granularidade horária
- Atributos derivados: ano, mês, dia, hora, dia da semana (em português), trimestre

### `dim_local`
- Localizações únicas extraídas do staging pela combinação `cidade + estado + país`
- Latitude e longitude representam a **média** das coordenadas dos avistamentos naquele local
- Região geográfica atribuída via dicionário de mapeamento por código de país (ex: `us` → "América do Norte")
- Países sem mapeamento recebem `"Outros"`

### `dim_formato`
- Shapes únicos extraídos do staging
- Cada shape recebeu um **nome normalizado** em português (ex: `fireball` → `"bola de fogo"`)
- Agrupados em categorias: Luminoso, Circular, Angular, Alongado, Complexo, Indefinido

### `dim_fonte`
- Tabela simples com as fontes dos dados; nesta versão contém apenas `"NUFORC"`

### `dim_aeroporto`
- Para cada localização única, calculado o aeroporto mais próximo usando **distância haversine** via vetorização NumPy
- Processamento em lotes de 500 locais para controle de memória
- Filtrado apenas aeroportos de porte relevante: `small_airport`, `medium_airport`, `large_airport`
- Atributos: nome do aeroporto, distância em km, tipo

### `dim_clima`
- Dados climáticos **estimados via modelo matemático**, sem chamadas a API externa
- Cálculo para os **200 locais com mais avistamentos** × 12 meses
- Temperatura média estimada pelo modelo de Willmott & Matsuura (função de latitude e mês)
- Cobertura de nuvens e visibilidade estimadas por funções trigonométricas sazonais
- Código de clima derivado da cobertura de nuvens (0=limpo a 3=nublado)
- Tabela de lookup (`lat_r × lon_r × mês`) usada para o join com a fato

### `dim_evento_espacial`
- Origem: dataset **Space Missions (Kaggle)** com missões de 1957 a 2020
- Parsing da data no formato `"Fri Aug 07, 2020"` com `pd.to_datetime`
- Campo `missao` extraído da coluna `Detail` após o separador `" | "`
- Deduplicação por `(missao, data_lancamento)`

### `dim_interesse_cultural`
- Coleta via **Wikimedia Pageviews API** para termos em inglês (UFO, UAP) e português (OVNI)
- Período coletado: jan/2010 a dez/2024 (efetivo com dados: jul/2015 a dez/2024)
- `ano_mes` armazenado como string `YYYYMM` (ex: `"202307"`)

---

## Tabela Fato — `fato_avistamento`

Montada via DuckDB com joins entre o staging e todas as dimensões:

| Chave | Tipo de Join | Observação |
|---|---|---|
| `sk_tempo` | `INNER JOIN` | Exige data válida no staging |
| `sk_local` | `INNER JOIN` | Exige combinação cidade/estado/país existente |
| `sk_formato` | `INNER JOIN` | Shape sempre presente após limpeza |
| `sk_fonte` | `INNER JOIN` | Fonte fixa "NUFORC" |
| `sk_aeroporto` | `LEFT JOIN` | Pode ser NULL se localização sem coordenadas |
| `sk_clima` | `LEFT JOIN` | Presente para os 200 locais mais frequentes (72,9% das linhas) |
| `sk_evento_espacial` | `LEFT JOIN LATERAL` | Evento espacial mais próximo em até ±30 dias |
| `sk_interesse_cultural` | `LEFT JOIN` | Sem sobreposição de datas — sempre NULL neste dataset |

### Cobertura final

| Coluna | Linhas preenchidas | % |
|---|---|---|
| `sk_evento_espacial` | 74.125 | 99,4% |
| `sk_clima` | 54.391 | 72,9% |
| `sk_interesse_cultural` | 0 | 0% — avistamentos até 2014, dados de pageviews a partir de 2015 |

### Medidas da fato
- `duracao_segundos` — duração do avistamento reportada pelo relator
- `lag_reporte_dias` — dias entre o avistamento e a postagem no NUFORC
- `latitude` / `longitude` — coordenadas do avistamento
- `quantidade_relato` — sempre 1 (granularidade de relato individual)

---

## Modelo Dimensional

```
dim_tempo ────────┐
dim_local ────────┤
dim_formato ──────┤
dim_fonte ────────┼──── fato_avistamento
dim_clima ────────┤
dim_aeroporto ────┤
dim_evento_espacial ──┤
dim_interesse_cultural ┘
```

Esquema estrela com 8 dimensões e 1 tabela fato central.
