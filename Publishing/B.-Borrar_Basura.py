import os

# Ruta de la carpeta
ruta_carpeta = './basura'

def borrar_archivos(carpeta):
    # Listar todos los archivos en la carpeta especificada
    for archivo in os.listdir(carpeta):
        archivo_path = os.path.join(carpeta, archivo)
        try:
            # Verificar si es un archivo (no una carpeta) y eliminarlo
            if os.path.isfile(archivo_path):
                os.remove(archivo_path)
                print(f"Archivo eliminado: {archivo_path}")
            else:
                print(f"Omitiendo directorio: {archivo_path}")
        except Exception as e:
            print(f"No se pudo eliminar {archivo_path}. Error: {e}")

# Ejecutar la función para borrar los archivos
borrar_archivos(ruta_carpeta)
