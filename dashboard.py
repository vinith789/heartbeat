import dash
from dash import dcc, html
from dash.dependencies import Output, Input
import plotly.graph_objs as go
from kafka import KafkaConsumer
import json
import threading
import queue
import time

# Queue to hold data from Kafka
data_queue = queue.Queue()

# Start Kafka consumer in background thread
def consume_kafka():
    consumer = KafkaConsumer(
        'icu_heart_rate',
        bootstrap_servers='localhost:9092',
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )
    for msg in consumer:
        data_queue.put(msg.value)

threading.Thread(target=consume_kafka, daemon=True).start()

# Initialize Dash app
app = dash.Dash(__name__)
app.title = "ICU Heart Rate Monitor"

# Containers
heart_rates = []
timestamps = []
alert_logs = []

# Layout
app.layout = html.Div([
    html.H2("💓 Real-time ICU Heart Rate Dashboard"),
    
    dcc.Graph(id='live-graph', style={'height': '60vh'}),
    
    html.Div(id='alert-box', style={
        'color': 'red',
        'fontWeight': 'bold',
        'fontSize': '20px',
        'padding': '10px',
        'border': '2px solid red',
        'marginTop': '10px'
    }),
    
    dcc.Interval(id='interval-update', interval=1000, n_intervals=0),
])

# Update graph and alert box
@app.callback(
    [Output('live-graph', 'figure'),
     Output('alert-box', 'children')],
    [Input('interval-update', 'n_intervals')]
)
def update_graph(n):
    alerts = []
    while not data_queue.empty():
        record = data_queue.get()
        hr = record['current_hr']
        ts = record['timestamp']
        
        heart_rates.append(hr)
        timestamps.append(ts)

        if hr > 120:
            alert = f"🚨 ALERT: High HR Detected - {hr} bpm at {time.strftime('%H:%M:%S')}"
            alert_logs.append(alert)
            alerts.append(alert)

        # Keep last 50 points
        if len(heart_rates) > 50:
            heart_rates.pop(0)
            timestamps.pop(0)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=timestamps,
        y=heart_rates,
        mode='lines+markers',
        line=dict(color='green'),
        name='Heart Rate'
    ))
    fig.update_layout(
        xaxis_title='Timestamp',
        yaxis_title='Heart Rate (bpm)',
        yaxis_range=[50, 200],
        title='Live Heart Rate from ICU',
        template='plotly_dark'
    )

    # Show only last 5 alerts
    return fig, "\n".join(alert_logs[-5:]) if alert_logs else "✅ No critical alerts."

# Run the dashboard
if __name__ == '__main__':
    app.run(debug=True)

