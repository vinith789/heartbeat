import pandas as pd
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv1D, LSTM, Dropout, Dense
from sklearn.preprocessing import MinMaxScaler
import os

# Load and segment data
def load_and_segment_data(filepath, window_size=200):
    df = pd.read_csv(filepath)
    X, y = [], []
    scaler = MinMaxScaler()
    for i in range(len(df) - window_size):
        window = df['heart_rate'].iloc[i:i+window_size].values.reshape(-1, 1)
        norm_window = scaler.fit_transform(window).flatten()
        X.append(norm_window)
        if 'label' in df.columns:
            y.append(df['label'].iloc[i + window_size])
    return np.array(X).reshape(-1, window_size, 1), np.array(y)

# Define model
def build_model():
    model = Sequential([
        Conv1D(64, 3, activation='relu', input_shape=(100, 1)),
        LSTM(64),
        Dropout(0.2),
        Dense(1, activation='sigmoid')
    ])
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return model

# Train and save
X, y = load_and_segment_data('icu_heartbeat.csv')
model = build_model()
model.fit(X, y, epochs=10, batch_size=32)

# Save in proper format for TF Serving
os.makedirs("icu_model/1", exist_ok=True)
model.export("icu_model/1")  # ✅ Correct for TensorFlow Serving


