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
