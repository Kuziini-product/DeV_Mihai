
import pandas as pd
import os
from fpdf import FPDF
from datetime import datetime
import json

ISTORIC_FOLDER = "output/istoric/"
os.makedirs(ISTORIC_FOLDER, exist_ok=True)

def safe(text):
    return str(text).encode('latin-1', errors='ignore').decode('latin-1')

def get_next_offer_number():
    existente = [f for f in os.listdir(ISTORIC_FOLDER) if f.startswith("OF-") and f.endswith(".pdf")]
    numere = [int(f.split("-")[1]) for f in existente if f.split("-")[1].isdigit()]
    return max(numere + [0]) + 1 if numere else 1

def export_excel_pdf(df, descriere, nume_client, dimensiuni, telefon_client, poza_path=None):
    nr_oferta = get_next_offer_number()
    nume_fisier_base = f"OF-2025-{str(nr_oferta).zfill(4)}_{nume_client.replace(' ', '')}"
    excel_path = os.path.join(ISTORIC_FOLDER, f"{nume_fisier_base}.xlsx")
    df.to_excel(excel_path, index=False)

    total = pd.to_numeric(df[df.columns[-1]], errors='coerce').sum()

    pdf_path = os.path.join(ISTORIC_FOLDER, f"{nume_fisier_base}.pdf")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.cell(200, 10, txt=safe(f"Kuziini | Ofertă mobilier pentru {nume_client}"), ln=True, align="C")
    pdf.ln(5)
    pdf.set_font("Helvetica", size=10)
    pdf.multi_cell(0, 10, safe(descriere))
    pdf.ln(5)
    for col in df.columns:
        pdf.cell(38, 10, safe(col), 1)
    pdf.ln()
    for _, row in df.iterrows():
        for val in row:
            pdf.cell(38, 10, safe(val), 1)
        pdf.ln()
    pdf.ln(5)
    pdf.set_font("Helvetica", size=11)
    pdf.cell(200, 10, txt=safe(f"Total estimativ: {total:.2f} lei"), ln=True, align="R")
    pdf.output(pdf_path)

    json_path = os.path.join(ISTORIC_FOLDER, f"{nume_fisier_base}.json")
    meta = {
        "nume_client": nume_client,
        "telefon_client": telefon_client,
        "dimensiuni": dimensiuni,
        "descriere": descriere,
        "valoare_total": float(total),
        "poza_path": poza_path if poza_path else ""
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    return pdf_path, total, nume_fisier_base

def lista_oferte_istoric():
    return sorted([f for f in os.listdir(ISTORIC_FOLDER) if f.endswith(".pdf")])
