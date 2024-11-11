import pandas as pd
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
        
        # Solicitar al usuario la ruta del archivo local y la URL del archivo remoto
        config["archivo_local"] = input("Ingresa la ruta del archivo local (Excel): ")
        config["archivo_remoto"] = input("Ingresa la URL del archivo remoto (Google Sheets o Excel): ")
        
        # Guardar la configuración en config.json para futuros usos
        with open('config1.json', 'w') as config_file:
            json.dump(config, config_file, indent=4)
        print("[INFO] Configuración guardada en 'config.json'.")
        
        return config

# Función para cargar archivos Excel
def cargar_excel(ruta, tipo='local'):
    try:
        df = pd.read_excel(ruta, header=1)
        df.fillna('', inplace=True)
        print(f"[SUCCESS] Archivo Excel '{tipo}' cargado exitosamente.")
        return df
    except FileNotFoundError:
        print(f"[ERROR] No se encontró el archivo Excel '{ruta}'.")
        exit(1)
    except Exception as e:
        print(f"[ERROR] Error al cargar el archivo Excel '{tipo}': {e}")
        exit(1)

# Función para descargar y cargar el archivo remoto
def cargar_excel_remoto(url):
    try:
        if 'docs.google.com' in url:
            url_excel = url.replace("/edit?usp=sharing", "/export?format=xlsx")
        else:
            url_excel = url  # Asume que es una URL directa a un archivo Excel

        response = requests.get(url_excel)
        if response.status_code != 200:
            print("[ERROR] No se pudo descargar el archivo remoto. Verifica la URL.")
            exit(1)

        with open('archivo_remoto.xlsx', 'wb') as f:
            f.write(response.content)

        print("[SUCCESS] Archivo remoto descargado y guardado como 'archivo_remoto.xlsx'.")
        return cargar_excel('archivo_remoto.xlsx', tipo='remoto')
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Error al descargar el archivo remoto: {e}")
        exit(1)

# Función para validar si una fila es válida (cuando Artist, ISRC, UPC y ID IDENTIFICADOR están vacíos)
def es_registro_valido(row):
    artist = str(row.get("Artist", '')).strip()
    isrc = str(row.get("ISRC", '')).strip()
    upc = str(row.get("UPC", '')).strip()
    id_identificador = str(row.get("ID IDENTIFICADOR", '')).strip()

    # Si todos los campos están vacíos, el registro es inválido
    if not artist and not isrc and not upc and not id_identificador:
        return False
    return True

