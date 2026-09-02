# Datos de tu contrato de Turismo
paga_base = 9.06
recargo_festivo = 0.20 # Esto es el 20%
# preguntamos cuántas horas has trabajaste
horas = input("¿Cuántas horas festivas trabajaste? ")
horas_float = float(horas) # Convertimos el texto a numero decimal
# Calculos
paga_por_hora_festiva = paga_base * (1 + recargo_festivo) # Calculamos la paga por hora festiva
total_dia = paga_por_hora_festiva * horas_float
print(f"Tu paga por hora festiva es: {paga_por_hora_festiva: .2f}€")
print(f"{horas_float} horas, cobraras: {total_dia: 0.2f}€ brutos")