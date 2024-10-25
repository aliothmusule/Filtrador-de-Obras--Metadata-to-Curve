import pandas as pd
from collections import defaultdict
from openpyxl import load_workbook
from openpyxl.styles import PatternFill
import json
import os

# Clase para representar un nodo en el árbol de búsqueda
class TreeNode:
    def __init__(self):
        self.children = {}
        self.records = []

# Clase para agrupar obras por ISRC
class TitleTree:
    def __init__(self):
        self.root = TreeNode()

    def insert(self, isrc, record):
        """Insertar un registro en el árbol, agrupando por ISRC"""
        node = self.root
        isrc = str(isrc)  # Asegurar que el ISRC es un string antes de insertarlo
        for char in isrc:
            if char not in node.children:
                node.children[char] = TreeNode()
            node = node.children[char]
        node.records.append(record)

    def search(self, isrc):
        """Buscar todas las coincidencias de un ISRC en el árbol"""
        node = self.root
        isrc = str(isrc)
        for char in isrc:
            if char not in node.children:
                return None
            node = node.children[char]
        return node.records if node.records else None

# Función para cargar la configuración desde config.json
def cargar_configuracion(config_file):
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
    else:
        config = {}

    # Valores predeterminados si faltan en el config.json
    if 'base_file' not in config:
        config['base_file'] = 'METADATA CENTRAL.xlsx'
    if 'colaboraciones_file' not in config:
        config['colaboraciones_file'] = 'colaboraciones.xlsx'
    if 'header_row_base' not in config:
        config['header_row_base'] = 1  # La fila 2 en Excel corresponde a header=1 en pandas
    if 'header_row_colaboraciones' not in config:
        config['header_row_colaboraciones'] = 0  # La fila 1 en Excel corresponde a header=0 en pandas
    if 'sheet_name_base' not in config:
        config['sheet_name_base'] = 0
    if 'sheet_name_metadata' not in config:
        config['sheet_name_metadata'] = 0
    if 'invalid_values' not in config:
        config['invalid_values'] = ["N/A", "","NO MLC",'NO', None]

    return config

# Función para cargar el archivo de Excel
def cargar_archivo_excel(file_path, header_row, sheet_name):
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name, header=header_row)
        print(f"Archivo '{file_path}' cargado correctamente.")
        print("Columnas disponibles:", df.columns.tolist())
        return df
    except Exception as e:
        print(f"Error al cargar el archivo '{file_path}': {e}")
        return None

# Función para validar identificadores (solo aceptamos los que tengan al menos 6 caracteres)
def es_identificador_valido(identificador):
    return identificador and isinstance(identificador, str) and len(identificador) >= 6

# Función para verificar duplicados en los archivos existentes
def verificar_duplicados(df_actual, nuevo_registro):
    """Verifica si el nuevo registro ya existe en el DataFrame"""
    return ((df_actual['ISRC'] == nuevo_registro['ISRC']) &
            (df_actual['Lanzamiento'] == nuevo_registro['Lanzamiento']) &
            (df_actual['Titulo'] == nuevo_registro['Titulo'])).any()

