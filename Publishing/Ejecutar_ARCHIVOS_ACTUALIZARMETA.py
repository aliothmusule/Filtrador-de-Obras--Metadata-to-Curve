import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from colorama import Fore, Style, init


##
##ARCHIVOS del 1 al 5.2
##
# Inicializar colorama para soportar colores en Windows
init()

def run_process(command, description):
    """Ejecuta un proceso externo con barra de progreso."""
    with tqdm(total=100, desc=description, bar_format="{l_bar}%s{bar}%s{r_bar}" % (Fore.CYAN, Fore.RESET)) as pbar:
        pbar.update(20)
        time.sleep(0.5)  # Simulación de carga
        subprocess.run(command)
        pbar.update(80)  # Completa la barra al finalizar
        pbar.close()
    print(Fore.GREEN + f"{description} completado con éxito." + Style.RESET_ALL)

def main():
    print(Fore.YELLOW + "-------------------INICIA CÓDIGO-----------------------" + Style.RESET_ALL)
    print(Fore.CYAN + "Iniciando proceso - Actualizar METADATA." + Style.RESET_ALL)

    # Procesos secuenciales
    run_process(['python', '0.2.-ACTUALIZAR_Cambiar_METADATA.py'], "Actualizando METADATA")
    run_process(['python', '1.-Publishing.py'], "Proceso 1 - Publicando")
    run_process(['python', '2.-separar_por_Porcentajes.py'], "Proceso 2 - Separación por Porcentajes")
    run_process(['python', '3.-Unificacion_Obras_Porcentajes.py'], "Proceso 3 - Unificación de Obras por Porcentajes")
    run_process(['python', '4.-Unificacion_ISWC.py'], "Proceso 4 - Unificación de ISWC")
    run_process(['python', '5.-ISWC_Limpieza.py'], "Proceso 5 - LIMPIEZA PORCENTAJES de obras")

    # Procesos paralelos
    print(Fore.MAGENTA + "Iniciando procesos 5.1 y 5.2 en paralelo..." + Style.RESET_ALL)
    tasks = {
        "Proceso 6.2 - Buscar Autor (U_ISWC_Individual)": ['python', '5.2.-[U_ISWC_INDIVIDUAL]Buscar_Autor.py']
    }

    ''' tasks = {
        "Proceso 6.1 - Buscar Autor (Individual)": ['python', '5.1.-[INDIVIDUAL]Buscar_Autor.py'],
        "Proceso 6.2 - Buscar Autor (U_ISWC_Individual)": ['python', '5.2.-[U_ISWC_INDIVIDUAL]Buscar_Autor.py']
    }
    '''
    # Ejecutar procesos en paralelo
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = {executor.submit(subprocess.run, cmd): desc for desc, cmd in tasks.items()}
        for future in as_completed(futures):
            desc = futures[future]
            print(Fore.GREEN + f"{desc} completado con éxito en paralelo." + Style.RESET_ALL)

    print(Fore.YELLOW + "-------------------Finaliza Código------------------------" + Style.RESET_ALL)

if __name__ == "__main__":
    main()
