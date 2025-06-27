#!/usr/bin/env python3
import os, json, uuid, time, datetime as dt, socket
import pandas as pd
from confluent_kafka import Consumer
import pyarrow as pa, pyarrow.parquet as pq
import s3fs

# --- ENV & default ---
BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
SRC_TOPIC  = os.getenv("KAFKA_SRC_TOPIC",  "fashion-products")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", 20))
S3_BUCKET  = os.getenv("S3_BUCKET", "fashion-lakehouse")
fs = s3fs.S3FileSystem(
    key   = os.getenv("AWS_ACCESS_KEY_ID", "minioadmin"),
    secret= os.getenv("AWS_SECRET_ACCESS_KEY", "minioadmin"),
    client_kwargs={"endpoint_url": os.getenv("S3_ENDPOINT_URL", "http://minio:9000")},
)

# --- Tunggu hostname Kafka bisa di-resolve (maks 20× coba) ---
for attempt in range(20):
    try:
        socket.gethostbyname("kafka")
        print("Kafka hostname resolved.")
        break
    except socket.gaierror:
        print(f"Waiting for Kafka DNS resolution... attempt {attempt + 1}/20")
        time.sleep(2)
else:
    raise RuntimeError("Kafka hostname could not be resolved after 20 attempts")

consumer = Consumer({
    "bootstrap.servers": BOOTSTRAP,
    "group.id": "fashion-python-consumer",
    "auto.offset.reset": "earliest",
})
consumer.subscribe([SRC_TOPIC])

buffer: list[dict] = []

def flush():
    """tulis buffer ke Parquet lalu kosongkan buffer"""
    global buffer
    if not buffer:
        return
    df = pd.DataFrame(buffer)
    table = pa.Table.from_pandas(df)
    ts = dt.datetime.utcnow()
    key = f"{S3_BUCKET}/{ts:%Y/%m/%d/%H}/{uuid.uuid4()}.parquet"
    with fs.open(key, "wb") as f:
        pq.write_table(table, f, compression="snappy")
    print(f"wrote {len(buffer)} rows → s3://{key}")
    buffer.clear()

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None or msg.error():
            continue

        obj = json.loads(msg.value())
        # Enrich default fields
        obj.setdefault("arrival_time", dt.datetime.utcnow().isoformat())
        obj.setdefault("sold_count", 0)
        obj.setdefault("rating", 0.0)
        obj.setdefault("views", 0)
        buffer.append(obj)

        if len(buffer) >= BATCH_SIZE:
            flush()
except KeyboardInterrupt:
    pass
finally:
    flush()
    consumer.close()
