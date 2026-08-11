import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression
import numpy as np

print("Conectando a la base de datos...")

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="dw_ventas"
)

print("Conexion exitosa")

# ####################################################
# # 1 VENTAS POR SUCURSAL POR MES
# ####################################################

query = """
SELECT
    s.nombre AS sucursal,
    t.anio,
    t.mes,
    SUM(f.ingreso) AS ventas
FROM fact_ventas f
JOIN dim_sucursal s ON f.sucursal_id = s.sucursal_id
JOIN dim_tiempo t ON f.tiempo_id = t.tiempo_id
GROUP BY s.nombre, t.anio, t.mes
"""

df = pd.read_sql(query, conn)
df.to_excel("ventas_por_sucursal.xlsx", index=False)

print("Reporte ventas por sucursal generado")

# ==============================
# REPORTE: SUCURSALES CON CAIDA DE VENTAS (2 MESES)
# ==============================

print("\n📉 REPORTE: Sucursales con caída de ventas entre meses")

# Crear fecha
df["Mes"] = pd.to_datetime(df["anio"].astype(str) + "-" + df["mes"].astype(str))

# Ventas por sucursal y mes
ventas_mensuales = df.groupby(["sucursal", "Mes"])["ventas"].sum().reset_index()

ventas_mensuales = ventas_mensuales.sort_values(["sucursal", "Mes"])

# Ventas del mes anterior
ventas_mensuales["Ventas_Mes_Anterior"] = ventas_mensuales.groupby("sucursal")["ventas"].shift(1)

# Detectar caídas
ventas_mensuales["Caida"] = ventas_mensuales["ventas"] < ventas_mensuales["Ventas_Mes_Anterior"]

# Diferencia de ventas
ventas_mensuales["Diferencia"] = ventas_mensuales["ventas"] - ventas_mensuales["Ventas_Mes_Anterior"]

# Porcentaje de caída
ventas_mensuales["Porcentaje_Caida"] = (
    (ventas_mensuales["Ventas_Mes_Anterior"] - ventas_mensuales["ventas"])
    / ventas_mensuales["Ventas_Mes_Anterior"]
) * 100

# Formato de periodo para Excel
ventas_mensuales["Periodo"] = ventas_mensuales["Mes"].dt.strftime("%Y-%m")

# Filtrar solo caídas
reporte_caida = ventas_mensuales[ventas_mensuales["Caida"] == True]

# Seleccionar columnas claras
reporte_caida = reporte_caida[
    ["sucursal","Periodo","ventas","Ventas_Mes_Anterior","Diferencia","Porcentaje_Caida"]
]

print("\nSucursales con caída de ventas:")
print(reporte_caida)

# Guardar reporte
reporte_caida.to_excel("reporte_caida_ventas_sucursales.xlsx", index=False)

print("\n✅ Reporte guardado: reporte_caida_ventas_sucursales.xlsx")

####################################################
# 2 PRODUCTOS MAS RENTABLES
####################################################

query = """
SELECT
    p.producto_id,
    p.nombre,
    p.categoria,
    SUM(f.ganancia) AS ganancia_total
FROM fact_ventas f
JOIN dim_producto p ON f.producto_id = p.producto_id
GROUP BY p.producto_id, p.nombre, p.categoria
ORDER BY ganancia_total DESC
LIMIT 50
"""

df = pd.read_sql(query, conn)

df.to_excel("productos_mas_rentables.xlsx", index=False)

print("Reporte productos rentables generado")

# ####################################################
# # 3 CLIENTES MAS FRECUENTES
# ####################################################

query = """
SELECT
    c.cliente_id,
    c.nombre,
    COUNT(f.venta_id) AS num_compras
FROM fact_ventas f
JOIN dim_cliente c ON f.cliente_id = c.cliente_id
GROUP BY c.cliente_id
ORDER BY num_compras DESC
LIMIT 100
"""

df = pd.read_sql(query, conn)
df.to_excel("clientes_mas_frecuentes.xlsx", index=False)

print("Reporte clientes frecuentes generado")

####################################################
# 4 PRODUCTOS CON MENOS DEL 10% DE GANANCIA
####################################################

query = """
SELECT
    p.nombre,
    SUM(f.ingreso) AS ingresos,
    SUM(f.ganancia) AS ganancia,
    ROUND(SUM(f.ganancia) * 100 / NULLIF(SUM(f.ingreso),0),2) AS margen
FROM fact_ventas f
JOIN dim_producto p ON f.producto_id = p.producto_id
GROUP BY p.producto_id, p.nombre
HAVING margen < 10
ORDER BY margen ASC
"""

