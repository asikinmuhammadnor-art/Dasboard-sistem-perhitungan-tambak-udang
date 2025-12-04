import streamlit as st
import pandas as pd
import duckdb
import plotly.express as px
import os
from dotenv import load_dotenv

##############################################
# PAGE SETUP
##############################################
st.set_page_config(
    page_title="🦐 UMKM Udang Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🦐 AI-Powered Dashboard Panen Udang")
st.caption("Prototype v1.0 - UMKM Shrimp Farming Analysis + AI Commentary")

##############################################
# LOAD API KEY (Opsional Groq)
##############################################
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if GROQ_API_KEY:
    from groq import Groq
    client = Groq(api_key=GROQ_API_KEY)
else:
    client = None

##############################################
# AI COMMENTARY
##############################################
def generate_ai_commentary(data: pd.DataFrame) -> str:
    if not client:
        return "⚠️ AI Commentary tidak aktif (API Key tidak ditemukan)."

    text_summary = data.to_string(index=False)

    prompt = f"""
    Berikut adalah data hasil perhitungan panen udang:
    {text_summary}

    Buat analisis yang singkat dalam bahasa Indonesia:
    - Estimasi panen dan hasil yang menonjol
    - Efisiensi pakan
    - Profitabilitas UMKM
    - Risiko dan perhatian budidaya
    """

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content

    except Exception as e:
        return f"❌ Error AI Commentary: {e}"

##############################################
# DATA UPLOAD
##############################################
uploaded_file = st.file_uploader("📂 Upload file input budidaya udang", type=["xlsx", "xls", "csv"])

if uploaded_file:

    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.subheader("📜 Data Input Budidaya")
    st.dataframe(df.head())

    # PASTIKAN KOLUMNYA ADA
    required_cols = ["Jumlah_Benur", "Total_Pakan_kg", "Size_Target_gr", "Harga_Jual_perkg", "Modal_Total"]

    if not all(col in df.columns for col in required_cols):
        st.error(f"⚠️ File harus memiliki kolom: {required_cols}")
        st.stop()

    ##############################################
    # PERHITUNGAN PANEN
    ##############################################
    st.subheader("🧮 Perhitungan Panen Udang")

    df["Perkiraan_Ekor_Panen"] = df["Jumlah_Benur"] * 0.85    # survival rate 85%
    df["Berat_per_ekor_kg"] = df["Size_Target_gr"] / 1000
    df["Total_Panen_kg"] = df["Perkiraan_Ekor_Panen"] * df["Berat_per_ekor_kg"]
    df["Omzet"] = df["Total_Panen_kg"] * df["Harga_Jual_perkg"]
    df["Profit"] = df["Omzet"] - df["Modal_Total"]

    st.dataframe(df)

    ##############################################
    # VISUALISASI
    ##############################################
    st.subheader("📊 Grafik Total Panen & Profit")

    fig = px.bar(
        df,
        x=df.index,
        y=["Total_Panen_kg", "Profit"],
        barmode="group",
        title="Total Panen (kg) dan Profit"
    )

    st.plotly_chart(fig, use_container_width=True)

    ##############################################
    # AUTO COMMENTARY
    ##############################################
    st.subheader("📝 Auto Commentary (Rule-based)")

    best_profit = df["Profit"].max()
    worst_profit = df["Profit"].min()

    commentary = f"""
    🔍 **Analisis Otomatis:**
    - Profit tertinggi: **Rp {best_profit:,.0f}**
    - Profit terendah: **Rp {worst_profit:,.0f}**
    - Total panen rata-rata: **{df["Total_Panen_kg"].mean():,.2f} kg**
    """

    st.markdown(commentary)

    ##############################################
    # AI COMMENTARY
    ##############################################
    st.subheader("🤖 AI Commentary")

    ai_comment = generate_ai_commentary(df)
    st.write(ai_comment)

    ##############################################
    # CHAT MODE
    ##############################################
    st.subheader("💬 Tanya AI Analis Udang")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {"role": "system", "content": "Anda adalah ahli analisis budidaya udang."},
            {"role": "assistant", "content": ai_comment}
        ]

    for msg in st.session_state.chat_history:
        st.chat_message(msg["role"]).write(msg["content"])

    if question := st.chat_input("Tanyakan sesuatu..."):
        st.session_state.chat_history.append({"role": "user", "content": question})
        st.chat_message("user").write(question)

        if client:
            try:
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=st.session_state.chat_history,
                    temperature=0.7
                )
                answer = response.choices[0].message.content
                st.session_state.chat_history.append({"role": "assistant", "content": answer})
                st.chat_message("assistant").write(answer)
            except Exception as e:
                st.error(f"❌ Error chat: {e}")
        else:
            st.chat_message("assistant").write("⚠️ AI Chat tidak aktif (API Key tidak ada).")

else:
    st.info("⬆️ Upload Excel/CSV untuk memulai.")
