import sqlite3
from datetime import datetime

horas = float(input("¿Cuantas horas hiciste hoy?: "))
paga_hora = 10.87
paga_hoy = horas * paga_hora

conexion = sqlite3.connect('mis_pagos.db')
cursor = conexion.cursor()

fecha_hoy = datetime.now().strftime("%Y-%m-%d")

cursor.execute("INSERT INTO registro_horas (fecha, horas, paga_total) VALUES  (?, ?, ?)",
               (fecha_hoy, horas, paga_hoy))
conexion.commit()
conexion.close()
print(f"Guardado: {horas} horas del dia {fecha_hoy}. Total hoy: {paga_hoy: .2f}€")