import math
from pathlib import Path

import pandas as pd
import requests
import streamlit as st
from jinja2 import Environment, FileSystemLoader

st.set_page_config(layout="wide")

BASE_DIR = Path(__file__).resolve().parent.parent

env = Environment(
    loader=FileSystemLoader(BASE_DIR / "templates"),
    trim_blocks=True,
    lstrip_blocks=True
)

card_template = env.get_template("card.html")
pagination_template = env.get_template("pagination.html")

css = (BASE_DIR / "static" / "styles.css").read_text(encoding="utf-8")
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

API_LIST_URL = "https://maganghub.kemnaker.go.id/be/v1/api/list/vacancies-aktif"

df = pd.read_csv(BASE_DIR / "data" / "posisi.csv")


def hitung_prob(row):
    kuota = row["jumlah_kuota"]
    daftar = row["jumlah_terdaftar"]
    if kuota <= 0:
        return 0.0
    if daftar < kuota:
        return 1.0

    p = kuota / max(daftar, 1)
    return min(1.0, max(0.0, p))



@st.cache_data(ttl=60)
def get_detail_posisi(id_posisi: str):
    params = {"id_posisi": id_posisi}
    r = requests.get(API_LIST_URL, params=params, timeout=5)
    r.raise_for_status()
    data = r.json()
    if not data.get("data"):
        return None
    item = data["data"][0]
    return {
        "jumlah_kuota": item.get("jumlah_kuota"),
        "jumlah_terdaftar": item.get("jumlah_terdaftar"),
    }


def enrich_page_with_realtime(df_page: pd.DataFrame) -> pd.DataFrame:
    df_page = df_page.copy()
    for idx, row in df_page.iterrows():
        detail = get_detail_posisi(row["id_posisi"])
        if not detail:
            continue
        if detail["jumlah_kuota"] is not None:
            df_page.at[idx, "jumlah_kuota"] = detail["jumlah_kuota"]
        if detail["jumlah_terdaftar"] is not None:
            df_page.at[idx, "jumlah_terdaftar"] = detail["jumlah_terdaftar"]
        p = hitung_prob(df_page.loc[idx])
        df_page.at[idx, "prob_val"] = p
        df_page.at[idx, "probabilitas"] = f"{int(p * 100)}%"
    return df_page


df["prob_val"] = df.apply(hitung_prob, axis=1)
df["probabilitas"] = (df["prob_val"] * 100).astype(int).astype(str) + "%"

all_prodi = (
    df["program_studi"]
    .str.split(",")
    .explode()
    .str.strip()
    .dropna()
    .unique()
)
all_prodi = sorted(all_prodi)

df_filtered = df.copy()

left_spacer, filter_col, right_spacer = st.columns([1, 6, 1])
with filter_col:
    col_f1, col_f2, col_f3 = st.columns(3)

    with col_f1:
        prodi_options = ["(Semua)"] + all_prodi
        prodi_selected = st.selectbox("Filter Program Studi", prodi_options)

    if prodi_selected != "(Semua)":
        df_filtered = df_filtered[
            df_filtered["program_studi"].str.contains(prodi_selected, na=False)
        ]

    with col_f2:
        prov_options = sorted(df_filtered["nama_provinsi"].unique().tolist())
        prov_selected = st.multiselect("Filter Provinsi", options=prov_options)

    if prov_selected:
        df_filtered = df_filtered[df_filtered["nama_provinsi"].isin(prov_selected)]

    with col_f3:
        kab_options = sorted(df_filtered["nama_kabupaten"].unique().tolist())
        kab_selected = st.multiselect("Filter Kabupaten/Kota", options=kab_options)

    if kab_selected:
        df_filtered = df_filtered[df_filtered["nama_kabupaten"].isin(kab_selected)]

df_filtered = df_filtered.sort_values("prob_val", ascending=False)

PAGE_SIZE = 20

total_rows = len(df_filtered)
total_pages = max(1, math.ceil(total_rows / PAGE_SIZE))

