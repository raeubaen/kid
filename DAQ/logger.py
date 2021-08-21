import serial
import struct
import time
import os
from datetime import datetime
import sys

data_folder = "../../wave_forms"
#data_folder = "/media/ruben/Volume/Orlando/wave_forms"
recording_time = int(sys.argv[1])

def _handshake(serialinst):

        # writes to Arduino the recording_time (minus 1 s, to be sure python reads all the data) in s
        nbytes = serialinst.write(str(recording_time - 1).encode())

        # reads back the recording_time in ms
        byte_back = serialinst.readline()
        print(f"Noise RMS: {byte_back.decode()} ADC units")

# enables communication with Arduino
ser = serial.Serial(
            port='/dev/ttyACM0',
            baudrate=115200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=recording_time,
)

# performs handshake
_handshake(ser)

# starts data acquisition
now = datetime.now() # current date and time of acquisition starting (precision of a second)
date_time = now.strftime("%m-%d-%Y, %H.%M.%S")

acquisition_path = os.path.join(data_folder, date_time)
os.makedirs(acquisition_path)

dt_f = open(os.path.join(acquisition_path, "dead_time.txt"), "w")
dt_f.write("#dead_time(ms)\n")

end_time = time.time() + recording_time
i = 0
while time.time() < end_time:
    # Reads data of 1 triggered event, containing :
    # 3333 samples in the form (I, Q, t)
    # 1 sample containing the time needed by arduino to send data to serial during the previous communication

    raw_data = ser.read(size=39996)   # 12 * (BUFFER_SIZE + 1)

    if len(raw_data) < 12: # on the last acquisition it can happen that nothing is read
      continue

    data_iter = struct.iter_unpack('iiI', raw_data[:-12])

    data_f = open(os.path.join(acquisition_path, f"signal{i}.dat"), "w")

    for it in data_iter:
        data_f.write("{} {} {}\n".format(*it))

    dt = struct.unpack('iiI', raw_data[-12:])
    dt_f.write(f"{dt[1]}\n")

    data_f.close()

    i += 1

dt_f.close()
