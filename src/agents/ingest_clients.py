import os
import sqlite3
import pandas as pd
import warnings

# Ignorar advertencias internas de formatos raros de Excel
warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')

EXCEL_FILE = "Inventario DSL 08-10-2026.xlsx"
DB_FILE = "dsl_inventory.db"

def init_db():
    """Crea la tabla de clientes si no existe en la base de datos."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL,
            telefono TEXT DEFAULT '',
            direccion TEXT DEFAULT '',
            saldo_deuda REAL DEFAULT 0.0
        )
    ''')
    conn.commit()
    conn.close()

def load_clients_from_excel():
    """Lee el Excel detectando dinámicamente la hoja y la fila de encabezados."""
    print(f"Inspeccionando el archivo '{EXCEL_FILE}'...")
    
    try:
        xls = pd.ExcelFile(EXCEL_FILE, engine='openpyxl')
        hojas = xls.sheet_names
    except Exception as e:
        return f"Error crítico al leer la estructura del Excel: {e}"

    # 1. Búsqueda inteligente de la hoja
    target_sheet = None
    for hoja in hojas:
        if "deuda" in hoja.lower() or "cliente" in hoja.lower():
            target_sheet = hoja
            break
            
    if not target_sheet:
        return f"No se encontró ninguna hoja relacionada a deudas. Hojas disponibles: {hojas}"

    print(f"Extrayendo datos de la hoja seleccionada: '{target_sheet}'...")
    
    try:
        # 2. Escáner Dinámico: Leemos sin encabezados para buscar la fila correcta
        df_temp = pd.read_excel(EXCEL_FILE, sheet_name=target_sheet, engine='openpyxl', header=None)
        
        header_row = 0
        for i in range(min(15, len(df_temp))): # Buscamos en las primeras 15 filas
            row_str = " ".join([str(val).lower() for val in df_temp.iloc[i].values])
            # Si la fila contiene la palabra clave, asumimos que es el encabezado
            if "cliente" in row_str or "nombre" in row_str:
                header_row = i
                break
                
        print(f"Encabezados reales detectados en la fila: {header_row + 1}")
        
        # 3. Leemos el dataframe usando la fila correcta como encabezado
        df_raw = pd.read_excel(EXCEL_FILE, sheet_name=target_sheet, engine='openpyxl', header=header_row)
    except Exception as e:
        return f"Error al leer los datos de la hoja '{target_sheet}': {e}"

    # Limpiamos nombres de columnas
    df_raw.columns = [str(col).strip().lower() for col in df_raw.columns]
    
    col_map = {}
    for col in df_raw.columns:
        if "cliente" in col or "nombre" in col:
            col_map[col] = "nombre"
        elif "deuda" in col or "saldo" in col or "monto" in col:
            col_map[col] = "saldo_deuda"
        elif "tel" in col or "cel" in col:
            col_map[col] = "telefono"
        elif "dir" in col or "domicilio" in col:
            col_map[col] = "direccion"

    df_clean = df_raw.rename(columns=col_map)
    
    if "nombre" not in df_clean.columns:
        return f"Columnas finales detectadas: {list(df_clean.columns)}. Falla en el mapeo de 'Nombre'."

    # Aseguramos formato numérico para las deudas
    if "saldo_deuda" not in df_clean.columns:
        df_clean["saldo_deuda"] = 0.0
    else:
        df_clean["saldo_deuda"] = pd.to_numeric(df_clean["saldo_deuda"], errors='coerce').fillna(0.0)

    # Descartamos filas vacías sin nombre de cliente
    df_clean = df_clean.dropna(subset=["nombre"])
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    registros_procesados = 0
    for _, row in df_clean.iterrows():
        nombre = str(row["nombre"]).strip().title()
        # Filtramos basura (celdas combinadas, totales, etc.)
        if not nombre or nombre.lower() == "nan" or "total" in nombre.lower():
            continue
            
        deuda = round(float(row["saldo_deuda"]), 2)
        telefono = str(row.get("telefono", "")).replace("nan", "").strip()
        direccion = str(row.get("direccion", "")).replace("nan", "").strip()

        # Inyectamos en SQLite
        cursor.execute('''
            INSERT INTO clientes (nombre, telefono, direccion, saldo_deuda)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(nombre) DO UPDATE SET 
                saldo_deuda = ?,
                telefono = CASE WHEN ? != '' THEN ? ELSE telefono END,
                direccion = CASE WHEN ? != '' THEN ? ELSE direccion END
        ''', (nombre, telefono, direccion, deuda, deuda, telefono, telefono, direccion, direccion))
        
        registros_procesados += 1

    conn.commit()
    conn.close()
    
    return f" [EXITO] Se sincronizaron {registros_procesados} clientes y sus deudas en la base de datos."

if __name__ == "__main__":
    init_db()
    resultado = load_clients_from_excel()
    print(resultado)