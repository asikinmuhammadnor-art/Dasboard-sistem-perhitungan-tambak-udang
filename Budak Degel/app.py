import streamlit as st
import pandas as pd
import plotly.express as px

##############################################
# PAGE CONFIG
##############################################
st.set_page_config(
    page_title="📟 Sistem Perhitungan Panen Udang",
    layout="wide"
)

st.title("📟 Sistem Perhitungan Panen Udang")
st.caption("Dashboard Analisis Panen Udang - Versi 1.0")

##############################################
# INPUT FORM
##############################################
st.sidebar.header("📥 Input Parameter Budidaya")

jumlah_benur = st.sidebar.number_input("Jumlah Benur (ekor)", min_value=1, value=100000)
total_pakan = st.sidebar.number_input("Total Pakan (kg)", min_value=1.0, value=2500.0)
size_target = st.sidebar.number_input("Target Size (ekor/kg)", min_value=10, value=60)
harga_jual = st.sidebar.number_input("Harga Jual per kg (Rp)", min_value=10000, value=65000)
total_modal = st.sidebar.number_input("Total Modal Produksi (Rp)", min_value=10000, value=120000000)

st.sidebar.markdown("---")

##############################################
# PERHITUNGAN OTOMATIS
##############################################

# Survival Rate (SR)
sr = 0.80  # default SR

jumlah_panen = jumlah_benur * sr
estimasi_biomassa = jumlah_panen / size_target

# FCR
fcr = total_pakan / estimasi_biomassa

# Harga total penjualan
total_penjualan = estimasi_biomassa * harga_jual

# Laba
profit = total_penjualan - total_modal

# Break Even Point
bep_kg = total_modal / harga_jual

##############################################
# OUTPUT TABEL HASIL
##############################################
st.subheader("📊 Hasil Perhitungan Panen Udang")

hasil_df = pd.DataFrame({
    "Parameter": [
        "Jumlah Benur Awal",
        "Survival Rate (SR)",
        "Jumlah Udang Panen (ekor)",
        "Target Size (ekor/kg)",
        "Estimasi Biomassa (kg)",
        "Total Pakan (kg)",
        "FCR",
        "Harga Jual per kg (Rp)",
        "Total Penjualan (Rp)",
        "Total Modal (Rp)",
        "Laba (Rp)",
        "Break Even Point (kg)"
    ],
    "Hasil": [
        jumlah_benur,
        f"{sr*100:.1f}%",
        int(jumlah_panen),
        size_target,
        f"{estimasi_biomassa:.2f}",
        total_pakan,
        f"{fcr:.2f}",
        harga_jual,
        f"{total_penjualan:,.0f}",
        f"{total_modal:,.0f}",
        f"{profit:,.0f}",
        f"{bep_kg:.2f}"
    ]
})

st.dataframe(hasil_df, use_container_width=True)

##############################################
# CHART
##############################################
st.subheader("📈 Grafik Estimasi Biomassa vs FCR")

chart_df = pd.DataFrame({
    "Parameter": ["Biomassa (kg)", "FCR"],
    "Value": [estimasi_biomassa, fcr]
})

fig = px.bar(chart_df, x="Parameter", y="Value",
             title="Grafik Biomassa & FCR Udang",
             text_auto=True)

st.plotly_chart(fig, use_container_width=True)

##############################################
# ANALISIS SINGKAT
##############################################
st.subheader("📝 Analisis Otomatis")

analisis = f"""
### 🔍 Ringkasan Analisis:
- Dengan **{jumlah_benur:,} benur** dan SR **{sr*100:.1f}%**, estimasi jumlah panen adalah **{int(jumlah_panen):,} ekor**.
- Dengan target size **{size_target} ekor/kg**, estimasi biomassa: **{estimasi_biomassa:.2f} kg**.
- FCR sebesar **{fcr:.2f}**, ini termasuk kategori **{'baik' if fcr < 1.5 else 'sedang' if fcr <= 1.8 else 'kurang efisien'}**.
- Perkiraan pendapatan: **Rp {total_penjualan:,.0f}**
- Total modal: **Rp {total_modal:,.0f}**
- 👉 **Laba bersih: Rp {profit:,.0f}**
- Titik impas tercapai di **{bep_kg:.2f} kg** produksi.

"""

st.markdown(analisis)
