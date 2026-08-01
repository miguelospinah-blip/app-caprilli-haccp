import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="HACCP Caprilli", page_icon="🍦")

st.title("Controllo Temperature HACCP 🍦")
st.caption("Caprilli Gelateria Naturale")

# --- CONEXIÓN CON GOOGLE SHEETS ---
def obtener_hoja():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    
    # Extraemos directamente los campos desde st.secrets
    if "gcp_service_account" in st.secrets:
        info = st.secrets["gcp_service_account"]
    else:
        info = st.secrets

    # Creamos un diccionario formateado asegurando saltos de línea limpios
    creds_dict = {
        "type": info["type"],
        "project_id": info["project_id"],
        "private_key_id": info["private_key_id"],
        "private_key": info["private_key"].replace("\\n", "\n"),
        "client_email": info["client_email"],
        "client_id": info["client_id"],
        "auth_uri": info["auth_uri"],
        "token_uri": info["token_uri"],
        "auth_provider_x509_cert_url": info["auth_provider_x509_cert_url"],
        "client_x509_cert_url": info["client_x509_cert_url"]
    }
    
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    return client.open("Base_Datos_HACCP").sheet1

# --- EVALUACIÓN INTERNA PARA EL REGISTRO HACCP ---
def evaluar_temperatura(equipo, valor):
    if valor == "Non in uso":
        return "Non in uso"
    
    val = float(valor)
    equipo_lower = equipo.lower()

    # Congeladores, Vaschette, Vetrine, Banche o Celli Negativi (Límite máximo -10.0°C)
    if any(k in equipo_lower for k in ["conservatore", "congelatore", "vetrina", "banco", "cella"]):
        if "cioccolato" not in equipo_lower and "latte" not in equipo_lower and "materie" not in equipo_lower:
            return "⚠ FUORI NORMA" if val > -10.0 else "OK Congelatore"

    # Maquinaria en Caliente / Atemperadoras (Laboratorio Cioccolato)
    if "scioglitrice" in equipo_lower or "temperatrice" in equipo_lower:
        return "⚠ FUORI NORMA" if (val < 20.0 or val > 50.0) else "OK Caldo"

    # Frigos normales / Materias Primas / Refrigeración (Límite máximo +6.0°C)
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
    
    # Maquinaria específica por Sede
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
        
        # 1. Mantecatore 2
        uso_m2 = st.checkbox("Mantecatore 2 (Yogurt/Conservazione) in uso", value=True)
        if uso_m2:
            lecturas["Mantecatore 2"] = st.number_input("Temp. Mantecatore 2 (°C)", value=4.0, step=0.5, format="%.1f")
        else:
            lecturas["Mantecatore 2"] = "Non in uso"

        # 2. Pastorizzatore 1 Icetech
        uso_past1 = st.checkbox("Pastorizzatore 1 (Icetech) in uso", value=True)
        if uso_past1:
            lecturas["Pastorizzatore 1 Icetech"] = st.number_input("Temp. Pastorizzatore 1 (°C)", value=4.0, step=0.5, format="%.1f")
        else:
            lecturas["Pastorizzatore 1 Icetech"] = "Non in uso"

        # 3. Pastorizzatore 2 Carpigiani
        uso_past2 = st.checkbox("Pastorizzatore 2 (Carpigiani) in uso", value=True)
        if uso_past2:
            lecturas["Pastorizzatore 2 (Carpigiani)"] = st.number_input("Temp. Pastorizzatore 2 (°C)", value=4.0, step=0.5, format="%.1f")
        else:
            lecturas["Pastorizzatore 2 (Carpigiani)"] = "Non in uso"

        # 4. Pastochef
        uso_pastochef = st.checkbox("Pastochef (Yogurt/Creme) in uso", value=True)
        if uso_pastochef:
            lecturas["Pastochef"] = st.number_input("Temp. Pastochef (°C)", value=4.0, step=0.5, format="%.1f")
        else:
            lecturas["Pastochef"] = "Non in uso"

    elif sede == "Laboratorio Cioccolato":
        st.write("🌡️ **Inserisci le temperature (Laboratorio Cioccolato):**")
        
        # Equipos Fríos / Conservación
        lecturas["Frigo 1"] = st.number_input("Frigo 1 (°C)", value=-13.0, step=0.5, format="%.1f")
        lecturas["Frigo 2"] = st.number_input("Frigo 2 (°C)", value=-13.0, step=0.5, format="%.1f")
        lecturas["Frigo 3"] = st.number_input("Frigo 3 (°C)", value=-13.0, step=0.5, format="%.1f")
        lecturas["Frigo 4"] = st.number_input("Frigo 4 (°C)", value=-13.0, step=0.5, format="%.1f")
        lecturas["Congelatore"] = st.number_input("Cngelatore (°C)", value=-13.0, step=0.5, format="%.1f")
     

    elif sede == "Laboratorio Pasticceria":
        st.write("🌡️ **Inserisci le temperature del locale (Laboratorio Pasticceria):**")
        lecturas["Cella Frigo"] = st.number_input("Cella Frigo (°C)", value=-18.0, step=0.5, format="%.1f")
        lecturas["Cella 1"] = st.number_input("Cella 1 (°C)", value=-18.0, step=0.5, format="%.1f")
        lecturas["Cella 2"] = st.number_input("Cella 2 (°C)", value=-18.0, step=0.5, format="%.1f")
        lecturas["Frigo armadietti"]  = st.number_input("Frigo armadietti (°C)", value=-15.0, step=0.5, format="%.1f")

    # BOTÓN ÚNICO DE ENVÍO
    submit = st.form_submit_button("🚀 Invia e Salva Registro")
    if submit:
        ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Estructuramos las filas para la base de datos (incluyendo la evaluación interna Stato)
        filas_nuevas = []
        for equipo, temp in lecturas.items():
            stato_temp = evaluar_temperatura(equipo, temp)
            filas_nuevas.append([ahora, sede, equipo, str(temp), operatore, stato_temp])
        
        df_nuevo = pd.DataFrame(filas_nuevas, columns=["Fecha_Hora", "Sede", "Equipo", "Temperatura", "Operatore", "Stato"])
        
        try:
            hoja = obtener_hoja()
            
            # Insertamos fila por fila al final del Google Sheet
            for fila in filas_nuevas:
                hoja.append_row(fila)
            
            st.success(f"✅ Registrate con successo {len(lecturas)} temperature per {sede}!")
            st.dataframe(df_nuevo)
            
        except Exception as e:
            st.error("❌ Errore durante il salvataggio nel database.")
            st.exception(e)