if "page" not in st.session_state:
    st.session_state.page = 1

params = st.query_params
if "page" in params:
    try:
        st.session_state.page = int(params["page"])
    except Exception:
        pass

if "last_count" not in st.session_state:
    st.session_state.last_count = total_rows
elif st.session_state.last_count != total_rows:
    st.session_state.page = 1
    st.session_state.last_count = total_rows

st.session_state.page = max(1, min(st.session_state.page, total_pages))

start_idx = (st.session_state.page - 1) * PAGE_SIZE
end_idx = start_idx + PAGE_SIZE

df_page = df_filtered.iloc[start_idx:end_idx]
df_page = enrich_page_with_realtime(df_page)

cards_html = '<div class="card-grid">'

for _, row in df_page.iterrows():
    link = f"https://maganghub.kemnaker.go.id/lowongan/view/{row['id_posisi']}"
    initials = "".join([w[0] for w in row["posisi"].split()[:2]]).upper()
    prob_pct = float(row["prob_val"]) * 100
    if prob_pct >= 80:
        corner_class = "corner-green"
    elif prob_pct >= 40:
        corner_class = "corner-orange"
    else:
        corner_class = "corner-red"

    html = card_template.render(
        link=link,
        initials=initials,
        corner_class=corner_class,
        posisi=row["posisi"],
        nama_perusahaan=row["nama_perusahaan"],
        nama_kabupaten=row["nama_kabupaten"].title(),
        jumlah_terdaftar=row["jumlah_terdaftar"],
        jumlah_kuota=row["jumlah_kuota"],
        probabilitas=row["probabilitas"],
        batas=row["Batas"],
    )
    cards_html += html

cards_html += "</div>"

st.markdown(cards_html, unsafe_allow_html=True)

if df_filtered.empty:
    st.info("Tidak ada lowongan yang cocok dengan filter yang dipilih.")

MAX_PAGES_DISPLAY = 7
current_page = st.session_state.page

if total_pages <= MAX_PAGES_DISPLAY:
    page_numbers = list(range(1, total_pages + 1))
else:
    half_window = MAX_PAGES_DISPLAY // 2
    start_page = max(1, current_page - half_window)
    end_page = start_page + MAX_PAGES_DISPLAY - 1
    if end_page > total_pages:
        end_page = total_pages
        start_page = end_page - MAX_PAGES_DISPLAY + 1
    page_numbers = list(range(start_page, end_page + 1))

pagination_html = pagination_template.render(
    current_page=current_page,
    page_numbers=page_numbers,
    total_pages=total_pages,
)

left_spacer, pag_col, toggle_col = st.columns([1, 4, 1])

with pag_col:
    st.markdown(
        f"<div class='pagination-wrapper'>{pagination_html}</div>",
        unsafe_allow_html=True,
    )

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

with toggle_col:
    st.toggle("Dark mode", key="dark_mode")

if st.session_state.dark_mode:
    dark_css = """
    .stApp{
        background:#0f172a;
        color:#e5e7eb;
    }
    .card{
        background:#020617;
        box-shadow:0 4px 20px rgba(0,0,0,.45);
    }
    .card-title{ color:#f9fafb; }
    .card-company{ color:#9ca3af; }
    .card-body{ color:#e5e7eb; }
    .tag-chip{
        background:#1e293b;
        border-color:#1e293b;
        color:#93c5fd;
    }
    .stat-table{ border-color:#1e293b; }
    .stat-header{
        background:#020617;
        color:#60a5fa;
    }
    .stat-value{ color:#e5e7eb; }
    .card-footer{
        border-top-color:#1e293b;
        color:#9ca3af;
    }
    .page-pill{
        background:#020617;
        border-color:#1e293b;
        color:#93c5fd;
    }
    .page-pill-active{
        background:#3b82f6;
        border-color:#3b82f6;
        color:#ffffff;
    }
    """
    st.markdown(f"<style>{dark_css}</style>", unsafe_allow_html=True)




