# Final-Project_BigData-B6

## Anggota Kelompok

| NRP        | Nama Lengkap              |
| ---------- | ------------------------- |
| 5027221038 | Dani Wahyu Anak Ary       |
| 5027221048 | Malvin Putra Rismahardian |
| 5027221084 | Farand Febriansyah        |
| 5027221088 | Veri Rahman               |

## Overview

Proyek ini membangun sistem _Data Lakehouse Real-Time_ untuk data penjualan produk fashion menggunakan pipeline yang terdiri dari Kafka, Python, MinIO, dan Streamlit.

Sistem ini menyediakan:

- Streaming data real-time dari CSV ke Kafka.
- Konsumsi Kafka dan simpan ke MinIO dalam format Parquet.
- Dashboard interaktif untuk eksplorasi data dan prediksi jumlah penjualan berdasarkan rating dan penjualan saat ini.

## Dataset

[https://www.kaggle.com/datasets/vikashrajluhaniwal/fashion-images](https://www.kaggle.com/datasets/vikashrajluhaniwal/fashion-images)

## Arsitektur

Sistem ini mengikuti arsitektur real-time lakehouse yang terdiri dari:

- Dataset CSV → Kafka → Kafka Consumer → MinIO → Streamlit
- Model prediksi sederhana menggunakan Linear Regression
- Data tersimpan dalam format Parquet di bucket `fashion-lakehouse` MinIO

![image](https://github.com/user-attachments/assets/096cc3c9-18d8-4549-bad9-137a17db87f4)

## How to run?

### Quick start

```bash
bash start.sh
```

Script ini akan:

- Build dan start container
- Membuat bucket MinIO jika belum ada
- Menjalankan producer dan processor
- Membuka dashboard di [http://localhost:8501](http://localhost:8501)

### Manual Steps

1. _Start Docker Compose_

```bash
docker-compose up -d --build
```

2. _Pastikan bucket MinIO tersedia_

```bash
docker-compose exec minio sh -c '
  mc alias set local http://localhost:9000 minioadmin minioadmin
  mc mb --ignore-existing local/fashion-lakehouse
'
```

3. _Jalankan producer real-time_

```bash
docker-compose exec streamlit \
  python kafka/producer_rt.py \
    --csv-path data/fashion_sales.csv \
    --interval 1 \
    --bootstrap-servers kafka:9092
```

4. _Dashboard_ akan tersedia di:

[http://localhost:8501](http://localhost:8501)

## Folder Struktur

```
.
├── start.sh
├── docker-compose.yml
├── Dockerfile.processor
├── requirements.txt
├── data/
│   └── fashion_sales.csv
├── kafka/
│   └── producer_rt.py
├── processor/
│   └── python_processor.py
├── streamlit_app/
│   ├── app.py
│   └── predictor.py
├── img/
│   └── Group_739.png
```

## Dashboard Fitur

| Tab        | Deskripsi                                                                         |
| ---------- | --------------------------------------------------------------------------------- |
| Gallery    | Menampilkan produk berdasarkan filter                                             |
| Top Sold   | Menampilkan 10 produk dengan penjualan tertinggi                                  |
| Insights   | Donut chart distribusi kategori & heatmap rating                                  |
| Prediction | Memasukkan nama produk dan sold_count saat ini untuk prediksi sold_count ke depan |

Contoh prediksi:

- Input: Sneakers A, sold_count: 320
- Output: predicted sold_count: 500

## Output Screenshots
- _Dashboard UI_

  ![arsitektur](Image/dashboard.png)

- _Gallery Product_

![arsitektur](Image/d-gallery.png)

- _Top Sold Products_

  ![arsitektur](Image/d-top-sales.png)

- _Prediction Feature_

  ![arsitektur](Image/d-prediction.png)

- _MinIO Dashboard_

 ![arsitektur](Image/minio.png)

## Catatan

- Dashboard menggunakan model LinearRegression untuk prediksi.
- Data disimpan sebagai file .parquet di MinIO.
- Jika ingin mengubah model, edit kode pada tab "Prediction" di streamlit_app/app.py.
