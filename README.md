# Otimização de Roteiros (Santa Catarina)

Aplicação Streamlit para redistribuir a carteira de clientes por região entre vendedores (Pauta D, Pauta M e Conveniência/PC), usando proximidade geográfica às âncoras dos vendedores e equilíbrio de quantidade de clientes por vendedor.

## Objetivo

- Filtrar por região (ex.: VALE)
- Escolher **2 pautas** (D + M, para testar remoção do PC) ou **3 pautas** (D + M + PC)
- Atribuir cada cliente ao vendedor mais próximo (nearest-neighbor)
- Rebalancear em torno da **média de clientes por vendedor**
- Marcar como **vermelho / A definir** quem fica além do limiar de km
- Exibir mapa Folium + tabela (código, razão, vendedor sugerido) com download CSV

## Arquitetura

```
CSV → pandas (validação) → nearest-neighbor + balanceamento → Folium + tabela → Streamlit Cloud
```

```
Home.py
pages/
  1_Carregar_Bases.py
  2_Otimizacao_Roteiros.py
src/
  data/     schema, loader, session
  models/   optimizer (haversine, assign, balance)
  viz/      mapa Folium
assets/amostras/
requirements.txt
.streamlit/config.toml
```

## Schema dos CSVs

### clientes.csv

| Coluna | Descrição |
|--------|-----------|
| codigo_cliente | Identificador único |
| razao | Razão social / nome |
| regiao | Região do filtro (ex.: VALE) |
| pauta_atual | D, M ou PC |
| codigo_vendedor_atual | Código do vendedor atual |
| lat | Latitude |
| lon | Longitude |

### vendedores.csv

| Coluna | Descrição |
|--------|-----------|
| codigo_vendedor | Identificador único |
| nome | Nome do vendedor |
| regiao | Região de atuação |
| pauta | D, M ou PC |
| lat | Latitude da base/endereço |
| lon | Longitude da base/endereço |

Pautas válidas: `D`, `M`, `PC`. Região é normalizada em maiúsculas.

## Como rodar local

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run Home.py
```

Na página **Carregar Bases**, use os CSVs reais ou marque a opção de amostra em `assets/amostras`.

## Controles da otimização

| Controle | Efeito |
|----------|--------|
| Região | Recorte dinâmico a partir do CSV |
| Nº de pautas 2 \| 3 | 2 = só D+M; 3 = inclui PC |
| Limiar km | Distância máxima; acima → status `a_definir` e vendedor `A definir` |
| Tolerância da média (%) | Folga no balanceamento de quantidade |

Cores no mapa: azul D, verde M, amarelo PC, vermelho A definir. Marcadores pretos com ícone = vendedores (âncoras).

## Deploy Streamlit Cloud

1. Repositório no GitHub com este código
2. Acesse [share.streamlit.io](https://share.streamlit.io) e faça login com GitHub
3. **New app** → selecione o repositório
4. Branch: `main`
5. Main file path: `Home.py`
6. Deploy

Não há secrets obrigatórios (Folium + OpenStreetMap).

Checklist pós-deploy: Home abre → Carregar Bases com amostra → Otimização → mapa e tabela.

## Extensão futura

- Calibrar limiar km e tolerância com bases reais por região
- Modo automático sugerindo 2 vs 3 pautas (folgado vs apertado)
- Ordem de visita dentro de cada pauta (TSP), se necessário

## Amostra incluída

`assets/amostras` contém regiões **VALE**, **NORTE** e **SUL** com coordenadas aproximadas em Santa Catarina, apenas para validar o fluxo.
