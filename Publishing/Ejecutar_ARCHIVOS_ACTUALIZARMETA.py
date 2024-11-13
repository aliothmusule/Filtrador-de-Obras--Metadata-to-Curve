
def main():

    # main.py
    import subprocess

    print("Iniciando proceso -Actualizar METADATA.")
    subprocess.run(['python', '0.2.-ACTUALIZAR_Cambiar_METADATA.py'])
    print("Archivo Actualizar METADATA realizado con exito.")
    subprocess.run(['python', '1.-Publishing.py'])
    print("Proceso 1.- Realizado correctamente.")
    subprocess.run(['python', '2.-separar_por_Porcentajes.py'])
    print("Proceso 2.- Realizado correctamente")
    subprocess.run(['python', '3.-Unificacion_Obras_Porcentajes.py'])
    print("Proceso 3 realizado con exito")
    subprocess.run(['python', '4.-Unificacion_ISWC.py'])
    print("Proceso 4.- Realizado con exito")
    subprocess.run(['python', '5.1.-[INDIVIDUAL]Buscar_Autor.py'])
    print("Proceso 5.1 Realizado con exito.")
    print("-------------------Finaliza codigo------------------------")

if __name__ == "__main__":
    main()