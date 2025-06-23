# Ficha de Desafio do Projeto Final  
*Disciplina: Aquisição, Pré-processamento e Exploração de Dados*  
*Curso: Pós-graduação em Ciência de Dados*  
Integrantes: **A. Cristiane R. Lima, Claudio Sampaio, Felipe Botero, José Henrique**  
Junho de 2025

---

## 1. Cenário

> **Indicadores Socioeconômicos e Votação Brasil 2022** – investigar como desenvolvimento humano, renda e educação se relacionam com a distribuição ideológica de votos no 1.º turno das eleições de 2022.

---

## 2. Problema Central

> Existe relação entre indicadores socioeconômicos dos estados brasileiros e padrões de votação ideológica em 2022?

### Perguntas Analíticas
- Estados com maior **IDHM** votaram mais em qual espectro: direita, esquerda ou centro?  
- Há correlação entre **analfabetismo** e votos em blocos ideológicos específicos?  
- **PIB per capita** influencia a ideologia predominante?  

---

## 3. Justificativas

- Fontes **públicas, nacionais e gratuitas** ⇒ transparência e replicabilidade.  
- Integração socioeconômica + votação gera **CSV pronto** para análises estatísticas e ML.  

---

## 4. Coleta de Dados

| Fonte | Conteúdo |
|-------|----------|
| **IBGE** | PIB, IDHM, Gini, analfabetismo, expectativa de vida, mortalidade infantil |
| **TSE** | Votos nominais válidos 1.º turno/2022 por partido |
| **Limite** | Foco em 2022, sem granularidade municipal |

---

## 5. Pré-processamento

1. **Indicadores socioeconômicos** – padronização de colunas, preenchimento de lacunas (Gini, analfabetismo).  
2. **Votos** – filtro 1.º turno, mapeamento partido → bloco ideológico.  
3. **Agregação** – soma de votos por UF + bloco, cálculo de percentuais.  
4. **Merge** – junção socioeconômico × votos via UF ⇢ `uf_votos_ideologia_socioeco_2022.csv`.  

---

## 6. Web Scraping de Indicadores-chave

### Taxa de Analfabetismo
- `requests` + `BeautifulSoup` para tabela IPEA.  
- Conversão em **DataFrame** → `analfabetismo_uf_2022.csv`.  

### Coeficiente de Gini
- Processo análogo, anos 2012-2024.  
- Normalização de números (vírgula → ponto).  
- Resultado: `indice_de_gini.csv`.  

---

## 7. Análises Exploratórias

### Composição Percentual de Votos
- Médias nacionais: **Esquerda 48 %**, **Direita 44 %**, Centros ≈ 8 %.  
- Gráfico de barras empilhadas por UF revela polarização e variações regionais.  

### Correlações de Pearson
| Variável | ρ Direita | ρ Esquerda |
|----------|-----------|------------|
| Analfabetismo % | **-0.76** | **+0.78** |
| PIB per capita | +0.54 | -0.56 |
| IDHM 2021 | +0.43 | -0.44 |
| ... | ... | ... |

*Insight:* maior analfabetismo correlaciona-se a voto de esquerda; maior renda/IDHM, a voto de direita.

---

## 8. Estrutura Ideológica (Agrupamento de Partidos)

| Bloco | Partidos |
|-------|----------|
| Esquerda | PT, PCB, UP, PSTU |
| Centro-Esquerda | PDT, PSB, REDE, PV |
| Centro | MDB, PSD, PODE, CIDADANIA, AVANTE |
| Centro-Direita | UNIÃO, PSDB, PP, NOVO, SOLIDARIEDADE |
| Direita | PL, PTB, DC, PATRIOTA, PRTB |

---

## 9. Repositório & Execução

```bash
git clone https://github.com/frpbotero/Eleicoes_2022
pip install -r requirements.txt
# Gerar dataset integrado
jupyter nbconvert --to notebook --execute notebooks/process_uf_socio_votos.ipynb
# Correlações
jupyter notebook notebooks/correlacao_pearson_dynamic_cols.ipynb
```

*Opcional:* iniciar **Ollama** e rodar `scripts/extract_metadata.py` para gerar metadados JSON.  

---

## 10. Conclusões

- **Polarização**: esquerda e direita dominam; centro tem papel secundário.  
- **Socioeconomia importa**: renda, educação e IDH apresentam correlações robustas com preferência ideológica.  
- **Dataset aberto** possibilita extensões com ML e painéis interativos para políticas públicas e estudos eleitorais.  
