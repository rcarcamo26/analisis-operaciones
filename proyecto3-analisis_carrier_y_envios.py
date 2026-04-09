import pandas as pd
import matplotlib.pyplot as plt
import sqlite3

df = pd.read_csv("shipments.csv")
print(df.head())

# Formato de fecha en ship_date y delivery_date
df['ship_date'] = pd.to_datetime(df['ship_date'])
df['delivery_date'] = pd.to_datetime(df['delivery_date'])

# Columna delivery_time
df["delivery_time"] = (df["delivery_date"] - df["ship_date"]).dt.days
df["delay_flag"] = (df["delivery_status"] == "Late").astype(int)

top_city_delay = df.groupby("destination_city")["delay_flag"].agg(["mean", "count"])
top_city_delay["delay_pct"] = top_city_delay["mean"] * 100
print(top_city_delay.sort_values("delay_pct", ascending=False))
print(top_city_delay)

carrier = df.groupby("carrier").agg({
    "delivery_time": "mean",
    "delay_flag": "mean",
    "shipping_cost": "mean",
    "order_id": "count"
})
carrier["delay_pct"] = carrier["delay_flag"] * 100
print(carrier)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

cost_prom = df.groupby("carrier")["shipping_cost"].mean()
cost_prom.plot(kind="bar", ax=ax1)
ax1.set_title("Costo Promedio por Carrier", fontweight="bold")
ax1.set_ylabel("Costo")

delivery_time_prom = df.groupby("carrier")["delivery_time"].mean()
delivery_time_prom.plot(kind="bar", ax=ax2)
ax2.set_title("Tiempo Promedio por Carrier", fontweight="bold")
ax2.set_ylabel("Tiempo")

plt.tight_layout()
plt.show()

conn = sqlite3.connect("shipments.db")
shipments = pd.read_csv("shipments.csv")
shipments.to_sql("shipments", conn, if_exists="replace", index=False)
resultado = pd.read_sql("""
    SELECT carrier,  
    AVG(JULIANDAY(delivery_date) - JULIANDAY(ship_date)) as promedio_dias_retraso, 
    MAX(JULIANDAY(delivery_date) - JULIANDAY(ship_date)) as max_dias_retraso,
    AVG(shipping_cost) as costo_promedio,
    AVG(CASE WHEN delivery_status = 'On time' THEN 1 ELSE 0 END) * 100 as entregas_a_tiempo,  
    AVG(CASE WHEN delivery_status = 'Late' THEN 1 ELSE 0 END) * 100 as entregas_retrasadas, 
    COUNT(order_id) as volumen_carrier,
    SUM(distance_km) as distancia_recorrida,
    AVG(distance_km) as distancia_recorrida_prom
    FROM shipments
    GROUP BY carrier
    ORDER BY volumen_carrier DESC
""", conn) 
pd.set_option("display.max_columns", None)
print(resultado)











