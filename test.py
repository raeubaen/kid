import time
import pandas as pd
import serial
import sys
import numpy as np
import matplotlib.pyplot as plt

nchannels = 3 # number of total channels (time axis + ADC channels)
datalen = 600 # numbers in each array that serial.print does in arduino

class SerialDataLogger:
	"""
	class for interfacing with the Arduino Data Logger
	The data logger runs on an Arduino DUE; the sketch is "SixChannelLogger.ino"
	and should also be in this directory
	"""
	def __init__(self, recording_time=600,verbose=True):
		self.recording_time = recording_time
		self.verbose = verbose

		self.time_axis = None

	def get_data(self):
		"""
		Initialise serial port and listen for data until timeout. 
		Convert the bytestream into numpy arrays for each channel

		Returns:

			7 numpy arrays (1D) representing time and ADC channels 0-5 
		"""
		# setup serial port - it's the native USB port so baudrate is irrelevant, 
		# the data is always transferred at full USB speed
		ser = serial.Serial(
			port='/dev/ttyACM0',
			baudrate=115200,
			parity=serial.PARITY_NONE,
			stopbits=serial.STOPBITS_ONE,
			bytesize=serial.EIGHTBITS,
			timeout=self.recording_time # seconds - should be the same amount of time as the arduino will send data for + 1
		)

		#testing - repeat serial read to confirm data arrays are always predictable
		#n_reps = 2
		#for i in range(n_reps):

		self._handshake(ser)
        
   		st = time.perf_counter()
        i = 0;
        while(time.perf_counter() - st < self.recording_time)
		    data = ser.read(2**27)	# this number should be larger than the number of
								    # bytes that will actually be sent
		    ser.close()				# close serial port
		    f = open(f"signal{i}.dat", "wb")
		    f.write(data)
		    f.close()
            i += 1;
		et = time.perf_counter() - st
		if self.verbose:
			print('Elapsed time reading data (s): ', et)

	def _handshake(self, serialinst):
		""" Send/receive pair of bytes to synchronize data gathering """
		nbytes = serialinst.write(self.recording_time.encode('a')) # can write anything here, just a single byte (any ASCII char)
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

	SR = SerialDataLogger(recording_time=11)

if __name__ == '__main__':
	main()
