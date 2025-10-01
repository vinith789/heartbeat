Heartbeat ventilator data pipeline (Node + Python)

Overview
- Node.js `server.js` listens for TCP ventilator data on one or more ports, forwards raw text to a Python analysis service, and serves a dashboard that displays analyzed results in real-time via Socket.IO.
- Python `analysis_service.py` exposes a simple /analyze endpoint that parses CSV-like strings (e.g. `HR=88,SPO2=96,RR=18,TV=480,FiO2=40`), performs basic threshold checks and returns JSON with alarms.
- `simulator.py` can send test CSV lines to a TCP port for development.

Quick start (PowerShell)

1) Install Python deps:

```powershell
python -m pip install -r .\requirements.txt
```

2) Start Python analysis service:

```powershell
python .\analysis_service.py
```

3) Install Node dependencies and start the server:

```powershell
npm install
npm start
```

By default the Node server serves the dashboard on http://localhost:3000 and listens for ventilator TCP data on ports 9001 and 9002.

4) Send test data to a port:

```powershell
python .\simulator.py --port 9001 --csv "HR=88,SPO2=96,RR=18,TV=480,FiO2=40" --count 5 --interval 1
```

Open the dashboard at http://localhost:3000

Configuration
- Set environment variable `VENT_PORTS` to a comma-separated list of ports (for example `9001,9002,9003`).
- Set `PYTHON_ANALYSIS_URL` if the analysis service runs on a different host/port.

Next steps / improvements
- Add authentication and TLS for the HTTP and TCP channels.
- Replace simple threshold logic with the existing ML model for advanced analysis.
- Add persistence and historical charts.
