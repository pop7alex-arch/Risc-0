import streamlit as st
import requests

# 1. Configurare Pagină & Stil Vizual Modern
st.set_page_config(
    page_title="RiskChecker Vamal-Fiscal",
    page_icon="🛡️",
    layout="centered"
)

# Stiluri CSS Personalizate pentru o Interfață Premium / Prietenoasă
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button {
        border-radius: 10px;
        font-weight: bold;
        height: 3em;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        margin-bottom: 10px;
        border: 1px solid #e9ecef;
    }
    .status-badge {
        padding: 5px 12px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.85em;
        display: inline-block;
    }
    .badge-active { background-color: #d4edda; color: #155724; }
    .badge-inactive { background-color: #f8d7da; color: #721c24; }
    </style>
""", unsafe_allow_html=True)

# Antet Aplicație
st.title("🛡️ RiskChecker Pro")
st.caption("Sistem Inteligent de Analiză și Extragere Date Firme (Vamă & Fiscal)")

st.divider()

# Stocare Stare APLICAȚIE (Session State)
if "data_loaded" not in st.session_state:
    st.session_state.data_loaded = False
    st.session_state.firma_data = {}

# ---------------------------------------------------------
# CASETĂ CĂUTARE AUTOMATĂ CUI
# ---------------------------------------------------------
st.subheader("🔎 Căutare Automată Firmă")
cui_input = st.text_input("Introdu CUI-ul firmei (doar cifre):", placeholder="Ex: 12345678")

if st.button("🚀 Extrage Toate Datele Gratuit", use_container_width=True, type="primary"):
    if cui_input:
        cui_curat = cui_input.strip().upper().replace("RO", "")
        with st.spinner("Se interoghează baze de date ANAF & Registrul Comerțului..."):
            
            loaded_info = {
                "cui": cui_curat,
                "nume": "",
                "inactiva": False,
                "tva": False,
                "adresa": "",
                "caen": "",
                "cifra_afaceri": 0.0,
                "angajati": 0,
                "profit": 0.0,
                "datorii": 0.0
            }
            
            # A. Interogare ANAF (Gratuit)
            try:
                url_anaf = "https://webservicesp.anaf.ro/PlatitorTvaRest/api/v8/ws/tva"
                payload = [{"cui": int(cui_curat), "data": "2026-01-01"}]
                res_anaf = requests.post(url_anaf, json=payload, timeout=5)
                
                if res_anaf.status_code == 200:
                    data_anaf = res_anaf.json()
                    if data_anaf.get("found"):
                        info = data_anaf["found"][0]
                        loaded_info["nume"] = info["date_generale"]["denumire"]
                        loaded_info["adresa"] = info["date_generale"]["adresa"]
                        loaded_info["inactiva"] = info["stare_inactiv"]["statusInactivi"]
                        loaded_info["tva"] = info["scpTVA"]["statusPtvax"]
            except Exception:
                st.warning("Avertisment: Serverul ANAF nu a răspuns la timp.")

            # B. Interogare Date Financiare / Bilanț (OpenAPI / Surse Publice)
            try:
                url_fin = f"https://openapi.ro/api/companies/{cui_curat}"
                res_fin = requests.get(url_fin, timeout=5)
                if res_fin.status_code == 200:
                    fin_data = res_fin.json()
                    loaded_info["caen"] = fin_data.get("main_activity", {}).get("code", "N/A")
                    
                    # Extragere din ultimul bilanț depus
                    last_financial = fin_data.get("last_financial_data", {})
                    loaded_info["cifra_afaceri"] = float(last_financial.get("turnover", 0))
                    loaded_info["angajati"] = int(last_financial.get("employees", 0))
                    loaded_info["profit"] = float(last_financial.get("net_profit", 0))
                    loaded_info["datorii"] = float(last_financial.get("debts", 0))
            except Exception:
                pass # Dacă nu există bilanț public accesibil, rămân valorile implicite

            if loaded_info["nume"]:
                st.session_state.firma_data = loaded_info
                st.session_state.data_loaded = True
                st.success(f"Date extrase cu succes pentru {loaded_info['nume']}!")
            else:
                st.error("Nu s-au putut extrage date pentru acest CUI. Verifică numărul introdus.")

st.divider()

# ---------------------------------------------------------
# AFIȘARE DASHBOARD CARDURI & EDITARE
# ---------------------------------------------------------
if st.session_state.data_loaded:
    data = st.session_state.firma_data
    
    st.subheader("🏢 Fişa Financiară & Stare Societate")
    
    # Header Profil Firmă
    badge_class = "badge-inactive" if data["inactiva"] else "badge-active"
    statu_text = "INACTIVĂ FISCAL" if data["inactiva"] else "ACTIVĂ FISCAL"
    
    st.markdown(f"""
        <div class="metric-card">
            <h3 style="margin:0;">{data['nume']}</h3>
            <p style="color:gray; margin-bottom:5px;">CUI: {data['cui']} | Sediu: {data['adresa']}</p>
            <span class="status-badge {badge_class}">{statu_text}</span>
            <span class="status-badge badge-active" style="margin-left:5px;">TVA: {'DA' if data['tva'] else 'NU'}</span>
        </div>
    """, unsafe_allow_html=True)
    
    # Carduri cu Metrici Financiare Extrase
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Cifră de Afaceri (Bilanț)", f"{data['cifra_afaceri']:,.0f} RON")
        st.metric("Număr Angajați", f"{data['angajati']}")
    with col2:
        st.metric("Profit Net", f"{data['profit']:,.0f} RON")
        st.metric("Datorii Totale", f"{data['datorii']:,.0f} RON")

st.subheader("⚙️ Configurare Parametri & Analiză Risc")

# Formular cu Datele Pre-completate
with st.expander("Modifică sau adaugă indicatori suplimentari", expanded=True):
    f_inactiva = st.checkbox("Firma e Inactivă / Insolvență", value=st.session_state.firma_data.get("inactiva", False))
    f_cazier = st.checkbox("Fapte în Cazierul Fiscal")
    f_sediu_colectiv = st.checkbox("Sediu Social Colectiv (>20 firme la adresă)")
    f_istoric = st.checkbox("Administrator cu antecedente de insolvență/faliment")
    
    cifra_afaceri = st.number_input("Cifră de afaceri (RON)", value=st.session_state.firma_data.get("cifra_afaceri", 0.0))
    nr_angajati = st.number_input("Număr Angajați", value=st.session_state.firma_data.get("angajati", 0))

st.subheader("📦 Operațiune Vamală Curentă")
col_v1, col_v2 = st.columns(2)
with col_v1:
    val_declarata = st.number_input("Valoare declarată/unitate (EUR)", min_value=0.0, step=10.0)
with col_v2:
    val_medie_ref = st.number_input("Valoare MEDIE de referință (EUR)", min_value=0.0, step=10.0)

regim_42 = st.checkbox("Utilizează Regimul Vamal 42 (TVA intracomunitar)")
ruta_offshore = st.checkbox("Rută / Origine cu risc ridicat (Offshore)")

st.divider()

# ---------------------------------------------------------
# ALGORITM CALCUL & AFIȘARE RAPORT
# ---------------------------------------------------------
if st.button("📊 GENEREAZĂ RAPORT DE RISC", type="primary", use_container_width=True):
    scor_risc = 0
    steaguri_rosii = []

    # 1. Risc Fiscal & Financiar
    if f_inactiva:
        scor_risc += 15
        steaguri_rosii.append("Firma este inactivă fiscal sau în insolvență (+15 pt)")
    if f_cazier:
        scor_risc += 10
        steaguri_rosii.append("Fapte înscrisă în cazierul fiscal (+10 pt)")
    if cifra_afaceri > 1000000 and nr_angajati == 0:
        scor_risc += 10
        steaguri_rosii.append("Substanță economică zero: Cifră de afaceri > 1 Mil. RON fără angajați (+10 pt)")
    if f_sediu_colectiv:
        scor_risc += 5
        steaguri_rosii.append("Sediu social înregistrat la adresă colectivă (+5 pt)")

    # 2. Risc Vamal (Comparat cu LIMITA DE MIJLOC / Medie)
    if val_medie_ref > 0 and val_declarata > 0:
        diferenta_procent = ((val_medie_ref - val_declarata) / val_medie_ref) * 100
        if diferenta_procent > 40:
            scor_risc += 20
            steaguri_rosii.append(f"Subevaluare vamală severă: valoare sub media de referință cu {diferenta_procent:.1f}% (+20 pt)")
        elif diferenta_procent >= 20:
            scor_risc += 10
            steaguri_rosii.append(f"Subevaluare vamală moderată: valoare sub media de referință cu {diferenta_procent:.1f}% (+10 pt)")

    if regim_42:
        scor_risc += 10
        steaguri_rosii.append("Risc ridicat asociat Regimului Vamal 42 (+10 pt)")
    if ruta_offshore:
        scor_risc += 5
        steaguri_rosii.append("Expediție din zonă offshore / risc ridicat (+5 pt)")

    # 3. Risc Rețea
    if f_istoric:
        scor_risc += 10
        steaguri_rosii.append("Administrator implicat anterior în firme cu datorii/faliment (+10 pt)")

    # Afișare Rezultate
    st.subheader("📋 Rezultat Raport Vamal")
    
    if scor_risc >= 70:
        st.error(f"🔴 SCOR DE RISC AGREGAT: {scor_risc} / 100 — RISC RIDICAT")
        st.warning("DECIZIE: Recomandat Control Fizic și Documentar Detaliat (CANAL ROȘU)")
    elif scor_risc >= 36:
        st.warning(f"🟡 SCOR DE RISC AGREGAT: {scor_risc} / 100 — RISC MEDIU")
        st.info("DECIZIE: Recomandat Control Documentar (CANAL GALBEN)")
    else:
        st.success(f"🟢 SCOR DE RISC AGREGAT: {scor_risc} / 100 — RISC SCĂZUT")
        st.info("DECIZIE: Vămuire Liberă / Control pe Firul Verde")

    if steaguri_rosii:
        st.markdown("### ⚠️ Indicatori de Risc Detectați (Red Flags)")
        for flag in steaguri_rosii:
            st.markdown(f"- {flag}")
