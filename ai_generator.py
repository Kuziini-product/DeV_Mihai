
from openai import OpenAI
import pandas as pd
import os
from dotenv import load_dotenv

# Încarcă cheia din mediu
load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

def genereaza_deviz_AI(descriere, dimensiuni, baza_date_df):
    # Limităm promptul la 30 de rânduri
    tabel_text = baza_date_df.head(30).to_csv(index=False)

    prompt = f"""
Avem următoarea bază de date cu materiale și prețuri:

{tabel_text}

Accesorii obligatorii:
  - Minim 4 balamale Blum (2 uși) sau mai multe, în funcție de înălțime (1 balama/350 mm per ușă)
  - Minifixuri HFL pentru asamblare
  - 4 picioare reglabile HFL
  - 2 mânere standard
  - Suporturi raft HFL (4 per raft)
  - Șuruburi și dibluri incluse

Generează un deviz tabelar Markdown cu: Nume | Cantitate | UM | Preț unitar | Total

Descriere:
Dimensiuni: {dimensiuni}
{descriere}
"""

    chat_response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4
    )

    raspuns = chat_response.choices[0].message.content

    linii = [linie for linie in raspuns.split("\n") if "|" in linie]
    curat = [[col.strip() for col in linie.split("|")] for linie in linii]
    df_deviz = pd.DataFrame(curat[1:], columns=curat[0]) if len(curat) > 1 else pd.DataFrame()

    return raspuns, df_deviz
