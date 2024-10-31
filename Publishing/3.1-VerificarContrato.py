import pandas as pd

# Archivo de origen y de exportación
archivo_origen = 'METADATA_PUBLISHING_UNIFICADO.xlsx'
archivo_exportado = 'resultado_verificacion.xlsx'

# Cargar el archivo de Excel
df = pd.read_excel(archivo_origen)

# Contar el número total de filas en el archivo
total_filas = len(df)
print(f"Total de filas en el archivo: {total_filas}")

# Agregar una columna que calcula la suma en 'Contrato'
def calcular_suma_contrato(contrato):
    if pd.notna(contrato):
        # Convertir a string y manejar diferentes tipos de datos
        contrato_str = str(contrato)
        if contrato_str.strip() != "":
            try:
                # Filtrar valores vacíos antes de la conversión a float
                valores = [float(valor) for valor in contrato_str.split(',') if valor.strip()]
                return sum(valores)
            except ValueError:
                return 0  # Si hay un valor no numérico, retornar 0
    return 0

df['Suma_Contrato'] = df['Contrato'].apply(calcular_suma_contrato)

# Exportar todas las filas al archivo de Excel, incluyendo la columna de suma
with pd.ExcelWriter(archivo_exportado, engine='xlsxwriter') as writer:
    df.to_excel(writer, index=False, sheet_name='Verificacion')

# Contar y mostrar el número de filas exportadas
total_filas_exportadas = len(df)
print(f"Total de filas exportadas: {total_filas_exportadas}")

print(f"El archivo '{archivo_exportado}' se ha creado exitosamente con todas las filas, incluyendo las sumas.")
