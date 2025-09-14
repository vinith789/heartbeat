import React, { useEffect, useState } from "react";

function App() {
  const [alerts, setAlerts] = useState([]);

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8080");
    ws.onmessage = (event) => {
      const alert = JSON.parse(event.data);
      setAlerts((prev) => [alert, ...prev.slice(0, 49)]);
    };
    return () => ws.close();
  }, []);

  return (
    <div className="p-4 bg-gray-100 min-h-screen">
      <h1 className="text-3xl font-bold mb-4">ICU Heart Rate Alerts</h1>
      <div className="space-y-4">
        {alerts.map((a, index) => (
          <div
            key={index}
            className="bg-white shadow-lg rounded-xl p-4 border-l-4 border-red-500"
          >
            <p>
              <strong>Time:</strong> {a.timestamp}
            </p>
            <p>
              <strong>Heart Rate:</strong> {a.heart_rate} bpm
            </p>
            <p>
              <strong>Anomaly Score:</strong> {a.anomaly_score}
            </p>
            <p>
              <strong>Status:</strong> {a.status}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;
