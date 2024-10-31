import pandas as pd
import os

# Archivo de destino
archivo_nuevo = 'METADATA_PUBLISHING_UNIFICADO.xlsx'

# Conjunto de ISRC inválidos
isrc_invalidos = {"Sin Codigo", '', ' '}

# Colores para los grupos
colores_visibles = [
    "#FFEBCC", "#FFF2CC", "#E6FFCC", "#CCFFE6", "#CCE6FF", "#E6CCFF", "#FFD1DC", "#FFCCCC",
    "#CCFFEB", "#CCE5FF", "#E0FFE6", "#FFFFCC", "#FFCCE5", "#FFEECC", "#D6E6FF", "#E6FFFA",
    "#FFDAB9", "#FFDFC4", "#E6F7FF", "#FFF9CC", "#FFF1E0", "#E8FFCC"
]

def asignar_color_grupo(grupo_id):
    return colores_visibles[(grupo_id - 1) % len(colores_visibles)]

class TreeNode:
    def __init__(self):
        self.records = []
        self.children = {}

class TitleTree:
    def __init__(self):
        self.root = TreeNode()

    def insert(self, key, record, isrc_invalido):
        if isrc_invalido:
            # Insertar como registro individual en lugar de unificar
            self.root.records.append(record)
        else:
            node = self.root
            if key not in node.children:
                node.children[key] = TreeNode()
            node.children[key].records.append(record)

    def get_groups(self):
        groups = []
        # Incluir cada registro con ISRC inválido como grupo separado
        for record in self.root.records:
            groups.append([record])
        for node in self.root.children.values():
            if node.records:
                groups.append(node.records)
        return groups

# Función para unificar registros utilizando el árbol
def unificar_registros_con_arbol(tree, columnas_comparacion):
    print("Iniciando unificación de registros en el árbol...")
    registros_unificados = []

    for grupo in tree.get_groups():
        if len(grupo) == 1:
            registros_unificados.append(grupo[0])
            continue

        grupo_unificado = grupo[0].copy()
        porcentaje_coincidencia = 0
        
        for registro in grupo[1:]:
            for columna in columnas_comparacion:
                valor_unificado = str(grupo_unificado[columna]) if pd.notna(grupo_unificado[columna]) else ""
                valor_actual = str(registro[columna]) if pd.notna(registro[columna]) else ""
                
                if valor_unificado == valor_actual:
                    porcentaje_coincidencia += 10
                elif valor_actual:
                    valores = valor_unificado.split(',') if valor_unificado else []
                    valores.append(valor_actual)
                    grupo_unificado[columna] = ','.join(valores)

        # Unificar "Autor", "Apellido", "%", y "Contrato" sin eliminar duplicados
        for columna in ['Autor', 'Apellido', '%', 'Contrato']:
            valores_columna = []
            for reg in grupo:
                if pd.notna(reg[columna]):
                    valores_columna.append(str(reg[columna]))
            grupo_unificado[columna] = ','.join(valores_columna)

        grupo_unificado['Porcentaje_Coincidencia'] = porcentaje_coincidencia
        registros_unificados.append(grupo_unificado)
        print(f"   Grupo con ISRC {grupo[0]['ISRC']} y Duración {grupo[0]['Duración ']} unificado con {len(grupo)} registros.")

    print("Unificación completa en el árbol.")
    return pd.DataFrame(registros_unificados)

# Cargar y procesar las hojas 'Grupos 100%' y 'Grupos < 100%'
columnas_comparacion = ['MLC', 'MEXICO (SACM)', 'ISWC', 'Autor', 'Apellido', '%', 'Contrato']
columnas_clave = ['ISRC', 'Duración ']

# Cargar datos y crear archivo nuevo
archivo_origen = 'METADATA_PUBLISHING_SEPARADO.xlsx'
if os.path.exists(archivo_origen):
    print("Cargando datos desde el archivo original...")
    df_100 = pd.read_excel(archivo_origen, sheet_name='Grupos 100%')
    df_menor_100 = pd.read_excel(archivo_origen, sheet_name='Grupos < 100%')
    print("Datos cargados correctamente.")
    
    total_registros_originales = len(df_100) + len(df_menor_100)
    print(f"Total de registros en 'Grupos 100%' y 'Grupos < 100%': {total_registros_originales}")

    print("Insertando registros en el árbol...")
    tree = TitleTree()
    for _, row in pd.concat([df_100, df_menor_100], ignore_index=True).iterrows():
        isrc = row['ISRC']
        duracion = row['Duración ']
        isrc_invalido = isrc in isrc_invalidos
        key = (isrc, duracion) if not isrc_invalido else None
        tree.insert(key, row, isrc_invalido)
    print("Todos los registros insertados en el árbol.")

    df_unificado = unificar_registros_con_arbol(tree, columnas_comparacion)

    total_registros_unificados = len(df_unificado)
    print(f"Total de registros en 'Unificados': {total_registros_unificados}")

    print("Guardando resultados en un archivo nuevo y aplicando colores...")
    with pd.ExcelWriter(archivo_nuevo, engine='xlsxwriter') as writer:
        workbook = writer.book
        df_unificado.to_excel(writer, index=False, sheet_name='Unificados')
        worksheet = writer.sheets['Unificados']
        
        for row_num, grupo in enumerate(df_unificado['Grupo Contador'], start=1):
            color = asignar_color_grupo(grupo)
            cell_format = workbook.add_format({'bg_color': color})
            worksheet.set_row(row_num, None, cell_format)

    print(f"Archivo nuevo '{archivo_nuevo}' creado exitosamente, hoja de 'Unificados' coloreada.")
else:
    print(f"El archivo '{archivo_origen}' no existe.")
