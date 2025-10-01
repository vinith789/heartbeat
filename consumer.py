from kafka import KafkaConsumer
import requests
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import json, argparse, os, time

def preprocess(window):
    scaler = MinMaxScaler()
    return scaler.fit_transform(np.array(window).reshape(-1, 1)).reshape(1, -1, 1)

def rule_based_alert(hr, score, threshold_hr=120, threshold_score=0.7):
    return hr > threshold_hr and score > threshold_score

# 🔔 NEW: Function to log alerts
def log_alert(hr, score):
    alert = {"hr": hr, "score": score}
    alerts = []

    # Read existing alerts (if file exists)
    if os.path.exists("alerts.json"):
        with open("alerts.json", "r") as f:
            try:
                alerts = json.load(f)
            except json.JSONDecodeError:
                alerts = []

    # Append new alert, keep only the latest 10
    alerts.append(alert)
    alerts = alerts[-10:]

    with open("alerts.json", "w") as f:
        json.dump(alerts, f)


def process_message(data):
    window = preprocess(data['window'])
    try:
        res = requests.post("http://localhost:8501/v1/models/icu_model:predict",
                            json={"instances": window.tolist()})
        score = res.json().get('predictions', [[0.0]])[0][0]
    except Exception:
        score = 0.0

    if rule_based_alert(data['current_hr'], score):
        print(f"🚨 [ALERT] HR={data['current_hr']} | Score={score:.3f}")
        log_alert(data['current_hr'], score)
    else:
        print(f"✅ HR={data['current_hr']} | Score={score:.3f}")


def start_consumer(local_only=False):
    if not local_only:
        try:
            consumer = KafkaConsumer('icu_heart_rate',
                                     bootstrap_servers='localhost:9092',
                                     value_deserializer=lambda v: json.loads(v.decode('utf-8')))
            for msg in consumer:
                data = msg.value
                process_message(data)
            return
        except Exception:
            print('⚠️ Kafka not available — falling back to local file mode')

    # Local file mode: read appended lines from local_messages.jsonl
    path = 'local_messages.jsonl'
    last_pos = 0
    while True:
        if not os.path.exists(path):
            time.sleep(1)
            continue
        with open(path, 'r', encoding='utf-8') as f:
            f.seek(last_pos)
            for line in f:
                try:
                    data = json.loads(line.strip())
                except Exception:
                    continue
                process_message(data)
            last_pos = f.tell()
        time.sleep(1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--local', action='store_true', help='Force local mode (read local_messages.jsonl)')
    args = parser.parse_args()
    start_consumer(local_only=args.local)


if __name__ == "__main__":
    main()
from kafka import KafkaConsumer
import requests
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import json
import os

def preprocess(window):
    scaler = MinMaxScaler()
    return scaler.fit_transform(np.array(window).reshape(-1, 1)).reshape(1, -1, 1)

def rule_based_alert(hr, score, threshold_hr=120, threshold_score=0.7):
    return hr > threshold_hr and score > threshold_score

# 🔔 NEW: Function to log alerts
def log_alert(hr, score):
    alert = {"hr": hr, "score": score}
    alerts = []

    # Read existing alerts (if file exists)
    if os.path.exists("alerts.json"):
        with open("alerts.json", "r") as f:
            try:
                alerts = json.load(f)
            except json.JSONDecodeError:
                alerts = []

    # Append new alert, keep only the latest 10
    alerts.append(alert)
    alerts = alerts[-10:]

    with open("alerts.json", "w") as f:
        json.dump(alerts, f)

def start_consumer():
    consumer = KafkaConsumer('icu_heart_rate',
                             bootstrap_servers='localhost:9092',
                             value_deserializer=lambda v: json.loads(v.decode('utf-8')))

    for msg in consumer:
        data = msg.value
        window = preprocess(data['window'])
        res = requests.post("http://localhost:8501/v1/models/icu_model:predict",
                            json={"instances": window.tolist()})
        score = res.json()['predictions'][0][0]

        if rule_based_alert(data['current_hr'], score):
            print(f"🚨 [ALERT] HR={data['current_hr']} | Score={score:.3f}")
            log_alert(data['current_hr'], score)  # 👈 Add this
        else:
            print(f"✅ HR={data['current_hr']} | Score={score:.3f}")

if __name__ == "__main__":
    start_consumer()
