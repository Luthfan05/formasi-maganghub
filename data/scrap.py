import requests
import json
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

def ambil_data(max_pages=1900, limit=20):
    hasil = []
    session = requests.Session()

    url_awal = f"https://maganghub.kemnaker.go.id/be/v1/api/list/vacancies-aktif?order_by=jumlah_terdaftar&order_direction=ASC&page=1&limit={limit}"
    first = session.get(url_awal).json()
    total_page = first.get("pagination", {}).get("total_page", max_pages)
    total_page = min(total_page, max_pages)

    def fetch_page(page):
        url = f"https://maganghub.kemnaker.go.id/be/v1/api/list/vacancies-aktif?order_by=jumlah_terdaftar&order_direction=ASC&page={page}&limit={limit}"
        r = session.get(url)
        if r.status_code != 200:
            return []
        return r.json().get("data", [])

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(fetch_page, p): p for p in range(1, total_page + 1)}

        for future in as_completed(futures):
            page_data = future.result()
            for item in page_data:
                try:
                    prodi_list = json.loads(item.get("program_studi", "[]"))
                    prodi_titles = [p.get("title", "") for p in prodi_list]

                    perusahaan = item.get("perusahaan", {})
                    jadwal = item.get('jadwal', {})

                    hasil.append({
                        "id_posisi": item.get("id_posisi"),
                        "posisi": item.get("posisi"),
                        "jumlah_kuota": item.get("jumlah_kuota"),
                        "jumlah_terdaftar": item.get("jumlah_terdaftar"),
                        "program_studi": ", ".join(prodi_titles),
                        "nama_perusahaan": perusahaan.get("nama_perusahaan"),
                        "nama_kabupaten": perusahaan.get("nama_kabupaten"),
                        "nama_provinsi": perusahaan.get("nama_provinsi"),
                        "Batas": jadwal.get("tanggal_pendaftaran_akhir")
                    })
                except Exception:
                    continue

    return hasil


data = ambil_data(max_pages=1900, limit=20)

if data:
    df = pd.DataFrame(data)
    df.to_csv("/content/posisi.csv", index=False, encoding="utf-8-sig")
    print(f"Data disimpan ke 'posisi.csv' ({len(df)} baris)")
else:
    print("Tidak ada data ditemukan.")
