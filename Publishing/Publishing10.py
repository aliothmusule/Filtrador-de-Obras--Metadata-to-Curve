import pandas as pd

# Definir las editoras a filtrar
editoras = [
    "BACKSTAGE EDITORA TX",
    "MUSIC BY BACKSTAGE PUBLISHING",
    "MUSIC BY CANZION LEGACY",
    "CANZION LEGACY",
    "CANZION PUBLISHING TX",
    "GRUPO CANZION EDITORA",
    "MUSIC BY HEAVEN LEGAZY",
    "HEAVEN LEGACY",
    "HEAVEN NETWORKS",
    "MUSIC BY HEAVEN PUBLISHING",
    "PUBLISHING BY COMPOSITORES",
    "COMPOSITORES PUBLISHING",
    "ALIENTO PUBLISHING",
    "CEV ADMINISTRATION",
    "CEV PUBLISHER LLC",
    "LK COLLECTIVE",
    "FRILOP MUSIC",
    "JUAN SALINAS MUSIC PUBLISHING",
    "LOS VENCEDORES PUBLISHING",
    "MUSIC BY GREEN MUSIC PUBLISHING",
    "MUSIC BY MAJESTIC RECORDS PUBLISHING",
    "MUSIC FROM AZ MUSIC",
    "REDIMI2 MUSIC PUBLISHING",
    "REYVOL MUSIK LLC",
    "COALO ZAMORANO PUBLISHING",
    "MIKE RODRIGUEZ MUSIC",
    "ADORA MUSIC INTERNATIONAL",
    "MAR DE CRISTAL PUBLISHING",
    "MONTESANTO PUBLISHING",
    "GRACE ESPANOL MUSICA"
]

# Estructura del árbol para organizar los registros
class TreeNode:
    def __init__(self):
        self.children = {}
        self.records = []

class TitleTree:
    def __init__(self):
        self.root = TreeNode()

    def insert(self, key, record):
        node = self.root
        for part in key:
            if part not in node.children:
                node.children[part] = TreeNode()
            node = node.children[part]
        node.records.append(record)

    def get_groups(self):
        groups = []
        def traverse(node):
            if node.records:
                groups.append(node.records)
            for child in node.children.values():
                traverse(child)
        traverse(self.root)
        return groups

# Cargar el archivo METADATA CENTRAL.xlsx
print("Cargando el archivo de metadatos...")
archivo_metadata = 'METADATA CENTRAL.xlsx'
metadata_df = pd.read_excel(archivo_metadata, header=1)  # El encabezado está en la fila 2
print("Archivo cargado exitosamente.")
print("Columnas detectadas en el archivo:", metadata_df.columns.tolist())  # Mostrar las columnas detectadas

# Filtrar las filas donde el "Publisher" esté en la lista de editoras
metadata_publishing_df = metadata_df[metadata_df['Publisher'].isin(editoras)].copy()
columnas_agrupacion = ['Artista', 'Titulo', 'Album', 'ISRC', 'Lanzamiento']
metadata_publishing_df[columnas_agrupacion] = metadata_publishing_df[columnas_agrupacion].astype(str)

# Asegurarse de que la columna "%" esté en formato numérico
metadata_publishing_df['%'] = pd.to_numeric(metadata_publishing_df['%'], errors='coerce')

# Crear el árbol e insertar registros basados en la clave de agrupación
print("Insertando registros en el árbol...")
tree = TitleTree()
for _, row in metadata_publishing_df.iterrows():
    key = tuple(row[col] for col in columnas_agrupacion)  # Clave de agrupación
    tree.insert(key, row)

# Calcular el porcentaje de contrato para cada grupo
print("Calculando el porcentaje de contrato para cada registro en el grupo...")
grupo_id = 1
for group in tree.get_groups():
    # Calcular la suma total de "%" en el grupo
    total_porcentaje = sum(float(record['%']) for record in group if pd.notna(record['%']))
    
    for record in group:
        # Calcular el porcentaje relativo "Contrato" para cada registro
        if pd.notna(record['%']) and total_porcentaje != 0:
            record['Contrato'] = (float(record['%']) / total_porcentaje) * 100
        else:
            record['Contrato'] = 0  # Si no hay valor en "%", o si total_porcentaje es 0
        
        # Asignar un número de grupo para referencia
        record['Grupo Contador'] = grupo_id
    
    grupo_id += 1

# Convertir los datos de nuevo a DataFrame con el contrato y contador de grupo asignado
metadata_publishing_df = pd.DataFrame([record for group in tree.get_groups() for record in group])

# Reordenar las columnas para que "Contrato" esté inmediatamente después de "%"
cols = metadata_publishing_df.columns.tolist()
indice_porcentaje = cols.index('%')  # Encontrar el índice de la columna "%"
# Insertar "Contrato" después de "%"
cols.insert(indice_porcentaje + 1, cols.pop(cols.index('Contrato')))
metadata_publishing_df = metadata_publishing_df[cols]

# Guardar los datos en un archivo final
archivo_exportado = 'METADATA_PUBLISHING10.xlsx'
metadata_publishing_df.to_excel(archivo_exportado, index=False)
print(f"Archivo exportado exitosamente como {archivo_exportado}")
