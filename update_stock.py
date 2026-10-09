
import sqlite3
import pandas as pd
import warnings

# Ignorar advertencias de formatos de Excel
warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')

EXCEL_FILE = 'DSL_stock_08-10-26.xlsx'
DB_FILE = 'dsl_inventory.db'

def update_inventory():
    print(f"Sincronizando inventario desde '{EXCEL_FILE}'...")
    
    try:
        # Leemos específicamente la hoja limpia
        df = pd.read_excel(EXCEL_FILE, sheet_name='Stock calculado')
    except Exception as e:
        return f"Error crítico al leer el Excel: {e}"

    # Limpieza de columnas
    df.columns = [str(col).strip() for col in df.columns]
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    productos_actualizados = 0
    productos_para_revisar = 0

    for index, row in df.iterrows():
        sku_excel = str(row.get('Código DSL', '')).strip()
        nombre_excel = str(row.get('Producto (Inventario)', '')).strip()
        
        # Filtramos filas vacías
        if not sku_excel or sku_excel.lower() == 'nan':
            continue
            
        stock_teorico = row.get('Stock teórico al 08/10')
        
        # Lógica de negocio: Si el stock viene vacío, asignamos 0 y levantamos bandera
        if pd.isna(stock_teorico):
            stock_teorico = 0.0
            productos_para_revisar += 1
        else:
            stock_teorico = float(stock_teorico)

        try:
            # Actualización con las columnas correctas detectadas en la auditoría
            cursor.execute('''
                UPDATE productos 
                SET stock_actual = ? 
                WHERE sku = ? OR nombre = ?
            ''', (stock_teorico, sku_excel, nombre_excel))
            
            if cursor.rowcount > 0:
                productos_actualizados += 1
                
        except sqlite3.OperationalError as e:
            print(f"Error de SQL: {e}. Deteniendo ejecución para proteger la base de datos.")
            break

    conn.commit()
    conn.close()
    
    print(f" [ÉXITO] Se actualizó el stock de {productos_actualizados} productos en '{DB_FILE}'.")
    if productos_para_revisar > 0:
        print(f" [ALERTA OPERATIVA] {productos_para_revisar} productos quedaron con stock 0 (Pendientes de revisión física).")

if __name__ == '__main__':
    update_inventory()