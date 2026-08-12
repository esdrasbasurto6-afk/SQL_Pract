```md
# SQL Pract — Data Warehouse y Análisis de Ventas

Proyecto de diseño y análisis de un **Data Warehouse de ventas**. Incluye la creación de una base de datos dimensional en MySQL, generación de datos sintéticos y análisis con Python, SQL y Machine Learning.

## Características

- Diseño de un esquema estrella para análisis de ventas.
- Base de datos MySQL con tablas de hechos y dimensiones.
- Generación de más de 2 millones de registros de ventas simuladas.
- Análisis de ventas por sucursal, producto, cliente, categoría y temporada.
- Identificación de productos más rentables y con bajo margen de ganancia.
- Detección de sucursales con caída de ventas.
- Segmentación de clientes y mercados mediante K-Means.
- Predicción de ventas mensuales mediante regresión lineal.
- Generación de reportes en Excel, CSV y gráficas PNG.

## Modelo de datos

El Data Warehouse utiliza una tabla de hechos y las siguientes dimensiones:

- `fact_ventas`
- `dim_tiempo`
- `dim_cliente`
- `dim_producto`
- `dim_sucursal`
- `dim_empleado`
- `dim_canal`

## Tecnologías

- MySQL
- SQL
- Python
- Pandas
- NumPy
- Scikit-learn
- Matplotlib
- Faker
- MySQL Connector

## Reportes generados

- Ventas mensuales por sucursal.
- Sucursales con disminución de ventas.
- Productos más rentables.
- Productos con margen menor al 10%.
- Clientes más frecuentes.
- Clientes candidatos a descuentos.
- Temporadas de mayor venta por categoría.
- Clasificación de clientes: Premium, Frecuente y Ocasional.
- Predicción de ventas para los próximos tres meses.
- Segmentación de mercado por ciudad y categoría.

## Instalación

1. Clona el repositorio:

   ```bash
   git clone <URL_DEL_REPOSITORIO>
   cd SQL_Pract-main
   ```

2. Crea la base de datos ejecutando el archivo `base.sql` en MySQL.

3. Instala las dependencias de Python:

   ```bash
   pip install mysql-connector-python pandas numpy matplotlib scikit-learn faker tqdm openpyxl
   ```

4. Configura tus credenciales de MySQL en los archivos `seeder.py` y `analisis_ventas.py`.

5. Genera los datos simulados:

   ```bash
   python seeder.py
   ```

6. Ejecuta el análisis:

   ```bash
   python analisis_ventas.py
   ```

Los reportes y gráficas se guardarán automáticamente en archivos `.xlsx`, `.csv` y `.png`.

## Autor

**Esdras Josué Basurto Sandoval**  
[GitHub](https://github.com/esdrasbasurto6-afk)
```
