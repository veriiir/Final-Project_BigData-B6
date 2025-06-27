set -euo pipefail

CSV_PATH=${CSV_PATH:-"data/fashion_sales.csv"}
INTERVAL=${INTERVAL:-1}                   # detik antara pesan
BUCKET=${BUCKET:-"fashion-lakehouse"}    # bucket di MinIO
COMPOSE=docker-compose

echo "Building + starting containers ..."
$COMPOSE up -d --build

wait_port() {
  local HOST=$1 PORT=$2 MSG=${3:-}
  echo -n "Waiting for $HOST:$PORT $MSG "
  until nc -z "$HOST" "$PORT"; do printf '.'; sleep 1; done
  echo " OK"
}

wait_port localhost 9092 "(Kafka broker)"
wait_port localhost 9000 "(MinIO)"

echo "Ensuring bucket \"$BUCKET\" exists ..."
# Jalankan mc di dalam container MinIO (tidak perlu network name manual)
$COMPOSE exec -T minio sh -c "
  mc alias set local http://localhost:9000 minioadmin minioadmin >/dev/null 2>&1 &&
  mc mb --ignore-existing local/$BUCKET
"

echo "Starting real-time producer …"
$COMPOSE exec -T streamlit \
  python kafka/producer_rt.py \
    --csv-path "$CSV_PATH" \
    --interval "$INTERVAL" \
    --bootstrap-servers kafka:9092 &

PRODUCER_PID=$!

echo "Tailing python-processor logs (Ctrl+C to stop viewing) …"
$COMPOSE logs -f python-processor &
LOG_PID=$!

URL=http://localhost:8501
if command -v xdg-open &>/dev/null;   then xdg-open   $URL & fi
if command -v open     &>/dev/null;   then open       $URL & fi

echo ""
echo "Pipeline is running. Dashboard → $URL"
echo "    Press Ctrl+C to stop producer & log tail."

trap 'echo; echo \"Stopping producer & log tail\"; kill $PRODUCER_PID $LOG_PID 2>/dev/null; exit' INT

wait $PRODUCER_PID