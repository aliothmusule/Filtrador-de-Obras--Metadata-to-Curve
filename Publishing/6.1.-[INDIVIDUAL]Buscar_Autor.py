import pandas as pd
import logging
from datetime import datetime
import os

# Configuración del logging para un solo archivo de log
log_filename = "(ISWC)Unificacion.log"
logging.basicConfig(filename=log_filename, level=logging.INFO, format='%(message)s', encoding='utf-8')

# Agregar un encabezado al inicio de cada ejecución
with open(log_filename, 'a', encoding='utf-8') as log_file:
    log_file.write(f"\n--- Ejecución iniciada: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n")

print("[PROCESS] Iniciando el proceso de unificación de archivos.")

# Crear la carpeta donde se guardarán los archivos de cada autor y las colaboraciones
output_folder = 'Archivos_Autores-y-Colaboracion_Compartida'
os.makedirs(output_folder, exist_ok=True)
print(f"[SUCCESS] Carpeta '{output_folder}' creada o ya existente.")

# Cargar el archivo de datos unificados
archivo_origen = 'METADATA_PUBLISHING_UNIFICADO.xlsx'

try:
    df = pd.read_excel(archivo_origen, sheet_name='Unificados')
    print(f"[SUCCESS] Archivo '{archivo_origen}' cargado exitosamente.")
except Exception as e:
    print(f"[ERROR] No se pudo cargar el archivo '{archivo_origen}': {e}")
    exit()

# Conjunto de valores de ISWC inválidos
iswc_invalidos = {"", " ", None, "Sin Codigo", '0', '--', 'Pendiente', 'Pendiente Reg.', 'PENDIENTE', 'NO', 'FaltaMedley', 0, 'Sin ISWC ', 'Sin ISWC', 'SIN ISWC', 'SIN Codigo'}

# Separar los registros con ISWC válido e inválido
df_invalidos = df[df['ISWC'].isin(iswc_invalidos)].copy()
df_validos = df[~df['ISWC'].isin(iswc_invalidos)].copy() # importante que no quiten el: ~ porque es parte del proceso de unificacion
print(f"[INFO] {len(df_invalidos)} registros con ISWC inválido y {len(df_validos)} registros con ISWC válido encontrados.")

# Detectar registros con múltiples autores
df_validos['is_shared'] = df_validos['Author'].fillna('') + ' ' + df_validos['Last Name'].fillna('')
df_validos['is_shared'] = df_validos['is_shared'].apply(lambda x: isinstance(x, str) and ('•' in x or ',' in x))

# Crear un diccionario para almacenar registros individuales por autor y una lista para colaboraciones
autores_data = {}
obras_compartidas = []

# Separar los registros en archivos individuales y el archivo de obras compartidas
print("[PROCESS] Separando registros individuales y colaboraciones..")
for _, row in df_validos.iterrows():
    # Convertir 'Author' y 'Last Name' a cadenas de texto en caso de que sean NaN o float
    author = str(row['Author']) if pd.notna(row['Author']) else 'Unknown'
    last_name = str(row['Last Name']) if pd.notna(row['Last Name']) else 'unknown'
    author_key = f"[{author}]_[{last_name}]"  # Formato [Author]_[Last Name]
    
    if row['is_shared']:
        obras_compartidas.append(row)
    else:
        if author_key not in autores_data:
            autores_data[author_key] = []
        autores_data[author_key].append(row)

# Guardar cada autor en un archivo Excel individual
print("[PROCESS] Guardando archivos individuales para cada autor...")
for author, rows in autores_data.items():
    try:
        df_author = pd.DataFrame(rows)
        author_filename = os.path.join(output_folder, f"{author.replace(' ', '_')}.xlsx")
        df_author.to_excel(author_filename, index=False, sheet_name="Obras")
        print(f"[SUCCESS] Archivo creado para '{author}' en '{author_filename}'.")
    except Exception as e:
        print(f"[ERROR] No se pudo crear el archivo para '{author}': {e}")

# Guardar el archivo de obras compartidas
if obras_compartidas:
    try:
        df_shared = pd.DataFrame(obras_compartidas)
        shared_filename = os.path.join(output_folder, "Obras_Compartidas.xlsx")
        df_shared.to_excel(shared_filename, index=False, sheet_name="Obras Compartidas")
        print(f"[SUCCESS] Archivo de obras compartidas creado en '{shared_filename}'.")
    except Exception as e:
        print(f"[ERROR] No se pudo crear el archivo de obras compartidas: {e}")
else:
    print("[WARNING] No se encontraron obras compartidas para guardar.")

# Finalizar el log
with open(log_filename, 'a', encoding='utf-8') as log_file:
    log_file.write(f"Archivos individuales creados en la carpeta '{output_folder}'.\n")
print(f"[SUCCESS] Proceso de unificación completado. Archivos creados en la carpeta '{output_folder}'.")
