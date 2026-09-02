import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="HACCP & ERP Caprilli", page_icon="🍦", layout="centered")

# --- 1. BARRA LATERAL: CONTROL DE ACCESOS Y SEGURIDAD POR CONTRASEÑA ---
st.sidebar.title("🔐 Accesso Sistema")
rol_seleccionado = st.sidebar.selectbox("Seleziona Ruolo:", ["Operatore (Base)", "Leader (Consultazione)", "Admin (Gestione Totale)"])

rol = None  # Inicializamos el rol definitivo

if rol_seleccionado == "Operatore (Base)":
    rol = "Operatore (Base)"
    st.sidebar.success("✅ Accesso operatore attivo")

elif rol_seleccionado == "Leader (Consultazione)":
    st.sidebar.divider()
    st.sidebar.write("🔒 **Area protetta per la Dirigenza**")
    password_leader = st.sidebar.text_input("Inserisci password Leader:", type="password")
    
    if password_leader == "Caprilli2026!":
        rol = "Leader (Consultazione)"
        st.sidebar.success("✅ Autenticato come Leader")
    elif password_leader != "":
        st.sidebar.error("❌ Password errata")

elif rol_seleccionado == "Admin (Gestione Totale)":
    st.sidebar.divider()
    st.sidebar.write("🛡️ **Area Riservata Amministratore**")
    password_admin = st.sidebar.text_input("Inserisci password Admin:", type="password")
    
    if password_admin == "AdminCaprilli99*":
        rol = "Admin (Gestione Totale)"
        st.sidebar.success("✅ Accesso Admin Autorizzato")
    elif password_admin != "":
        st.sidebar.error("❌ Password errata")

st.sidebar.divider()
st.sidebar.info(f"Profilo attivo: **{rol if rol else 'In attesa di autenticazione'}**")

# --- LOGO Y TÍTULO CENTRADOS ---
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    try:
        st.image("Logo.png", use_container_width=True)
    except Exception:
        pass

st.markdown("<h1 style='text-align: center;'>Portale Operativo Caprilli 🍦</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>Caprilli Gelateria Naturale</p>", unsafe_allow_html=True)
st.divider()

# --- CONEXIÓN DIRECTA CON GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

# Aseguramos que la clave privada cargue los saltos de línea correctamente si vienen alterados
try:
    if "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
        if "private_key" in st.secrets["connections"]["gsheets"]:
            st.secrets["connections"]["gsheets"]["private_key"] = st.secrets["connections"]["gsheets"]["private_key"].replace("\\n", "\n")
except Exception:
    pass

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


