
import pandas as pd

# Cargar el archivo Excel
archivo_entrada = "archivo_original.xlsx"
archivo_salida = "archivo_transformado.xlsx"

data = pd.read_excel(archivo_entrada)

# Asegurar que las columnas clave están presentes
columnas_requeridas = ['REGISTRO', 'TITULO DE OBRA', 'CALIDAD', 'PARTICIPANTES', 'GPO']
for columna in columnas_requeridas:
    if columna not in data.columns:
        raise ValueError(f"Falta la columna requerida: {columna}")

# Inicializar una lista para almacenar las filas transformadas
filas_transformadas = []

# Iterar por cada fila para agrupar participantes
registro_actual = None
titulo_actual = None
calidad_actual = None
gpo_actual = None
participantes_acumulados = []

for _, fila in data.iterrows():
    if not pd.isna(fila['REGISTRO']):
        # Guardar el grupo actual si existe
        if registro_actual is not None:
            filas_transformadas.append({
                'REGISTRO': registro_actual,
                'TITULO DE OBRA': titulo_actual,
                'CALIDAD': calidad_actual,
                'PARTICIPANTES': ', '.join(participantes_acumulados),
                'GPO': gpo_actual
            })
        # Actualizar valores para el nuevo grupo
        registro_actual = fila['REGISTRO']
        titulo_actual = fila['TITULO DE OBRA']
        calidad_actual = fila['CALIDAD']
        gpo_actual = fila['GPO']
        participantes_acumulados = [fila['PARTICIPANTES']]
    else:
        # Agregar participante al grupo actual
        participantes_acumulados.append(fila['PARTICIPANTES'])

# Agregar el último grupo
if registro_actual is not None:
    filas_transformadas.append({
        'REGISTRO': registro_actual,
        'TITULO DE OBRA': titulo_actual,
        'CALIDAD': calidad_actual,
        'PARTICIPANTES': ', '.join(participantes_acumulados),
        'GPO': gpo_actual
    })

# Crear un DataFrame con las filas transformadas
data_transformada = pd.DataFrame(filas_transformadas)

# Guardar el resultado en un nuevo archivo Excel
data_transformada.to_excel(archivo_salida, index=False)

print(f"Archivo transformado guardado como: {archivo_salida}")
