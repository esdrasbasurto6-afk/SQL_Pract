import mysql.connector
import random
from faker import Faker
from tqdm import tqdm
from datetime import datetime, timedelta

fake = Faker()

# CONEXION A LA BASEDE DATOS 
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="dw_ventas"
)

cursor = conn.cursor()


start_date = datetime(2019,1,1)
end_date = datetime(2025,12,31)

delta = end_date - start_date
tiempo_id = 1

for i in range(delta.days + 1):
    fecha = start_date + timedelta(days=i)

    cursor.execute("""
        INSERT INTO dim_tiempo VALUES (%s,%s,%s,%s,%s,%s,%s)
    """, (
        tiempo_id,
        fecha,
        fecha.year,
        fecha.month,
        fecha.day,
        (fecha.month-1)//3 + 1,
        fecha.strftime("%B")
    ))

    tiempo_id += 1

conn.commit()
print("Tiempo cargado")



for i in range(50000):
    cursor.execute("""
        INSERT INTO dim_cliente
        (nombre,genero,edad,ciudad,estado,pais,segmento)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
    """, (
        fake.name(),
        random.choice(["M","F"]),
        random.randint(18,75),
        fake.city(),
        fake.state(),
        "México",
        random.choice(["Premium","Regular","Básico"])
    ))

conn.commit()
print("Clientes cargados")



for i in range(5000):
    cursor.execute("""
        INSERT INTO dim_producto
        (nombre,categoria,subcategoria,marca,precio)
        VALUES (%s,%s,%s,%s,%s)
    """, (
        fake.word().capitalize(),
        random.choice(["Electrónica","Ropa","Hogar","Alimentos","Oficina"]),
        fake.word(),
        fake.company(),
        round(random.uniform(50,5000),2)
    ))

conn.commit()
print("Productos cargados")



for i in range(300):
    cursor.execute("""
        INSERT INTO dim_sucursal
        (nombre,ciudad,estado,pais,tipo)
        VALUES (%s,%s,%s,%s,%s)
    """, (
        f"Sucursal {i+1}",
        fake.city(),
        fake.state(),
        "México",
        random.choice(["Tienda","Express","Mayorista"])
    ))

conn.commit()



for i in range(5000):
    cursor.execute("""
        INSERT INTO dim_empleado
        (nombre,puesto,antiguedad,salario)
        VALUES (%s,%s,%s,%s)
    """, (
        fake.name(),
        random.choice(["Vendedor","Supervisor","Gerente"]),
        random.randint(1,20),
        round(random.uniform(8000,40000),2)
    ))

conn.commit()



canales = ["Web","App","Mostrador","Teléfono","Marketplace"]

for c in canales:
    cursor.execute("""
        INSERT INTO dim_canal (nombre,tipo)
        VALUES (%s,%s)
    """,(c,"Digital" if c in ["Web","App"] else "Físico"))

conn.commit()



TOTAL = 2_000_000
BATCH = 10000

print("Insertando ventas...")

for i in tqdm(range(0, TOTAL, BATCH)):

    datos = []

    for j in range(BATCH):

        cantidad = random.randint(1,10)
        precio = random.uniform(50,5000)

        ingreso = cantidad * precio
        descuento = ingreso * random.uniform(0,0.15)
        costo = ingreso * random.uniform(0.5,0.8)
        ganancia = ingreso - descuento - costo

        datos.append((
            random.randint(1,tiempo_id-1),
            random.randint(1,50000),
            random.randint(1,5000),
            random.randint(1,300),
            random.randint(1,5000),
            random.randint(1,5),
            cantidad,
            round(ingreso,2),
            round(descuento,2),
            round(costo,2),
            round(ganancia,2)
        ))

    cursor.executemany("""
        INSERT INTO fact_ventas
        (tiempo_id,cliente_id,producto_id,sucursal_id,empleado_id,canal_id,
         cantidad,ingreso,descuento,costo,ganancia)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, datos)

    conn.commit()

print("Carga terminada")

cursor.close()
conn.close()