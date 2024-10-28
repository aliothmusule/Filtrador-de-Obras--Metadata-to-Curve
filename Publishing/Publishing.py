import pandas as pd

# Leer 'DIRECTORIO PUBLISHING.xlsx' y obtener los valores de la segunda columna 'Publishing'
publishing_df = pd.read_excel('DIRECTORIO PUBLISHING.xlsx')

# Asumiendo que la columna 'Publishing' es la segunda columna
publishing_values = publishing_df.iloc[:, 1].dropna().astype(str).str.strip().tolist()

# Leer 'METADATA CENTRAL.xlsx' con el encabezado en la fila 2 (índice 1 en pandas)
metadata_df = pd.read_excel('METADATA CENTRAL.xlsx', header=1)

# Asegurarse de que los valores en la columna 'Publisher' sean cadenas y eliminar espacios
metadata_df['Publisher'] = metadata_df['Publisher'].astype(str).str.strip()

# Filtrar las filas donde 'Publisher' está en la lista de 'publishing_values'
filtered_df = metadata_df[metadata_df['Publisher'].isin(publishing_values)]

# Exportar el resultado a 'METADATA_PUBLISHING.xlsx'
filtered_df.to_excel('METADATA_PUBLISHING.xlsx', index=False)

print("El archivo 'METADATA_PUBLISHING.xlsx' ha sido creado exitosamente.")
