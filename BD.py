import pandas as pd
import os
import glob

def cargar_bd_obras():
    """Carga o crea el archivo 'BD_OBRAS.xlsx' con las columnas especificadas."""
    columnas = [
        'id_curve', '#', 'ISRC', 'Lanzamiento', 'Titulo', 'Autor', '%', 'MLC', 'ISWC', 'USA (BMI-ASCAP)', 'WORK ID', 'Harry Fox', 
        'MEXICO (SACM)', 'GUATEMALA (AEI)', 'COLOMBIA (SAYCO)', 'ACINPRO analogo', 
        'ACINPRO digital', 'ARGENTINA (SADAIC)', 'BRASIL', 'ESPAÑA SGAE'
    ]
    
    if os.path.exists('BD_OBRAS.xlsx'):
        df_bd = pd.read_excel('BD_OBRAS.xlsx')
        print("Archivo BD_OBRAS.xlsx cargado exitosamente.")
    else:
        df_bd = pd.DataFrame(columns=columnas)
        print("Archivo BD_OBRAS.xlsx creado exitosamente.")
    return df_bd

def verificar_duplicados(df_bd, nuevo_registro):
    """Verifica si el nuevo registro ya existe en BD_OBRAS para evitar duplicados (ignora id_curve y '#')."""
    return (
        (df_bd['ISRC'] == nuevo_registro['ISRC']) & 
        (df_bd['Titulo'] == nuevo_registro['Titulo']) & 
        (df_bd['Lanzamiento'] == nuevo_registro['Lanzamiento'])
    ).any()

def agregar_datos_a_bd(df_nuevos, df_bd):
    """Agrega datos sin duplicados e ignora las columnas 'id_curve' y '#' en la comparación, luego asigna 'id_curve' autoincremental."""
    
    # Selección de columnas necesarias
    columnas_requeridas = [
        'ISRC', 'Lanzamiento', 'Titulo', 'Autor', '%',
        'MLC', 'ISWC', 'USA (BMI-ASCAP)', 'WORK ID', 'Harry Fox', 'MEXICO (SACM)',
        'GUATEMALA (AEI)', 'COLOMBIA (SAYCO)', 'ACINPRO analogo', 'ACINPRO digital',
        'ARGENTINA (SADAIC)', 'BRASIL', 'ESPAÑA SGAE'
    ]
    
    # Filtrar solo las columnas necesarias
    df_nuevos = df_nuevos[columnas_requeridas]
    
    # Verificar duplicados con las columnas de comparación necesarias
    columnas_comparacion = [col for col in columnas_requeridas if col in df_bd.columns]
    nuevos_registros = df_nuevos[~df_nuevos[columnas_comparacion].apply(lambda row: verificar_duplicados(df_bd, row), axis=1)]
    
    if nuevos_registros.empty:
        print("No hay nuevos registros que agregar.")
        return df_bd, False  # Indicador de que no se agregó ningún registro

    # Asignar ID autoincremental en la primera columna
    max_id = df_bd['id_curve'].max() if not df_bd.empty else 0
    nuevos_registros.insert(0, 'id_curve', range(int(max_id) + 1, int(max_id) + 1 + len(nuevos_registros)))
    
    # Añadir columna '#' en blanco
    if '#' not in nuevos_registros.columns:
        nuevos_registros.insert(1, '#', '')  # Columna '#' en blanco

    # Concatenar y actualizar BD_OBRAS
    df_bd = pd.concat([df_bd, nuevos_registros], ignore_index=True)
    print(f"{len(nuevos_registros)} nuevos registros preparados para agregar a BD_OBRAS.")
    return df_bd, True  # Indicador de que se agregaron registros nuevos

def guardar_bd(df_bd):
    """Guarda el DataFrame en 'BD_OBRAS.xlsx'."""
    with pd.ExcelWriter('BD_OBRAS.xlsx', engine='openpyxl') as writer:
        df_bd.to_excel(writer, index=False)
    print("Archivo BD_OBRAS.xlsx actualizado exitosamente.")

