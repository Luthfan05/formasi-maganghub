import streamlit as st
import requests
import pandas as pd
import math
import textwrap

st.set_page_config(page_title="Email Lookup", layout="wide")
st.header("Cek Data Peserta Berdasarkan Email")

st.markdown("""
Masukkan email peserta.  
""")

df = pd.DataFrame()

with st.container():
    email = st.text_input("Email", placeholder="nama@gmail.com")
    search = st.button("Cari Data", type="primary")

API_BASE = "https://maganghub.kemnaker.go.id/be/v1/api/list/crud-program-participants"

headers = {
    "Authorization": st.secrets["api"]["token"]
}


def fetch_all_participants(id_posisi):
    """Loop API pagination sampai semua data terkumpul."""
    all_rows = []

    # Request pertama → untuk cek total & halaman
    url = f"{API_BASE}?id_posisi={id_posisi}&page=1"
    r = requests.get(url, headers=headers)
    data = r.json()

    total = data["meta"]["pagination"]["total"]
    per_page = data["meta"]["pagination"]["per_page"]
    last_page = math.ceil(total / per_page)

    # Loop halaman
    for p in range(1, last_page + 1):
        url_paged = f"{API_BASE}?id_posisi={id_posisi}&page={p}"
        r_page = requests.get(url_paged, headers=headers)
        page_data = r_page.json()

        if "data" in page_data:
            all_rows.extend(page_data["data"])

    return all_rows, total


if search:

    if not email.strip():
        st.warning("Masukkan email terlebih dahulu.")
        st.stop()

    with st.spinner("Mengambil data dari server..."):

        # 1️⃣ Ambil data berdasarkan email
        url = f"{API_BASE}?email={email}"

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

            st.success("Data berhasil diambil!")

            # 2️⃣ Buat tabel output
            filtered = []

            for row in rows:

                users = row.get("users", {})
                program_posisi = row.get("program_posisi", {})
                perusahaan = row.get("perusahaan", {})
                jadwal = row.get("jadwal", {})
                status_seleksi = row.get("ref_status_seleksi", {})
                id_posisi = program_posisi.get("id_posisi")

                # 🔥 Loop semua peserta berdasarkan id_posisi
                all_participants, total_pendaftar = fetch_all_participants(id_posisi)

                # 🔥 Hitung diterima perusahaan lain (id_status_seleksi = 4)
                diterima_lain = sum(
                    1 for x in all_participants
                    if x.get("ref_status_seleksi", {}).get("id_status_seleksi") == 4
                )
                diterima = sum(
                    1 for x in all_participants
                    if x.get("ref_status_seleksi", {}).get("id_status_seleksi") == 2
                )
                filtered.append({
                    "Posisi": program_posisi.get("posisi"),
                    "Perusahaan": perusahaan.get("nama_perusahaan"),
                    "Alamat": perusahaan.get("alamat"),
                    "Tanggal Daftar": jadwal.get("tanggal_pendaftaran_awal"),
                    "Status Seleksi": status_seleksi.get("nama_status_seleksi"),
                    'Diterima': diterima,
                    "Total Pendaftar": total_pendaftar,
                    "Diterima Perusahaan Lain": diterima_lain
                })

            df = pd.DataFrame(filtered)
            df["Tanggal Daftar"] = pd.to_datetime(df["Tanggal Daftar"])
            df = df.sort_values(by="Tanggal Daftar", ascending=False)
        except Exception as e:
            df = pd.DataFrame(filtered)
            df["Tanggal Daftar"] = pd.to_datetime(df["Tanggal Daftar"])
            df = df.sort_values(by="Tanggal Daftar", ascending=False)



st.markdown("""
    <style>
        /* Background */
        .main {
            background-color: #0f1116 !important;
        }

        /* Card container override */
        .stCard {
            background: #1c1f26;
            padding: 20px 22px;
            border-radius: 18px;
            box-shadow: 0 0 18px rgba(0,0,0,0.35);
            border: 1px solid rgba(255,255,255,0.05);
        }

        /* Title color */
        .stCard h3 {
            color: #5cff9d !important;
            margin-bottom: 2px;
            font-size: 1.1rem;
        }

        /* Subtitle */
        .subtext {
            font-size: 0.70rem;
            color: #cfcfcf;
            margin-bottom: 12px;
            line-height: 1.2;
        }

        /* Metric box style */
        .metric-box {
            background: #111319;
            padding: 12px 15px;
            border-radius: 14px;
            text-align: center;
            border: 1px solid rgba(255,255,255,0.04);
        }

        .metric-label {
            font-size: 0.75rem;
            color: #9ca3af;
            margin-bottom: 3px;
        }

        .metric-value {
            font-size: 1.3rem;
            font-weight: 700;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)



cols = st.columns(2)

for idx, (_, row) in enumerate(df.iterrows()):
    col = cols[idx % 2]

    with col:
        st.markdown("<div class='stCard'>", unsafe_allow_html=True)

        # Judul posisi
        st.markdown(f"<h3>{row['Posisi']}</h3>", unsafe_allow_html=True)

        # Informasi perusahaan
        st.markdown(
            f"""
            <div class='subtext'>
                <b>{row['Perusahaan']}</b><br>
                {row['Alamat']}<br>
                Tanggal Daftar: {row['Tanggal Daftar']}
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("<hr style='border:1px solid rgba(255,255,255,0.08);'>", unsafe_allow_html=True)

        # Grid metrics 2x2
        m1, m2 = st.columns(2)
        m3, m4 = st.columns(2)

        with m1:
            st.markdown(
                f"""
                <div class='metric-box'>
                    <div class='metric-label'>Status Seleksi</div>
                    <div class='metric-value'>{row['Status Seleksi']}</div>
                </div>
                """, unsafe_allow_html=True
            )

        with m2:
            st.markdown(
                f"""
                <div class='metric-box'>
                    <div class='metric-label'>Diterima</div>
                    <div class='metric-value'>{row['Diterima']}</div>
                </div>
                """, unsafe_allow_html=True
            )

        with m3:
            st.markdown(
                f"""
                <div class='metric-box'>
                    <div class='metric-label'>Total Pendaftar</div>
                    <div class='metric-value'>{row['Total Pendaftar']}</div>
                </div>
                """, unsafe_allow_html=True
            )

        with m4:
            st.markdown(
                f"""
                <div class='metric-box'>
                    <div class='metric-label'>Diterima Perusahaan Lain</div>
                    <div class='metric-value'>{row['Diterima Perusahaan Lain']}</div>
                </div>
                """, unsafe_allow_html=True
            )

        st.markdown("</div>", unsafe_allow_html=True)