import pandas as pd

# Cargar el archivo de Excel
archivo_origen = 'METADATA_PUBLISHING_SEPARADO.xlsx'
archivo_exportado = 'Registros_no_validos.xlsx'

# Cargar la hoja "Grupos < 100%" en un DataFrame
df = pd.read_excel(archivo_origen, sheet_name='Grupos < 100%')

# Filtrar los registros donde '%' es 100 y 'Contrato' es 50
df_no_validos = df[(df['%'] == 100) & (df['Contrato'] == 50)]

# Guardar los registros filtrados en un nuevo archivo de Excel
with pd.ExcelWriter(archivo_exportado, engine='xlsxwriter') as writer:
    df_no_validos.to_excel(writer, index=False, sheet_name='No Validos')

print(f"Archivo '{archivo_exportado}' creado con los registros no válidos.")
