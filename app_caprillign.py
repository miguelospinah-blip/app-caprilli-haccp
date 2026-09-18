import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="HACCP & ERP Caprilli", page_icon="🍦", layout="centered")

# --- 1. BARRA LATERAL: CONTROL DE ACCESOS Y SEGURIDAD POR CONTRASEÑA ---
st.sidebar.title("🔐 Accesso Sistema")
rol_seleccionado = st.sidebar.selectbox("Seleziona Ruolo:", ["Operatore (Base)", "Leader (Consultazione)", "Admin (Gestione Totale)"])

rol = None  

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

try:
    if "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
        if "private_key" in st.secrets["connections"]["gsheets"]:
            st.secrets["connections"]["gsheets"]["private_key"] = st.secrets["connections"]["gsheets"]["private_key"].replace("\\n", "\n")
except Exception:
    pass

# --- GESTIÓN DE HORA LOCAL (ITALIA - ROME) ---
def obtener_tiempo_actual():
    try:
        return datetime.now(ZoneInfo("Europe/Rome"))
    except Exception:
        return datetime.now()

# --- LISTAS DINÁMICAS EN SESSION STATE ---
if 'lista_operatori' not in st.session_state:
    st.session_state.lista_operatori = ["Alessandra", "Chiara", "Miguel", "Antonio", "Ricardo", "Tommaso", "Francesco", "Matilde", "Giorgia", "Linda", "Manuel", "Luduvica", "Asia", "Edoardo"]

if 'lista_sapori_gelato' not in st.session_state:
    st.session_state.lista_sapori_gelato = [
        "Limone", "Mango", "Pesca", "Mora", "Mirtillo", "Fico", "YMN", "Fior di latte", 
        "Stracciatella", "Cocco", "Crema Diretta", "Crema Caprilli", "Vaniglia", "Mascarpone", 
        "CheeseCake", "Tamaro", "Nocciola", "Pistacchio", "Caramello", "Burro di Arachidi", 
        "Meglio della Nutela", "Caffe", "Cioccolato al latte", "Fondente", "Liquiritzia", 
        "Yogurt Soft", "Yogurt", "Caramello Mou", "Caramello Salato", "Infuso Caffe"
    ]

if 'lista_basi_sciroppi' not in st.session_state:
    st.session_state.lista_basi_sciroppi = [
        "Sciroppo / Base", "Base Bianca", "Base Gialla Frutta", "Base Cioccolato", "Base Neutra"
    ]

# --- EVALUACIÓN INTELIGENTE Y CALIBRADA DE TEMPERATURAS ---
def evaluar_temperatura(equipo, valor):
    if valor == "Non in uso":
        return "Non in uso"
    
    val = float(valor)
    equipo_lower = equipo.lower()

    if "cioccolato" in equipo_lower:
        return "⚠ FUORI NORMA" if (val < 12.0 or val > 20.0) else "OK Cioccolato"

    if any(k in equipo_lower for k in ["conservatore", "congelatore", "banco 1", "banco 2", "vetrina 1", "vetrina 2", "vetrina 3", "vetrina 4", "cella 1", "cella 2"]):
        if "latte" not in equipo_lower and "materie" not in equipo_lower and "frigo" not in equipo_lower:
            return "⚠ FUORI NORMA" if val > -10.0 else "OK Congelatore"

    if "scioglitrice" in equipo_lower or "temperatrice" in equipo_lower:
        return "⚠ FUORI NORMA" if (val < 20.0 or val > 50.0) else "OK Caldo"

    if any(k in equipo_lower for k in ["frigo", "cella", "panna", "farciture", "yogurt", "granite"]):
        return "⚠ FUORI NORMA" if (val < -1.0 or val > 8.0) else "OK Frigo"

    return "⚠ FUORI NORMA" if val > 8.0 else "OK Frigo"


