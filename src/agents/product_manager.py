import os
import sqlite3

DB_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "dsl_inventory.db"
)

class ProductManagerAgent:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path

    def alta_producto(self, sku, nombre, stock_inicial, precio_costo, proveedor="", descripcion=""):
        """Registra un producto completamente nuevo en la base de datos."""
        
        # Validación básica
        if not sku or not nombre:
            return " Error: El SKU y el Nombre son obligatorios."

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Verificar si el SKU ya existe para evitar duplicados
        cursor.execute("SELECT nombre FROM productos WHERE sku = ?", (sku,))
        if cursor.fetchone():
            conn.close()
            return f" Error: El SKU '{sku}' ya existe en la base de datos."

        valor_total = stock_inicial * precio_costo

        try:
            cursor.execute("""
                INSERT INTO productos (sku, nombre, stock_actual, precio_costo, valor_total_costo, proveedor, codigo_proveedor, descripcion)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (sku, nombre, stock_inicial, precio_costo, valor_total, proveedor, "", descripcion))
            
            conn.commit()
            mensaje = f" [ALTA EXITOSA] Se incorporó '{nombre}' (SKU: {sku}) con {stock_inicial} unidades al inventario."
        except Exception as e:
            mensaje = f" Error al insertar en la base de datos: {e}"
        finally:
            conn.close()

        return mensaje

if __name__ == "__main__":
    manager = ProductManagerAgent()
    
    # Ejemplo de uso: Ingresar las nuevas camisetas
    resultado = manager.alta_producto(
        sku="CAM-4050-CHRIS", 
        nombre="Camisetas 40x50 color Chris", 
        stock_inicial=20,       
        precio_costo=1033.50,      
        proveedor="Nuevo Proveedor"
    )
    print(resultado)