import pandas as pd
import logging
from datetime import datetime

# Configuración del logging para un solo archivo de log
log_filename = "(ISWC)Unificacion.log"
logging.basicConfig(filename=log_filename, level=logging.INFO, format='%(message)s', encoding='utf-8')

# Agregar un encabezado al inicio de cada ejecución
with open(log_filename, 'a', encoding='utf-8') as log_file:
    log_file.write(f"\n--- Ejecución iniciada: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n")

# Cargar el archivo de datos unificados
archivo_origen = 'METADATA_PUBLISHING_UNIFICADO.xlsx'
archivo_destino = 'METADATA_PUBLISHING_U_ISWC.xlsx'

# Conjunto de valores de ISWC inválidos
iswc_invalidos = {"", " ", None, "Sin Codigo", '0', '--', 'Pendiente', 'Pendiente Reg.', 'PENDIENTE', 'NO', 'FaltaMedley', 0,'Sin ISWC ','Sin ISWC','SIN ISWC','SIN Codigo'}

# Cargar los datos desde la hoja 'Unificados'
df = pd.read_excel(archivo_origen, sheet_name='Unificados')

# Columnas para unificar, basadas en la imagen proporcionada
'''
columnas_unificar = [
    '#', 'Artist', 'Title', 'Album', 'Género', 'ISRC', 'UPC', 'Release Date', 'Duration',
    'Sound Recording', 'Sello', 'Producer', 'Engineer', 'Master Engineer', 'Mixter', 'Arranger',
    'Author', 'Last Name', '%', 'Contrato', 'IPI', 'PRO', 'Publisher', 'IPI.1', 'PRO.1', '%.1',
    'Mech', 'Perf', 'Sync', 'ADQ. PUBLISHING', 'CCLI', 'MLC', 'M Reports', 'Harry Fox', 'Sound Ex',
    'USA (BMI-ASCAP)', 'WORK ID', 'ISWC', 'MEXICO (SACM)', 'GUATEMALA (AEI)', 'COLOMBIA (SAYCO)',
    'ACINPRO analogo', 'ACINPRO digital', 'ARGENTINA (SADAIC)', 'COSTA RICA', 'PANAMA',
    'EL SALVADOR', 'NICARAGUA', 'BELICE', 'HONDURAS', 'REPUBLICA DOMINICANA', 'BRASIL', 'ESPAÑA SGAE',
    'ECUADOR', 'PARAGUAY', 'INDAUTOR', 'USCO', 'Año', 'FORMATO', 'Eliminado de Youtube','ID IDENTIFICADOR','FORMATO',
    'Catálogo completo', 'REVISION', 'REVISION .1'
]'''
columnas_unificar = [
    '#', 'Artist', 'Title', 'Album', 'Genres', 'ISRC', 'UPC', 'Release Date', 'Duration',
    'Sound Recording', 'Label', 'Producer', 'Engineer', 'Master Engineer', 'Mixer', 'Arranger',
    'Author', 'Last Name', '%','Contrato' 'IPI', 'PRO', 'Publisher', 'IPI.1', 'PRO.1', '%.1',
    'Mech', 'Perf', 'Sync', 'ADQ. publishing', 'CCLI', 'MLC', 'M Reports', 'Harry Fox', 'Sound Ex',
    'USA (BMI-ASCAP)', 'WORK ID', 'ISWC', 'Mexico (SACM)', 'GUATEMALA (AEI)', 'COLOMBIA (SAYCO)',
    'ACINPRO analogo', 'ACINPRO digital', 'ARGENTINA (SADAIC)', 'COSTA RICA', 'PANAMA',
    'EL SALVADOR', 'NICARAGUA', 'BELICE', 'HONDURAS', 'REPUBLICA DOMINICANA', 'BRASIL', 'ESPAÑA SGAE',
    'ECUADOR', 'PARAGUAY', 'INDAUTOR', 'USCO', 'Year', 'ID IDENTIFICADOR', 'FORMATO',
    'Catálogo completo', 'REVISION', 'REVISION .1'
]





# Separar los registros con ISWC válido e inválido

df_invalidos = df[df['ISWC'].isin(iswc_invalidos) | df['ISWC'].apply(pd.isna)].copy()
df_validos = df[~df['ISWC'].isin(iswc_invalidos) & ~df['ISWC'].apply(pd.isna)].copy()
# Función para unificar registros con el mismo ISWC e imprimir los ISRC que se están unificando
def unificar_por_iswc(df, columnas):
    registros_log = []
    for iswc, group in df.groupby('ISWC'):
        isrc_list = group['ISRC'].dropna().unique()
        registros_log.append(f"ISWC '{iswc}': ISRCs {', '.join(isrc_list)}")

        # Crear el registro unificado usando '-' como separador en todas las columnas
        df_unificado = group.agg(lambda x: '•'.join(sorted(set(str(i) for i in x if pd.notna(i)))))
        registros_log.append(f"Registro unificado: {df_unificado.to_dict()}")

    # Escribir todos los registros de la unificación al log de una vez
    with open(log_filename, 'a', encoding='utf-8') as log_file:
        log_file.write("\n".join(registros_log) + "\n")
    
    df_unificado = df.groupby('ISWC').agg(lambda x: '•'.join(sorted(set(str(i) for i in x if pd.notna(i)))))
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

# Imprimir la cantidad de filas creadas en el DataFrame final
print(f"Se crearon un total de {len(df_final)} filas en el archivo '{archivo_destino}'.")
print(f"{len(df_final)+1} filas contando header.")
print(f"Archivo '{archivo_destino}' creado exitosamente con registros unificados por ISWC.")