# =====================================================================
# VISTA 1: ROL OPERATORE
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
            "Seleziona la sede", "Laboratorio Cioccolato", "Laboratorio Gelato", "Laboratorio Pasticceria", "Viale Italia", "Cavour"
        ])

        if sede == "Seleziona la sede":
            st.warning("⚠️ Per favore, seleziona una sede o reparto per continuare.")
        else:
            st.markdown(f"### Registrazione per: **{sede}**")

            with st.form(key=f"form_haccp_{sede}"):
                operatore = st.selectbox("Nome Operatore:", ["Seleziona il tuo nome"] + st.session_state.lista_operatori)
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
                        ahora_str = obtener_tiempo_actual().strftime("%Y-%m-%d %H:%M:%S")
                        filas_nuevas = []
                        for equipo, temp in lecturas.items():
                            filas_nuevas.append({
                                "Fecha_Hora": ahora_str, "Sede": sede, "Equipo": equipo,
                                "Temperatura": str(temp), "Operatore": operatore, "Stato": evaluar_temperatura(equipo, temp), "Risolto": "No"
                            })
                        df_nuevo = pd.DataFrame(filas_nuevas)
                        try:
                            existing_data = conn.read(spreadsheet="Base_Datos_HACCP", worksheet="Foglio1", ttl=0)
                            conn.update(spreadsheet="Base_Datos_HACCP", worksheet="Foglio1", data=pd.concat([existing_data, df_nuevo], ignore_index=True))
                            st.success(f"✅ Registrate con successo {len(lecturas)} temperature per {sede}!")
                        except Exception as e:
                            st.error("❌ Errore durante il salvataggio nel database.")
                            st.exception(e)

    # --- SUB-MODO: MENÚ DE PRODUCCIÓN (3 LABS) ---
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
                st.session_state.modo_operatore = "prod_cioccolato"
                st.rerun()
        with col_p3:
            if st.button("🍰 Laboratorio Pasticceria", use_container_width=True):
                st.session_state.modo_operatore = "prod_pasticceria"
                st.rerun()

    # --- SUB-MODO: LABORATORIO GELATO ---
    elif st.session_state.modo_operatore == "prod_gelato":
        if st.button("⬅ Torna ai Laboratori"):
            st.session_state.modo_operatore = "produzione_menu"
            st.rerun()
            
        st.markdown("### 🍦 Registrazione Produzione - Laboratorio Gelato")
        tipo_gelato_sel = st.radio("Seleziona categoria:", ["Gelato Proprio", "Base / Sciroppo"], horizontal=True)
        
        with st.form("form_prod_gelato"):
            op_gelato = st.selectbox("Nome Operatore:", ["Seleziona il tuo nome"] + st.session_state.lista_operatori)
            
            if tipo_gelato_sel == "Gelato Proprio":
                sapore = st.selectbox("Seleziona Gusto / Preparazione:", st.session_state.lista_sapori_gelato)
                dias_caducidad = 90
            else:
                sapore = st.selectbox("Seleziona Base / Sciroppo:", st.session_state.lista_basi_sciroppi)
                dias_caducidad = 7
                
            kili = st.number_input("Chili totali prodotti (Kg):", min_value=0.5, max_value=100.0, value=11.0, step=0.5)
            
            ahora_dt = obtener_tiempo_actual()
            fecha_scadenza = (ahora_dt + timedelta(days=dias_caducidad)).strftime("%Y-%m-%d")
            st.info(f"📅 Scadenza stimata automatica: **{fecha_scadenza}**")

            note_opcional = st.text_input("Note opzionali (non alterano il lotto):")
            
            submit_prod = st.form_submit_button("💾 Salva Produzione Gelato")
            
            if submit_prod:
                if op_gelato == "Seleziona il tuo nome":
                    st.error("❌ Per favore, seleziona il tuo nome.")
                else:
                    ahora_str = ahora_dt.strftime("%Y-%m-%d %H:%M:%S")
                    anio_dos = ahora_dt.strftime("%y")
                    dia_juliano = ahora_dt.strftime("%j")
                    hora_minuto = ahora_dt.strftime("%H%M")
                    lotto_automatico = f"L{anio_dos}{dia_juliano}{hora_minuto}"

                    df_prod = pd.DataFrame([{
                        "Data_Ora": ahora_str, "Lotto": lotto_automatico, "Note_Opzionali": note_opcional if note_opcional else "",
                        "Tipo": tipo_gelato_sel, "Reparto": "Laboratorio Gelato", "Prodotto_Gusto": sapore,
                        "Kili_Prodotti": kili, "Operatore": op_gelato, "Scadenza": fecha_scadenza
                    }])
                    try:
                        ex_prod = conn.read(spreadsheet="Base_Datos_HACCP", worksheet="Produzione_Gelato", ttl=0)
                        conn.update(spreadsheet="Base_Datos_HACCP", worksheet="Produzione_Gelato", data=pd.concat([ex_prod, df_prod], ignore_index=True))
                        st.success(f"✅ Registrato '{sapore}' con lotto **{lotto_automatico}**!")
                    except Exception as e:
                        st.error("❌ Errore.")
                        st.exception(e)

    # --- SUB-MODO: LABORATORIO CIOCCOLATO (Corregido df_cioc) ---
    elif st.session_state.modo_operatore == "prod_cioccolato":
        if st.button("⬅ Torna ai Laboratori"):
            st.session_state.modo_operatore = "produzione_menu"
            st.rerun()
            
        st.markdown("### 🍫 Registrazione Produzione - Laboratorio Cioccolato")
        st.info("💡 Campi strutturati ufficiali dinamici per il reparto cioccolato.")
        
        op_cioc = st.selectbox("Nome Operatore:", ["Seleziona il tuo nome"] + st.session_state.lista_operatori)
        
        categoria_cioc = st.selectbox("Categoria Prodotto:", [
            "Tavole di cioccolata", "Dragées", "Praline", "Piccola minuteria", "Spalmabili", "Marmellate", "Bon bon gelato"
        ])
        
        sottocategoria = "Nessuna"
        if categoria_cioc == "Tavole di cioccolata":
            sottocategoria = st.selectbox("Tipologia Tavola:", ["Tavole ripiene", "Tavole con inclusioni", "Tavole lisce"])
        elif categoria_cioc == "Praline":
            sottocategoria = st.selectbox("Tipologia Pralina:", ["Anidre", "Non anidre"])
        else:
            st.markdown(f"📌 *Tipologia per {categoria_cioc}: Standard / Unica*")

        nome_referenza = st.text_input("ID / Nome Referenza o Gusto:")
        festivita = st.selectbox("Ricorrenza / Festività (opzionale):", [
            "Nessuna", "Natale", "Pasqua", "Festa della mamma", "Festa del papà", "Epifania", "San Valentino", "Altro"
        ])

        col_c1, col_c2 = st.columns(2)
        with col_c1:
            quantita = st.number_input("Quantità prodotta:", min_value=0.1, max_value=1000.0, value=10.0, step=0.5)
        with col_c2:
            unita_misura = st.selectbox("Unità di misura:", ["Pezzi", "Kg"])

        modalita_formato = st.selectbox("Modalità / Formato:", [
            "Pezzo / sfuso", "Confezione a pezzi", "Vasetto a peso", "Uso interno altra produzione"
        ])

        n_confezioni = 0
        grammi_confezione = 0
        destinazione_interna = ""
        if "Confezione" in modalita_formato or "Vasetto" in modalita_formato:
            n_confezioni = st.number_input("Numero confezioni / vasetti:", min_value=1, max_value=500, value=10)
            grammi_confezione = st.number_input("Grammi o pezzi per confezione:", min_value=1.0, max_value=5000.0, value=200.0)
        elif modalita_formato == "Uso interno altra produzione":
            destinazione_interna = st.text_input("Destinazione interna (es. uova pasquali, soggetti):")

        fecha_scadenza_cioc = st.date_input("Data di Scadenza (inserimento manuale):", value=date.today() + timedelta(days=60))
        note_cioc = st.text_input("Note opzionali:")
        
        if st.button("💾 Salva Produzione Cioccolato"):
            if op_cioc == "Seleziona il tuo nome" or not nome_referenza:
                st.error("❌ Seleziona l'operatore e inserisci il nome della referenza.")
            else:
                ahora_dt = obtener_tiempo_actual()
                ahora_str = ahora_dt.strftime("%Y-%m-%d %H:%M:%S")
                lotto_automatico = f"LC{ahora_dt.strftime('%y%j')}"
                
                df_cioc = pd.DataFrame([{
                    "Data_Ora": ahora_str, "Lotto": lotto_automatico, "Note_Opzionali": note_cioc,
                    "Categoria": categoria_cioc, "Sottocategoria": sottocategoria, "Prodotto_Gusto": nome_referenza,
                    "Ricorrenza": festivita, "Quantita": quantita, "Unita": unita_misura,
                    "Formato": modalita_formato, "N_Confezioni": n_confezioni, "Destinazione_Interna": destinazione_interna,
                    "Reparto": "Laboratorio Cioccolato", "Operatore": op_cioc, "Scadenza": fecha_scadenza_cioc.strftime("%Y-%m-%d")
                }])
                try:
                    ex_prod = conn.read(spreadsheet="Base_Datos_HACCP", worksheet="Produzione_Cioccolato", ttl=0)
                    conn.update(spreadsheet="Base_Datos_HACCP", worksheet="Produzione_Cioccolato", data=pd.concat([ex_prod, df_cioc], ignore_index=True))
                    st.success(f"✅ Prodotto di cioccolata '{nome_referenza}' registrato con successo!")
                except Exception as e:
                    st.error("❌ Errore di salvataggio (Assicurati che esista il foglio 'Produzione_Cioccolato' nel Google Sheet).")
                    st.exception(e)

    # --- SUB-MODO: LABORATORIO PASTICCERIA ---
    elif st.session_state.modo_operatore == "prod_pasticceria":
        if st.button("⬅ Torna ai Laboratori"):
            st.session_state.modo_operatore = "produzione_menu"
            st.rerun()
            
        st.markdown("### 🍰 Registrazione Produzione - Laboratorio Pasticceria")
        with st.form("form_prod_pasticceria"):
            op_past = st.selectbox("Nome Operatore:", ["Seleziona il tuo nome"] + st.session_state.lista_operatori)
            prodotto_past = st.text_input("Prodotto / Preparazione Pasticceria:")
            kili_past = st.number_input("Quantità (Kg / Pezzi):", min_value=0.1, max_value=50.0, value=5.0, step=0.5)
            note_past = st.text_input("Note opzionali:")
            
            submit_past = st.form_submit_button("💾 Salva Produzione Pasticceria")
            if submit_past:
                if op_past == "Seleziona il tuo nome":
                    st.error("❌ Seleziona il tuo nome.")
                else:
                    ahora_dt = obtener_tiempo_actual()
                    ahora_str = ahora_dt.strftime("%Y-%m-%d %H:%M:%S")
                    lotto_automatico = f"LP{ahora_dt.strftime('%y%j%H%M')}"
                    
                    df_past = pd.DataFrame([{
                        "Data_Ora": ahora_str, "Lotto": lotto_automatico, "Note_Opzionali": note_past,
                        "Reparto": "Laboratorio Pasticceria", "Prodotto_Gusto": prodotto_past,
                        "Kili_Prodotti": kili_past, "Operatore": op_past, "Scadenza": (ahora_dt + timedelta(days=15)).strftime("%Y-%m-%d")
                    }])
                    try:
                        ex_prod = conn.read(spreadsheet="Base_Datos_HACCP", worksheet="Produzione_Pasticceria", ttl=0)
                        conn.update(spreadsheet="Base_Datos_HACCP", worksheet="Produzione_Pasticceria", data=pd.concat([ex_prod, df_past], ignore_index=True))
                        st.success(f"✅ Pasticceria registrata con lotto **{lotto_automatico}**!")
                    except Exception as e:
                        st.error("❌ Errore (Assicurati che esista il foglio 'Produzione_Pasticceria' nel Google Sheet).")
                        st.exception(e)


