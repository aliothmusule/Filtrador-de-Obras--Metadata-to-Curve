import pandas as pd
import os

# Configuración inicial
archivo_central = 'METADATA CENTRAL.xlsx'
output_folder = 'C-Registros_Autores'
os.makedirs(output_folder, exist_ok=True)

# Cargar datos desde el archivo de Excel
try:
    df = pd.read_excel(archivo_central, skiprows=1)  # Saltar las primeras dos filas
    print(f"[SUCCESS] Archivo '{archivo_central}' cargado exitosamente.")
except Exception as e:
    print(f"[ERROR] No se pudo cargar el archivo '{archivo_central}': {e}")
    exit()

# Limpiar datos de columnas relevantes
df['Author'] = df['Author'].fillna('').astype(str)
df['Last Name'] = df['Last Name'].fillna('').astype(str)

# Lógica para identificar registros
def es_coincidencia(author_field, last_name_field, nombre, apellido):
    """Verifica si el autor y apellido aparecen en los campos, considerando separadores."""
    authors_split = str(author_field).replace("•", ",").split(",")
    last_names_split = str(last_name_field).replace("•", ",").split(",")
    return any(
        nombre.strip() in auth.strip() and apellido.strip() in ln.strip()
        for auth, ln in zip(authors_split, last_names_split)
    )

while True:
    # Ingresar el autor a buscar
    autor_input = input("Ingresa el nombre del autor a buscar (puede ser parcial) o escribe 'SALIR' para terminar: ").strip()
    if autor_input.upper() == "SALIR":
        print("[INFO] Proceso finalizado.")
        break

    # Buscar coincidencias en las columnas `Author` y `Last Name`
    coincidencias = df[
        df['Author'].str.contains(autor_input, case=False, na=False) |
        df['Last Name'].str.contains(autor_input, case=False, na=False)
    ]

    if coincidencias.empty:
        print(f"[WARNING] No se encontraron coincidencias para el autor '{autor_input}'.")
        continue

    # Unificar coincidencias por autor único
    autores_unicos = (
        coincidencias.groupby(['Author', 'Last Name'])
        .size()
        .reset_index()[['Author', 'Last Name']]
    )

    # Mostrar coincidencias únicas
    print("\n[INFO] Coincidencias únicas encontradas:")
    for idx, row in autores_unicos.iterrows():
        print(f"{idx + 1}: {row['Author']} {row['Last Name']}")

    # Seleccionar autor
    try:
        opcion = int(input("\nSelecciona el número del autor que deseas analizar: "))
        autor_seleccionado = autores_unicos.iloc[opcion - 1]
    except (ValueError, IndexError):
        print("[ERROR] Selección inválida, intenta nuevamente.")
        continue

    nombre_seleccionado = autor_seleccionado['Author'].strip()
    apellido_seleccionado = autor_seleccionado['Last Name'].strip()

    print(f"\n[INFO] Autor seleccionado: {nombre_seleccionado} {apellido_seleccionado}")

    # Filtrar registros totales del autor
    registros_totales = df[
        df.apply(
            lambda x: es_coincidencia(x['Author'], x['Last Name'], nombre_seleccionado, apellido_seleccionado),
            axis=1
        )
    ]

    # Filtrar registros individuales
    registros_individuales = registros_totales[
        (df['Author'].str.strip() == nombre_seleccionado) &
        (df['Last Name'].str.strip() == apellido_seleccionado)
    ]

    # Mostrar estadísticas
    print("\n[RESULTADOS]")
    print(f"Total de registros del autor '{nombre_seleccionado} {apellido_seleccionado}': {len(registros_totales)}")
    print(f"Registros individuales: {len(registros_individuales)}")

    # Guardar resultados en archivos separados
    try:
        registros_totales.to_excel(os.path.join(output_folder, f"{nombre_seleccionado}_{apellido_seleccionado}_Totales.xlsx"), index=False)
        registros_individuales.to_excel(os.path.join(output_folder, f"{nombre_seleccionado}_{apellido_seleccionado}_Individuales.xlsx"), index=False)
        print("\n[EXITO] Los archivos han sido generados en la carpeta 'C-Registros_Autores':")
        print(f"- {nombre_seleccionado}_{apellido_seleccionado}_Totales.xlsx")
        print(f"- {nombre_seleccionado}_{apellido_seleccionado}_Individuales.xlsx")
    except Exception as e:
        print(f"[ERROR] No se pudieron guardar los archivos: {e}")
