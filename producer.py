from kafka import KafkaProducer
import pandas as pd, json, time, argparse, os


def simulate_csv_data(filepath):
    df = pd.read_csv(filepath)
    for i in range(100, len(df)):
        window = [int(x) for x in df['heart_rate'].iloc[i-100:i].tolist()]
        current_hr = int(df['heart_rate'].iloc[i])
        timestamp = str(df['timestamp'].iloc[i]) if 'timestamp' in df.columns else str(time.time())
        yield {
            "window": window,
            "current_hr": current_hr,
            "timestamp": timestamp
        }
        time.sleep(1)

def start_producer(filepath):
    # Try Kafka first; if Kafka is unavailable user can run with --local
    producer = None
    try:
        producer = KafkaProducer(
            bootstrap_servers='localhost:9092',
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
    except Exception:
        producer = None

    if producer:
        for record in simulate_csv_data(filepath):
            producer.send('icu_heart_rate', value=record)
            print(f"📤 Sent HR: {record['current_hr']}")
    else:
        # Fallback to local JSONL file for testing without Kafka
        out_file = 'local_messages.jsonl'
        print(f"⚠️ Kafka not available — writing messages to {out_file}")
        with open(out_file, 'a', encoding='utf-8') as f:
            for record in simulate_csv_data(filepath):
                f.write(json.dumps(record) + '\n')
                f.flush()
                print(f"📤 (local) Wrote HR: {record['current_hr']}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--local', action='store_true', help='Force local mode (no Kafka)')
    parser.add_argument('csv', nargs='?', default='icu_heartbeat.csv')
    args = parser.parse_args()

    if args.local:
        # Remove existing local file to start fresh
        try:
            os.remove('local_messages.jsonl')
        except OSError:
            pass
        # Run producer but skip Kafka attempt
        for record in simulate_csv_data(args.csv):
            with open('local_messages.jsonl', 'a', encoding='utf-8') as f:
                f.write(json.dumps(record) + '\n')
                f.flush()
                print(f"📤 (local) Wrote HR: {record['current_hr']}")
    else:
        start_producer(args.csv)


if __name__ == "__main__":
    main()

