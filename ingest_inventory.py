import sqlite3
import pandas as pd

EXCEL_FILE = "Inventario 30 set 26.pdf.xls"
DB_FILE = "dsl_inventory.db"


def find_header_row(file_path, sheet_name="Inventario"):
    """Escanea las primeras filas del Excel para ubicar la línea exacta de encabezados."""
    df_tmp = pd.read_excel(file_path, sheet_name=sheet_name, header=None)

    for idx, row in df_tmp.iterrows():
        row_values = [str(val).lower() for val in row.values]
        if any(
            term in val
            for val in row_values
            for term in ["artí", "artic", "producto", "codigo", "cant"]
        ):
            return idx
        if idx > 25:
            break
    return 0


def build_database():
    print("Iniciando la lectura e inspección dinámica de la planilla...")

    header_idx = find_header_row(EXCEL_FILE, sheet_name="Inventario")
    print(f"Encabezados detectados en la fila: {header_idx + 1}")

    df_raw = pd.read_excel(
        EXCEL_FILE, sheet_name="Inventario", header=header_idx
    )
    df_raw.columns = [str(col).strip() for col in df_raw.columns]

    # Mapeo de columnas asegurando nombres únicos en el destino
    col_map = {}
    assigned_targets = set()

    for col in df_raw.columns:
        col_lower = col.lower()
        target = None

        if any(x in col_lower for x in ["artí", "artic", "producto"]):
            target = "nombre"
        elif "cod" in col_lower and "prov" in col_lower:
            target = "codigo_proveedor"
        elif "cod" in col_lower or "sku" in col_lower:
            target = "sku"
        elif any(x in col_lower for x in ["cant", "stock"]):
            target = "stock_actual"
        elif (
            any(
                x in col_lower
                for x in ["p comp", "p.compra", "p compra", "costo"]
            )
            and "total" not in col_lower
        ):
            target = "precio_costo"
        elif "total" in col_lower:
            col_map[col] = "valor_total_costo"
            target = "valor_total_costo"
        elif "prov" in col_lower:
            target = "proveedor"
        elif "desc" in col_lower:
            target = "descripcion"

        if target and target not in assigned_targets:
            col_map[col] = target
            assigned_targets.add(target)

    df_raw = df_raw.rename(columns=col_map)

    # Eliminar cualquier columna duplicada en memoria antes de guardar
    df_raw = df_raw.loc[:, ~df_raw.columns.duplicated()].copy()

    if "nombre" not in df_raw.columns:
        print("\nColumnas detectadas en la planilla:", list(df_raw.columns))
        raise KeyError(
            "No se identificó la columna de productos. Revisa la estructura del Excel."
        )

    # Filtrar filas nulas o encabezados repetidos
    df_clean = df_raw.dropna(subset=["nombre"]).copy()
    df_clean = df_clean[
        ~df_clean["nombre"]
        .astype(str)
        .str.lower()
        .str.contains("artí|artic|producto|total compra")
    ]

    # Formatear SKU a texto
    if "sku" in df_clean.columns:
        df_clean["sku"] = (
            df_clean["sku"]
            .fillna("")
            .astype(str)
            .apply(
                lambda x: x.split(".")[0].zfill(4)
                if x and x.lower() not in ["nan", "none", ""]
                else ""
            )
        )
    else:
        df_clean["sku"] = ""

    # Formatear números
    df_clean["stock_actual"] = (
        pd.to_numeric(df_clean.get("stock_actual", 0), errors="coerce")
        .fillna(0)
        .astype(int)
    )
    df_clean["precio_costo"] = (
        pd.to_numeric(df_clean.get("precio_costo", 0.0), errors="coerce")
        .fillna(0.0)
        .round(2)
    )
    df_clean["valor_total_costo"] = (
        pd.to_numeric(df_clean.get("valor_total_costo", 0.0), errors="coerce")
        .fillna(0.0)
        .round(2)
    )

    columnas_db = [
        "sku",
        "nombre",
        "stock_actual",
        "precio_costo",
        "valor_total_costo",
        "proveedor",
        "codigo_proveedor",
        "descripcion",
    ]

    for col in columnas_db:
        if col not in df_clean.columns:
            df_clean[col] = ""

    df_final = df_clean[columnas_db].copy()

    # Guardar en SQLite
    conn = sqlite3.connect(DB_FILE)
    df_final.to_sql("productos", conn, if_exists="replace", index=False)

    cursor = conn.cursor()
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_productos_sku ON productos(sku);"
    )
    conn.commit()

    total_registros = len(df_final)
    con_stock = len(df_final[df_final["stock_actual"] > 0])
    conn.close()

    print(f"\n Base de datos '{DB_FILE}' generada exitosamente.")
    print(f" Total productos procesados: {total_registros}")
    print(f" Productos con stock activo: {con_stock}")


if __name__ == "__main__":
    build_database()