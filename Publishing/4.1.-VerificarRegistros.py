import pandas as pd

# Definir las editoras a filtrar
editoras = [
    "BACKSTAGE EDITORA TX", "MUSIC BY BACKSTAGE PUBLISHING", "MUSIC BY CANZION LEGACY",
    "CANZION LEGACY", "CANZION PUBLISHING TX", "GRUPO CANZION EDITORA",
    "MUSIC BY HEAVEN LEGAZY", "HEAVEN LEGACY", "HEAVEN NETWORKS", "MUSIC BY HEAVEN PUBLISHING",
    "PUBLISHING BY COMPOSITORES", "COMPOSITORES PUBLISHING", "ALIENTO PUBLISHING",
    "CEV ADMINISTRATION", "CEV PUBLISHER LLC", "LK COLLECTIVE", "FRILOP MUSIC",
    "JUAN SALINAS MUSIC PUBLISHING", "LOS VENCEDORES PUBLISHING", "MUSIC BY GREEN MUSIC PUBLISHING",
    "MUSIC BY MAJESTIC RECORDS PUBLISHING", "MUSIC FROM AZ MUSIC", "REDIMI2 MUSIC PUBLISHING",
    "REYVOL MUSIK LLC", "COALO ZAMORANO PUBLISHING", "MIKE RODRIGUEZ MUSIC",
    "ADORA MUSIC INTERNATIONAL", "MAR DE CRISTAL PUBLISHING", "MONTESANTO PUBLISHING",
    "GRACE ESPANOL MUSICA"
]

# Cargar los tres archivos de metadatos
archivo_metadata = 'METADATA_PUBLISHING_COLOR.xlsx'
archivo_metadata_central = 'METADATA CENTRAL.xlsx'
archivo_metadata_publishing_color = 'METADATA_PUBLISHING_COLOR.xlsx'  # Asumimos que es el nombre correcto

print("Cargando los archivos de metadatos...")
metadata_df = pd.read_excel(archivo_metadata, header=0)
metadata_central_df = pd.read_excel(archivo_metadata_central, header=1)
metadata_publishing_color_df = pd.read_excel(archivo_metadata_publishing_color, header=0)
print("Archivos cargados exitosamente.")

# Filtrar registros de los tres conjuntos por editoras
metadata_df['Publisher'] = metadata_df['Publisher'].astype(str).str.strip()
metadata_central_df['Publisher'] = metadata_central_df['Publisher'].astype(str).str.strip()
metadata_publishing_color_df['Publisher'] = metadata_publishing_color_df['Publisher'].astype(str).str.strip()

metadata_publishing_df = metadata_df[metadata_df['Publisher'].isin(editoras)].copy()
metadata_central_filtered = metadata_central_df[metadata_central_df['Publisher'].isin(editoras)].copy()
metadata_publishing_color_filtered = metadata_publishing_color_df[metadata_publishing_color_df['Publisher'].isin(editoras)].copy()

# Comparar y encontrar registros adicionales en metadata_publishing_df
columnas_agrupacion = ['Artista', 'Titulo', 'Album', 'ISRC', 'Lanzamiento']
metadata_publishing_df[columnas_agrupacion] = metadata_publishing_df[columnas_agrupacion].astype(str)
metadata_central_filtered[columnas_agrupacion] = metadata_central_filtered[columnas_agrupacion].astype(str)
metadata_publishing_color_filtered[columnas_agrupacion] = metadata_publishing_color_filtered[columnas_agrupacion].astype(str)

# Comparar metadata_publishing_df con metadata_central_filtered y metadata_publishing_color_filtered
merged_with_central = metadata_publishing_df.merge(
    metadata_central_filtered, on=columnas_agrupacion, how='left', indicator=True
).loc[lambda x: x['_merge'] == 'left_only'].drop(columns=['_merge'])

extra_records = merged_with_central.merge(
    metadata_publishing_color_filtered, on=columnas_agrupacion, how='left', indicator=True
).loc[lambda x: x['_merge'] == 'left_only'].drop(columns=['_merge'])

# Mostrar totales y guardar registros adicionales
print(f"Total de registros en metadata_publishing: {len(metadata_publishing_df)}")
print(f"Total de registros en metadata_central filtrado: {len(metadata_central_filtered)}")
print(f"Total de registros en metadata_publishing_color filtrado: {len(metadata_publishing_color_filtered)}")
print(f"Registros adicionales en metadata_publishing_df: {len(extra_records)}")

# Guardar los registros adicionales en un archivo Excel para revisión
archivo_extra_registros = 'REGISTROS_ADICIONALES_TRIPLE_COMPARACION.xlsx'
extra_records.to_excel(archivo_extra_registros, index=False)
print(f"Archivo '{archivo_extra_registros}' creado con los registros adicionales para su revisión.")
