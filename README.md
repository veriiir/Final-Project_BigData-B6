# Final Project: Big Data dan Data Lakehouse - Kelompok B6

## Anggota Kelompok

| NRP        | Nama Lengkap              |
| ---------- | ------------------------- |
| 5027221038 | Dani Wahyu Anak Ary       |
| 5027221048 | Malvin Putra Rismahardian |
| 5027221084 | Farand Febriansyah        |
| 5027221088 | Veri Rahman               |

# Analisis Penjualan Fashion: Prediksi Penjualan Produk

## Deskripsi Masalah

Penjualan produk fashion sangat dipengaruhi oleh banyak faktor seperti rating pelanggan, popularitas, harga, dan kategori produk. Proyek ini bertujuan membangun sistem data lakehouse real-time untuk menampilkan visualisasi data produk sekaligus melakukan prediksi jumlah penjualan berikutnya menggunakan model machine learning berbasis regresi.

## Tujuan Proyek

- Membangun pipeline real-time dengan Kafka dan MinIO untuk menyimpan data produk fashion

- Membuat proses ETL dari Kafka Producer ke MinIO

- Melatih model regresi untuk memprediksi jumlah penjualan

- Menyediakan dashboard interaktif menggunakan Streamlit

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

## Komponen

| Komponen     | Deskripsi |
|--------------|-----------|
| **Apache Kafka** | Digunakan untuk mengalirkan data penjualan produk fashion secara real-time dari file CSV ke pipeline pemrosesan. |
| **MinIO** | Berfungsi sebagai object storage (Data Lake) untuk menyimpan data dalam format *.parquet*, serta menyimpan model jika diperlukan. |
| **Python** | Bahasa utama yang digunakan untuk membangun Kafka Producer, Kafka Consumer, pemrosesan data, serta pelatihan dan prediksi model. |
| **Streamlit** | Membangun dashboard interaktif untuk menampilkan galeri produk, analitik penjualan, serta fitur prediksi penjualan ke depan. |
| **Docker & Docker Compose** | Mengorkestrasi dan menjalankan seluruh layanan proyek secara terisolasi dan otomatis. |
| **Scikit-Learn** | Digunakan untuk pelatihan model Linear Regression yang memprediksi sold_count berdasarkan rating dan data historis. |
| **Altair & Pandas** | Digunakan untuk visualisasi data (grafik batang, donut chart, heatmap) dan manipulasi data tabular. |
| **S3FS** | Library untuk mengakses MinIO (compatible dengan S3 API) langsung dari Python dan Streamlit. |

### Tech Stack

| Kategori              | Teknologi                                      |
|-----------------------|------------------------------------------------|
| **Containerization**  | Docker, Docker Compose                         |
| **Data Streaming**    | Apache Kafka                                   |
| **Data Lake Storage** | MinIO                                          |
| **Backend & ML**      | Python                                         |
| **Library Python**    | Kafka-Python, MinIO                            |
| **Dashboard**         | Streamlit                                      |

## Langkah Menjalankan Proyek dalam 1 Command

### Quick start

```bash
bash start.sh atau ./start.sh
```
apabila permission denied, coba lakukan:
```bash
chmod +x start.sh
```

Script ini akan:

