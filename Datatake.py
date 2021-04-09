import serial
import csv
import pandas as pd
import matplotlib.pyplot as plt
from sys import getsizeof
import struct


recording_time = 180
i = 0


def _handshake(serialinst):
        """ Send/receive pair of bytes to synchronize data gathering """
        serialinst.reset_input_buffer()
        serialinst.reset_output_buffer()
        nbytes = serialinst.write(str(recording_time).encode()) # can write anything here, just a single byte (any ASCII char)
        #wait for byte to be received before returning
        st = time.perf_counter()
        byte_back = serialinst.readline()
        et = time.perf_counter()
                
                
#Stabilisco collegamento con Arduino

ser = serial.Serial(port = '/dev/cu.usbmodem1421', baudrate = 115200, bytesize=serial.EIGHTBITS, timeout = .1)   # apro la porta seriale
ser.flushInput()       # non fa sovrappore i dati            

_handshake(ser)
  
    
#Presa dati

start_time = time.perf_counter()
    
while(time.perf_counter() - start_time < recording_time):
        raw_data = ser.read(size=39996)
        data = struct.iter_unpack('iiI',raw_data)
        
        for it in data:
            fullpath = "presa" + str(i) + ".csv"
            print(fullpath)
            with open(fullpath,"a") as f:           # "a" = append
                writer = csv.writer(f)
                writer.writerow(it)
                f.close()
i += 1
