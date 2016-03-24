# for keyboard
from pykeyboard import PyKeyboard
import serial
import numpy as np
from time import sleep

# Arduino
serialPort = "/dev/ttyACM0"
BAUD_RATE = 9600
ser = serial.Serial(serialPort, BAUD_RATE)
k = PyKeyboard()

counter = 0

sleep(.1)
while True:
    row = ser.readline().decode("utf-8").strip()
    if "," in row:
        row = row.split(",")
        int_row = np.array([int(val) for val in row])

    if "enter" in row:
        k.type_string("%s" % int_row)
        counter += 1
        
    if "space" in row:
        k.type_string(" ")

    if counter == 8:
    	ser.write(b'h')
    	counter += 1
    	sleep(.1)    
    print(row)
