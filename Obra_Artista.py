import pandas as pd
import time
import sys
import difflib
import os
import glob
import json

# Valores no válidos
VALORES_NO_VALIDOS = ["N/A", "", "NO MLC", "NO", None]

def eliminar_valores_no_validos(df):
    """Elimina valores no válidos de las celdas en el DataFrame."""
    df = df.applymap(lambda x: None if x in VALORES_NO_VALIDOS else x)
    return df.dropna(how='all')  # Eliminar filas completamente vacías

def verificar_duplicados(df_actual, nuevo_registro):
    """Verifica si el nuevo registro ya existe en el DataFrame"""
    return (
        (df_actual['ISRC'] == nuevo_registro['ISRC']) & 
        (df_actual['Titulo'] == nuevo_registro['Titulo']) & 
        (df_actual['Lanzamiento'] == nuevo_registro['Lanzamiento'])
    ).any()

def exportar_sin_duplicados(df_nuevos, archivo, columnas_a_exportar, sheet_name):
    """Función que exporta los datos a un archivo, verificando y evitando duplicados"""
    df_nuevos = eliminar_valores_no_validos(df_nuevos)  # Eliminar valores no válidos

    if os.path.exists(archivo):
        df_existente = pd.read_excel(archivo)
        print(f"El archivo {archivo} ya existe. Verificando duplicados...")
        
        # Filtrar solo las filas que no están duplicadas
        df_nuevos_unicos = df_nuevos[~df_nuevos.apply(lambda row: verificar_duplicados(df_existente, row), axis=1)]
        
        if df_nuevos_unicos.empty:
            print("No hay nuevos registros que agregar.")
            return

        # Combinar los datos existentes con los nuevos
        df_combinado = pd.concat([df_existente, df_nuevos_unicos], ignore_index=True)
    else:
        df_combinado = df_nuevos
        print(f"El archivo {archivo} no existe. Creando un nuevo archivo.")

    # Exportar los datos al archivo con el nombre de la hoja personalizada
    with pd.ExcelWriter(archivo, engine='openpyxl') as writer:
        df_combinado[columnas_a_exportar].to_excel(writer, sheet_name=sheet_name, index=False)
    print(f"Datos exportados correctamente a {archivo} con la hoja '{sheet_name}'.")