def cargar_datos_unificados():
    """Carga los datos de la hoja 'Unificación_Obras' de 'Agrupacion_y_Unificacion_obras.xlsx'."""
    archivo_unificado = 'Agrupacion_y_Unificacion_obras.xlsx'
    if not os.path.exists(archivo_unificado):
        print("No se encontró el archivo 'Agrupacion_y_Unificacion_obras.xlsx'.")
        return None

    try:
        df_unificacion = pd.read_excel(archivo_unificado, sheet_name='Unificación_Obras')
        print(f"Datos de la hoja 'Unificación_Obras' en {archivo_unificado} cargados exitosamente.")
        return df_unificacion
    except Exception as e:
        print(f"Error al cargar la hoja 'Unificación_Obras': {e}")
        return None

def cargar_datos_individuales():
    """Busca y carga archivos que comienzan con 'obras_compositor_100' en la misma ruta del código para seleccionar una obra individual."""
    archivos = glob.glob('./obras_compositor_100*.xlsx')
    if not archivos:
        print("No se encontraron archivos de obras individuales.")
        return None

    print("Archivos de obras individuales disponibles:")
    for idx, archivo in enumerate(archivos, start=1):
        print(f"{idx}. {archivo}")
    
    seleccion = input("Seleccione el número del archivo que desea agregar o 0 para cancelar: ")
    try:
        seleccion = int(seleccion)
        if seleccion == 0:
            return None
        archivo_seleccionado = archivos[seleccion - 1]
        df_individual = pd.read_excel(archivo_seleccionado)
        print(f"Datos de {archivo_seleccionado} cargados exitosamente.")
        return df_individual
    except (ValueError, IndexError):
        print("Selección inválida.")
        return None

def modificar_registro(df_bd):
    """Permite modificar un registro específico buscando por 'id_curve'."""
    try:
        id_curve = int(input("Ingrese el 'id_curve' del registro que desea modificar: "))
        if id_curve not in df_bd['id_curve'].values:
            print("El 'id_curve' no existe.")
            return df_bd  # Retorna sin cambios si el id_curve no existe
        
        registro = df_bd.loc[df_bd['id_curve'] == id_curve]
        print("\nRegistro encontrado:")
        print(registro)
        
        # Mostrar opciones de columna para modificar
        print("\nColumnas disponibles para modificar:")
        for i, col in enumerate(df_bd.columns, start=1): 
            print(f"{i}. {col}")
        
        col_idx = int(input("Seleccione el número de la columna que desea modificar: ")) - 1
        if col_idx < 0 or col_idx >= len(df_bd.columns):
            print("Selección de columna inválida.")
            return df_bd

        col_name = df_bd.columns[col_idx]
        nuevo_valor = input(f"Ingrese el nuevo valor para '{col_name}': ")
        
        # Modificar el registro
        df_bd.loc[df_bd['id_curve'] == id_curve, col_name] = nuevo_valor
        print("\nRegistro modificado exitosamente. Resultado final:")
        print(df_bd.loc[df_bd['id_curve'] == id_curve])

        return df_bd
    except ValueError:
        print("Entrada inválida.")
        return df_bd

def main():
    while True:
        print("\nMenu:")
        print("1. Agregar datos unificados")
        print("2. Agregar obra de compositor individual")
        print("3. Modificar un registro")
        print("4. Salir")
        
        opcion = input("Seleccione una opción: ")

        if opcion == '1':
            df_bd = cargar_bd_obras()
            df_unificados = cargar_datos_unificados()
            if df_unificados is not None:
                df_bd_actualizado, registros_agregados = agregar_datos_a_bd(df_unificados, df_bd)
                if registros_agregados:
                    guardar_bd(df_bd_actualizado)  # Solo guarda si hubo registros nuevos

        elif opcion == '2':
            df_bd = cargar_bd_obras()
            df_individual = cargar_datos_individuales()
            if df_individual is not None:
                df_bd_actualizado, registros_agregados = agregar_datos_a_bd(df_individual, df_bd)
                if registros_agregados:
                    guardar_bd(df_bd_actualizado)  # Solo guarda si hubo registros nuevos

        elif opcion == '3':
            df_bd = cargar_bd_obras()
            df_bd_modificado = modificar_registro(df_bd)
            guardar_bd(df_bd_modificado)  # Guardar después de modificar

        elif opcion == '4':
            break

        else:
            print("Opción inválida. Intente de nuevo.")

if __name__ == '__main__':
    main()
