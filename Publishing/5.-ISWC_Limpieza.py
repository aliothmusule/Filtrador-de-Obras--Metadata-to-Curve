import pandas as pd
from tqdm import tqdm
from colorama import Fore, Style, init
import time

# Inicializar colorama
init(autoreset=True)

# Configuración de archivos
archivo_origen = 'METADATA_PUBLISHING_U_ISWC.xlsx'
archivo_destino = 'METADATA_PUBLISHING_U_ISWC_LIMPIADO.xlsx'

# Mensaje inicial
print(f"{Fore.CYAN}Iniciando el proceso de limpieza de datos...{Style.RESET_ALL}\n")

try:
    # Cargar los datos desde el archivo generado
    print(f"{Fore.YELLOW}Cargando archivo de origen: {archivo_origen}...{Style.RESET_ALL}")
    df = pd.read_excel(archivo_origen, sheet_name='Unificados_Por_ISWC')
    time.sleep(1)  # Simular un proceso de carga

    print(f"{Fore.GREEN}Archivo cargado exitosamente.{Style.RESET_ALL}\n")

    # Función para limpiar los valores específicos en las columnas de interés
    def limpiar_valores(columnas, df):
        for columna in tqdm(columnas, desc=f"{Fore.MAGENTA}Procesando columnas{Style.RESET_ALL}", colour="magenta"):
            # Agregar barra de progreso
            time.sleep(0.5)  # Simulación de proceso
            df[columna] = df[columna].apply(
                lambda x: "100" if str(x) in {"100•100.0", "100.0•100"} else x
            )
        return df

    # Columnas a revisar
    columnas_revisar = ['%', 'Contrato']

    # Aplicar la limpieza
    print(f"{Fore.YELLOW}Iniciando la limpieza de las columnas seleccionadas...{Style.RESET_ALL}")
    df_limpio = limpiar_valores(columnas_revisar, df)

    # Guardar el archivo resultante
    print(f"{Fore.YELLOW}Guardando el archivo limpio: {archivo_destino}...{Style.RESET_ALL}")
    with pd.ExcelWriter(archivo_destino, engine='xlsxwriter') as writer:
        df_limpio.to_excel(writer, index=False, sheet_name='Unificados_Por_ISWC_Limpio')
    
    print(f"{Fore.GREEN}Archivo limpio '{archivo_destino}' creado exitosamente.{Style.RESET_ALL}")

except FileNotFoundError:
    print(f"{Fore.RED}Error: El archivo {archivo_origen} no se encontró. Verifica la ruta y el nombre.{Style.RESET_ALL}")

except Exception as e:
    print(f"{Fore.RED}Error inesperado: {e}{Style.RESET_ALL}")

else:
    print(f"{Fore.CYAN}\nProceso completado con éxito.{Style.RESET_ALL}")
finally:
    print(f"{Fore.BLUE}Terminando el programa...{Style.RESET_ALL}")
