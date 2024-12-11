import pandas as pd
import os
from collections import defaultdict

# Configuración inicial
output_folder = 'U_ISWC_Archivos_Autores_y_Colaboracion_Compartida'
os.makedirs(output_folder, exist_ok=True)
archivo_origen = 'METADATA_PUBLISHING_U_ISWC.xlsx'

# Lista de autores específicos en formato "Nombre_Apellido"
autores_especificos = ["Marcos_Vidal Roloff", "Marcos_Witt"]  # Ajusta según sea necesario

# Cargar datos desde el archivo de Excel
try:
    df = pd.read_excel(archivo_origen, sheet_name='Unificados_Por_ISWC')
    print(f"[SUCCESS] Archivo '{archivo_origen}' cargado exitosamente.")
except Exception as e:
    print(f"[ERROR] No se pudo cargar el archivo '{archivo_origen}': {e}")
    exit()

# Crear estructuras para almacenar datos
autores_data = defaultdict(list)  # Registros individuales de autores específicos
obras_compartidas = defaultdict(list)  # Colaboraciones por obra
autores_colaboraciones = defaultdict(list)  # Obras compartidas específicas por autor
errores_autores = set(autores_especificos)  # Para rastrear autores no encontrados

# Procesar registros
for _, row in df.iterrows():
    # Verificar el registro individual del autor
    author_exact = str(row['Author']).strip()
    last_name_exact = str(row['Last Name']).strip()
    
    for author_specific in autores_especificos:
        nombre, apellido = author_specific.split("_", 1)
        
        # Lógica para el archivo individual (coincidencia exacta en Author y Last Name)
        if author_exact == nombre and last_name_exact == apellido:
            errores_autores.discard(author_specific)
            autores_data[author_specific].append(row)
        
        # Lógica para colaboraciones específicas (Author o Last Name contienen el nombre y apellido)
        authors_split = str(row['Author']).replace("•", ",").split(",")
        last_names_split = str(row['Last Name']).replace("•", ",").split(",")
        if any(nombre.strip() in auth.strip() and apellido.strip() in ln.strip() 
               for auth, ln in zip(authors_split, last_names_split)):
            obras_compartidas[row['ISWC']].append(row)
            autores_colaboraciones[author_specific].append(row)

# Crear archivos individuales para cada autor específico
print("[PROCESS] Generando archivos individuales para autores específicos...")
for author, registros in autores_data.items():
    try:
        df_author = pd.DataFrame(registros)
        author_filename = os.path.join(output_folder, f"{author}.xlsx")
        df_author.to_excel(author_filename, index=False, sheet_name="Obras Individuales")
        print(f"[SUCCESS] Archivo creado para '{author}' en '{author_filename}'.")
    except Exception as e:
        print(f"[ERROR] No se pudo crear el archivo para '{author}': {e}")

# Crear archivos individuales con colaboraciones específicas para cada autor
print("[PROCESS] Generando archivos de colaboraciones específicas para cada autor...")
for author, registros in autores_colaboraciones.items():
    try:
        df_author_colab = pd.DataFrame(registros).drop_duplicates()
        author_colab_filename = os.path.join(output_folder, f"{author}_Colaboraciones.xlsx")
        df_author_colab.to_excel(author_colab_filename, index=False, sheet_name="Obras Compartidas")
        print(f"[SUCCESS] Archivo de colaboraciones creado para '{author}' en '{author_colab_filename}'.")
    except Exception as e:
        print(f"[ERROR] No se pudo crear el archivo de colaboraciones para '{author}': {e}")

# Crear un archivo consolidado para las obras compartidas generales
print("[PROCESS] Generando archivo de obras compartidas generales...")
try:
    colaboraciones_output = []
    for _, registros in obras_compartidas.items():
        for registro in registros:
            colaboraciones_output.append(registro)
    
    if colaboraciones_output:
        df_colaboraciones = pd.DataFrame(colaboraciones_output).drop_duplicates()
        shared_filename = os.path.join(output_folder, "Obras_Compartidas_General.xlsx")
        df_colaboraciones.to_excel(shared_filename, index=False, sheet_name="Colaboraciones Generales")
        print(f"[SUCCESS] Archivo de obras compartidas generales creado en '{shared_filename}'.")
    else:
        print("[WARNING] No se encontraron colaboraciones relacionadas.")
except Exception as e:
    print(f"[ERROR] No se pudo crear el archivo de obras compartidas generales: {e}")

# Reportar autores no encontrados
if errores_autores:
    print("[ERROR] Los siguientes autores no fueron encontrados en los registros:")
    for autor in errores_autores:
        print(f" - {autor}")

print("[SUCCESS] Proceso completado. Archivos generados en la carpeta de salida.")
