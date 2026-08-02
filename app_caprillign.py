import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="HACCP Caprilli", page_icon="🍦")

st.title("Controllo Temperature HACCP 🍦")
st.caption("Caprilli Gelateria Naturale")

# --- CONEXIÓN DIRECTA CON GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- EVALUACIÓN INTERNA PARA EL REGISTRO HACCP ---
def evaluar_temperatura(equipo, valor):
    if valor == "Non in uso":
        return "Non in uso"
    
    val = float(valor)
    equipo_lower = equipo.lower()

    if any(k in equipo_lower for k in ["conservatore", "congelatore", "vetrina", "banco", "cella"]):
        if "cioccolato" not in equipo_lower and "latte" not in equipo_lower and "materie" not in equipo_lower:
            return "⚠ FUORI NORMA" if val > -10.0 else "OK Congelatore"

    if "scioglitrice" in equipo_lower or "temperatrice" in equipo_lower:
        return "⚠ FUORI NORMA" if (val < 20.0 or val > 50.0) else "OK Caldo"

    return "⚠ FUORI NORMA" if val > 6.0 else "OK Frigo"

# --- 2. SELECTOR DE SEDE ---
sede = st.selectbox("Seleziona la sede / reparto:", [
    "Laboratorio Cioccolato", 
    "Laboratorio Gelato", 
    "Laboratorio Pasticceria", 
    "Viale Italia", 
    "Cavour"
])

st.markdown(f"### Registrazione per: **{sede}**")

