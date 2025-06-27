import os, json, time, argparse, logging
from datetime import datetime
import pandas as pd
from confluent_kafka import Producer

def get_producer(bootstrap: str) -> Producer:
    return Producer({
        "bootstrap.servers": bootstrap,
        "linger.ms": 5
    })

def ack(err, msg):
    if err:
        logging.error("delivery failed: %s", err)
    else:
        logging.debug("delivered to %s [%d] offset %d",
                      msg.topic(), msg.partition(), msg.offset())

def run():
    p = argparse.ArgumentParser(description="Real-time CSV → Kafka Producer")
    p.add_argument("--csv-path", default="data/fashion_sales.csv", help="Path to input CSV file")
    p.add_argument("--bootstrap-servers", default="kafka:9092")
    p.add_argument("--topic", default="fashion-products")
    p.add_argument("--interval", type=float, default=1.0, help="Sleep seconds between messages")
    p.add_argument("--usecols", default=None, help="Comma-separated list of columns to load")
    p.add_argument("--query", default=None, help="Pandas query string for filtering rows")
    p.add_argument("--sample", type=int, default=None, help="Random sample N rows after filtering")
    args = p.parse_args()

    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)s — %(message)s")

    if not os.path.exists(args.csv_path):
        logging.error("CSV file not found: %s", args.csv_path)
        raise FileNotFoundError(args.csv_path)

    usecols = None if not args.usecols else [c.strip() for c in args.usecols.split(",")]
    df = pd.read_csv(args.csv_path, engine="pyarrow", usecols=usecols)

    if args.query:
        try:
            df = df.query(args.query)
        except Exception as e:
            logging.error("Invalid query: %s", e)
            return

    if args.sample:
        df = df.sample(n=min(args.sample, len(df)), random_state=42)

    if df.empty:
        logging.warning("No data after filtering/sampling — exiting.")
        return

    logging.info("Loaded %d rows", len(df))

    producer = get_producer(args.bootstrap_servers)

    try:
        for rec in df.to_dict("records"):
            rec["arrival_time"] = datetime.utcnow().isoformat()
            producer.produce(args.topic, json.dumps(rec).encode(), callback=ack)
            producer.poll(0)
            logging.info("→ sent %s", rec.get("ProductId", rec.get("ImageName", "N/A")))
            time.sleep(args.interval)
    except KeyboardInterrupt:
        logging.info("Interrupted by user.")
    finally:
        logging.info("Flushing …")
        producer.flush()

if __name__ == "__main__":
    run()
