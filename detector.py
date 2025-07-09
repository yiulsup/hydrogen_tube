import serial
import time
import re
import socket

def parse_float(value: str) -> float:
    # Check if the value ends with '-' indicating a negative number
    if value.endswith('-'):
        return float(value[:-1]) * -1  # Remove '-' and make it negative
    return float(value) 

HOST = "192.168.0.55"
PORT = 5005

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))
ser = serial.Serial(baudrate=9600, port="COM7", timeout=1000)

buffer = ""  # Initialize buffer to collect input
first = True
second = False
while True:
    if ser.in_waiting > 0:  # Check if there’s incoming data
        if first == True:
            char = ser.read().decode('utf-8', errors='ignore')  # Read one byte
            print(f"Received: {repr(char)}")
            buffer += char  # Add the character to the buffer

        if second == True:
            data = ser.readline().decode('utf-8', errors='ignore')
            client_socket.sendall(data.encode('utf-8'))
            print(data) 

        # Check if the target message is in the buffer
        if "sensor is activated!!" in buffer:
            print("Sensor activated detected!")
            buffer = ""  # Clear buffer after detecting the message
            command = "date 2025-07-07 00:00:00"
            ser.write(command.encode('utf-8'))
            print("write completed")
            second = True
            first = False

client_socket.close()
