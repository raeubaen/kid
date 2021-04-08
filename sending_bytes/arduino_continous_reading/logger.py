import time
import pandas as pd
import serial
import sys
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import os
import struct

class SerialDataLogger:

    def __init__(self, data_folder, recording_time=600, verbose=True):
        self.recording_time = recording_time
        self.verbose = verbose
        self.data_folder = data_folder
        self.time_axis = None

    def get_data(self):

        # setup serial port - it's the native USB port so baudrate is irrelevant, 
        # the data is always transferred at full USB speed
        ser = serial.Serial(
            port='/dev/ttyACM0',
            baudrate=115200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=self.recording_time 
        )

        self._handshake(ser)

        start_time = time.perf_counter()

        now = datetime.now() # current date and time of acquisition starting (precision of a second)
        date_time = now.strftime("%m-%d-%Y, %H.%M.%S")
        acquisition_path = os.path.join(self.data_folder, date_time)
        os.makedirs(acquisition_path)
        f = open(os.path.join(acquisition_path, "signal.dat"), "a")
        f.write("v none time\n")
        while(time.perf_counter() - start_time < self.recording_time):
            raw_data = ser.read(size=12000)

            unpacked_data_iterator = struct.iter_unpack("iiI", raw_data)
            for sample in unpacked_data_iterator:
                f.write("{} {} {}\n".format(*sample))
        f.close()

        et = time.perf_counter() - start_time
        if self.verbose:
            print('Elapsed time reading data (s): ', et)

    def _handshake(self, serialinst):
        """ Send/receive pair of bytes to synchronize data gathering """
        serialinst.reset_input_buffer()
        serialinst.reset_output_buffer()
        nbytes = serialinst.write(str(self.recording_time).encode()) # can write anything here, just a single byte (any ASCII char)
        if self.verbose:
            print('Wrote bytes to serial port: ', nbytes)
        #wait for byte to be received before returning
        st = time.perf_counter()
        byte_back = serialinst.readline()
        et = time.perf_counter()
        if self.verbose:
            print('Received handshake data from serial port: ', byte_back)
            print('Time between send and receive: ', et-st)

def main():
    """ Grab data once and save it to file, with current timestamp """

    # the waveforms directory must be out of the github repo (to avoid putting all the data on github every time)
    # the waveforms directory must be created by hand if not present
    SR = SerialDataLogger("../../wave_forms", recording_time=30)
    SR.get_data()

if __name__ == '__main__':
    main()
