from flask import Flask, jsonify, Response
import random
import re

app = Flask(__name__)

def generate_random_data():
    data_list = []
    for i in range(1, 1001):
        data_list.append({
            "device_no": i,
            "left":   [random.uniform(10,11), random.uniform(5,6), random.uniform(0,1)],
            "center": [random.uniform(10,11), random.uniform(5,6), random.uniform(0,1)],
            "right":  [random.uniform(10,11), random.uniform(5,6), random.uniform(0,1)],
        })
    return data_list

@app.route("/data/all")
def data_all():
    return jsonify(generate_random_data())

@app.route("/data/<axis>")
@app.route("/data/<axis>/<range>")
def data(axis, range=None):
    axis_map = {"x": 0, "y": 1, "z": 2}
    idx = axis_map.get(axis, 0)
    data_list = generate_random_data()

    start, end = 1, 1000
    if range:
        m = re.match(r"(\d+)-(\d+)", range)
        if m:
            start, end = int(m.group(1)), int(m.group(2))

    filtered = []
    for d in data_list:
        if start <= d["device_no"] <= end:
            filtered.append({
                "device_no": d["device_no"],
                "left": d["left"][idx],
                "center": d["center"][idx],
                "right": d["right"][idx]
            })
    return jsonify(filtered)

@app.route("/")
def index_all():
    return Response(build_html_multi(["x", "y", "z"]), mimetype='text/html')

@app.route("/<axis>/<range>")
def index_range(axis, range):
    start, end = 1, 1000
    m = re.match(r"(\d+)-(\d+)", range)
    if m:
        start, end = int(m.group(1)), int(m.group(2))
    return Response(build_html_single(axis, start, end), mimetype='text/html')

@app.route("/<axis>")
@app.route("/<axis>/")
def index_single(axis):
    return Response(build_html_single(axis, 1, 1000), mimetype='text/html')

@app.route("/<axes>")
def index_combinations(axes):
    axes_set = set(axes)
    valid_pairs = [ {"x","y"}, {"y","z"}, {"x","z"} ]
    for pair in valid_pairs:
        if axes_set == pair:
            return Response(build_html_multi(sorted(list(pair))), mimetype='text/html')
    return "Invalid combination", 404

def build_html_multi(axes_list):
    axis_map = {"x": 0, "y": 1, "z": 2}
    colors = {"x": "#FF5733", "y": "#33B5FF", "z": "#28A745"}
    html_head = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Real-time Ground Settlement Sensor Data</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; background: #f0f0f0; }
            .graphs { display: flex; flex-wrap: wrap; justify-content: center; align-items: flex-start; gap: 20px; margin: 20px; }
            .chart-container { background: white; border: 1px solid #ccc; border-radius: 8px; width: 40%; padding: 10px; box-sizing: border-box; }
            canvas { width: 100% !important; height: auto !important; }
        </style>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>
    <body>
        <h1>Real-time Ground Settlement Sensor Data</h1>
        <div class="graphs">
    """
    html_charts = ""
    for ax in axes_list:
        html_charts += f'<div class="chart-container"><h3>{ax.upper()} Axis</h3><canvas id="chart{ax.upper()}"></canvas></div>'

    html_script_start = """
        </div>
        <script>
    """
    html_chart_objects = ""
    for ax in axes_list:
        html_chart_objects += f"""
            const ctx{ax.upper()} = document.getElementById('chart{ax.upper()}').getContext('2d');
            const chart{ax.upper()} = new Chart(ctx{ax.upper()}, {{
                type: 'line',
                data: {{ labels: [], datasets: [{{ label: '{ax.upper()} axis', data: [], borderWidth: 1, fill: false, borderColor: '{colors[ax]}' }}] }},
                options: {{
                    responsive: true,
                    scales: {{ y: {{ min: 0, max: 50 }} }}
                }}
            }});"""
    html_fetch_script = """
            async function fetchDataAndUpdateAll() {
                const response = await fetch('/data/all');
                const data = await response.json();
    """
    for ax in axes_list:
        idx = axis_map[ax]
        html_fetch_script += f"""
                let labels{ax.upper()} = [], values{ax.upper()} = [];
                data.forEach(d => {{
                    labels{ax.upper()}.push(`${{d.device_no}}-L`);
                    labels{ax.upper()}.push(`${{d.device_no}}-C`);
                    labels{ax.upper()}.push(`${{d.device_no}}-R`);
                    values{ax.upper()}.push(d.left[{idx}]);
                    values{ax.upper()}.push(d.center[{idx}]);
                    values{ax.upper()}.push(d.right[{idx}]);
                }});
                chart{ax.upper()}.data.labels = labels{ax.upper()};
                chart{ax.upper()}.data.datasets[0].data = values{ax.upper()};
                chart{ax.upper()}.update();
        """
    html_end = """
            }
            setInterval(fetchDataAndUpdateAll, 2000);
            fetchDataAndUpdateAll();
        </script>
    </body>
    </html>
    """
    return html_head + html_charts + html_script_start + html_chart_objects + html_fetch_script + html_end

def build_html_single(axis, start, end):
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Real-time Ground Settlement Sensor Data ({axis.upper()} axis {start}-{end})</title>
        <style>
            body {{ font-family: Arial, sans-serif; text-align: center; background: #f0f0f0; }}
            canvas {{ background: white; border: 1px solid #ccc; border-radius: 8px; margin-top: 20px; }}
            button {{ margin-top: 10px; padding: 8px 12px; font-size: 14px; border-radius: 6px; border: 1px solid #888; cursor: pointer; }}
        </style>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-zoom@2.0.1"></script>
    </head>
    <body>
        <h1>Real-time Ground Settlement Sensor Data ({axis.upper()} Axis {start}-{end})</h1>
        <canvas id="myChart" width="1200" height="400"></canvas><br>
        <button onclick="resetZoom()">Reset Zoom</button>
        <script>
            const ctx = document.getElementById('myChart').getContext('2d');
            let chart = new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: [],
                    datasets: [{{ label: '{axis.upper()} axis value', data: [], borderWidth: 2, fill: false, borderColor: '#0074D9' }}]
                }},
                options: {{
                    responsive: true,
                    scales: {{ y: {{ min: 0, max: 50 }} }},
                    plugins: {{
                        zoom: {{
                            zoom: {{ wheel: {{enabled: true}}, drag: {{enabled: true}}, mode: 'xy' }},
                            pan: {{ enabled: true, mode: 'xy' }}
                        }}
                    }}
                }}
            }});
            async function fetchDataAndUpdate() {{
                const response = await fetch('/data/{axis}/{start}-{end}');
                const data = await response.json();
                let labels = [], values = [];
                data.forEach(d => {{
                    labels.push(`${{d.device_no}}-L`);
                    labels.push(`${{d.device_no}}-C`);
                    labels.push(`${{d.device_no}}-R`);
                    values.push(d.left);
                    values.push(d.center);
                    values.push(d.right);
                }});
                chart.data.labels = labels;
                chart.data.datasets[0].data = values;
                chart.update();
            }}
            function resetZoom() {{ chart.resetZoom(); }}
            setInterval(fetchDataAndUpdate, 2000);
            fetchDataAndUpdate();
        </script>
    </body>
    </html>
    """
    return html_content

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
