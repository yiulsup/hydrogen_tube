import requests
import json
import time
from datetime import datetime
import random

# 서버 주소 (본인 서버 주소로 변경)
SERVER_URL = "http://192.168.0.113:8000/api/data"

# IoT Device ID
DEVICE_ID = "iot_002"

def generate_data():
    """가상의 센서 데이터 생성"""
    print("generated data")
    return {
        "device_id": DEVICE_ID,
        "timestamp": datetime.utcnow().isoformat(),
        "temperature": round(random.uniform(20.0, 30.0), 2),
        "humidity": round(random.uniform(40.0, 70.0), 2)
    }

def send_data(payload):
    """HTTP POST로 서버에 데이터 전송"""
    try:
        response = requests.post(
            SERVER_URL,
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        print(f"[{datetime.utcnow()}] Sent: {payload}")
        print(f"Server responded with: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    while True:
        data = generate_data()
        send_data(data)
        time.sleep(10)
