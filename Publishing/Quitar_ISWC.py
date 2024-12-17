import pandas as pd
import logging
import re
from datetime import datetime

# Configuración del logging para un solo archivo de log
log_filename = "(ISWC)QUITAO.log"
logging.basicConfig(filename=log_filename, level=logging.INFO, format='%(message)s', encoding='utf-8')

# Agregar un encabezado al inicio de cada ejecución
with open(log_filename, 'a', encoding='utf-8') as log_file:
    log_file.write(f"\n--- Ejecución iniciada: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n")

# Archivo origen y destino
archivo_origen = 'METADATA CENTRAL.xlsx'
archivo_destino = 'ISWC_VALIDO.xlsx'

# Expresión regular para ISWC válido con texto dinámico
def es_iswc_valido(valor):
    if pd.isna(valor):
        return False
    patron = r'^(.*?T\d{9,10}.*?|.*?T-\d{3,}\..*?-\d.*?|.*?T\d{9,10}/T\d{9,10}.*?|.*?\d{2,}%.*)$'  # Patrón que permite texto dinámico
    return re.search(patron, str(valor).strip())

# Cargar los datos desde la hoja 'Unificados', ajustando el header a la fila 2 (índice 1)
df = pd.read_excel(archivo_origen, sheet_name='MC', header=1)

# Limpiar ISWC pero mantener todas las filas originales
def limpiar_iswc(df):
    df['ISWC'] = df['ISWC'].apply(lambda x: x if es_iswc_valido(x) else None)
    
    # Log de registros inválidos
    with open(log_filename, 'a', encoding='utf-8') as log_file:
        for idx, valor in df['ISWC'].items():
            if valor is None:
                log_file.write(f"Fila {idx + 2}: ISWC inválido reemplazado con None.\n")

    return df

# Limpiar ISWC
print("Limpiando ISWC...")
df_limpio = limpiar_iswc(df)

# Guardar el archivo resultante con todas las filas originales
with pd.ExcelWriter(archivo_destino, engine='xlsxwriter') as writer:
    df_limpio.to_excel(writer, index=False, sheet_name='METADATA_ISWC_VALIDO', startrow=1)

print(f"Archivo '{archivo_destino}' creado exitosamente con todas las filas y ISWC limpiado.")
