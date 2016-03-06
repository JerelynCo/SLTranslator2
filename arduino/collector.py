import serial, serial.tools.list_ports
import sys

serialPort = "/dev/ttyACM0"
BAUD_RATE = 9600

# For output file
ofile = open(str(time.strftime("%m%d%y_%H%M")+"_log.csv"), 'w')

# Setting up of serial
ser = serial.Serial(serialPort, BAUD_RATE)

while(1):
	line = ser.readline().decode("utf-8")
	# Writing of the data from the serial
	print(line)
	ofile.write(line)

ser.close()  
ofile.close() 