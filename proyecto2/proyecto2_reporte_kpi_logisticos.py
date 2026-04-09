"""
Proyecto 2: Reporte Automático de KPI Logísticos
Análisis de cumplimiento y eficiencia por proveedor.
Análisis con gráficos de tasas de cumplimiento y
días de retraso por proveedor, exportando a archivo
en Excel.
Autor: Rigoberto Cárcamo
"""

import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
from openpyxl.drawing.image import Image


conn = sqlite3.connect("analisis_proveedores.db")

# Tabla 1: Proveedores

proveedores = pd.read_csv("proveedores.csv")
proveedores.to_sql("proveedores", conn, if_exists="replace", index=False)

# Tabla 2: Productos

productos = pd.read_csv("productos.csv")
productos.to_sql("productos", conn, if_exists="replace", index=False)

# Tabla 3: Entregas

entregas = pd.read_csv("entregas.csv")
entregas.to_sql("entregas", conn, if_exists="replace", index=False)


# consulta Tasa de cumplimiento por proveedor
kpi_proveedores = pd.read_sql("""
        SELECT proveedores.nombre, COUNT(proveedores.nombre) as total_entregas, 
        SUM(CASE WHEN estado = 'a_tiempo' THEN 1 ELSE 0 END) as entregas_a_tiempo, 
        SUM(CASE WHEN estado = 'retrasado' THEN 1 ELSE 0 END) as entregas_retrasadas,
        ROUND(SUM(CASE WHEN estado = 'a_tiempo' THEN 1.0 ELSE 0 END) * 100 / COUNT(*), 1) as pct_cumplimiento
        FROM entregas
        JOIN proveedores on entregas.id_proveedor = proveedores.id_proveedor
        GROUP BY proveedores.nombre
        """, conn)


# consulta para conocer el promedio y el máximo de días de retraso en entregas retrasadas por proveedor.

dias_retraso = pd.read_sql("""
    SELECT proveedores.nombre,
           AVG(JULIANDAY(fecha_real) - JULIANDAY(fecha_prometida)) as promedio_dias_retraso,
           MAX(JULIANDAY(fecha_real) - JULIANDAY(fecha_prometida)) as max_dias_retraso
    FROM entregas
    JOIN proveedores ON entregas.id_proveedor = proveedores.id_proveedor
    WHERE estado = 'retrasado'
    GROUP BY proveedores.nombre
    ORDER BY promedio_dias_retraso DESC
""", conn)


# Gráficos:
# Gráfico Tasa de Cumplimiento por proveedor
tasa_cumplimiento = kpi_proveedores.set_index("nombre")["pct_cumplimiento"].plot(kind="barh")
plt.title("KPI Cumplimiento Proveedores")
plt.ylabel("Porcentaje Cumplimiento")
plt.tight_layout()

plt.savefig("grafica_kpi_proveedores.png")
plt.close()

# Gráfico Días de retraso por proveedor0
retraso_x_proveedor = dias_retraso.set_index("nombre")["promedio_dias_retraso"].plot(kind="bar")
plt.title("Retrasos por Proveedor")
plt.ylabel("Días de Retraso")
plt.tight_layout()

plt.savefig("grafica_retrasos_x_proveedor.png")
plt.close()

# exportar a excel
with pd.ExcelWriter("analisis_proveedores.xlsx") as writer:
    # Hoja 1:
    kpi_proveedores.to_excel(writer, sheet_name="KPI Proveedores", index=False)

    # Hoja 2:
    dias_retraso.to_excel(writer, sheet_name="Días de Retraso", index=False)

    # Gráfico KPI Cumplimiento Vendedores.

    worksheet = writer.sheets["KPI Proveedores"]

    img_kpi = Image("grafica_kpi_proveedores.png")
    worksheet.add_image(img_kpi, "H2")


    # Gráfico Días de Retraso

    worksheet = writer.sheets["Días de Retraso"]

    img_retraso = Image("grafica_retrasos_x_proveedor.png")
    worksheet.add_image(img_retraso, "H2")

print("Reporte completo exportado")









