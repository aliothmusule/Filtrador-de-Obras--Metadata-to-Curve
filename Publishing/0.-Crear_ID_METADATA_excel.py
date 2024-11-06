import pandas as pd
import random
import hashlib

# Ruta del archivo de Excel
file_path = 'METADATA CENTRAL.xlsx'

# Cargar el archivo de Excel, especificando la fila del encabezado
try:
    df = pd.read_excel(file_path, header=1)  # Fila 2 como encabezado (índice 1)
except FileNotFoundError:
    print("Archivo no encontrado. Por favor, asegúrate de que 'METADATA CENTRAL.xlsx' está en el directorio correcto.")
    exit()

# Función para generar el ID único como un hash MD5 completo
def generar_id_hash(row):
    # Generar un identificador base con valores y números aleatorios
    base_id = f"{random.randint(100000, 999999)}-{row['Title']}{row['Author']}{row['Last Name']}{row['%']}-{random.randint(100000, 999999)}"
    
    # Crear el hash MD5 del base_id completo
    id_hash = hashlib.md5(base_id.encode()).hexdigest()
    return id_hash

# Menú interactivo
while True:
    print("\nOpciones:")
    print("1. Generar ID hash en toda la columna 'ID IDENTIFICADOR' (sin sobrescribir datos existentes)")
    print("2. Generar ID hash en filas específicas (sin sobrescribir datos existentes)")
    print("3. Sobrescribir todos los ID en toda la columna 'ID IDENTIFICADOR'")
    print("4. Sobrescribir ID en filas específicas")
    print("5. Salir")

    opcion = input("Elige una opción (1, 2, 3, 4 o 5): ")

    if opcion == "1":
        # Generar ID hash para toda la columna desde la fila 3 si la celda está vacía
        df['ID IDENTIFICADOR'] = df.apply(
            lambda row: generar_id_hash(row) if pd.isna(row['ID IDENTIFICADOR']) else row['ID IDENTIFICADOR'], axis=1
        )
        print("IDs hash generados para toda la columna desde la fila 3 en adelante, sin sobrescribir datos existentes.")

    elif opcion == "2":
        filas = input("Introduce los números de fila separados por comas (ejemplo: 3,5,7): ")
        filas = [int(fila.strip()) - 3 for fila in filas.split(",") if fila.strip().isdigit()]  # Convertir a índices (fila - 3)
        
        # Generar ID hash solo en las filas especificadas que están vacías en 'ID IDENTIFICADOR'
        for fila in filas:
            if fila >= 0 and fila < len(df):  # Verificar que esté dentro del rango y a partir del índice ajustado
                if pd.isna(df.at[fila, 'ID IDENTIFICADOR']):  # Solo generar ID si la celda está vacía
                    df.at[fila, 'ID IDENTIFICADOR'] = generar_id_hash(df.iloc[fila])
                    print(f"ID hash generado para la fila {fila + 3}.")
                else:
                    print(f"La fila {fila + 3} ya tiene un ID asignado y no fue sobreescrita.")
            else:
                print(f"Advertencia: La fila {fila + 3} está fuera del rango válido.")

    elif opcion == "3":
        # Sobrescribir todos los ID en toda la columna
        df['ID IDENTIFICADOR'] = df.apply(generar_id_hash, axis=1)
        print("Todos los IDs en la columna 'ID IDENTIFICADOR' han sido sobrescritos.")

    elif opcion == "4":
        filas = input("Introduce los números de fila separados por comas (ejemplo: 3,5,7): ")
        filas = [int(fila.strip()) - 3 for fila in filas.split(",") if fila.strip().isdigit()]  # Convertir a índices (fila - 3)
        
        # Sobrescribir ID en filas específicas
        for fila in filas:
            if fila >= 0 and fila < len(df):  # Verificar que esté dentro del rango y a partir del índice ajustado
                df.at[fila, 'ID IDENTIFICADOR'] = generar_id_hash(df.iloc[fila])
                print(f"ID hash sobrescrito para la fila {fila + 3}.")
            else:
                print(f"Advertencia: La fila {fila + 3} está fuera del rango válido.")

    elif opcion == "5":
        print("Saliendo del programa.")
        break
    else:
        print("Opción no válida. Intenta de nuevo.")

# Guardar el archivo modificado
output_path = 'METADATA CENTRAL_HASH.xlsx'
df.to_excel(output_path, index=False)
print(f"Archivo guardado como '{output_path}'.")
