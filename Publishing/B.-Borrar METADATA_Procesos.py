import os

# Lista de archivos específicos a eliminar en la misma ubicación que este script
archivos_a_eliminar = [
    "METADATA_PUBLISHING_SEPARADO.xlsx",
    "METADATA_PUBLISHING_COLOR.xlsx",
    "METADATA_PUBLISHING_U_ISWC.xlsx",
    "METADATA_PUBLISHING_UNIFICADO.xlsx"
]

# Obtener la ruta de la carpeta actual donde se ejecuta el script
ruta_carpeta = os.path.dirname(__file__)  # Obtiene la ubicación del script .py

def borrar_archivos_especificos(carpeta, archivos):
    # Recorrer la lista de archivos específicos a eliminar
    for archivo in archivos:
        archivo_path = os.path.join(carpeta, archivo)
        try:
            # Verificar si el archivo existe en la carpeta y eliminarlo
            if os.path.isfile(archivo_path):
                os.remove(archivo_path)
                print(f"Archivo eliminado: {archivo_path}")
            else:
                print(f"Archivo no encontrado u omitido: {archivo_path}")
        except Exception as e:
            print(f"No se pudo eliminar {archivo_path}. Error: {e}")

# Ejecutar la función para borrar los archivos específicos en la misma ubicación del script
borrar_archivos_especificos(ruta_carpeta, archivos_a_eliminar)
