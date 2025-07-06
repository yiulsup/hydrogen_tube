from flask import Flask, render_template_string, jsonify
import mysql.connector
import json

app = Flask(__name__)

def get_data():
    conn = mysql.connector.connect(
        host='localhost',
        database='iot_data',
        user='iot_user',
        password='Newflame#6856'
    )
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT 100")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows[::-1]  # 시간 오름차순

@app.route("/api/data", methods=["GET"])
def api_data():
    data = get_data()
    return jsonify(data)

html_template = """
<!doctype html>
<html>
<head>
    <title>IoT Dashboard - Realtime</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f0f2f5;
        }
        .container {
            width: 80%;
            margin: auto;
            display: flex;
            flex-direction: column;
            gap: 30px;
            padding-top: 20px;
        }
        .card {
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            padding: 20px;
        }
        .card h3 {
            text-align: center;
            margin-bottom: 15px;
        }
    </style>
</head>
<body>
    <h2 style="text-align:center;">Real-time IoT Dashboard</h2>
    <div class="container">
        <div class="card">
            <h3>Temperature Chart (°C)</h3>
            <canvas id="tempChart"></canvas>
        </div>
        <div class="card">
            <h3>Humidity Chart (%)</h3>
            <canvas id="humChart"></canvas>
        </div>
    </div>
    <script>
        let tempChart, humChart;

        async function fetchData() {
            const res = await fetch('/api/data');
            const data = await res.json();
            return {
                labels: data.map(d => d.timestamp),
                temperatures: data.map(d => d.temperature),
                humidities: data.map(d => d.humidity)
            };
        }

        async function initChart() {
            const ctxTemp = document.getElementById('tempChart').getContext('2d');
            const ctxHum = document.getElementById('humChart').getContext('2d');

            const {labels, temperatures, humidities} = await fetchData();

            tempChart = new Chart(ctxTemp, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Temperature (°C)',
                        data: temperatures,
                        borderWidth: 2
                    }]
                }
            });

            humChart = new Chart(ctxHum, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Humidity (%)',
                        data: humidities,
                        borderWidth: 2
                    }]
                }
            });
        }

        async function updateChart() {
            const {labels, temperatures, humidities} = await fetchData();
            tempChart.data.labels = labels;
            tempChart.data.datasets[0].data = temperatures;
            tempChart.update();

            humChart.data.labels = labels;
            humChart.data.datasets[0].data = humidities;
            humChart.update();
        }

        initChart();
        setInterval(updateChart, 5000);
    </script>
</body>
</html>
"""

@app.route("/dashboard")
def dashboard():
    return render_template_string(html_template)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

