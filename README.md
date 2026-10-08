# 📦 DSL Descartables - Sistema ERP y Agente de Automatización

> **Caso de Estudio de Portafolio:** Automatización integral de inventarios, gestión de cuentas corrientes y canal de ventas para distribuidoras mayoristas, resolviendo fricciones operativas reales.

## 🚀 El Problema de Negocio (Fricción Operativa)
En la operativa diaria de **Distribuidora San Lorenzo**, la gestión manual de 280+ productos, la actualización semanal de listas de precios de múltiples proveedores (Zuma, Vasa) y el seguimiento de deudas de clientes en planillas de cálculo dispersas generaban cuellos de botella operativos y riesgos de pérdida de stock.

## 💡 La Solución Propuesta
Desarrollo de una arquitectura modular basada en Python, SQLite y Streamlit que actúa como una **Fuente Única de Verdad (Single Source of Truth)**. El sistema automatiza:
1. **Pipelines ETL Resilientes:** Ingesta y saneamiento de planillas Excel complejas con estructuras irregulares.
2. **Control de Inventario y POS:** Gestión centralizada de stock activo y cuentas corrientes de clientes.
3. **Agentes de IA y Automatización:** Futuros módulos para procesamiento automático de listas de costos y generación de catálogos comerciales.

## 🛠️ Arquitectura Técnica y Stack
* **Lenguaje:** Python 3.12
* **Procesamiento de Datos:** Pandas, Openpyxl (ETL dinámico)
* **Base de Datos:** SQLite (Diseño relacional optimizado para resiliencia de datos)
* **Interfaz de Usuario:** Streamlit (en desarrollo)

## 📂 Estructura del Repositorio
```text
dsl-inventory-system/
│
├── src/
│   ├── agents/
│   │   ├── ingest_clients.py      # Pipeline ETL inteligente para deudas y clientes
│   │   └── product_manager.py     # Gestor y alta de productos en inventario
│   └── ...
├── ingest_inventory.py            # Saneamiento e ingesta de stock central
├── Inventario DSL 08-10-2026.xlsx # Matriz de datos de origen (anonimizada/privada)
└── README.md