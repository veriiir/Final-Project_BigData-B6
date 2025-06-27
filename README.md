


# Final-Project_BigData-B6
## Anggota Kelompok

| NRP        | Nama Lengkap              |
| ---------- | ------------------------- |
| 5027221038 | Dani Wahyu Anak Ary       |
| 5027221048 | Malvin Putra Rismahardian |
| 5027221084 | Farand Febriansyah        |
| 5027221088 | Veri Rahman               |

## Overview

Proyek ini membangun sistem *Data Lakehouse Real-Time* untuk data penjualan produk fashion menggunakan pipeline yang terdiri dari Kafka, Python, MinIO, dan Streamlit.

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

(https://github.com/veriiir/Final-Project_BigData-B6/blob/main/Image/tab.png?raw=true)

## How to run?

### Quick start

```bash
bash start.sh
````

Script ini akan:

* Build dan start container
* Membuat bucket MinIO jika belum ada
* Menjalankan producer dan processor
* Membuka dashboard di [http://localhost:8501](http://localhost:8501)

### Manual Steps

1. *Start Docker Compose*

```bash
docker-compose up -d --build
```

2. *Pastikan bucket MinIO tersedia*

```bash
docker-compose exec minio sh -c '
  mc alias set local http://localhost:9000 minioadmin minioadmin
  mc mb --ignore-existing local/fashion-lakehouse
'
```

3. *Jalankan producer real-time*

```bash
docker-compose exec streamlit \
  python kafka/producer_rt.py \
    --csv-path data/fashion_sales.csv \
    --interval 1 \
    --bootstrap-servers kafka:9092
```

4. *Dashboard* akan tersedia di:

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
│   └── requirements.txt
├── img/
│   └── Group_739.png
```

## Dashboard Fitur

| Tab        | Deskripsi                                                                           |
| ---------- | ----------------------------------------------------------------------------------- |
| Gallery    | Menampilkan produk berdasarkan filter                                               |
| Top Sold   | Menampilkan 10 produk dengan penjualan tertinggi                                    |
| Insights   | Donut chart distribusi kategori & heatmap rating                                    |
| Prediction | Memasukkan nama produk dan sold\_count saat ini untuk prediksi sold\_count ke depan |

Contoh prediksi:

* Input: Sneakers A, sold\_count: 320
* Output: predicted sold\_count: 500

## Output Screenshots

* *Top Sold Products*

  DOKUM

* *Prediction Feature*

  DOKUM

* *MinIO Dashboard*

  DOKUM

## Catatan

* Dashboard menggunakan model LinearRegression untuk prediksi.
* Data disimpan sebagai file .parquet di MinIO.
* Jika ingin mengubah model, edit kode pada tab "Prediction" di streamlit\_app/app.py.


