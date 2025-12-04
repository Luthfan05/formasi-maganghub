# Formasi MagangHub

Aplikasi Streamlit untuk eksplorasi dan visualisasi data lowongan magang pada platform MagangHub, termasuk pencarian status pendaftaran peserta, penelusuran posisi magang aktif, serta penyaringan lowongan berdasarkan kriteria akademik dan wilayah.

Aplikasi ini dibuat untuk keperluan analisis data dan tidak berafiliasi secara resmi dengan MagangHub atau instansi terkait.

## Fitur Utama

### 1. Pencarian Status Peserta Berdasarkan Email (Page 1)
Pengguna dapat memasukkan alamat email peserta untuk melihat:
- Daftar posisi yang pernah dilamar
- Nama perusahaan dan alamat
- Tanggal pendaftaran
- Status seleksi
- Jumlah peserta yang diterima pada posisi tersebut
- Total pendaftar pada posisi yang sama
- Jumlah peserta yang diterima di perusahaan lain

Data diperoleh dengan melakukan permintaan HTTP ke endpoint internal yang digunakan oleh aplikasi web untuk menampilkan informasi peserta.

### 2. Pengambilan Seluruh Posisi Aktif (Scraping via Request)
Data diambil dengan melakukan request HTTP ke endpoint internal yang digunakan oleh aplikasi web MagangHub.

Proses ini dilakukan melalui:
`data/scrap.py`
Hasilnya disimpan dalam bentuk file CSV dan digunakan sebagai sumber data utama aplikasi, sehingga proses visualisasi dan filter dapat berjalan cepat tanpa melakukan permintaan berulang.

### 3. Filter Lowongan Based on Kriteria (Page 2)
Aplikasi menyediakan fitur penyaringan lowongan magang berdasarkan:
- Program Studi
- Provinsi
- Kabupaten atau Kota

Proses filter dilakukan secara lokal menggunakan pandas. Hasil filter kemudian ditampilkan dalam bentuk kartu dengan pagination untuk menjaga performa aplikasi.

### 4. Redirect ke Halaman Lowongan
Setiap entri lowongan menyediakan tautan langsung ke halaman lowongan pada situs MagangHub, sehingga pengguna dapat melanjutkan eksplorasi atau pendaftaran langsung ke sumber aslinya.

### 5. Penyegaran Data Pendaftar Per Halaman
Untuk menjaga performa:
- Data jumlah pendaftar hanya diambil ulang untuk halaman aktif
- Permintaan dilakukan berdasarkan identitas posisi
- Mekanisme cache digunakan untuk menghindari permintaan berulang dalam waktu singkat

## Struktur Folder
```formasi-maganghub/
├─ data/
│ ├─ posisi.csv
│ └─ scrap.py
├─ pages/
│ └─ 2_Filter_jurusan.py
├─ static/
│ └─ styles.css
├─ templates/
│ ├─ card.html
│ └─ pagination.html
├─ 1_Status_Magang.py
├─ requirements.txt
└─ README.md
```


## Framework dan Library
- Streamlit
- Pandas
- Requests
- Jinja2

## Catatan Penggunaan
- Aplikasi ini tidak menyediakan akses administratif atau modifikasi data.
- Seluruh data ditampilkan sebagaimana tersedia melalui mekanisme yang dapat diamati pada aplikasi web.
- Penggunaan aplikasi disarankan untuk tujuan pembelajaran, eksplorasi, dan analisis data.

## Disclaimer
Aplikasi ini bersifat tidak resmi dan tidak memiliki hubungan dengan pengelola MagangHub maupun instansi pemerintah terkait. Seluruh merek dan konten yang ditampilkan merupakan milik masing-masing pihak.
