import serial
import csv
import pandas as pd
import matplotlib.pyplot as plt
from sys import getsizeof
import struct
import time

recording_time = 10
i = 0


def _handshake(serialinst):
        """ Send/receive pair of bytes to synchronize data gathering """
        serialinst.reset_input_buffer()
        serialinst.reset_output_buffer()
        nbytes = serialinst.write(str(recording_time).encode()) # can write anything here, just a single byte (any ASCII char)
        #wait for byte to be received before returning
        st = time.perf_counter()
        byte_back = serialinst.readline()
        print(byte_back)
        et = time.perf_counter()
                
                
#Stabilisco collegamento con Arduino
ser = serial.Serial(
            port='/dev/ttyACM0',
            baudrate=115200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=recording_time,
)

#ser.flushInput()       # non fa sovrappore i dati            

_handshake(ser)
  
    
#Presa dati

start_time = time.perf_counter()
    
a = open("fileacaso.txt", "w")
b = open("roba.txt", "w")
while(time.perf_counter() - start_time < recording_time):
        raw_data = ser.read(size=39996)
        data = struct.iter_unpack('iiI', raw_data)
        
        for it in data:
            b.write("{} {} {}\n".format(*it))
        
        a.write(f"Dead time ms: {ser.readline().decode()}")
i += 1
