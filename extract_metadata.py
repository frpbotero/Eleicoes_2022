# -*- coding: utf-8 -*-
"""Processa CSVs do data‑lake raw, gera descrições via Ollama e salva metadados.

• Leitura robusta de arquivos CSV com fallback de codificação.
• Descrição automática via modelo local (Ollama) com tratamento de falhas.
• Metadados individuais e resumo consolidado em JSON.
"""

from __future__ import annotations

import json
import logging
import os
import sys
from pathlib import Path
from typing import Iterable, List

import pandas as pd
import requests

# ---------------------------------------------------------------------------
# Configurações gerais -------------------------------------------------------
# ---------------------------------------------------------------------------
CSV_FOLDER: str = "data_lake/raw/csv"
DATA_LAKE_BASE_PATH: str = "data_lake"  # diretório base (criado se não existir)
OLLAMA_URL: str = "http://localhost:11434//api/chat"
OLLAMA_MODEL = "deepseek-r1:1.5b" 

# Token / tempo máximo para a requisição ao Ollama (segundos)
OLLAMA_TIMEOUT: int = 60

# Cria diretórios necessários
os.makedirs(Path(DATA_LAKE_BASE_PATH, "raw", "csv"), exist_ok=True)
os.makedirs(Path(DATA_LAKE_BASE_PATH, "metadata"), exist_ok=True)

# Configuração de logging ----------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s | %(asctime)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Funções utilitárias --------------------------------------------------------
# ---------------------------------------------------------------------------

def create_description(csv_text_for_llm: str, model: str = OLLAMA_MODEL) -> str:
    """
    Gera uma descrição concisa para um CSV usando um LLM do Ollama (modo chat).
    """
    system_message = (
        "You are a highly concise data summarizer. "
        "Strictly adhere to the output format. "
        "Do NOT include any preamble, conversational text, or internal thoughts. "
        "Do NOT reveal your chain-of-thought or analysis steps whatsoever. "
        "Give a plain-English description of the CSV the user provides. "
        "Answer in exactly two short lines, precisely in this format:\n"
        "1) Columns: [List of columns here]\n"
        "2) Rows represent: [What the rows represent here]"
    )

    user_message = f"Please summarize the following CSV data:\n\n{csv_text_for_llm}"

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ],
        "stream": False,
    }

    try:
        resp = requests.post(
            OLLAMA_URL,
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload),
            timeout=OLLAMA_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()

        if data.get("error"):
            raise RuntimeError(data["error"])

        # Para o endpoint /api/chat, a resposta está em data['message']['content']
        generated_content = data.get("message", {}).get("content", "").strip()

        # Pós-processamento para garantir o formato de 2 linhas
        lines = [line.strip() for line in generated_content.split('\n') if line.strip()]
        
        output_lines = []
        for line in lines:
            if line.startswith("1) Columns:") or line.startswith("2) Rows represent:"):
                output_lines.append(line)
        
        if len(output_lines) == 2:
            return "\n".join(output_lines)
        else:
            logger.warning("LLM output format unexpected. Raw response: %s", generated_content)
            # Como fallback, remove a tag <think> e tenta retornar as primeiras 2 linhas significativas
            cleaned_content = generated_content.replace("<think>", "").replace("</think>", "").strip()
            fallback_lines = [line.strip() for line in cleaned_content.split('\n') if line.strip()]
            
            # Retorna as duas primeiras linhas não-vazias que se parecem com o formato
            if len(fallback_lines) >= 2:
                 # Heurística para pegar as que parecem as colunas e rows represent
                final_output = []
                for f_line in fallback_lines:
                    if "Columns:" in f_line or "Rows represent:" in f_line:
                        final_output.append(f_line)
                    if len(final_output) == 2:
                        break
                return "\n".join(final_output) if len(final_output) == 2 else cleaned_content
            return cleaned_content # Retorna tudo limpo se não conseguir formatar

    except (requests.RequestException, json.JSONDecodeError, RuntimeError) as exc:
        logger.warning("LLM description failed (%s): %s", type(exc).__name__, exc)
        return "Automatic description unavailable."


def read_csv_as_string(path: str, encodings: Iterable[str] = ("utf-8", "latin1")) -> str:
    """Retorna o conteúdo do CSV como *string* tentando múltiplas codificações."""
    for enc in encodings:
        try:
            with open(path, "r", encoding=enc) as fh:
                return fh.read()
        except UnicodeDecodeError:
            logger.debug("UnicodeDecodeError for %s with %s", path, enc)
            continue
        except FileNotFoundError:
            logger.error("File not found: %s", path)
            break
    return ""  # vazio se nenhuma codificação funcionar


# ---------------------------------------------------------------------------
# Pipeline principal ---------------------------------------------------------
# ---------------------------------------------------------------------------

def process_csv_folder(csv_folder: str) -> None:
    """Percorre todos os CSVs e gera metadados."""
    all_files_metadata: dict[str, dict] = {}

    for entry in Path(csv_folder).iterdir():
        if not entry.is_file() or entry.suffix.lower() != ".csv":
            continue

        filename = entry.name
        logger.info("Processando %s", filename)

        try:
            # DataFrame com fallback de codificação
            try:
                df = pd.read_csv(entry, encoding="utf-8")
            except UnicodeDecodeError:
                df = pd.read_csv(entry, encoding="latin1")

        except Exception as exc:
            logger.error("Falha ao ler %s: %s", filename, exc, exc_info=True)
            continue  # pula para o próximo arquivo

        # Amostra do CSV em string (100 primeiras linhas é suficiente p/ descrição)
        csv_sample = df.head(100).to_csv(index=False)
        description_text = create_description(csv_sample)

        metadata = {
            "file_name": filename,
            "description": description_text,
            "file_path_original": str(entry),
            "file_size_bytes": entry.stat().st_size,
            "file_type": "csv",
            "columns": df.columns.tolist(),
            "delimiter": ",",  # ajustar se necessário
            "date_collected": pd.Timestamp.today().strftime("%Y-%m-%d"),
            "responsible": "Botero",
            "row_count": int(len(df)),
            "first_5_rows_preview": df.head().to_dict(orient="records"),
        }

        # Salva metadados individuais
        metadata_path = Path(DATA_LAKE_BASE_PATH, "metadata", f"metadata_{entry.stem.lower()}.json")
        try:
            metadata_path.write_text(json.dumps(metadata, indent=4), encoding="utf-8")
            logger.info("Metadados salvos em: %s", metadata_path)
        except Exception as exc:
            logger.error("Falha ao salvar metadados de %s: %s", filename, exc, exc_info=True)

        all_files_metadata[filename] = metadata

    # Resumo consolidado ------------------------------------------------------
    summary_path = Path(DATA_LAKE_BASE_PATH, "metadata", "all_files_summary_metadata.json")
    try:
        summary_path.write_text(json.dumps(all_files_metadata, indent=4), encoding="utf-8")
        logger.info("\nSumário consolidado salvo em: %s", summary_path)
    except Exception as exc:
        logger.error("Falha ao salvar sumário consolidado: %s", exc, exc_info=True)


# ---------------------------------------------------------------------------
# Execução -------------------------------------------------------------------
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    if not Path(CSV_FOLDER).exists():
        logger.error("Diretório CSV inexistente: %s", CSV_FOLDER)
        sys.exit(1)

    process_csv_folder(CSV_FOLDER)