# Función para buscar coincidencias por ISRC y lanzamiento, y luego sumar los porcentajes
def buscar_y_sumar_por_isrc_y_lanzamiento(tree, df_colaboraciones, invalid_values):
    # Verificar si el archivo ya existe antes de intentar cargar las hojas
    if os.path.exists('Agrupacion_y_Unificacion_obras.xlsx'):
        try:
            df_grupos_existente = pd.read_excel('Agrupacion_y_Unificacion_obras.xlsx', sheet_name='Unificación_Obras')
        except ValueError:
            df_grupos_existente = pd.DataFrame()  # Si la hoja no existe, iniciar un DataFrame vacío
        try:
            df_obras_existente = pd.read_excel('Agrupacion_y_Unificacion_obras.xlsx', sheet_name='Agrupación_Obras')
        except ValueError:
            df_obras_existente = pd.DataFrame()  # Si la hoja no existe, iniciar un DataFrame vacío
    else:
        df_grupos_existente = pd.DataFrame()  # Crear DataFrames vacíos si no existe el archivo
        df_obras_existente = pd.DataFrame()

    # DataFrame para guardar los grupos de obras
    grupos_resultados = []
    obras_grupos = []  # Lista para guardar todas las obras que pertenecen a un grupo
    obras_no_agrupadas = []  # Lista para guardar las obras que no tienen coincidencias

    # Lista de columnas que contienen identificadores
    columnas_identificadores = [
        'MLC', 'ISWC', 'USA (BMI-ASCAP)', 'WORK ID', 'Harry Fox', 
        'MEXICO (SACM)', 'GUATEMALA (AEI)', 'COLOMBIA (SAYCO)', 'ACINPRO analogo', 
        'ACINPRO digital', 'ARGENTINA (SADAIC)', 'BRASIL', 'ESPAÑA SGAE'
    ]

    colores = ['FFFF99', 'FFCC99', '99CCFF', 'CCFFCC', 'FF99CC']  # Colores para identificar los grupos
    color_index = 0

    for index, row in df_colaboraciones.iterrows():
        isrc = row.get('ISRC', None) if es_identificador_valido(row.get('ISRC', None)) else None
        lanzamiento = row.get('Lanzamiento', None)
        current_percentage = row.get('%', 0)

        # Buscar en el árbol por ISRC primero
        if isrc:
            coincidencias = tree.search(isrc)

            if coincidencias:
                # Filtrar coincidencias por la fecha de lanzamiento
                coincidencias_filtradas = [match for match in coincidencias if match['Lanzamiento'] == lanzamiento]

                if coincidencias_filtradas:
                    print(f"\nCoincidencias encontradas para ISRC '{isrc}' con lanzamiento '{lanzamiento}':")
                    for match in coincidencias_filtradas:
                        print(f"Título: {match['Titulo']}, Porcentaje: {match['%']}")

                    # Sumar porcentajes de las coincidencias SIN incluir el porcentaje del registro actual
                    percentages_metadata = [match['%'] for match in coincidencias_filtradas]
                    total_suma = sum(percentages_metadata)

                    print(f"Suma de porcentajes para ISRC '{isrc}' con lanzamiento '{lanzamiento}': {total_suma:.2f}%\n")

                    # Recopilar los nombres completos (Autor y Apellido)
                    nombres_completos_unificados = ', '.join(
                        (match['Autor'] + ' ' + match['Apellido']).strip() 
                        for match in coincidencias_filtradas 
                        if pd.notna(match['Autor']) and pd.notna(match['Apellido'])
                    )

                    # Recopilar los valores de los identificadores (MLC, ISWC, etc.)
                    identificadores = {}
                    for col in columnas_identificadores:
                        # Tomar el primer valor no vacío de cada identificador en las coincidencias
                        identificadores[col] = next((match[col] for match in coincidencias_filtradas if pd.notna(match[col]) and match[col] not in invalid_values), '')

                    # Guardar los datos del grupo en el DataFrame
                    grupo = {
                        'ISRC': isrc,
                        'Lanzamiento': lanzamiento,
                        'Titulo': row.get('Titulo', ''),
                        'Autor': nombres_completos_unificados,
                        '%': total_suma,
                        'Grupo Color': colores[color_index % len(colores)]  # Asignar color al grupo
                    }

                    # Agregar los identificadores al grupo
                    grupo.update(identificadores)

                    # Verificar si ya existe en la hoja de agrupación
                    if df_grupos_existente.empty or not verificar_duplicados(df_grupos_existente, grupo):
                        grupos_resultados.append(grupo)

                    # Agregar todas las obras del grupo a la lista 'obras_grupos'
                    for obra in coincidencias_filtradas:
                        obra['Grupo Color'] = colores[color_index % len(colores)]  # Asignar el mismo color para las obras del grupo
                        
                        # Verificar si ya existe en la hoja de unificación
                        if df_obras_existente.empty or not verificar_duplicados(df_obras_existente, obra):
                            obras_grupos.append(obra)

                    # Cambiar el color para el siguiente grupo
                    color_index += 1
                else:
                    print(f"No se encontraron coincidencias para ISRC '{isrc}' con el lanzamiento '{lanzamiento}'.\n")
                    # Si no se encuentra coincidencia, agregar la obra a 'No Agrupados'
                    row['Motivo'] = "Sin coincidencia por lanzamiento"
                    obras_no_agrupadas.append(row)
            else:
                print(f"No se encontraron coincidencias para ISRC '{isrc}'.\n")
                row['Motivo'] = "Sin coincidencia por ISRC"
                obras_no_agrupadas.append(row)
        else:
            print(f"No se pudo procesar el registro sin un ISRC válido en la fila {index + 2}.\n")

    # Exportar todo en un único archivo con tres hojas
    with pd.ExcelWriter('Agrupacion_y_Unificacion_obras.xlsx', engine='openpyxl', mode='a' if os.path.exists('Agrupacion_y_Unificacion_obras.xlsx') else 'w') as writer:
        if grupos_resultados:
            df_grupos = pd.DataFrame(grupos_resultados)
            df_grupos.to_excel(writer, sheet_name='Unificación_Obras', index=False)
            print(f"\nLos nuevos grupos de obras han sido exportados en la hoja 'Unificación_Obras'.")
        else:
            print("No se encontraron nuevos grupos de obras para exportar.")

        if obras_grupos:
            df_obras_grupos = pd.DataFrame(obras_grupos)
            df_obras_grupos.to_excel(writer, sheet_name='Agrupación_Obras', index=False)
            print(f"\nLas nuevas obras de los grupos han sido exportadas en la hoja 'Agrupación_Obras'.")

        if obras_no_agrupadas:
            df_no_agrupados = pd.DataFrame(obras_no_agrupadas)
            df_no_agrupados.to_excel(writer, sheet_name='No Agrupados', index=False)
            print(f"\nLas obras no agrupadas han sido exportadas en la hoja 'No Agrupados'.")

    # Aplicar el coloreado de fondo por grupo después de haber exportado
    wb = load_workbook('Agrupacion_y_Unificacion_obras.xlsx')
    
    # Colorear "Unificación_Obras"
    ws_grupos = wb['Unificación_Obras']
    for i in range(2, ws_grupos.max_row + 1):  # Comenzamos desde la fila 2 (sin encabezado)
        color_hex = ws_grupos.cell(row=i, column=ws_grupos.max_column).value
        if color_hex:
            color_fill = PatternFill(start_color=color_hex, end_color=color_hex, fill_type="solid")
            for j in range(1, ws_grupos.max_column):  # No colorear la columna de color
                ws_grupos.cell(row=i, column=j).fill = color_fill

    # Colorear "Agrupación_Obras"
    ws_obras = wb['Agrupación_Obras']
    for i in range(2, ws_obras.max_row + 1):  # Comenzamos desde la fila 2 (sin encabezado)
        color_hex = ws_obras.cell(row=i, column=ws_obras.max_column).value
        if color_hex:
            color_fill = PatternFill(start_color=color_hex, end_color=color_hex, fill_type="solid")
            for j in range(1, ws_obras.max_column):  # No colorear la columna de color
                ws_obras.cell(row=i, column=j).fill = color_fill

    wb.save('Agrupacion_y_Unificacion_obras.xlsx')
    print("\nColores aplicados correctamente en las hojas 'Unificación_Obras' y 'Agrupación_Obras'.")