# =====================================================================
# VISTA 2: ROL LEADER
# =====================================================================
elif rol == "Leader (Consultazione)":
    st.subheader("📊 Dashboard Direttiva & Business Intelligence")
    
    tab_temp, tab_prod, tab_alertas = st.tabs(["🌡️ Monitoraggio Temperature", "🍦 Analisi Produzione", "🚨 Anomalie Frigoriferi"])
    
    with tab_temp:
        st.markdown("### 🌡️ Monitoraggio per Reparto & Audit Lavoratori")
        try:
            df_temp = conn.read(spreadsheet="Base_Datos_HACCP", worksheet="Foglio1", ttl=0)
            if not df_temp.empty:
                repartos = ["Laboratorio Cioccolato", "Laboratorio Gelato", "Laboratorio Pasticceria", "Viale Italia", "Cavour"]
                
                st.markdown("#### 🟢 Stato Attuale per Reparto")
                cols = st.columns(len(repartos))
                for i, rep in enumerate(repartos):
                    with cols[i]:
                        st.markdown(f"**{rep}**")
                        df_rep = df_temp[df_temp["Sede"] == rep]
                        if not df_rep.empty:
                            estados = df_rep["Stato"].value_counts()
                            st.bar_chart(estados)
                        else:
                            st.info("Nessun dato")

                st.divider()
                st.markdown("#### 📋 Storico Registri Temperature")
                st.dataframe(df_temp.tail(15), use_container_width=True)
                
                st.divider()
                st.markdown("#### 👥 Audit Operatori: Registri effettuati per lavoratore")
                if "Operatore" in df_temp.columns:
                    conteo_ops = df_temp["Operatore"].value_counts()
                    st.bar_chart(conteo_ops)
            else:
                st.info("Nessun dato sulle temperature trovato.")
        except Exception as e:
            st.warning("Errore nel caricamento del monitoraggio temperature.")
            st.exception(e)

    with tab_prod:
        st.markdown("### 🍦 Analisi Produzione (Giornaliera o Mensile)")
        reparto_sel = st.selectbox("Seleziona Reparto da analizzare:", ["Laboratorio Gelato", "Laboratorio Cioccolato", "Laboratorio Pasticceria"])
        
        sheet_name = "Produzione_Gelato"
        if reparto_sel == "Laboratorio Cioccolato":
            sheet_name = "Produzione_Cioccolato"
        elif reparto_sel == "Laboratorio Pasticceria":
            sheet_name = "Produzione_Pasticceria"

        try:
            df_p = conn.read(spreadsheet="Base_Datos_HACCP", worksheet=sheet_name, ttl=0)
            if not df_p.empty:
                df_p["Data_Ora_dt"] = pd.to_datetime(df_p["Data_Ora"], errors="coerce")
                
                tipo_vista = st.radio("Visualizza per:", ["Giorno specifico", "Intero Mese"], horizontal=True, key="vista_prod")
                
                if tipo_vista == "Giorno specifico":
                    data_selezionata = st.date_input("Seleziona la data:", value=date.today())
                    df_p_filtrado = df_p[df_p["Data_Ora_dt"].dt.date == data_selezionata]
                    titulo_filtro = f"del giorno {data_selezionata.strftime('%d/%m/%Y')}"
                else:
                    hoy = datetime.now()
                    col_pm1, col_pm2 = st.columns(2)
                    with col_pm1:
                        mes_sel = st.selectbox("Mese:", list(range(1, 13)), index=hoy.month - 1, format_func=lambda x: ["Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno", "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"][x-1])
                    with col_pm2:
                        anio_sel = st.number_input("Anno:", min_value=2024, max_value=2030, value=hoy.year)
                    
                    df_p_filtrado = df_p[(df_p["Data_Ora_dt"].dt.month == mes_sel) & (df_p["Data_Ora_dt"].dt.year == anio_sel)]
                    titulo_filtro = f"del mese {mes_sel}/{anio_sel}"

                st.divider()

                if not df_p_filtrado.empty:
                    col_m1, col_m2 = st.columns(2)
                    col_m1.metric(f"Registrazioni {titulo_filtro}", len(df_p_filtrado))
                    
                    st.markdown(f"### 📊 Produzione {titulo_filtro}")
                    col_graf = "Kili_Prodotti" if "Kili_Prodotti" in df_p_filtrado.columns else "Quantita"
                    if "Prodotto_Gusto" in df_p_filtrado.columns and col_graf in df_p_filtrado.columns:
                        df_grafico = df_p_filtrado.groupby("Prodotto_Gusto")[col_graf].sum()
                        st.bar_chart(df_grafico)

                    st.write("📋 **Storico Dettagliato:**")
                    st.dataframe(df_p_filtrado.drop(columns=["Data_Ora_dt"]), use_container_width=True)
                else:
                    st.info(f"ℹ️ Nessuna produzione registrata {titulo_filtro} per {reparto_sel}.")
            else:
                st.info(f"ℹ️ Il foglio '{sheet_name}' è vuoto o non contiene dati.")
        except Exception as e:
            st.warning(f"Assicurati che esista il foglio '{sheet_name}' nel tuo Google Sheets.")
            st.exception(e)

    with tab_alertas:
        st.markdown("### 🚨 Gestione Frigoriferi Fuori Norma")
        try:
            df_t = conn.read(spreadsheet="Base_Datos_HACCP", worksheet="Foglio1", ttl=0)
            if not df_t.empty and "Stato" in df_t.columns:
                fuori = df_t[(df_t["Stato"] == "⚠ FUORI NORMA") & (df_t.get("Risolto", "No") == "No")]
                
                if not fuori.empty:
                    st.error(f"⚠️ Attenzione! Ci sono {len(fuori)} apparecchiature con anomalie attive.")
                    st.dataframe(fuori, use_container_width=True)
                    
                    idx_resolver = st.selectbox("Seleziona riga da segnare come risolta:", fuori.index)
                    if st.button("🛠️ Segna come Risolto"):
                        df_t.loc[idx_resolver, "Risolto"] = "Sì"
                        conn.update(spreadsheet="Base_Datos_HACCP", worksheet="Foglio1", data=df_t)
                        st.success("✅ Incidente segnato come risolto!")
                        st.rerun()
                else:
                    st.success("🎉 Ottimo! Nessun frigorifero fuori norma al momento.")
            else:
                st.info("Nessun dato di anomalia trovato.")
        except Exception as e:
            st.warning("Errore nel modulo di controllo anomalie.")


