import pandas as pd
import os
import shutil
from pathlib import Path


# Caminho completo do arquivo original
file_path = "/home/botero/Documents/POS/ETL/31.05/Olympic_Games.csv"

# Diretório onde o arquivo será salvo
data_lake_path = 'data_lake'

# Garante que o diretório existe
os.makedirs(data_lake_path, exist_ok=True)

# Nome do arquivo original
filename = os.path.basename(file_path)
file = Path(file_path)


# Caminho final de destino
destiny_path = os.path.join(f'{data_lake_path}/raw/csv', filename)


# Leitura do CSV original
df = pd.read_csv(file_path, encoding='latin1')  

# Salvando no novo local
df.to_csv(destiny_path, index=False)

print(f"Arquivo salvo em: {destiny_path}")

metadata_phisical = {
    "file_name": filename,
    "description":"Database original with results of the Olympic Games",
    "file_path": destiny_path,
    "level": "gold",
    "file_type": "csv",
    "version": "1.0",
}
# Salvando os metadados em um arquivo JSON
metadata_path_data_lake = os.path.join(f'{data_lake_path}/metadata', 'metadata_data_lake.json')
os.makedirs(os.path.dirname(metadata_path_data_lake), exist_ok=True)
with open(metadata_path_data_lake, 'w') as f:
    import json
    json.dump(metadata_phisical, f, indent=4)
print(f"Metadados salvos em: {metadata_path_data_lake}")



# Exibindo os metadados
print("Metadados do arquivo:")
for key, value in metadata_phisical.items():
    print(f"{key}: {value}")

# Exibindo as primeiras linhas do DataFrame
print("\nPrimeiras linhas do DataFrame:")   



metadata_file =  {
    "file_name": filename,
    "description":"Database original with results of the Olympic Games",
    "file_path": destiny_path,
    "file_size": os.path.getsize(destiny_path),
    "file_type": "csv",
    "columns": df.columns.tolist(),
    "delimitator": ",",
    "date_colected": pd.to_datetime('today').strftime('%Y-%m-%d'),
    "responsible": "Botero",
    "row_count": len(df),

}

metadata_path_file = os.path.join(f'{data_lake_path}/metadata', f'metadata_{file.stem.lower()}.json')
os.makedirs(os.path.dirname(metadata_path_file), exist_ok=True)
with open(metadata_path_file, 'w') as f:
    import json
    json.dump(metadata_file, f, indent=4)
print(f"Metadados salvos em: {metadata_path_file}")



# Exibindo os metadados
print("Metadados do arquivo:")
for key, value in metadata_file.items():
    print(f"{key}: {value}")

# Exibindo as primeiras linhas do DataFrame
print("\nPrimeiras linhas do DataFrame:")   