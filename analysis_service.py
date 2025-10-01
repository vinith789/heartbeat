from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


def parse_csv_like(raw: str):
    """Parse inputs like 'HR=88,SPO2=96,RR=18,TV=480,FiO2=40' into dict"""
    data = {}
    if not raw:
        return data
    parts = [p.strip() for p in raw.split(',') if '=' in p]
    for p in parts:
        k, v = p.split('=', 1)
        k = k.strip()
        v = v.strip()
        try:
            if '.' in v:
                data[k] = float(v)
            else:
                data[k] = int(v)
        except ValueError:
            data[k] = v
    return data


def analyze(values: dict):
    alarms = []
    # Heart rate
    hr = values.get('HR')
    if hr is not None:
        if hr < 50 or hr > 140:
            alarms.append('HR out of range')
    # SPO2
    spo2 = values.get('SPO2')
    if spo2 is not None:
        if spo2 < 90:
            alarms.append('Low SpO2')
    # Respiratory rate
    rr = values.get('RR')
    if rr is not None:
        if rr < 8 or rr > 30:
            alarms.append('RR out of range')
    # Tidal volume
    tv = values.get('TV')
    if tv is not None:
        if tv < 200 or tv > 1000:
            alarms.append('TV out of range')
    # FiO2
    fio2 = values.get('FiO2')
    if fio2 is not None:
        if fio2 < 21 or fio2 > 100:
            alarms.append('FiO2 out of range')

    status = 'ok' if not alarms else 'alarm'
    return { 'alarms': alarms, 'status': status }


@app.route('/analyze', methods=['POST'])
def analyze_route():
    payload = request.get_json(force=True)
    raw = payload.get('raw') if payload else None
    port = payload.get('port') if payload else None
    values = parse_csv_like(raw)
    result = analyze(values)
    return jsonify({ 'port': port, 'values': values, 'result': result })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
