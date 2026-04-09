import pandas as pd

import matplotlib.pyplot as plt

from openpyxl.drawing.image import Image

df = pd.read_csv("operaciones.csv")

df["valor"] = df["cantidad"] * df["precio_unitario"]

pd.set_option("display.max_columns", None)
print(df.head(5))
print(df.describe())

#Tabla 1: Total de valor y cantidad por categoria
print(df.groupby("categoria")[["valor", "cantidad"]].sum())

#Tabla 2: Total de valor por region y estado
print(df.groupby(["region", "estado"])["valor"].sum())

#Tabla 3: Total de valor por vendedor, ordenado de mayor a menor
print(df.groupby("vendedor")["valor"].sum().sort_values(ascending=False))

#Productos con bajo rendimiento:
por_producto = df.groupby("producto")["valor"].sum()
print(por_producto[por_producto < 2000])

with pd.ExcelWriter("reporte_operaciones.xlsx") as writer:
    # Hoja 1:
    df.to_excel(writer, sheet_name="Datos", index=False)

    # Hoja 2: Total de valor y cantidad por categoria
    resumen_categoria = df.groupby("categoria")[["valor", "cantidad"]].sum().reset_index()
    resumen_categoria.to_excel(writer, sheet_name="Por Categoria", index=False)

    # Hoja 3: Total de valor por vendedor
    por_vendedor = df.groupby("vendedor")["valor"].sum().sort_values(ascending=False).reset_index()
    por_vendedor.to_excel(writer, sheet_name="Por Vendedor", index=False)

    # Hoja 4: Productos con bajo rendimiento:
    bajo_rendimiento = por_producto[por_producto < 2000].reset_index()
    bajo_rendimiento.to_excel(writer, sheet_name="Bajo Rendimiento", index=False)

    # Gráficos:
    # Gráfico Valor Total por Vendedor
    total_x_vendedor = df.groupby("vendedor")["valor"].sum().sort_values(ascending=False)
    total_x_vendedor.plot(kind="bar")
    plt.title("Valor total por Vendedor")
    plt.ylabel("Valor")
    plt.tight_layout()

    plt.savefig("grafica_vendedores.png")
    plt.close()


    worksheet = writer.sheets["Por Vendedor"]

    img = Image("grafica_vendedores.png")
    worksheet.add_image(img, "E2")

    # Gráfico Valor por Categoría
    categorias = df.groupby("categoria")["valor"].sum()
    categorias.plot(kind="pie")
    plt.title("Valor total por Categoría")
    plt.ylabel("Valor")
    plt.tight_layout()

    plt.savefig("grafica_categorias.png")
    plt.close()

    worksheet = writer.sheets["Por Categoria"]

    img = Image("grafica_categorias.png")
    worksheet.add_image(img, "E2")

    # Gráfico Valor Total por Región
    regiones = df.groupby("region")["valor"].sum()
    regiones.plot(kind="barh")
    plt.title("Valor total por Región")
    plt.ylabel("Valor")
    plt.tight_layout()

    plt.savefig("grafica_regiones.png")
    plt.close()

    worksheet = writer.sheets["Datos"]

    img = Image("grafica_regiones.png")
    worksheet.add_image(img, "E2")

print("Reporte completo exportado")