df = pd.read_sql(query, conn)

df.to_excel("productos_margen_menor_10.xlsx", index=False)

print("Reporte productos con margen menor al 10% generado")


####################################################
# 5 CLIENTES QUE COMPRARON MAS DE 4 VECES EN UNA SEMANA
####################################################

query = """
SELECT
    c.cliente_id,
    c.nombre,
    YEARWEEK(t.fecha) AS semana,
    COUNT(*) AS compras
FROM fact_ventas f
JOIN dim_cliente c ON f.cliente_id = c.cliente_id
JOIN dim_tiempo t ON f.tiempo_id = t.tiempo_id
GROUP BY c.cliente_id, c.nombre, semana
HAVING compras > 4
ORDER BY compras DESC
"""

df = pd.read_sql(query, conn)

df.to_excel("clientes_para_descuento.xlsx", index=False)

print("Reporte clientes con posible descuento generado")

####################################################
# 6 TEMPORADAS PICO DE VENTAS (TRIMESTRE + CATEGORIA)
####################################################

query = """
SELECT
    t.anio,
    t.trimestre,
    p.categoria,
    SUM(f.ingreso) AS ventas
FROM fact_ventas f
JOIN dim_tiempo t ON f.tiempo_id = t.tiempo_id
JOIN dim_producto p ON f.producto_id = p.producto_id
GROUP BY t.anio, t.trimestre, p.categoria
"""

df = pd.read_sql(query, conn)

# Ordenar datos para graficar correctamente
df = df.sort_values(["categoria", "anio", "trimestre"])

# Crear columna de temporada
df["temporada"] = df["anio"].astype(str) + " Q" + df["trimestre"].astype(str)

# Detectar temporada pico por categoría
temporadas_pico = (
    df.sort_values("ventas", ascending=False)
      .groupby("categoria")
      .head(1)
)

print("\nTemporadas pico por categoria:")
print(temporadas_pico)

# Guardar reporte
temporadas_pico.to_csv("temporadas_pico_categoria.csv", index=False)

# Generar una gráfica por categoría
import matplotlib.ticker as ticker

for categoria in df["categoria"].unique():

    subset = df[df["categoria"] == categoria]

    plt.figure(figsize=(10,5))

    plt.plot(subset["temporada"], subset["ventas"], marker="o")

    # Mostrar valor en cada punto
    for i, row in subset.iterrows():
        plt.text(
            row["temporada"],
            row["ventas"],
            f'{row["ventas"]/1_000_000:.1f}M',
            ha='center',
            va='bottom',
            fontsize=9
        )

    plt.title(f"Ventas por temporada - {categoria}")
    plt.xlabel("Temporada (Trimestre)")
    plt.ylabel("Ventas (Millones)")

    # Formato del eje Y en millones
    plt.gca().yaxis.set_major_formatter(
        ticker.FuncFormatter(lambda x, pos: f'{x/1_000_000:.0f}M')
    )

    plt.xticks(rotation=45)

    plt.tight_layout()

    plt.savefig(f"ventas_temporada_{categoria}.png")
    plt.close()

print("Graficos generados por categoria")
print("Reporte CSV generado: temporadas_pico_categoria.csv")

# ####################################################
# # 7 CLASIFICACION DE CLIENTES (K-MEANS)
# ####################################################

query = """
SELECT
    c.cliente_id,
    SUM(f.ingreso) AS total_gasto,
    COUNT(f.venta_id) AS num_compras,
    AVG(f.ingreso) AS ticket_promedio
FROM fact_ventas f
JOIN dim_cliente c ON f.cliente_id = c.cliente_id
GROUP BY c.cliente_id
"""

df = pd.read_sql(query, conn)

# Variables para clustering
X = df[["total_gasto","num_compras","ticket_promedio"]]

# Modelo K-Means
kmeans = KMeans(n_clusters=3, random_state=42)
df["cluster"] = kmeans.fit_predict(X)

# # ==============================
# # TRADUCIR CLUSTERS A SEGMENTOS
# # ==============================

# Calcular gasto promedio por cluster
cluster_stats = df.groupby("cluster")["total_gasto"].mean().sort_values(ascending=False)

# Obtener orden de clusters según gasto
cluster_order = cluster_stats.index.tolist()

