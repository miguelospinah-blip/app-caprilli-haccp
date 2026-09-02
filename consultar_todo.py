import sqlite3

conexion = sqlite3.connect('mis_pagos.db')
cursor = conexion.cursor()

cursor.execute("SELECT * FROM registro_horas")
filas = cursor.fetchall()

print("---HISTORIAL DE PAGOS---")
print(f"{'ID':<5} {'Fecha':<12} {'Horas':<8} {'Pago Total (€)'}")
print("-" * 40)

for fila in filas:
    print (f"{fila[0]:<5} {fila[1]:<12} {fila[2]:<8} {fila[3]:.2f}"
           )
    
conexion.close()