import pandas as pd

# Cargar el archivo de datos unificados
archivo_origen = 'METADATA_PUBLISHING_UNIFICADO.xlsx'
archivo_destino = 'METADATA_PUBLISHING__U_ISWC.xlsx'

# Conjunto de valores de ISWC inválidos
iswc_invalidos = {"", " ", None, "Sin Codigo"}

# Cargar los datos desde la hoja 'Unificados'
df = pd.read_excel(archivo_origen, sheet_name='Unificados')

# Columnas para unificar, basadas en la imagen proporcionada
columnas_unificar = [
    '#', 'Artista', 'Titulo', 'Album', 'Género', 'ISRC', 'UPC', 'Lanzamiento', 'Duración ',
    'Sound Recording', 'Sello', 'Producer', 'Engineer', 'Master Engineer', 'Mixter', 'Arranger',
    'Autor', 'Apellido', '%', 'Contrato', 'IPI', 'PRO', 'Publisher', 'IPI.1', 'PRO.1', '%.1',
    'Mech', 'Perf', 'Sync', 'ADQ. PUBLISHING', 'CCLI', 'MLC', 'M Reports', 'Harry Fox', 'Sound Ex',
    'USA (BMI-ASCAP)', 'WORK ID', 'ISWC', 'MEXICO (SACM)', 'GUATEMALA (AEI)', 'COLOMBIA (SAYCO)',
    'ACINPRO analogo', 'ACINPRO digital', 'ARGENTINA (SADAIC)', 'COSTA RICA', 'PANAMA',
    'EL SALVADOR', 'NICARAGUA', 'BELICE', 'HONDURAS', 'REPUBLICA DOMINICANA', 'BRASIL', 'ESPAÑA SGAE',
    'ECUADOR', 'PARAGUAY', 'INDAUTOR', 'USCO', 'Año', 'FORMATO', 'Eliminado de Youtube',
    'Catálogo completo', 'REVISION', 'REVISION .1', 'Grupo Contador'
]

# Separar los registros con ISWC válido e inválido
df_invalidos = df[df['ISWC'].isin(iswc_invalidos)].copy()
df_validos = df[~df['ISWC'].isin(iswc_invalidos)].copy()

# Función para unificar registros con el mismo ISWC
def unificar_por_iswc(df, columnas):
    df_unificado = df.groupby('ISWC').agg(lambda x: ', '.join(sorted(set(str(i) for i in x if pd.notna(i)))))
    df_unificado.reset_index(inplace=True)
    return df_unificado

# Aplicar la unificación a los registros con ISWC válido
df_unificado_iswc = unificar_por_iswc(df_validos, columnas_unificar)

# Combinar los registros unificados y los individuales (sin ISWC)
df_final = pd.concat([df_unificado_iswc, df_invalidos], ignore_index=True)

# Guardar el archivo resultante
with pd.ExcelWriter(archivo_destino, engine='xlsxwriter') as writer:
    df_final.to_excel(writer, index=False, sheet_name='Unificados_Por_ISWC')
    workbook = writer.book
    worksheet = writer.sheets['Unificados_Por_ISWC']

    colores_visibles = [
        "#FFEBCC", "#FFF2CC", "#E6FFCC", "#CCFFE6", "#CCE6FF", "#E6CCFF", "#FFD1DC", "#FFCCCC",
        "#CCFFEB", "#CCE5FF", "#E0FFE6", "#FFFFCC", "#FFCCE5", "#FFEECC", "#D6E6FF", "#E6FFFA",
        "#FFDAB9", "#FFDFC4", "#E6F7FF", "#FFF9CC", "#FFF1E0", "#E8FFCC"
    ]

    # Aplicar colores cíclicamente para diferenciar los grupos
    for row_num in range(1, len(df_final) + 1):
        color = colores_visibles[(row_num - 1) % len(colores_visibles)]
        cell_format = workbook.add_format({'bg_color': color})
        worksheet.set_row(row_num, None, cell_format)

print(f"Archivo '{archivo_destino}' creado exitosamente con registros unificados por ISWC.")
