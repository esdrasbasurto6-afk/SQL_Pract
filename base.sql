CREATE DATABASE IF NOT EXISTS dw_ventas;
USE dw_ventas;

CREATE TABLE dim_tiempo (
    tiempo_id INT PRIMARY KEY,
    fecha DATE,
    anio INT,
    mes INT,
    dia INT,
    trimestre INT,
    nombre_mes VARCHAR(20)
);

CREATE TABLE dim_cliente (
    cliente_id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100),
    genero VARCHAR(10),
    edad INT,
    ciudad VARCHAR(100),
    estado VARCHAR(100),
    pais VARCHAR(100),
    segmento VARCHAR(50)
);

CREATE TABLE dim_producto (
    producto_id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100),
    categoria VARCHAR(100),
    subcategoria VARCHAR(100),
    marca VARCHAR(100),
    precio DECIMAL(10,2)
);



CREATE TABLE dim_sucursal (
    sucursal_id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100),
    ciudad VARCHAR(100),
    estado VARCHAR(100),
    pais VARCHAR(100),
    tipo VARCHAR(50)
);
CREATE TABLE dim_empleado (
    empleado_id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100),
    puesto VARCHAR(100),
    antiguedad INT,
    salario DECIMAL(10,2)
);
CREATE TABLE dim_canal (
    canal_id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50),
    tipo VARCHAR(50)
);

CREATE TABLE fact_ventas (
    venta_id BIGINT AUTO_INCREMENT PRIMARY KEY,

    tiempo_id INT,
    cliente_id INT,
    producto_id INT,
    sucursal_id INT,
    empleado_id INT,
    canal_id INT,

    cantidad INT,
    ingreso DECIMAL(12,2),
    descuento DECIMAL(12,2),
    costo DECIMAL(12,2),
    ganancia DECIMAL(12,2),

    FOREIGN KEY (tiempo_id) REFERENCES dim_tiempo(tiempo_id),
    FOREIGN KEY (cliente_id) REFERENCES dim_cliente(cliente_id),
    FOREIGN KEY (producto_id) REFERENCES dim_producto(producto_id),
    FOREIGN KEY (sucursal_id) REFERENCES dim_sucursal(sucursal_id),
    FOREIGN KEY (empleado_id) REFERENCES dim_empleado(empleado_id),
    FOREIGN KEY (canal_id) REFERENCES dim_canal(canal_id)
);

CREATE INDEX idx_fecha ON dim_tiempo(fecha);
CREATE INDEX idx_cliente ON fact_ventas(cliente_id);
CREATE INDEX idx_producto ON fact_ventas(producto_id);
CREATE INDEX idx_tiempo ON fact_ventas(tiempo_id);