# =====================================================================
# VISTA 3: ROL ADMIN
# =====================================================================
elif rol == "Admin (Gestione Totale)":
    st.subheader("🛠️ Pannello di Amministrazione & Parametri")
    
    tab_trab, tab_sab = st.tabs(["👥 Gestione Lavoratori", "🍧 Gestione Gusti e Basi"])
    
    with tab_trab:
        st.markdown("### Aggiungi o Rimuovi Lavoratori")
        nuevo_op = st.text_input("Nome nuovo lavoratore:")
        if st.button("➕ Aggiungi Lavoratore"):
            if nuevo_op and nuevo_op not in st.session_state.lista_operatori:
                st.session_state.lista_operatori.append(nuevo_op)
                st.success(f"Lavoratore {nuevo_op} aggiunto con successo!")
        
        st.write("**Lavoratori attivi attuali:**")
        st.write(st.session_state.lista_operatori)
        
        rem_op = st.selectbox("Seleziona lavoratore da rimuovere:", st.session_state.lista_operatori)
        if st.button("🗑️ Rimuovi Lavoratore"):
            st.session_state.lista_operatori.remove(rem_op)
            st.success("Lavoratore rimosso!")
            st.rerun()

    with tab_sab:
        st.markdown("### Aggiungi o Rimuovi Gusti / Basi")
        cat_destino = st.radio("Seleziona categoria:", ["Gelato Proprio", "Base / Sciroppo"], horizontal=True, key="cat_gusti")
        
        nuevo_gusto = st.text_input("Nome nuovo gusto/preparazione:", key="input_nuovo_gusto")
        if st.button("➕ Aggiungi Gusto", key="btn_add_gusto"):
            if cat_destino == "Gelato Proprio":
                if nuevo_gusto and nuevo_gusto not in st.session_state.lista_sapori_gelato:
                    st.session_state.lista_sapori_gelato.append(nuevo_gusto)
                    st.success("Gusto gelato aggiunto con successo!")
                    st.rerun()
                else:
                    st.warning("⚠️ Inserisci un nome valido o il gusto esiste già.")
            else:
                if nuevo_gusto and nuevo_gusto not in st.session_state.lista_basi_sciroppi:
                    st.session_state.lista_basi_sciroppi.append(nuevo_gusto)
                    st.success("Base/Sciroppo aggiunto con successo!")
                    st.rerun()
                else:
                    st.warning("⚠️ Inserisci un nome valido o la base esiste già.")
                
        st.divider()
        
        lista_ref = st.session_state.lista_sapori_gelato if cat_destino == "Gelato Proprio" else st.session_state.lista_basi_sciroppi
        
        st.write(f"**Catalogo attuale ({cat_destino}):**")
        st.write(lista_ref)
        
        st.divider()
        st.markdown("### 🗑️ Rimuovi Gusto / Base")
        if lista_ref:
            rem_gusto = st.selectbox("Seleziona elemento da rimuovere:", lista_ref, key="sel_rem_gusto")
            if st.button("🗑️ Rimuovi Elemento", key="btn_rem_gusto"):
                if cat_destino == "Gelato Proprio":
                    if rem_gusto in st.session_state.lista_sapori_gelato:
                        st.session_state.lista_sapori_gelato.remove(rem_gusto)
                        st.success(f"Elemento '{rem_gusto}' rimosso con successo!")
                        st.rerun()
                else:
                    if rem_gusto in st.session_state.lista_basi_sciroppi:
                        st.session_state.lista_basi_sciroppi.remove(rem_gusto)
                        st.success(f"Elemento '{rem_gusto}' rimosso con successo!")
                        st.rerun()
        else:
            st.info("Nessun elemento disponibile in questa categoria.")

elif rol is None:
    st.info("👈 Seleziona il tuo ruolo nella barra laterale e inserisci la password.")