# =====================================================================
# VISTA 1: ROL OPERATORE (Con selección entre Temperatura y Producción)
# =====================================================================
if rol == "Operatore (Base)":
    
    if 'modo_operatore' not in st.session_state:
        st.session_state.modo_operatore = "menu"

    if st.session_state.modo_operatore == "menu":
        st.markdown("### Seleziona l'attività da svolgere:")
        
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            if st.button("🌡️ REGISTRAZIONE TEMPERATURA", use_container_width=True):
                st.session_state.modo_operatore = "temperatura"
                st.rerun()
        with col_m2:
            if st.button("🍦 REGISTRAZIONE PRODUZIONE", use_container_width=True):
                st.session_state.modo_operatore = "produzione_menu"
                st.rerun()

    # --- SUB-MODO: TEMPERATURAS ---
    elif st.session_state.modo_operatore == "temperatura":
        if st.button("⬅ Torna al Menu Principale"):
            st.session_state.modo_operatore = "menu"
            st.rerun()
            
        sede = st.selectbox("Seleziona la sede / reparto:", [
            "Seleziona la sede",
            "Laboratorio Cioccolato", 
            "Laboratorio Gelato", 
            "Laboratorio Pasticceria", 
            "Viale Italia", 
            "Cavour"
        ])

        if sede == "Seleziona la sede":
            st.warning("⚠️ Per favore, seleziona una sede o reparto per continuare.")
        else:
            st.markdown(f"### Registrazione per: **{sede}**")

            with st.form(key=f"form_haccp_{sede}"):
                operatore = st.selectbox("Nome Operatore:", ["Seleziona il tuo nome", "Alessandra", "Chiara", "Miguel", "Antonio", "Ricardo", "Tommaso", "Francesco", "Matilde", "Giorgia", "Linda", "Manuel", "Luduvica", "Asia", "Edoardo"])
                st.divider()
                
                lecturas = {}
                
                if sede == "Viale Italia":
                    st.write("🌡️ **Inserisci le temperature del locale (Viale Italia):**")
                    lecturas["Vetrina 1"] = st.number_input("Vetrina 1 (°C)", value=-18.0, step=0.5, format="%.1f")
                    lecturas["Vetrina 2"] = st.number_input("Vetrina 2 (°C)", value=-18.0, step=0.5, format="%.1f")
                    lecturas["Vetrina 3"] = st.number_input("Vetrina 3 (°C)", value=-18.0, step=0.5, format="%.1f")
                    lecturas["Frigo Banco"] = st.number_input("Frigo Banco (°C)", value=6.0, step=0.5, format="%.1f")
                    lecturas["Banco 1"] = st.number_input("Banco 1 (°C)", value=-18.0, step=0.5, format="%.1f")
                    lecturas["Banco 2"] = st.number_input("Banco 2 (°C)", value=-18.0, step=0.5, format="%.1f")
                    lecturas["Granite"] = st.number_input("Ganite (°C)", value=-18.0, step=0.5, format="%.1f")
                    lecturas["Panna"] = st.number_input("Panna (°C)", value=-18.0, step=0.5, format="%.1f")
                    lecturas["Farciture"] = st.number_input("Farciture (°C)", value=6.0, step=0.5, format="%.1f")
                    lecturas["Yogurt"] = st.number_input("Yogurt (°C)", value=-18.0, step=0.5, format="%.1f")
                    lecturas["Vetrina Cioccolato 1"] = st.number_input("Vetrina Cioccolato 1 (°C)", value=18.0, step=0.5, format="%.1f")
                    lecturas["Vetrina Cioccolato 2"] = st.number_input("Vetrina Cioccolato 2 (°C)", value=18.0, step=0.5, format="%.1f")

                elif sede == "Cavour":
                    st.write("🌡️ **Inserisci le temperature del locale (Cavour):**")
                    lecturas["Vetrina 1"] = st.number_input("Vetrina 1 (°C)", value=-18.0, step=0.5, format="%.1f")
                    lecturas["Vetrina 2"] = st.number_input("Vetrina 2 (°C)", value=-18.0, step=0.5, format="%.1f")
                    lecturas["Vetrina 3"] = st.number_input("Vetrina 3 (°C)", value=-18.0, step=0.5, format="%.1f")
                    lecturas["Vetrina 4"] = st.number_input("Vetrina 4 (°C)", value=-18.0, step=0.5, format="%.1f")
                    lecturas["Frigo Banco"] = st.number_input("Frigo Banco(°C)", value=6.0, step=0.5, format="%.1f")
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
                    lecturas["Frigo Materie prime 1"]   = st.number_input("Frigo Latte/Materie Prime 1 (°C)", value=6.0, step=0.5, format="%.1f")
                    lecturas["Frigo Materie prime 2"]   = st.number_input("Frigo Latte/Materie Prime 2 (°C)", value=6.0, step=0.5, format="%.1f")
                    
                    st.divider()
                    st.write("⚙️ **Macchine di Lavorazione / Pastorizzazione:**")
                    
                    uso_m2 = st.checkbox("Mantecatore 2 (Yogurt/Conservazione) in uso", value=True)
                    lecturas["Mantecatore 2"] = st.number_input("Temp. Mantecatore 2 (°C)", value=4.0, step=0.5, format="%.1f") if uso_m2 else "Non in uso"

                    uso_past1 = st.checkbox("Pastorizzatore 1 (Icetech) in uso", value=True)
                    lecturas["Pastorizzatore 1 Icetech"] = st.number_input("Temp. Pastorizzatore 1 (°C)", value=4.0, step=0.5, format="%.1f") if uso_past1 else "Non in uso"

                    uso_past2 = st.checkbox("Pastorizzatore 2 (Carpigiani) in uso", value=True)
                    lecturas["Pastorizzatore 2 (Carpigiani)"] = st.number_input("Temp. Pastorizzatore 2 (°C)", value=4.0, step=0.5, format="%.1f") if uso_past2 else "Non in uso"

                    uso_pastochef = st.checkbox("Pastochef (Yogurt/Creme) in uso", value=True)
                    lecturas["Pastochef"] = st.number_input("Temp. Pastochef (°C)", value=4.0, step=0.5, format="%.1f") if uso_pastochef else "Non in uso"

                elif sede == "Laboratorio Cioccolato":
                    st.write("🌡️ **Inserisci le temperature (Laboratorio Cioccolato):**")
                    lecturas["Frigo 1"] = st.number_input("Frigo 1 (°C)", value=-13.0, step=0.5, format="%.1f")
                    lecturas["Frigo 2"] = st.number_input("Frigo 2 (°C)", value=18.0, step=0.5, format="%.1f")
                    lecturas["Frigo 3"] = st.number_input("Frigo 3 (°C)", value=6.0, step=0.5, format="%.1f")
                    lecturas["Frigo 4"] = st.number_input("Frigo 4 (°C)", value=18.0, step=0.5, format="%.1f")
                    lecturas["Congelatore"] = st.number_input("Congelatore (°C)", value=-20.0, step=0.5, format="%.1f")

                elif sede == "Laboratorio Pasticceria":
                    st.write("🌡️ **Inserisci le temperature del locale (Laboratorio Pasticceria):**")
                    lecturas["Cella Frigo"] = st.number_input("Cella Frigo (°C)", value=6.0, step=0.5, format="%.1f")
                    lecturas["Cella 1"] = st.number_input("Cella 1 (°C)", value=-18.0, step=0.5, format="%.1f")
                    lecturas["Cella 2"] = st.number_input("Cella 2 (°C)", value=-18.0, step=0.5, format="%.1f")
                    lecturas["Frigo armadietti"]  = st.number_input("Frigo armadietti (°C)", value=6.0, step=0.5, format="%.1f")

                submit = st.form_submit_button("🚀 Invia e Salva Registro")
                if submit:
                    if operatore == "Seleziona il tuo nome":
                        st.error("❌ Per favore, seleziona il tuo nome operatore prima di inviare.")
                    else:
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
                            existing_data = conn.read(spreadsheet="Base_Datos_HACCP", worksheet="Foglio1", ttl=0)
                            updated_df = pd.concat([existing_data, df_nuevo], ignore_index=True)
                            conn.update(spreadsheet="Base_Datos_HACCP", worksheet="Foglio1", data=updated_df)
                            
                            st.success(f"✅ Registrate con successo {len(lecturas)} temperature per {sede}!")
                            st.dataframe(df_nuevo)
                            
                        except Exception as e:
                            st.error("❌ Errore durante il salvataggio nel database.")
                            st.exception(e)

    # --- SUB-MODO: MENÚ DE PRODUCCIÓN ---
    elif st.session_state.modo_operatore == "produzione_menu":
        if st.button("⬅ Torna al Menu Principale"):
            st.session_state.modo_operatore = "menu"
            st.rerun()
            
        st.markdown("### 🏭 Seleziona il Laboratorio per la Produzione:")
        
        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            if st.button("🍦 Laboratorio Gelato", use_container_width=True):
                st.session_state.modo_operatore = "prod_gelato"
                st.rerun()
        with col_p2:
            if st.button("🍫 Laboratorio Cioccolato", use_container_width=True):
                st.info("Modulo in sviluppo.")
        with col_p3:
            if st.button("🍰 Laboratorio Pasticceria", use_container_width=True):
                st.info("Modulo in sviluppo.")

    # --- SUB-MODO: PRODUCCIÓN LABORATORIO GELATO (Simplificado) ---
    elif st.session_state.modo_operatore == "prod_gelato":
        if st.button("⬅ Torna ai Laboratori"):
            st.session_state.modo_operatore = "produzione_menu"
            st.rerun()
            
        st.markdown("### 🍦 Registrazione Produzione - Laboratorio Gelato")
        st.info("💡 Inserisci semplicemente il gusto e i chili totali prodotti secondo la pesata.")
        
        with st.form("form_prod_gelato"):
            op_gelato = st.selectbox("Nome Operatore:", ["Seleziona il tuo nome", "Alessandra", "Chiara", "Miguel", "Antonio", "Ricardo", "Tommaso", "Francesco", "Matilde", "Giorgia", "Linda", "Manuel", "Luduvica", "Asia", "Edoardo"])
            
            sapore = st.selectbox("Seleziona Gusto / Preparazione:", [
                "Crema Diretta", "Pistacchio", "Cioccolato Fondente", "Nocciola", "Fior di latte", 
                "Stracciatella", "Brownie", "Cocco", "Meglio della Nutella", "Frutti di Bosco", "Caramello Salato", "Sciroppo / Base"
            ])
            
            kili = st.number_input("Chili totali prodotti (Kg):", min_value=0.5, max_value=100.0, value=11.0, step=0.5)
            note_prod = st.text_area("Note o numero lotto (opzionale):")
            
            submit_prod = st.form_submit_button("💾 Salva Produzione")
            
            if submit_prod:
                if op_gelato == "Seleziona il tuo nome":
                    st.error("❌ Per favore, seleziona il tuo nome operatore.")
                else:
                    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    df_prod = pd.DataFrame([{
                        "Data_Ora": ahora,
                        "Reparto": "Laboratorio Gelato",
                        "Operatore": op_gelato,
                        "Prodotto_Gusto": sapore,
                        "Kili_Prodotti": kili,
                        "Note": note_prod
                    }])
                    
                    try:
                        ex_prod = conn.read(spreadsheet="Base_Datos_HACCP", worksheet="Produzione_Gelato", ttl=0)
                        conn.update(spreadsheet="Base_Datos_HACCP", worksheet="Produzione_Gelato", data=pd.concat([ex_prod, df_prod], ignore_index=True))
                        st.success(f"✅ Registrati {kili} Kg di '{sapore}' con successo!")
                        st.dataframe(df_prod)
                    except Exception as e:
                        st.error("❌ Errore: Assicurati che esista un foglio chiamato 'Produzione_Gelato' nel tuo Google Sheets.")
                        st.exception(e)