# Función para comparar datos y generar reporte
def comparar_datos(df_local, df_remoto):
    id_col = 'ID IDENTIFICADOR'
    title_col = 'Title'
    diferencias = []
    nuevos_registros = []
    registros_eliminados = []  # Nueva lista para los eliminados

    columnas_ignorar = ['Release Date']

    try:
        local_ids = df_local.groupby(id_col)
        remoto_ids = df_remoto.groupby(id_col)

        print("[INFO] Iniciando comparación de datos...")

        # Comparar registros del archivo remoto contra el local
        for id_identificador, grupo_remoto in remoto_ids:
            grupo_remoto = grupo_remoto[grupo_remoto.apply(es_registro_valido, axis=1)]

            for _, row_remoto in grupo_remoto.iterrows():
                id_remoto = str(row_remoto.get(id_col, '')).strip()
                title_remoto = str(row_remoto.get(title_col, '')).strip()

                if not id_remoto and (row_remoto["Artist"] or row_remoto["ISRC"] or row_remoto["UPC"]):
                    nuevos_registros.append({k: v for k, v in row_remoto.items() if k not in columnas_ignorar})
                    print("[NUEVO SIN IDENTIFICAR] Registro con datos parciales agregado como nuevo.")
                    continue

                if id_remoto in local_ids.groups:
                    grupo_local = local_ids.get_group(id_remoto)
                    diferencia_encontrada = False

                    for _, row_local in grupo_local.iterrows():
                        diferencias_registro = {"Title": title_remoto}
                        for columna in df_local.columns:
                            if columna in columnas_ignorar:
                                continue
                            valor_local = str(row_local.get(columna, '')).strip()
                            valor_remoto = str(row_remoto.get(columna, '')).strip()
                            
                            if valor_local != valor_remoto:
                                diferencias_registro[columna] = {
                                    "local": valor_local,
                                    "remoto": valor_remoto
                                }
                                diferencia_encontrada = True

                        if diferencia_encontrada:
                            diferencias.append({
                                id_col: id_remoto,
                                "Title": title_remoto,
                                "diferencias": diferencias_registro
                            })
                            print(f"[DIFERENCIA] ID '{id_remoto}' tiene datos diferentes.")
                else:
                    nuevos_registros.append({k: v for k, v in row_remoto.items() if k not in columnas_ignorar})
                    print(f"[NUEVO] ID '{id_remoto}' es un nuevo registro.")

        # Identificar registros eliminados (presentes en local pero no en remoto)
        for id_identificador, grupo_local in local_ids:
            if id_identificador not in remoto_ids.groups:
                for _, row_local in grupo_local.iterrows():
                    registros_eliminados.append({k: v for k, v in row_local.items() if k not in columnas_ignorar})
                print(f"[ELIMINADO] ID '{id_identificador}' no se encontró en el archivo remoto.")

        print("[INFO] Comparación de datos finalizada.")
    except KeyError as e:
        print(f"[ERROR] No se encontró la columna clave '{id_col}' en uno de los archivos: {e}")
        exit(1)
    except Exception as e:
        print(f"[ERROR] Error durante la comparación de datos: {e}")
        exit(1)

    return diferencias, nuevos_registros, registros_eliminados

# Función para guardar los resultados actuales en 'resultado_actual.json' y el historial en 'historial.log'
def guardar_resultados(diferencias, nuevos_registros, registros_eliminados):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    resultado = {
        "timestamp": timestamp,
        "diferencias": diferencias,
        "nuevos_registros": nuevos_registros,
        "registros_eliminados": registros_eliminados
    }

    # Guardar el resultado actual en 'resultado_actual.json'
    with open('resultado_actual.json', 'w', encoding='utf-8') as resultado_file:
        json.dump(resultado, resultado_file, ensure_ascii=False, indent=4)
    print("[INFO] Resultado actual guardado en 'resultado_actual.json'.")

    # Agregar el registro al historial en 'historial.log'
    with open('historial.log', 'a', encoding='utf-8') as historial_file:
        historial_file.write(json.dumps(resultado, ensure_ascii=False, indent=4) + '\n')
    print("[INFO] Registro agregado al historial en 'historial.log'.")

# Función principal
def main():
    print("[INFO] Iniciando el proceso...")
    config = cargar_configuracion()

    archivo_local = config.get("archivo_local")
    archivo_remoto_url = config.get("archivo_remoto")
    print(f"archivo_local: {archivo_local}, archivo_remoto_url: {archivo_remoto_url}")

    if not archivo_local or not archivo_remoto_url:
        print("[ERROR] La configuración no contiene los archivos necesarios.")
        exit(1)

    # Cargar archivos
    df_local = cargar_excel(archivo_local)
    df_remoto = cargar_excel_remoto(archivo_remoto_url)

    # Comparar datos
    diferencias, nuevos_registros, registros_eliminados = comparar_datos(df_local, df_remoto)

    # Guardar resultados
    guardar_resultados(diferencias, nuevos_registros, registros_eliminados)

    # Variables para el conteo de registros
    total_diferencias = len(diferencias)
    total_nuevos = len(nuevos_registros)
    total_eliminados = len(registros_eliminados)

    # Imprimir resultados en consola
    print("[INFO] Proceso completado exitosamente.")
    print(f"Total de diferencias: {total_diferencias}")
    print(f"Total de nuevos registros: {total_nuevos}")
    print(f"Total de registros eliminados: {total_eliminados}")
    print(f"Verifique los datos actuales en resultado_actual.json")

if __name__ == "__main__":
    main()
