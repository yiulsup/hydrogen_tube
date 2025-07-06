from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

# MySQL 연결
def get_db_connection():
    connection = mysql.connector.connect(
        host='localhost',
        database='iot_data',
        user='iot_user',
        password='Newflame#6856'  # 꼭 본인 비밀번호로 변경!
    )
    return connection

# API endpoint
@app.route('/api/data', methods=['POST'])
def receive_data():
    data = request.get_json()
    print("Received data:", data)
    
    # JSON에서 데이터 추출
    device_id = data.get('device_id')
    timestamp = data.get('timestamp')
    temperature = data.get('temperature')
    humidity = data.get('humidity')
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = """
            INSERT INTO sensor_data (device_id, timestamp, temperature, humidity)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(sql, (device_id, timestamp, temperature, humidity))
        conn.commit()
        return jsonify({"status": "success"}), 201
    except Error as e:
        print("DB Error:", e)
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# 서버 실행
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)