# =====================================================================
# VISTA 2: ROL LEADER / JEFE (Dashboard BI + Consulta)
# =====================================================================
elif rol == "Leader (Consultazione)":
    st.subheader("📊 Dashboard Direttiva & Business Intelligence")
    st.info("Benvenuto Capo! Panoramica in tempo reale delle temperature e della produzione.")
    
    tab_temp, tab_prod = st.tabs(["🌡️ Monitoraggio Temperature", "🍦 Analisi Produzione (Kili)"])
    
    with tab_temp:
        try:
            df_temp = conn.read(spreadsheet="Base_Datos_HACCP", worksheet="Foglio1", ttl=0)
            
            if not df_temp.empty:
                total_registros = len(df_temp)
                fuori_norma = len(df_temp[df_temp["Stato"] == "⚠ FUORI NORMA"]) if "Stato" in df_temp.columns else 0
                conformita = ((total_registros - fuori_norma) / total_registros) * 100 if total_registros > 0 else 100
                
                col_k1, col_k2, col_k3 = st.columns(3)
                col_k1.metric("Registri Totali", total_registros)
                col_k2.metric("Fuori Norma", fuori_norma, delta_color="inverse" if fuori_norma > 0 else "normal")
                col_k3.metric("Conformità HACCP", f"{conformita:.1f}%")
                
                st.divider()
                st.markdown("### 📈 Stato dei Registri per Sede")
                if "Sede" in df_temp.columns:
                    conteo_sedes = df_temp["Sede"].value_counts()
                    st.bar_chart(conteo_sedes)
                
                st.write("📋 **Ultimi registri inseriti:**")
                st.dataframe(df_temp.tail(10), use_container_width=True)
            else:
                st.warning("Nessun dato sulle temperature trovato.")
        except Exception as e:
            st.warning("Caricamento dati temperature in corso...")

    with tab_prod:
        try:
            df_prod_bi = conn.read(spreadsheet="Base_Datos_HACCP", worksheet="Produzione_Gelato", ttl=0)
            
            if not df_prod_bi.empty:
                total_kili = df_prod_bi["Kili_Prodotti"].sum() if "Kili_Prodotti" in df_prod_bi.columns else 0
                total_lotti = len(df_prod_bi)
                
                col_p1, col_p2 = st.columns(2)
                col_p1.metric("Chili Totali Prodotti", f"{total_kili} Kg")
                col_p2.metric("Lotti Registrati", total_lotti)
                
                st.divider()
                st.markdown("### 📊 Produzione per Gusto (Kg)")
                if "Prodotto_Gusto" in df_prod_bi.columns and "Kili_Prodotti" in df_prod_bi.columns:
                    df_gusti = df_prod_bi.groupby("Prodotto_Gusto")["Kili_Prodotti"].sum()
                    st.bar_chart(df_gusti)
                
                st.write("📋 **Storico Produzioni:**")
                st.dataframe(df_prod_bi.tail(15), use_container_width=True)
            else:
                st.info("ℹ️ Non ci sono ancora registrazioni di produzione nel foglio 'Produzione_Gelato'.")
        except Exception as e:
            st.warning("Assicurati che esista il foglio 'Produzione_Gelato' nel tuo Google Sheets.")


# =====================================================================
# VISTA 3: ROL ADMIN (Gestión Total)
# =====================================================================
elif rol == "Admin (Gestione Totale)":
    st.subheader("🛠️ Pannello di Amministrazione")
    st.warning("Accesso amministrativo completo abilitato.")
    
    try:
        data_admin = conn.read(spreadsheet="Base_Datos_HACCP", worksheet="Foglio1", ttl=0)
        st.write(f"Record totali nel database temperature: **{len(data_admin)}**")
        st.dataframe(data_admin, use_container_width=True)
        
        if st.button("🔄 Aggiorna Dati Database"):
            st.rerun()
            
    except Exception as e:
        st.error("Impossibile caricare il database.")
        st.exception(e)

elif rol is None:
    st.info("👈 Seleziona il tuo ruolo nella barra laterale e inserisci la password corrispondente per accedere alle sezioni protette.")