import streamlit as st

# Setări pagină mobil
st.set_page_config(page_title="RiskChecker", page_icon="🔍", layout="centered")

st.title("🔍 RiskChecker Vamal-Fiscal")
st.caption("Sistem de analiză și evaluare a riscului comercial")

st.divider()

# --- SECTIUNEA 1: DATE COMPANIE ---
st.header("1. Profil Companie")
cui = st.text_input("CUI / Cod EORI", placeholder="ex: RO12345678")
nume_firma = st.text_input("Denumire Firmă", placeholder="ex: IMPORT EXPORT SRL")

col1, col2 = st.columns(2)
with col1:
    inactiva = st.checkbox("Firma e Inactivă / Insolvență")
    cazier = st.checkbox("Are fapte în Cazierul Fiscal")
with col2:
    sediu_colectiv = st.checkbox("Sediu Social Colectiv (>20 firme)")
    istoric_faliment = st.checkbox("Admin. cu firme falimentare")

st.divider()

# --- SECTIUNEA 2: PARAMETRI FINANCIARI ---
st.header("2. Indicatori Financiari")
cifra_afaceri = st.number_input("Cifră de afaceri (RON)", min_value=0.0, step=10000.0)
nr_angajati = st.number_input("Număr Angajați", min_value=0, step=1)
active_fixe = st.number_input("Active Fixe (RON)", min_value=0.0, step=5000.0)

st.divider()

# --- SECTIUNEA 3: OPERAȚIUNE VAMALĂ ---
st.header("3. Detalii Import / Export")
cod_taric = st.text_input("Cod TARIC / HS Code", placeholder="ex: 8517.12.00")

col3, col4 = st.columns(2)
with col3:
    val_declarata = st.number_input("Valoare declarată/unitate (EUR)", min_value=0.0, step=10.0)
with col4:
    val_medie_ref = st.number_input("Valoare MEDIE de referință (EUR)", min_value=0.0, step=10.0)

regim_42 = st.checkbox("Utilizează Regimul Vamal 42")
ruta_offshore = st.checkbox("Rută / Origine cu risc (Offshore)")

st.divider()

# --- ALGORITM DE CALCUL SCOR DE RISC ---
if st.button("CALCULEAZĂ SCOR DE RISC", type="primary", use_container_width=True):
    scor_risc = 0
    steaguri_rosii = []

    # 1. Evaluare Risc Fiscal
    if inactiva:
        scor_risc += 15
        steaguri_rosii.append("Firma este inactivă fiscal sau în insolvență (+15 pt)")
    if cazier:
        scor_risc += 10
        steaguri_rosii.append("Fapte înscrisă în cazierul fiscal (+10 pt)")
    if cifra_afaceri > 1000000 and nr_angajati == 0 and active_fixe < 10000:
        scor_risc += 10
        steaguri_rosii.append("Substanță economică zero: CA uriașă fără angajați și active (+10 pt)")
    if sediu_colectiv:
        scor_risc += 5
        steaguri_rosii.append("Sediu social la adresă colectivă (+5 pt)")

    # 2. Evaluare Risc Vamal (Raportat la Limita de Mijloc / Medie)
    if val_medie_ref > 0 and val_declarata > 0:
        diferenta_procent = ((val_medie_ref - val_declarata) / val_medie_ref) * 100
        if diferenta_procent > 40:
            scor_risc += 20
            steaguri_rosii.append(f"Subevaluare vamală severă: sub media de referință cu {diferenta_procent:.1f}% (+20 pt)")
        elif diferenta_procent >= 20:
            scor_risc += 10
            steaguri_rosii.append(f"Subevaluare vamală moderată: sub media de referință cu {diferenta_procent:.1f}% (+10 pt)")

    if regim_42:
        scor_risc += 10
        steaguri_rosii.append("Risc ridicat asociat Regimului 42 (+10 pt)")
    if ruta_offshore:
        scor_risc += 5
        steaguri_rosii.append("Expediție din zonă offshore (+5 pt)")

    # 3. Evaluare Risc Rețea
    if istoric_faliment:
        scor_risc += 10
        steaguri_rosii.append("Administrator implicat în firme radiate cu datorii (+10 pt)")

    # Rezultate
    st.subheader("Rezultat Evaluare")
    
    if scor_risc >= 70:
        st.error(f"🔴 SCOR DE RISC: {scor_risc} / 100 — RISC RIDICAT")
        st.warning("RECOMANDARE: Control fizic și documentar detaliat (Canal Roșu)")
    elif scor_risc >= 36:
        st.warning(f"🟡 SCOR DE RISC: {scor_risc} / 100 — RISC MEDIU")
        st.info("RECOMANDARE: Control documentar (Canal Galben)")
    else:
        st.success(f"🟢 SCOR DE RISC: {scor_risc} / 100 — RISC SCĂZUT")
        st.info("RECOMANDARE: Vămuire / Control pe firul verde")

    if steaguri_rosii:
        st.write("**Alerte de Risc Detectate:**")
        for flag in steaguri_rosii:
            st.write(f"- {flag}")
