import pandas as pd
import os

# Configuración inicial
archivo_central = 'METADATA CENTRAL.xlsx'
archivo_iswc = 'METADATA_PUBLISHING_U_ISWC.xlsx'
output_folder = 'C-Registros_Autores'
os.makedirs(output_folder, exist_ok=True)

# Función para verificar coincidencias considerando separadores
def es_coincidencia(campo, valor):
    """Verifica si el valor está en el campo considerando separadores como ',' o '•'."""
    if pd.isna(campo):
        return False
    elementos = str(campo).replace("•", ",").split(",")
    return any(valor.strip().lower() in elemento.strip().lower() for elemento in elementos)

# Cargar archivos
try:
    df_central = pd.read_excel(archivo_central, skiprows=2)
    df_iswc = pd.read_excel(archivo_iswc)
    print(f"[SUCCESS] Archivos cargados correctamente.")
except Exception as e:
    print(f"[ERROR] No se pudieron cargar los archivos: {e}")
    exit()

# Limpiar datos
df_central['Author'] = df_central['Author'].fillna('').astype(str)
df_central['Last Name'] = df_central['Last Name'].fillna('').astype(str)
df_iswc['Author'] = df_iswc['Author'].fillna('').astype(str)
df_iswc['Last Name'] = df_iswc['Last Name'].fillna('').astype(str)
df_iswc['Title'] = df_iswc['Title'].fillna('').astype(str)

# Ingresar el autor a buscar
autor_input = input("Ingresa el nombre del autor a buscar (puede ser parcial): ").strip()

# Buscar coincidencias de autor en `METADATA CENTRAL.xlsx`
coincidencias = df_central[
    df_central['Author'].str.contains(autor_input, case=False, na=False) |
    df_central['Last Name'].str.contains(autor_input, case=False, na=False)
]

if coincidencias.empty:
    print(f"[WARNING] No se encontraron coincidencias para el autor '{autor_input}' en METADATA CENTRAL.")
    exit()

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
opcion = int(input("\nSelecciona el número del autor que deseas analizar: "))
autor_seleccionado = autores_unicos.iloc[opcion - 1]
nombre_seleccionado = autor_seleccionado['Author'].strip()
apellido_seleccionado = autor_seleccionado['Last Name'].strip()

print(f"\n[INFO] Autor seleccionado: {nombre_seleccionado} {apellido_seleccionado}")

# Buscar registros individuales en METADATA CENTRAL
registros_individuales = df_central[
    (df_central['Author'].str.strip() == nombre_seleccionado) &
    (df_central['Last Name'].str.strip() == apellido_seleccionado)
]

# Buscar colaboraciones en METADATA_PUBLISHING_U_ISWC
registros_colaboraciones = df_iswc[
    df_iswc.apply(
        lambda x: es_coincidencia(x['Author'], nombre_seleccionado) and
                  es_coincidencia(x['Last Name'], apellido_seleccionado),
        axis=1
    )
]

# Buscar títulos relacionados en METADATA CENTRAL
titulos_colaboraciones = registros_colaboraciones['Title'].dropna().unique()
registros_titulos = df_central[
    df_central.apply(
        lambda x: any(es_coincidencia(x['Title'], titulo) for titulo in titulos_colaboraciones),
        axis=1
    )
]

# Unir registros individuales y colaboraciones
registros_totales = pd.concat([registros_individuales, registros_titulos]).drop_duplicates()

# Mostrar estadísticas
print("\n[RESULTADOS]")
print(f"Total de registros del autor '{nombre_seleccionado} {apellido_seleccionado}': {len(registros_totales)}")
print(f"Registros individuales: {len(registros_individuales)}")
print(f"Registros con colaboraciones: {len(registros_titulos)}")

# Guardar resultados en archivos
try:
    registros_totales.to_excel(os.path.join(output_folder, f"{nombre_seleccionado}_{apellido_seleccionado}_Totales.xlsx"), index=False)
    registros_individuales.to_excel(os.path.join(output_folder, f"{nombre_seleccionado}_{apellido_seleccionado}_Individuales.xlsx"), index=False)
    registros_titulos.to_excel(os.path.join(output_folder, f"{nombre_seleccionado}_{apellido_seleccionado}_Colaboraciones.xlsx"), index=False)
    print("\n[EXITO] Los archivos han sido generados en la carpeta 'C-Registros_Autores':")
    print(f"- {nombre_seleccionado}_{apellido_seleccionado}_Totales.xlsx")
    print(f"- {nombre_seleccionado}_{apellido_seleccionado}_Individuales.xlsx")
    print(f"- {nombre_seleccionado}_{apellido_seleccionado}_Colaboraciones.xlsx")
except Exception as e:
    print(f"[ERROR] No se pudieron guardar los archivos: {e}")
