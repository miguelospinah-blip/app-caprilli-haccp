import sqlite3

conexion = sqlite3.connect('mis_pagos.db')
cursor = conexion.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS registro_horas (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        fecha TEXT, 
        horas REAL, 
        paga_total REAL
    )
''')
conexion.commit()
conexion.close()
print("¡Base de datos lista!")