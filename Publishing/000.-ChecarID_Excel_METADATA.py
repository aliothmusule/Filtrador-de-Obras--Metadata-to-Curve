import os
import json
import requests
import pandas as pd
from datetime import datetime

# Función para cargar el archivo de configuración
def cargar_configuracion():
    try:
        with open('config1.json', 'r') as config_file:
            config = json.load(config_file)
        print("[SUCCESS] Archivo de configuración cargado exitosamente.")
        return config
    except (FileNotFoundError, json.JSONDecodeError):
        print("[WARNING] No se encontró el archivo 'config1.json' o está vacío.")
        config = {}
        
        # Solicitar al usuario la URL del archivo remoto
        config["archivo_remoto"] = input("Ingresa la URL del archivo remoto (Google Sheets o Excel): ")
        
        # Guardar la configuración en config1.json para futuros usos
        with open('config1.json', 'w') as config_file:
            json.dump(config, config_file, indent=4)
        print("[INFO] Configuración guardada en 'config1.json'.")
        
        return config

# Función para descargar y guardar siempre el archivo remoto en la ruta especificada
def descargar_y_guardar_excel(url, nombre_archivo):
    if 'docs.google.com' in url:
        url_excel = url.replace("/edit?usp=sharing", "/export?format=xlsx")
    else:
        url_excel = url

    if os.path.exists(nombre_archivo):
        os.remove(nombre_archivo)
        print(f"[INFO] Archivo existente '{nombre_archivo}' eliminado.")

    try:
        response = requests.get(url_excel)
        if response.status_code != 200:
            print("[ERROR] No se pudo descargar el archivo remoto. Verifica la URL.")
            exit(1)

        with open(nombre_archivo, 'wb') as f:
            f.write(response.content)
        print(f"[SUCCESS] Archivo remoto descargado y guardado como '{nombre_archivo}'.")
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Error al descargar el archivo remoto: {e}")
        exit(1)

# Función para cargar archivos Excel en un DataFrame
def cargar_excel(nombre_archivo):
    try:
        df = pd.read_excel(nombre_archivo, header=1)
        
        # Convertir la columna Release Date a string para evitar problemas de JSON
        if 'Release Date' in df.columns:
            df['Release Date'] = df['Release Date'].astype(str)
            
        df.fillna(value=pd.NA, inplace=True)
        print(f"[SUCCESS] Archivo '{nombre_archivo}' cargado exitosamente.")
        return df
    except FileNotFoundError:
        print(f"[ERROR] No se encontró el archivo '{nombre_archivo}'.")
        exit(1)
    except Exception as e:
        print(f"[ERROR] Error al cargar el archivo '{nombre_archivo}': {e}")
        exit(1)

# Función para verificar eliminados y modificados
def verificar_eliminados_y_modificados(df_local, df_remoto):
    id_col = 'ID IDENTIFICADOR'
    eliminados = []
    modificados = []

    # Crear conjuntos de IDs para facilitar la comparación
    ids_local = set(df_local[id_col])
    ids_remoto = set(df_remoto[id_col])

    # Identificar registros eliminados (presentes en local pero no en remoto)
    eliminados_ids = ids_local - ids_remoto
    eliminados = df_local[df_local[id_col].isin(eliminados_ids)].map(str).to_dict(orient='records')
    print(f"[INFO] Registros eliminados encontrados: {len(eliminados)}")

    # Identificar registros modificados (compara filas excluyendo la columna identificador)
    for _, row_local in df_local.iterrows():
        id_local = row_local[id_col]
        
        # Si el ID está en ambos, se procede a verificar modificaciones
        if id_local in ids_remoto:
            # Obtener la fila correspondiente en remoto
            row_remoto = df_remoto[df_remoto[id_col] == id_local].iloc[0]
            diferencias = {}
            for columna in df_local.columns:
                if columna == id_col:  # Ignorar columna de identificador
                    continue
                valor_local = str(row_local[columna]).strip()
                valor_remoto = str(row_remoto[columna]).strip()
                
                if valor_local != valor_remoto:
                    diferencias[columna] = {"local": valor_local, "remoto": valor_remoto}
            
            if diferencias:
                modificados.append({
                    id_col: id_local,
                    "diferencias": diferencias
                })

    print(f"[INFO] Registros modificados encontrados: {len(modificados)}")
    return eliminados, modificados

# Función para guardar los resultados en un archivo JSON
def guardar_resultados(eliminados, modificados):
    resultado = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "eliminados": eliminados,
        "modificados": modificados
    }

    try:
        with open('resultado_verificacion.json', 'w', encoding='utf-8') as resultado_file:
            json.dump(resultado, resultado_file, ensure_ascii=False, indent=4)
        print("[SUCCESS] Resultados guardados en 'resultado_verificacion.json'.")
    except Exception as e:
        print(f"[ERROR] No se pudo guardar el archivo 'resultado_verificacion.json': {e}")
        exit(1)

# Función principal
def main():
    print("[INFO] Iniciando el proceso...")
    config = cargar_configuracion()

    archivo_remoto_url = config.get("archivo_remoto")
    archivo_local = "METADATA CENTRAL.xlsx"
    archivo_remoto = "archivo_remoto.xlsx"

    if not archivo_remoto_url:
        print("[ERROR] La configuración no contiene la URL del archivo remoto.")
        exit(1)

    # Descargar y guardar el archivo remoto en la misma ubicación, sobrescribiendo el existente
    descargar_y_guardar_excel(archivo_remoto_url, archivo_remoto)

    # Cargar archivos en DataFrames
    df_local = cargar_excel(archivo_local)
    df_remoto = cargar_excel(archivo_remoto)

    # Verificar eliminados y modificados
    eliminados, modificados = verificar_eliminados_y_modificados(df_local, df_remoto)

    # Guardar resultados en JSON
    guardar_resultados(eliminados, modificados)

    print("[INFO] Proceso completado exitosamente.")

if __name__ == "__main__":
    main()