def main(base_file=None):
    config_file = 'config.json'
    
    # Cargar la configuración desde config.json
    config = cargar_configuracion(config_file)

    # Si no se proporciona un archivo, usar el archivo por defecto de config
    base_file = base_file if base_file else config['base_file']

    # Cargar el archivo base (Metadata)
    df_base = cargar_archivo_excel(base_file, config['header_row_base'], config['sheet_name_base'])
    
    # Cargar el archivo de colaboraciones
    df_colaboraciones = cargar_archivo_excel(config['colaboraciones_file'], config['header_row_colaboraciones'], config['sheet_name_metadata'])

    if df_base is None or df_colaboraciones is None:
        print("Error al cargar los archivos de Excel. Verifique las rutas y configuraciones.")
        return

    # Crear el árbol de ISRC
    tree = TitleTree()
    for _, row in df_base.iterrows():
        isrc = row['ISRC']
        tree.insert(isrc, row)

    # Llamar a la función de búsqueda y suma por ISRC y lanzamiento
    buscar_y_sumar_por_isrc_y_lanzamiento(tree, df_colaboraciones, config['invalid_values'])


if __name__ == '__main__':
    titulo = "Agrupación y Unificación de obras"
    autor = "Alioth Musule A."

    color_rojo = "\033[31m"
    color_verde = "\033[32m"
    color_reset = "\033[0m"

    print(f"{color_rojo}╔═════════════════════════════════════════╗{color_reset}")
    print(f"{color_rojo}║{color_verde}  ██████████████████████████████████████ {color_reset}")
    print(f"{color_rojo}║{color_verde}  ██  {color_reset}{titulo} ")
    print(f"{color_rojo}║{color_verde}  ██████████████████████████████████████ {color_reset}")
    print(f"{color_rojo}╚═════════════════════════════════════════╝{color_reset}")
    print(f"                                Hecho por {autor}")
    
    main()  # Usa el archivo predeterminado