# --- 3. FORMULARIO UNIFICADO ---
with st.form(key=f"form_haccp_{sede}"):
    operatore = st.selectbox("Nome Operatore:", ["Alessandra", "Chiara", "Miguel", "Ricardo", "Tommaso", "Francesco", "Matilde", "Giorgia", "Linda", "Manuel", "Luduvica", "Asia", "Edoardo"])
    st.divider()
    
    lecturas = {}
    
    if sede == "Viale Italia":
        st.write("🌡️ **Inserisci le temperature del locale (Viale Italia):**")
        lecturas["Vetrina 1"] = st.number_input("Vetrina 1 (°C)", value=-18.0, step=0.5, format="%.1f")
        lecturas["Vetrina 2"] = st.number_input("Vetrina 2 (°C)", value=-18.0, step=0.5, format="%.1f")
        lecturas["Vetrina 3"] = st.number_input("Vetrina 3 (°C)", value=-18.0, step=0.5, format="%.1f")
        lecturas["Frigo Banco"] = st.number_input("Frigo Banco(°C)", value=-18.0, step=0.5, format="%.1f")
        lecturas["Banco 1"] = st.number_input("Banco 1 (°C)", value=-18.0, step=0.5, format="%.1f")
        lecturas["Banco 2"] = st.number_input("Banco 2 (°C)", value=-18.0, step=0.5, format="%.1f")
        lecturas["Granite"] = st.number_input("Ganite (°C)", value=-18.0, step=0.5, format="%.1f")
        lecturas["Panna"] = st.number_input("Panna (°C)", value=-18.0, step=0.5, format="%.1f")
        lecturas["Farciture"] = st.number_input("Farciture (°C)", value=-18.0, step=0.5, format="%.1f")
        lecturas["Yogurt"] = st.number_input("Yogurt (°C)", value=-18.0, step=0.5, format="%.1f")
        lecturas["Vetrina Cioccolato 1"] = st.number_input("Vetrina Cioccolato 1 (°C)", value=-18.0, step=0.5, format="%.1f")
        lecturas["Vetrina Cioccolato 2"] = st.number_input("Vetrina Cioccolato 2 (°C)", value=-18.0, step=0.5, format="%.1f")

    elif sede == "Cavour":
        st.write("🌡️ **Inserisci le temperature del locale (Cavour):**")
        lecturas["Vetrina 1"] = st.number_input("Vetrina 1 (°C)", value=-18.0, step=0.5, format="%.1f")
        lecturas["Vetrina 2"] = st.number_input("Vetrina 2 (°C)", value=-18.0, step=0.5, format="%.1f")
        lecturas["Vetrina 3"] = st.number_input("Vetrina 3 (°C)", value=-18.0, step=0.5, format="%.1f")
        lecturas["Vetrina 4"] = st.number_input("Vetrina 4 (°C)", value=-18.0, step=0.5, format="%.1f")
        lecturas["Frigo Banco"] = st.number_input("Frigo Banco(°C)", value=-18.0, step=0.5, format="%.1f")
        lecturas["Banco 1"] = st.number_input("Banco 1 (°C)", value=-18.0, step=0.5, format="%.1f")
        lecturas["Banco 2"] = st.number_input("Banco 2 (°C)", value=-18.0, step=0.5, format="%.1f")
        lecturas["Granite"] = st.number_input("Ganite (°C)", value=-18.0, step=0.5, format="%.1f")
        lecturas["Panna"] = st.number_input("Panna (°C)", value=-18.0, step=0.5, format="%.1f")
        lecturas["Farciture"] = st.number_input("Farciture (°C)", value=-18.0, step=0.5, format="%.1f")
        lecturas["Yogurt"] = st.number_input("Yogurt (°C)", value=-18.0, step=0.5, format="%.1f")

    elif sede == "Laboratorio Gelato":
        st.write("🌡️ **Inserisci le temperature (Laboratorio Gelato):**")
        lecturas["Conservatore Negativo 1"] = st.number_input("Conservatore Negativo 1 (°C)", value=-13.0, step=0.5, format="%.1f")
        lecturas["Conservatore Negativo 2"] = st.number_input("Conservatore Negativo 2 (°C)", value=-13.0, step=0.5, format="%.1f")
        lecturas["Frigo Materie prime 1"]   = st.number_input("Frigo Latte/Materie Prime 1 (°C)", value=4.0, step=0.5, format="%.1f")
        lecturas["Frigo Materie prime 2"]   = st.number_input("Frigo Latte/Materie Prime 2 (°C)", value=4.0, step=0.5, format="%.1f")
        
        st.divider()
        st.write("⚙️ **Macchine di Lavorazione / Pastorizzazione:**")
        
        uso_m2 = st.checkbox("Mantecatore 2 (Yogurt/Conservazione) in uso", value=True)
        if uso_m2:
            lecturas["Mantecatore 2"] = st.number_input("Temp. Mantecatore 2 (°C)", value=4.0, step=0.5, format="%.1f")
        else:
            lecturas["Mantecatore 2"] = "Non in uso"

        uso_past1 = st.checkbox("Pastorizzatore 1 (Icetech) in uso", value=True)
        if uso_past1:
            lecturas["Pastorizzatore 1 Icetech"] = st.number_input("Temp. Pastorizzatore 1 (°C)", value=4.0, step=0.5, format="%.1f")
        else:
            lecturas["Pastorizzatore 1 Icetech"] = "Non in uso"

        uso_past2 = st.checkbox("Pastorizzatore 2 (Carpigiani) in uso", value=True)
        if uso_past2:
            lecturas["Pastorizzatore 2 (Carpigiani)"] = st.number_input("Temp. Pastorizzatore 2 (°C)", value=4.0, step=0.5, format="%.1f")
        else:
            lecturas["Pastorizzatore 2 (Carpigiani)"] = "Non in uso"

        uso_pastochef = st.checkbox("Pastochef (Yogurt/Creme) in uso", value=True)
        if uso_pastochef:
            lecturas["Pastochef"] = st.number_input("Temp. Pastochef (°C)", value=4.0, step=0.5, format="%.1f")
        else:
            lecturas["Pastochef"] = "Non in uso"

    elif sede == "Laboratorio Cioccolato":
        st.write("🌡️ **Inserisci le temperature (Laboratorio Cioccolato):**")
        
        lecturas["Frigo 1"] = st.number_input("Frigo 1 (°C)", value=-13.0, step=0.5, format="%.1f")
        lecturas["Frigo 2"] = st.number_input("Frigo 2 (°C)", value=-13.0, step=0.5, format="%.1f")
        lecturas["Frigo 3"] = st.number_input("Frigo 3 (°C)", value=-13.0, step=0.5, format="%.1f")
        lecturas["Frigo 4"] = st.number_input("Frigo 4 (°C)", value=-13.0, step=0.5, format="%.1f")
        lecturas["Congelatore"] = st.number_input("Congelatore (°C)", value=-13.0, step=0.5, format="%.1f")

    elif sede == "Laboratorio Pasticceria":
        st.write("🌡️ **Inserisci le temperature del locale (Laboratorio Pasticceria):**")
        lecturas["Cella Frigo"] = st.number_input("Cella Frigo (°C)", value=-18.0, step=0.5, format="%.1f")
        lecturas["Cella 1"] = st.number_input("Cella 1 (°C)", value=-18.0, step=0.5, format="%.1f")
        lecturas["Cella 2"] = st.number_input("Cella 2 (°C)", value=-18.0, step=0.5, format="%.1f")
        lecturas["Frigo armadietti"]  = st.number_input("Frigo armadietti (°C)", value=-15.0, step=0.5, format="%.1f")

    submit = st.form_submit_button("🚀 Invia e Salva Registro")
    if submit:
        ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        filas_nuevas = []
        for equipo, temp in lecturas.items():
            stato_temp = evaluar_temperatura(equipo, temp)
            filas_nuevas.append({
                "Fecha_Hora": ahora,
                "Sede": sede,
                "Equipo": equipo,
                "Temperatura": str(temp),
                "Operatore": operatore,
                "Stato": stato_temp
            })
        
        df_nuevo = pd.DataFrame(filas_nuevas)
        
        try:
            # Lee datos existentes y añade las filas nuevas
            existing_data = conn.read(worksheet="Foglio1", ttl=0)
            updated_df = pd.concat([existing_data, df_nuevo], ignore_index=True)
            conn.update(worksheet="Foglio1", data=updated_df)
            
            st.success(f"✅ Registrate con successo {len(lecturas)} temperature per {sede}!")
            st.dataframe(df_nuevo)
            
        except Exception as e:
            st.error("❌ Errore durante il salvataggio nel database.")
            st.exception(e)