labels = {
    cluster_order[0]: "Premium",
    cluster_order[1]: "Frecuente",
    cluster_order[2]: "Ocasional"
}

# Crear columna con el segmento de cliente
df["segmento_cliente"] = df["cluster"].map(labels)

print("\nSegmentacion de clientes:")
print(df[["cliente_id","total_gasto","segmento_cliente"]].head())

# Mostrar resumen por segmento
print("\nResumen por segmento:")
print(df["segmento_cliente"].value_counts())

# Guardar resultado
df.to_excel("clasificacion_clientes.xlsx", index=False)

print("Clasificacion de clientes generada")

####################################################
# 8 PREDICCION DE VENTAS (REGRESION LINEAL)
####################################################
import matplotlib.ticker as ticker

query = """
SELECT
    t.anio,
    t.mes,
    SUM(f.ingreso) AS ventas
FROM fact_ventas f
JOIN dim_tiempo t ON f.tiempo_id = t.tiempo_id
GROUP BY t.anio, t.mes
ORDER BY t.anio, t.mes
"""

df = pd.read_sql(query, conn)

# Crear etiqueta de fecha
df["fecha"] = df["anio"].astype(str) + "-" + df["mes"].astype(str)

# Variable de tiempo para el modelo
df["periodo"] = range(len(df))

X = df[["periodo"]]
y = df["ventas"]

modelo = LinearRegression()
modelo.fit(X,y)

# Predecir 3 meses
future = np.array([[len(df)], [len(df)+1], [len(df)+2]])
pred = modelo.predict(future)

# GRAFICA 

plt.figure(figsize=(12,6))

# Ventas reales
plt.plot(df["fecha"], df["ventas"], marker="o", label="Ventas reales")

# Predicción
x_pred = range(len(df), len(df)+3)
plt.plot(x_pred, pred, marker="o", linestyle="--", label="Prediccion")

# Formato eje Y en millones
plt.gca().yaxis.set_major_formatter(
    ticker.FuncFormatter(lambda x, pos: f'{x/1_000_000:.0f}M')
)

# Mostrar valores en los puntos reales
for i, v in enumerate(df["ventas"]):
    plt.text(i, v, f'{v/1_000_000:.0f}M', ha='center', va='bottom', fontsize=8)

# Mostrar valores en predicción
for i, v in enumerate(pred):
    plt.text(len(df)+i, v, f'{v/1_000_000:.0f}M', ha='center', va='bottom', fontsize=8)

plt.title("Prediccion de ventas mensuales")
plt.xlabel("Periodo")
plt.ylabel("Ventas (Millones)")
plt.xticks(rotation=45)

plt.legend()
plt.tight_layout()

plt.savefig("prediccion_ventas.png")
plt.close()

print("Grafico de prediccion generado")

####################################################
# 9 SEGMENTACION DE MERCADO (CLUSTERING)
####################################################

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

query = """
SELECT
    s.ciudad,
    p.categoria,
    SUM(f.ingreso) AS ventas
FROM fact_ventas f
JOIN dim_sucursal s ON f.sucursal_id = s.sucursal_id
JOIN dim_producto p ON f.producto_id = p.producto_id
GROUP BY s.ciudad, p.categoria
"""

df = pd.read_sql(query, conn)

# ---------------------------------
# Convertir a matriz ciudad x categoria
# ---------------------------------

tabla = df.pivot_table(
    index="ciudad",
    columns="categoria",
    values="ventas",
    fill_value=0
)

# ---------------------------------
# Escalar datos
# ---------------------------------

scaler = StandardScaler()
X_scaled = scaler.fit_transform(tabla)

# ---------------------------------
# Aplicar K-Means
# ---------------------------------

kmeans = KMeans(n_clusters=3, random_state=42)
clusters = kmeans.fit_predict(X_scaled)

tabla["cluster"] = clusters

# ---------------------------------
# Producto preponderante por region
# ---------------------------------

producto_preponderante = tabla.drop("cluster", axis=1).idxmax(axis=1)

resultado = pd.DataFrame({
    "region": tabla.index,
    "producto_preponderante": producto_preponderante,
    "cluster": clusters
})

print("\nSegmentacion de mercado:")
print(resultado)


resultado.to_excel("segmentacion_mercado.xlsx", index=False)

print("Segmentacion de mercado con clustering generada")

###################################################

conn.close()

print("TODOS LOS REPORTES GENERADOS")