# Indicadores Socioeconômicos & Votação 2022 (Brasil)

_Repositório que consolida **indicadores socioeconômicos** de cada Unidade da Federação (UF) em 2022 e cruza esses dados com o **resultado de votos nominais válidos** do 1.º turno das eleições de 2022, agrupando os partidos em blocos ideológicos._

## Conteúdo

| Caminho / arquivo | Descrição |
| ----------------- | --------- |
| `data_lake/raw/csv/indicadores_uf_2022.csv` | PIB, PIB per capita, IDH, Gini, expectativa de vida, mortalidade infantil, analfabetismo e IPCA por UF (2022). |
| `data_lake/raw/csv/votacao_partido_munzona_2022_BR.csv` | Votos nominais válidos por partido, zona e município (TSE). |
| `scripts/extract_metadata.py` | **Processa todos os CSVs do _data-lake/raw_ e gera metadados em JSON usando um modelo local via Ollama.** |
| `notebooks/process_uf_socio_votos.ipynb` | Gera o dataset integrado `uf_votos_ideologia_socioeco_2022.csv`. |
| `notebooks/correlacao_pearson_dynamic_cols.ipynb` | Calcula correlações de Pearson entre variáveis socioeconômicas e blocos ideológicos. |
| `notebooks/ideologia_media_votos_notebook.ipynb` | Explora a média de votos por bloco ideológico e cria gráficos. |
| `data_lake/processed/uf_votos_ideologia_socioeco_2022.csv` | Dataset final (27 × N colunas) pronto para análise. |

## Estrutura de Blocos Ideológicos

| Bloco | Partidos incluídos (2022) |
| ----- | ------------------------- |
| **esquerda** | PT, PCB, UP, PSTU |
| **centro-esquerda** | PDT, PSB, REDE, PV |
| **centro** | MDB, PSD, PODE, CIDADANIA, AVANTE |
| **centro-direita** | UNIÃO, PSDB, PP, NOVO, SOLIDARIEDADE |
| **direita** | PL, PTB, DC, PATRIOTA, PRTB |

## Pré-requisitos

* Python ≥ 3.9  
* Pacotes: **pandas**, **matplotlib**, **jupyter** (ou VS Code)  
* **Ollama server** instalado: <https://ollama.ai>  
* Modelo local `deepseek-r1:1.5b` baixado:  
  ```bash
  ollama pull deepseek-r1:1.5b
  ```

```bash
pip install -r requirements.txt
```

> O arquivo `requirements.txt` deve conter, no mínimo:  
> `pandas>=2.0`   `matplotlib>=3.8`   `notebook`

## Executando passo a passo

1. **Geração do dataset integrado**  
   ```bash
   jupyter nbconvert --to notebook --execute notebooks/process_uf_socio_votos.ipynb
   ```

2. **Exploração de correlações**  
   Abra e execute `notebooks/correlacao_pearson_dynamic_cols.ipynb`.

3. **Visualização de médias ideológicas**  
   Abra e execute `notebooks/ideologia_media_votos_notebook.ipynb`.

4. **(Opcional) Geração de metadados dos CSVs**  
   ```bash
   # Inicie o Ollama (caso não esteja ativo)
   ollama serve &

   # Execute o script
   python scripts/extract_metadata.py
   ```
   *Saída:* arquivos JSON em `data_lake/metadata/` – um por CSV e o sumário `all_files_summary_metadata.json`.

## Dados brutos

* IBGE – Contas Regionais 2022  
* IBGE – PNAD Contínua (Gini, Analfabetismo)  
* IBGE – Projeções Demográficas (Esperança de vida, Mortalidade infantil)  
* TSE – Resultados Eleitorais 2022 (votos nominais válidos)  

Todas as fontes são públicas e gratuitas.


## Apresentação

* https://youtu.be/ndF_9L-OpOs?feature=shared

## Licença

[MIT](LICENSE)
