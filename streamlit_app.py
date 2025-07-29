
import streamlit as st
import pandas as pd
import base64
from pathlib import Path
from PIL import Image
from ai_generator import genereaza_deviz_AI
from image_utils import extrage_dimensiuni_din_imagine
from deviz_exporter import export_excel_pdf, lista_oferte_istoric
import os
from dotenv import load_dotenv
import json
import time

load_dotenv()
st.set_page_config(page_title="Kuziini | Configurator Devize", layout="centered")

logo_path = Path("assets/Kuziini_logo_negru.png")
if logo_path.exists():
    st.image(str(logo_path), width=300)
else:
    st.markdown("### 🪑 Kuziini | Configurator Devize")

st.markdown("## Configurator Devize pentru Corpuri de Mobilier")

nume_client = st.text_input("Nume client", value=st.session_state.get("nume_client", ""))
telefon_client = st.text_input("Telefon client", value=st.session_state.get("telefon_client", ""))

poza = st.file_uploader("Încarcă o imagine (jpg/png)", type=["jpg", "png"])
dimensiuni_auto = ""
if poza:
    dimensiuni_auto = extrage_dimensiuni_din_imagine(poza)
    st.success(f"Dimensiuni extrase: {dimensiuni_auto}")

col1, col2, col3 = st.columns(3)
with col1:
    lungime = st.text_input("Lungime (mm)", value=st.session_state.get("lungime", ""))
with col2:
    latime = st.text_input("Lățime (mm)", value=st.session_state.get("latime", ""))
with col3:
    inaltime = st.text_input("Înălțime (mm)", value=st.session_state.get("inaltime", ""))

descriere = st.text_area("Descriere corp mobilier", height=150, value=st.session_state.get("descriere", ""))

st.session_state.update({
    "lungime": lungime,
    "latime": latime,
    "inaltime": inaltime,
    "descriere": descriere,
    "nume_client": nume_client,
    "telefon_client": telefon_client
})

dimensiuni = f"{lungime}x{latime}x{inaltime}"

col_db, col_val = st.columns([2, 1])
try:
    df = pd.read_csv("Accesorii.csv", encoding="latin1")
    col_db.success("Baza de date a fost încărcată cu succes.")
except Exception as e:
    col_db.error(f"Eroare la citirea fișierului Accesorii.csv: {e}")
    st.stop()

istoric_json = sorted([f for f in os.listdir("output/istoric") if f.endswith(".json")])
if istoric_json:
    with open(os.path.join("output/istoric", istoric_json[-1]), encoding="utf-8") as f:
        meta = json.load(f)
        col_val.info(f"📦 Ultimul deviz: {meta['valoare_total']:.2f} lei")
else:
    col_val.info("📦 Ultimul deviz: -")

deviz_df = pd.DataFrame()
if st.button("🔧 Generează deviz"):
    with st.spinner("Se generează devizul..."):
        raspuns, deviz_df = genereaza_deviz_AI(descriere, dimensiuni, df)
        poza_path = None
        if poza:
            ext = Path(poza.name).suffix
            poza_path = f"assets/uploads/{nume_client.replace(' ', '')}_{int(time.time())}{ext}"
            Path("assets/uploads").mkdir(parents=True, exist_ok=True)
            with open(poza_path, "wb") as f:
                f.write(poza.getbuffer())

        pdf_path, total, nume_fisier_base = export_excel_pdf(
            deviz_df, descriere, nume_client, dimensiuni, telefon_client, poza_path)

        st.success(f"✅ Deviz generat | 💰 Total: {total:.2f} lei")
        with open(pdf_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
            href = f'<a href="data:application/octet-stream;base64,{b64}" download="{os.path.basename(pdf_path)}">📥 Descarcă PDF</a>'
            st.markdown(href, unsafe_allow_html=True)

if not deviz_df.empty and st.button("👁️ Afișează devizul în aplicație"):
    st.markdown("### 🔍 Deviz generat")
    st.dataframe(deviz_df)

st.markdown("### 📂 Istoric complet oferte")
for f in sorted(os.listdir("output/istoric")):
    if f.endswith(".json"):
        path_json = os.path.join("output/istoric", f)
        with open(path_json, encoding="utf-8") as meta_file:
            meta = json.load(meta_file)
            st.markdown(f"**🔖 {f[:-5]}**")
            cols = st.columns([2, 1])
            with cols[0]:
                st.markdown(f"👤 Client: {meta['nume_client']}")
                st.markdown(f"📏 Dimensiuni: {meta['dimensiuni']}")
                st.markdown(f"✍️ Descriere: {meta['descriere']}")
                st.markdown(f"💰 Total: {meta['valoare_total']:.2f} lei")
            with cols[1]:
                if meta["poza_path"] and os.path.exists(meta["poza_path"]):
                    st.image(meta["poza_path"], width=160)