def main():
    config_file = 'config.json'
    config = {}

    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)

    excel_file = config.get('excel_file', None)

    if excel_file and os.path.exists(excel_file):
        print(f"Usando el archivo predeterminado: {excel_file}")
    else:
        print("No se ha establecido un archivo Excel predeterminado o el archivo no existe.")
        excel_files = glob.glob('*.xlsx')
        for idx, file in enumerate(excel_files, 1):
            print(f"{idx}. {file}")
        seleccion = input("Seleccione el número del archivo que desea usar: ")
        try:
            seleccion = int(seleccion)
            if seleccion >= 1 and seleccion <= len(excel_files):
                excel_file = excel_files[seleccion - 1]
            else:
                print("Selección inválida.")
                sys.exit(1)
        except ValueError:
            print("Selección inválida.")
            sys.exit(1)
        set_default = input("¿Desea establecer este archivo como predeterminado? (s/n): ")
        if set_default.lower() == 's':
            config['excel_file'] = excel_file

    sheet_name = config.get('sheet_name', None)
    header_row = config.get('header_row', None)

    if not sheet_name or header_row is None:
        try:
            sheet_names = pd.ExcelFile(excel_file).sheet_names
            print("Hojas disponibles en el archivo Excel:")
            for idx, name in enumerate(sheet_names, 1):
                print(f"{idx}. {name}")
            sheet_selection = input("Seleccione el número de la hoja que desea usar (presione Enter para usar la primera hoja): ")
            if sheet_selection == '':
                sheet_name = 0
            else:
                try:
                    sheet_selection = int(sheet_selection)
                    sheet_name = sheet_names[sheet_selection - 1]
                except ValueError:
                    sheet_name = 0
            header_row_input = input("Ingrese el número de la fila que contiene los encabezados (por defecto 2): ")
            header_row = int(header_row_input) - 1 if header_row_input else 1
        except Exception as e:
            print("Error al obtener las hojas del archivo Excel:", e)
            sheet_name = 0
            header_row = 1

    try:
        df = pd.read_excel(excel_file, sheet_name=sheet_name, header=header_row)
        print("Datos cargados correctamente.")
    except Exception as e:
        print("Error al cargar el archivo Excel:", e)
        sys.exit(1)

    df['NombreCompleto'] = (df['Autor'].fillna('').astype(str) + ' ' + df['Apellido'].fillna('').astype(str)).str.strip()

    compositor_input = input("Ingrese el nombre del compositor (nombre y/o apellido): ")
    nombres_completos = df['NombreCompleto'].dropna().unique().tolist()
    coincidencias = difflib.get_close_matches(compositor_input, nombres_completos, n=5, cutoff=0.5)

    if not coincidencias:
        print("No se encontraron coincidencias cercanas.")
        sys.exit(1)
    else:
        for idx, nombre in enumerate(coincidencias, 1):
            print(f"{idx}. {nombre}")
        seleccion = input("Ingrese el número correspondiente al nombre, o 0 para cancelar: ")
        try:
            seleccion = int(seleccion)
            if seleccion == 0:
                sys.exit(1)
            compositor = coincidencias[seleccion - 1]
        except (ValueError, IndexError):
            print("Selección inválida.")
            sys.exit(1)

    resultados = df[df['NombreCompleto'] == compositor]

    if resultados.empty:
        print("No se encontraron resultados para el compositor seleccionado.")
        sys.exit(1)

    columnas_a_exportar = [
        '#', 'Artista', 'Titulo', 'Album', 'ISRC', 'UPC', 'Lanzamiento','Duración', 'Sound Recording',
        'Sello', 'Autor', 'Apellido', '%','Contrato', 'IPI', 'Publisher', 'CCLI', 'MLC', 'Harry Fox',
        'USA (BMI-ASCAP)', 'WORK ID', 'ISWC', 'MEXICO (SACM)', 'GUATEMALA (AEI)', 'COLOMBIA (SAYCO)',
        'ACINPRO analogo', 'ACINPRO digital', 'ARGENTINA (SADAIC)', 'BRASIL', 'ESPAÑA SGAE'
    ]

    opcion_exportar = input("¿Deseas exportar todas las obras, solo filtradas por porcentaje (100%), o colaboraciones? (todo/filtrado/colaboracion): ")

    compositor_filename = compositor.replace(" ", "_").replace("/", "_").replace("\\", "_")
    nombre_hoja = f"Obras 100 {compositor}"  # Crear nombre dinámico para la hoja

    if opcion_exportar == "filtrado":
        obras_100 = resultados[resultados['%'] == 100]
        exportar_sin_duplicados(obras_100, f'obras_compositor_100_{compositor_filename}.xlsx', columnas_a_exportar, sheet_name=f'{compositor} obras 100')

    elif opcion_exportar == "colaboracion":
        obras_100 = resultados[resultados['%'] == 100]
        obras_colaboracion = resultados[resultados['%'] < 100]

        exportar_sin_duplicados(obras_100, f'obras_compositor_100_{compositor_filename}.xlsx', columnas_a_exportar, sheet_name=f'{compositor} obras 100')
        exportar_sin_duplicados(obras_colaboracion, 'colaboraciones.xlsx', columnas_a_exportar, sheet_name='Colaboraciones')

    else:
        exportar_sin_duplicados(resultados, f'obras_compositor_todas_{compositor_filename}.xlsx', columnas_a_exportar, sheet_name=f'{compositor} obras completas')

    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    main()