- Build dan start container
- Membuat bucket MinIO jika belum ada
- Menjalankan producer dan processor
- Membuka dashboard di [http://localhost:8501](http://localhost:8501)

### Langkah Menjalankan Proyek secara Manual

1. _Start Docker Compose_
   
Build dan jalankan seluruh layanan:
```bash
docker-compose up -d --build
```
Ini akan otomatis menjalankan layanan berikut:

- Apache Kafka (data streaming)

- MinIO (object storage)

- Streamlit (dashboard)

- Kafka Producer dan Processor (real-time pipeline)

2. _Cek & Buat Bucket MinIO_

Buka terminal:
```bash
docker-compose exec minio sh
```
Kemudian di dalam container MinIO:
```bash
mc alias set local http://localhost:9000 minioadmin minioadmin
mc mb --ignore-existing local/fashion-lakehouse
exit
```
  _Bucket fashion-lakehouse akan digunakan untuk menyimpan file Parquet hasil konsumsi Kafka dan model prediksi._

3. _Jalankan Kafka Producer (Real-Time)_

Jalankan Kafka producer untuk membaca data dari file CSV dan mengirimkan ke Kafka Topic _fashion-products_:

```bash
docker-compose exec streamlit \
  python kafka/producer_rt.py \
    --csv-path data/fashion_sales.csv \
    --interval 1 \
    --bootstrap-servers kafka:9092
```
  _File fashion_sales.csv berisi data penjualan produk fashion, akan dikirimkan baris demi baris ke Kafka setiap 1 detik._

4. _Cek File di MinIO_

- Akses MinIO dashboard di: http://localhost:9000

- Login:

  - Username: minioadmin

  - Password: minioadmin

- Masuk ke bucket fashion-lakehouse dan pastikan file .parquet muncul setelah beberapa detik

5. _Akses Dashboard Streamlit_

Buka browser:
[http://localhost:8501](http://localhost:8501)

Dashboard akan menampilkan:

- Gallery Produk

- Top Sold Products

- Donut Chart Kategori

- Prediksi Penjualan Produk

## Langkah Menghentikan Proyek

1. Untuk menghentikan semua layanan, buka terminal baru di direktori proyek dan jalankan:
```bash
docker-compose down
```

2. Untuk menghapus juga data yang ada di MinIO, gunakan:
```bash
docker-compose down -v
```

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

- Input: Ant Kids Boys Rock Grey Tshirts sold_count: 301, rating: 4.50
- Output: predicted sold_count: 435
![arsitektur](Image/contoh-predict.png)

## Output

### - _Dashboard UI_

  ![arsitektur](Image/dashboard.png)

Deskripsi:

- Ini adalah tampilan utama dashboard setelah data berhasil dimuat dari MinIO.

- Di bagian atas terdapat KPI seperti:

  - Total SKUs: jumlah total produk fashion yang tersedia.

  - Categories: jumlah kategori produk unik.

  - Avg. Rating: rata-rata penilaian dari semua produk.

- Terdapat tombol Download filtered CSV untuk mengunduh data yang telah difilter.

- Navigasi tab tersedia untuk menjelajahi fitur seperti Gallery, Top Sold, Insights, Category Sales, dan Prediction.

### - _Gallery Product_

![arsitektur](Image/d-gallery.png)

Deskripsi:

- Menampilkan gambar-gambar produk dari dataset berdasarkan filter yang dipilih.

- Setiap produk ditampilkan dengan gambar dan judul produk.

- Disusun secara grid otomatis menggunakan Streamlit columns() dan CSS hover untuk efek pembesaran.

- Berguna untuk melihat visual produk fashion berdasarkan gender, warna, kategori, dan lainnya.

### - _Top Sold Products_

  ![arsitektur](Image/d-top-sales.png)

Deskripsi:

- Menampilkan 10 produk dengan penjualan tertinggi berdasarkan nilai sold_count.

- Disajikan dalam bentuk bar chart dan dataframe untuk mempermudah perbandingan.

- Chart menunjukkan visual penjualan, sedangkan tabel memberikan rincian nama produk, jumlah terjual, dan rating.

### - _Prediction Feature_

  ![arsitektur](Image/d-prediction.png)

Deskripsi:

- Fitur prediksi penjualan produk di masa depan menggunakan model Linear Regression.

- User memilih produk, memasukkan nilai sold_count saat ini.

- Sistem secara otomatis menampilkan rating produk tersebut.

- Setelah klik tombol Predict, akan muncul prediksi penjualan berikutnya beserta:

  - Perbedaan nilai prediksi dengan penjualan saat ini.

  - Nilai akurasi model (R²) dan Mean Absolute Error (MAE).

- Berguna untuk mengestimasi performa produk ke depannya.

### - _MinIO Dashboard_

 ![arsitektur](Image/minio.png)

## Catatan

- Model prediksi menggunakan LinearRegression/RandomForest sederhana.

- Semua file parquet dan model tersimpan di MinIO.

- Jika ingin memperbarui model, ubah predictor.py dan fungsi train_model().
