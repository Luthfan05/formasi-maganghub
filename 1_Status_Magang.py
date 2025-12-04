import math

import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="Cek Data Peserta", layout="wide")
st.title("Cek Data Peserta Berdasarkan Email")

st.markdown("Masukkan email peserta.")

df = pd.DataFrame()

with st.container():
    email = st.text_input("Email", placeholder="nama@gmail.com")
    search = st.button("Cari Data", type="primary")

API_BASE = "https://maganghub.kemnaker.go.id/be/v1/api/list/crud-program-participants"
headers = {
    "Authorization": st.secrets["api"]["token"]
}


def fetch_all_participants(id_posisi):
    all_rows = []
    url = f"{API_BASE}?id_posisi={id_posisi}&page=1"
    r = requests.get(url, headers=headers, timeout=15)
    data = r.json()

    total = data["meta"]["pagination"]["total"]
    per_page = data["meta"]["pagination"]["per_page"]
    last_page = math.ceil(total / per_page)

    for p in range(1, last_page + 1):
        url_paged = f"{API_BASE}?id_posisi={id_posisi}&page={p}"
        r_page = requests.get(url_paged, headers=headers, timeout=15)
        page_data = r_page.json()
        if "data" in page_data:
            all_rows.extend(page_data["data"])

    return all_rows, total


if search:
    if not email.strip():
        st.warning("Masukkan email terlebih dahulu.")
        st.stop()

    with st.spinner("Mengambil data dari server..."):
        url = f"{API_BASE}?email={email}"
        filtered = []

        try:
            response = requests.get(url, headers=headers, timeout=15)

            if response.status_code != 200:
                st.error(f"Server error: {response.status_code}")
                st.json(response.json())
                st.stop()

            data = response.json()

            if "data" not in data or len(data["data"]) == 0:
                st.info("Tidak ada data peserta ditemukan.")
                st.stop()

            rows = data["data"]

            for row in rows:
                users = row.get("users", {})
                program_posisi = row.get("program_posisi", {})
                perusahaan = row.get("perusahaan", {})
                jadwal = row.get("jadwal", {})
                status_seleksi = row.get("ref_status_seleksi", {})
                id_posisi = program_posisi.get("id_posisi")

                all_participants, total_pendaftar = fetch_all_participants(id_posisi)

                diterima_lain = sum(
                    1
                    for x in all_participants
                    if x.get("ref_status_seleksi", {}).get("id_status_seleksi") == 4
                )
                diterima = sum(
                    1
                    for x in all_participants
                    if x.get("ref_status_seleksi", {}).get("id_status_seleksi") == 2
                )

                filtered.append(
                    {
                        "Posisi": program_posisi.get("posisi"),
                        "Perusahaan": perusahaan.get("nama_perusahaan"),
                        "Alamat": perusahaan.get("alamat"),
                        "Tanggal Daftar": jadwal.get("tanggal_pendaftaran_awal"),
                        "Status Seleksi": status_seleksi.get("nama_status_seleksi"),
                        "Diterima": diterima,
                        "Total Pendaftar": total_pendaftar,
                        "Diterima Perusahaan Lain": diterima_lain,
                    }
                )

            df = pd.DataFrame(filtered)
            df["Tanggal Daftar"] = pd.to_datetime(df["Tanggal Daftar"])
            df = df.sort_values(by="Tanggal Daftar", ascending=False)
        except Exception:
            df = pd.DataFrame(filtered)
            if not df.empty:
                df["Tanggal Daftar"] = pd.to_datetime(df["Tanggal Daftar"])
                df = df.sort_values(by="Tanggal Daftar", ascending=False)

st.markdown(
    """
<style>
.stApp{
    background:#e5ebf3;
    color:#111827;
    font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
}
.stTextInput>div>div>input{
    background:#ffffff;
}
.result-grid{
    display:grid;
    grid-template-columns:repeat(auto-fit,minmax(320px,1fr));
    gap:1.5rem;
    margin-top:1.5rem;
}
.stCard{
    background:#ffffff;
    border-radius:12px;
    box-shadow:0 1px 4px rgba(15,23,42,0.08),0 6px 18px rgba(15,23,42,0.12);
    padding:1rem 1.1rem 0.9rem 1.1rem;
    display:flex;
    flex-direction:column;
    gap:0.4rem;
}
.card-title{
    font-size:0.95rem;
    font-weight:600;
    color:#111827;
    margin-bottom:0.2rem;
}
.subtext{
    font-size:0.78rem;
    color:#4b5563;
    line-height:1.25rem;
    margin-bottom:0.5rem;
}
.metric-grid{
    display:grid;
    grid-template-columns:repeat(2,minmax(0,1fr));
    gap:0.6rem;
    margin-top:0.4rem;
}
.metric-box{
    background:#f3f4f6;
    border-radius:10px;
    padding:0.55rem 0.7rem;
    text-align:left;
}
.metric-label{
    font-size:0.7rem;
    color:#6b7280;
    margin-bottom:0.15rem;
}
.metric-value{
    font-size:0.95rem;
    font-weight:600;
    color:#111827;
}
</style>
""",
    unsafe_allow_html=True,
)

if not df.empty:
    st.markdown("<div class='result-grid'>", unsafe_allow_html=True)

    for _, row in df.iterrows():
        st.markdown("<div class='stCard'>", unsafe_allow_html=True)

        st.markdown(
            f"<div class='card-title'>{row['Posisi']}</div>",
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class='subtext'>
                <b>{row['Perusahaan']}</b><br>
                {row['Alamat']}<br>
                Tanggal Daftar: {row['Tanggal Daftar'].date()}
            </div>
            """,
            unsafe_allow_html=True,
        )

        m1, m2 = st.columns(2)
        m3, m4 = st.columns(2)

        with m1:
            st.markdown(
                f"""
                <div class='metric-box'>
                    <div class='metric-label'>Status Seleksi</div>
                    <div class='metric-value'>{row['Status Seleksi']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with m2:
            st.markdown(
                f"""
                <div class='metric-box'>
                    <div class='metric-label'>Diterima</div>
                    <div class='metric-value'>{row['Diterima']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with m3:
            st.markdown(
                f"""
                <div class='metric-box'>
                    <div class='metric-label'>Total Pendaftar</div>
                    <div class='metric-value'>{row['Total Pendaftar']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with m4:
            st.markdown(
                f"""
                <div class='metric-box'>
                    <div class='metric-label'>Diterima Perusahaan Lain</div>
                    <div class='metric-value'>{row['Diterima Perusahaan Lain']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
