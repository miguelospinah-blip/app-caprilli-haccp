dias = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
horas_totales = 0
paga_por_hora = 10.87
print("---REGISTRO SEMANAL DE HORAS---")
for dia in dias:
    respuesta = input(f"¿Cuantas horas hiciste el {dia}?: ")
    horas_totales = horas_totales + float(respuesta)
    paga_total = horas_totales * paga_por_hora
print("-" * 30)
print(f"Total de horas de la semana: {horas_totales}")
print(f"Tu pagatotal estimada de la semana es de: {paga_total: .2f}€")