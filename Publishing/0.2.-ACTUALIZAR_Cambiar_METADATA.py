import os
import json
import requests
from datetime import datetime

# Función para cargar el archivo de configuración
def cargar_configuracion():
    try:
        with open('config1.json', 'r') as config_file:
            config = json.load(config_file)
        print("[SUCCESS] Archivo de configuración cargado exitosamente.")
        return config
    except (FileNotFoundError, json.JSONDecodeError):
        print("[WARNING] No se encontró el archivo 'config.json' o está vacío.")
        config = {}
        
        # Solicitar al usuario la URL del archivo remoto
        config["archivo_remoto"] = input("Ingresa la URL del archivo remoto (Google Sheets o Excel): ")
        
        # Guardar la configuración en config.json para futuros usos
        with open('config1.json', 'w') as config_file:
            json.dump(config, config_file, indent=4)
        print("[INFO] Configuración guardada en 'config.json'.")
        
        return config

# Función para mover el archivo METADATA CENTRAL existente a la carpeta 'basura' y renombrarlo
def mover_y_renombrar_a_basura(nombre_archivo):
    carpeta_basura = "basura"
    if not os.path.exists(carpeta_basura):
        os.makedirs(carpeta_basura)
        print("[INFO] Carpeta 'basura' creada.")
    
    # Verificar si el archivo existe y moverlo
    if os.path.exists(nombre_archivo):
        # Obtener fecha y hora actual para el nuevo nombre del archivo
        fecha_hora_actual = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_nuevo = f"METADATA CENTRAL_{fecha_hora_actual}.xlsx"
        archivo_destino = os.path.join(carpeta_basura, nombre_nuevo)
        
        # Mover y renombrar el archivo
        os.rename(nombre_archivo, archivo_destino)
        print(f"[SUCCESS] Archivo '{nombre_archivo}' movido y renombrado a '{archivo_destino}'.")

# Función para descargar y guardar el archivo remoto en la ruta especificada
def descargar_y_guardar_excel(url, nombre_archivo_descargado):
    # Convertir la URL de Google Sheets para descargar en formato Excel si es necesario
    if 'docs.google.com' in url:
        url_excel = url.replace("/edit?usp=sharing", "/export?format=xlsx")
    else:
        url_excel = url  # Asume que es una URL directa a un archivo Excel

    # Descargar el nuevo archivo
    try:
        response = requests.get(url_excel)
        if response.status_code != 200:
            print("[ERROR] No se pudo descargar el archivo remoto. Verifica la URL.")
            exit(1)

        # Guardar el archivo descargado con el nombre especificado en la misma ubicación
        with open(nombre_archivo_descargado, 'wb') as f:
            f.write(response.content)
        print(f"[SUCCESS] Archivo remoto descargado y guardado como '{nombre_archivo_descargado}'.")
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Error al descargar el archivo remoto: {e}")
        exit(1)

# Función principal
def main():
    print("[INFO] Iniciando el proceso... actualizando METADATA CENTRAL.xlsx")
    config = cargar_configuracion()

    archivo_remoto_url = config.get("archivo_remoto")
    archivo_local = "METADATA CENTRAL.xlsx"  # Nombre del archivo local existente
    archivo_descargado = "METADATA CENTRAL.xlsx"  # Nombre que se renombrará para el archivo descargado desde la URL.

    if not archivo_remoto_url:
        print("[ERROR] La configuración no contiene la URL del archivo remoto.")
        exit(1)

    # Mover el archivo local existente a la carpeta 'basura' y renombrarlo antes de descargar el nuevo
    mover_y_renombrar_a_basura(archivo_local)

    # Descargar y guardar el nuevo archivo en la misma ubicación con un nombre diferente
    descargar_y_guardar_excel(archivo_remoto_url, archivo_descargado)

    print("[INFO] Proceso completado exitosamente.")

if __name__ == "__main__":
    main()