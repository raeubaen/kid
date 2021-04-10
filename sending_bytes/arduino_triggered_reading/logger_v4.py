import serial
import struct
import time
import os
from datetime import datetime

data_folder = "../../../wave_forms"
recording_time = 10

def _handshake(serialinst):
        # resets buffer
        serialinst.reset_input_buffer()
        serialinst.reset_output_buffer()

        # tells to Arduino the recording_time in s (minus 1 second, to be sure python reads all the data)
        nbytes = serialinst.write(str(recording_time - 1).encode())

        # reads back the recording_time in ms
        byte_back = serialinst.readline()
        print(byte_back)

# Enables communication with Arduino
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


# Starts data acquisition

now = datetime.now() # current date and time of acquisition starting (precision of a second)
date_time = now.strftime("%m-%d-%Y, %H.%M.%S")

acquisition_path = os.path.join(data_folder, date_time)
os.makedirs(acquisition_path)

dt_f = open("dead_time.txt", "w")

end_time = time.time() + recording_time
i = 0
while time.time() < end_time:
    raw_data = ser.read(size=39996)
    data_gen = struct.iter_unpack('iiI', raw_data)

    data_f = open(os.path.join(acquisition_path, f"signal{i}.dat"), "w")

    for it in data_gen:
      if it[2] != 0: # sampled data
        data_f.write("{} {} {}\n".format(*it))
      elif it[1] != 0: # trigger_on signal (with dead time information)
         data_f.write("TRIGGER_ON\n")
         dt_f.write(f"{it[1]}\n")
      else:
        pass
    data_f.close()

    i += 1

dt_f.close()
