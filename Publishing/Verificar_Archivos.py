import pandas as pd
import requests
from io import BytesIO
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox, StringVar
from urllib.parse import urlparse
import json
import os
import logging

# Configuración del logging para guardar errores en un archivo log
logging.basicConfig(filename='comparador_excel.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

hd = 1  # Fila para encabezado
hdexcel = hd + 1  # Fila en formato de Excel (cuenta 1 base)

class ExcelComparatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Comparador de Excel - Tkinter")
        self.root.geometry("1200x700")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Marco principal para contener los widgets
        main_frame = tk.Frame(root, padx=10, pady=10)
        main_frame.grid(sticky="nsew")
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # Widgets de la interfaz
        self.file_path_var = tk.StringVar()
        self.url_var = tk.StringVar()

        tk.Label(main_frame, text="Ruta del archivo local:").grid(row=0, column=0, sticky="e", pady=5)
        tk.Entry(main_frame, textvariable=self.file_path_var, width=50).grid(row=0, column=1, sticky="w", pady=5)
        tk.Button(main_frame, text="Cargar archivo local", command=self.cargar_archivo_local).grid(row=0, column=2, padx=5)

        tk.Label(main_frame, text="URL del archivo remoto:").grid(row=1, column=0, sticky="e", pady=5)
        tk.Entry(main_frame, textvariable=self.url_var, width=50).grid(row=1, column=1, sticky="w", pady=5)
        tk.Button(main_frame, text="Guardar por Defecto", command=self.guardar_por_defecto).grid(row=1, column=2, padx=5, pady=5)
        tk.Button(main_frame, text="Borrar por Defecto", command=self.borrar_por_defecto).grid(row=2, column=2, padx=5, pady=5)
        tk.Button(main_frame, text="Comparar Archivos", command=self.comparar_archivos).grid(row=3, column=1, pady=10)

        # Secciones para mostrar resultados de comparación
        self.left_frame = tk.Frame(main_frame, padx=10, pady=10)
        self.left_frame.grid(row=4, column=0, sticky="nsew")
        self.right_frame = tk.Frame(main_frame, padx=10, pady=10)
        self.right_frame.grid(row=4, column=1, sticky="nsew")

        # Área de texto para el archivo local
        self.resultado_local_text = scrolledtext.ScrolledText(self.left_frame, wrap=tk.WORD, width=60, height=20)
        self.resultado_local_text.grid(row=0, column=0, pady=5, sticky="nsew")

        # Área de texto para el archivo remoto
        self.resultado_remoto_text = scrolledtext.ScrolledText(self.right_frame, wrap=tk.WORD, width=60, height=20)
        self.resultado_remoto_text.grid(row=0, column=0, pady=5, sticky="nsew")

        # Sincronizar desplazamiento entre ambos textos
        self.resultado_local_text.bind("<MouseWheel>", self.sync_scroll)
        self.resultado_remoto_text.bind("<MouseWheel>", self.sync_scroll)

        # Vincular la selección de celdas en ambas áreas de texto
        self.resultado_local_text.bind("<Button-1>", self.highlight_selection)
        self.resultado_remoto_text.bind("<Button-1>", self.highlight_selection)

        # Definir estilos de color para el resultado
        self.resultado_local_text.tag_config('highlight', background='yellow')
        self.resultado_remoto_text.tag_config('highlight', background='yellow')
        self.resultado_local_text.tag_config('unique', foreground='blue')  # Registros únicos en el local
        self.resultado_remoto_text.tag_config('unique', foreground='orange')  # Registros únicos en el remoto
        self.resultado_local_text.tag_config('diff', foreground='red')
        self.resultado_remoto_text.tag_config('diff', foreground='red')

        main_frame.rowconfigure(4, weight=1)
        self.left_frame.rowconfigure(0, weight=1)
        self.right_frame.rowconfigure(0, weight=1)

        # Barra de estado en la parte inferior izquierda
        self.status_var = StringVar()
        self.status_var.set("Esperando acción del usuario...")
        self.status_label = tk.Label(root, textvariable=self.status_var, anchor='w', relief=tk.SUNKEN)
        self.status_label.grid(row=1, column=0, sticky="we")

        # Cargar configuración por defecto si existe
        self.cargar_por_defecto()

    def cargar_archivo_local(self):
        archivo = filedialog.askopenfilename(filetypes=[("Archivos de Excel", "*.xlsx")])
        if archivo:
            self.file_path_var.set(archivo)
            self.status_var.set(f"Archivo local cargado: {archivo}")

    def guardar_por_defecto(self):
        config_data = {
            "archivo_local": self.file_path_var.get(),
            "archivo_remoto": self.url_var.get()
        }
        with open('config_default.json', 'w') as config_file:
            json.dump(config_data, config_file, indent=4)
        self.status_var.set("Configuración guardada como predeterminada.")

    def cargar_por_defecto(self):
        if os.path.exists('config_default.json'):
            with open('config_default.json', 'r') as config_file:
                config_data = json.load(config_file)
                self.file_path_var.set(config_data.get("archivo_local", ""))
                self.url_var.set(config_data.get("archivo_remoto", ""))
            self.status_var.set("Configuración por defecto cargada.")

    def borrar_por_defecto(self):
        if os.path.exists('config_default.json'):
            os.remove('config_default.json')
            self.file_path_var.set("")
            self.url_var.set("")
            self.status_var.set("Configuración predeterminada eliminada.")

    def descargar_google_sheets(self, url):
        parsed_url = urlparse(url)
        if "docs.google.com" in parsed_url.netloc and "spreadsheets" in parsed_url.path:
            sheet_id = parsed_url.path.split("/")[3]
            export_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
            return export_url
        return None

    def cargar_dataframe(self, archivo, tipo):
        try:
            df = pd.read_excel(archivo, header=hd, engine='openpyxl')
            self.status_var.set(f"{tipo} cargado correctamente.")
            return df
        except Exception as e:
            logging.error(f"No se pudo abrir el archivo {tipo}: {str(e)}")
            messagebox.showerror("Error", f"No se pudo abrir el archivo {tipo}. Asegúrate de que el archivo es válido: {str(e)}")
            self.status_var.set(f"Error al cargar el archivo {tipo}.")
            return None

    def sync_scroll(self, event):
        """ Sincroniza el desplazamiento de ambas áreas de texto """
        if event.widget == self.resultado_local_text:
            self.resultado_remoto_text.yview_scroll(int(-1 * (event.delta / 120)), "units")
        elif event.widget == self.resultado_remoto_text:
            self.resultado_local_text.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def highlight_selection(self, event):
        """ Resalta la celda específica seleccionada en ambas áreas de texto """
        widget = event.widget
        if widget == self.resultado_local_text:
            other_widget = self.resultado_remoto_text
        else:
            other_widget = self.resultado_local_text

        # Limpiar los resaltados anteriores
        self.resultado_local_text.tag_remove('highlight', '1.0', 'end')
        self.resultado_remoto_text.tag_remove('highlight', '1.0', 'end')

        try:
            # Obtener la línea y la columna del clic
            index = widget.index(f"@{event.x},{event.y}")
            line, _ = index.split('.')

            # Obtener el texto de la línea
            line_content = widget.get(f"{line}.0", f"{line}.end")

            # Resaltar la línea completa en ambas áreas de texto
            widget.tag_add('highlight', f"{line}.0", f"{line}.end")
            other_widget.tag_add('highlight', f"{line}.0", f"{line}.end")
        except tk.TclError:
            # En caso de error de selección (por ejemplo, si no se hace clic en una línea válida)
            pass

    def comparar_archivos(self):
        archivo_local = self.file_path_var.get()
        archivo_url = self.url_var.get()

        if not archivo_local or not archivo_url:
            messagebox.showerror("Error", "Por favor, selecciona un archivo local y proporciona una URL.")
            self.status_var.set("Error: falta archivo local o URL.")
            return

        # Cargar el archivo Excel local
        df_local = self.cargar_dataframe(archivo_local, "archivo local")
        if df_local is None:
            return

        # Descargar el archivo remoto y cargarlo en un DataFrame
        google_sheets_url = self.descargar_google_sheets(archivo_url)
        try:
            if google_sheets_url:
                response = requests.get(google_sheets_url)
                response.raise_for_status()
                df_remoto = pd.read_csv(BytesIO(response.content), header=hd)
                self.status_var.set("Archivo Google Sheets descargado y cargado correctamente.")
            else:
                response = requests.get(archivo_url)
                response.raise_for_status()
                df_remoto = pd.read_excel(BytesIO(response.content), header=hd, engine='openpyxl')
                self.status_var.set("Archivo remoto descargado y cargado correctamente.")
        except Exception as e:
            logging.error(f"No se pudo descargar o abrir el archivo desde la URL: {str(e)}")
            messagebox.showerror("Error", f"No se pudo descargar o abrir el archivo desde la URL: {str(e)}")
            self.status_var.set("Error al descargar el archivo remoto.")
            return

        # Limpiar las áreas de texto para mostrar los resultados de la comparación
        self.resultado_local_text.delete('1.0', tk.END)
        self.resultado_remoto_text.delete('1.0', tk.END)

        # Definir columnas necesarias para filtrar datos válidos
        columnas_necesarias = ['Artist', 'Title', 'ISRC']

        # Filtrar las filas con al menos un valor en 'Artist', 'Title', o 'ISRC'
        filas_validas_local = df_local[df_local[columnas_necesarias].notna().any(axis=1)]
        filas_validas_remoto = df_remoto[df_remoto[columnas_necesarias].notna().any(axis=1)]

        # Comparación fila por fila utilizando el 'ID IDENTIFICADOR'
        if 'ID IDENTIFICADOR' in filas_validas_local.columns and 'ID IDENTIFICADOR' in filas_validas_remoto.columns:
            filas_validas_local.set_index('ID IDENTIFICADOR', inplace=True)
            filas_validas_remoto.set_index('ID IDENTIFICADOR', inplace=True)

            ids_local = set(filas_validas_local.index)
            ids_remoto = set(filas_validas_remoto.index)

            ids_solo_local = ids_local - ids_remoto
            ids_solo_remoto = ids_remoto - ids_local
            ids_comunes = ids_local.intersection(ids_remoto)

            # Mostrar las filas únicas del archivo local
            if ids_solo_local:
                self.resultado_local_text.insert(tk.END, "Filas presentes solo en el archivo local:\n")
                for id_local in ids_solo_local:
                    self.resultado_local_text.insert(tk.END, f"{filas_validas_local.loc[id_local].to_dict()}\n", 'unique')

            # Mostrar las filas únicas del archivo remoto
            if ids_solo_remoto:
                self.resultado_remoto_text.insert(tk.END, "Filas presentes solo en el archivo remoto:\n")
                for id_remoto in ids_solo_remoto:
                    self.resultado_remoto_text.insert(tk.END, f"{filas_validas_remoto.loc[id_remoto].to_dict()}\n", 'unique')

            # Mostrar las diferencias en los registros comunes
            if ids_comunes:
                for id_comun in ids_comunes:
                    fila_local = filas_validas_local.loc[id_comun]
                    fila_remoto = filas_validas_remoto.loc[id_comun]
                    if not fila_local.equals(fila_remoto):
                        diferencias = fila_local != fila_remoto
                        for columna, es_diferente in diferencias.items():
                            if es_diferente:
                                self.resultado_local_text.insert(tk.END, f"ID IDENTIFICADOR {id_comun} - Columna '{columna}': Local = {fila_local[columna]}\n", 'diff')
                                self.resultado_remoto_text.insert(tk.END, f"ID IDENTIFICADOR {id_comun} - Columna '{columna}': Remoto = {fila_remoto[columna]}\n", 'diff')

            self.status_var.set("Comparación completa: se encontraron diferencias.")
        else:
            messagebox.showerror("Error", "Los archivos no contienen la columna 'ID IDENTIFICADOR' para comparar.")
            self.status_var.set("Error: falta la columna 'ID IDENTIFICADOR'.")

# Crear la ventana principal de la aplicación
root = tk.Tk()
app = ExcelComparatorApp(root)
root.mainloop()
