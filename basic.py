import serial
import time
import csv
import os

os.system("rm data2.csv")

ser = serial.Serial('/dev/ttyACM0')
ser.flushInput()

list_in_floats = []
list_data = []

while True:
        ser_data = ser.readline().rstrip()
        decoded_data = str(ser_data[0:len(ser_data)].decode("utf-8"))
        list_data = decoded_data.split(",")
        for item in list_data:
          list_in_floats.append(float(item))

        print(list_in_floats[0])
        with open("data2.csv","a") as f:
          writer = csv.writer(f,delimiter=",")
          writer.writerow([list_in_floats])

        list_in_floats.clear()
        list_data.clear()

ser.close()
