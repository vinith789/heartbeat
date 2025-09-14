from kafka import KafkaProducer
import pandas as pd, json, time

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
    producer = KafkaProducer(
        bootstrap_servers='localhost:9092',
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    for record in simulate_csv_data(filepath):
        producer.send('icu_heart_rate', value=record)
        print(f"📤 Sent HR: {record['current_hr']}")

if __name__ == "__main__":
    start_producer('icu_heartbeat.csv')
