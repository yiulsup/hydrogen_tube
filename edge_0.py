import serial
import time

ser = serial.Serial(baudrate=9600, port="COM7", timeout=1)

buffer = ""

while True:
    char = ser.read().decode('utf-8', errors='ignore')
    #print(char)
    buffer += char 
    if "Motion Sensor Start!!!" in buffer:
        print(buffer)
        buffer = ""

    if "sensor is activated!!" in buffer:
        command = "date 2000-01-01 00:00:00\n\r"
        ser.write(command.encode('utf-8'))
        print(buffer)
        buffer = ""
        print(f"write completed with {command}")
     
        
    if "Ref:" in buffer and buffer.strip().endswith('-'):
            ref_part = buffer.split("Ref:", 1)[1]
            if ',' in ref_part:
                print(f"{buffer.strip()}")
                buffer = ""


