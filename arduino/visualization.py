import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import serial, serial.tools.list_ports
import sys
import numpy as np
from collections import deque
import time

BAUD_RATE = 9600
FS_COUNT = 5 #Flex sensors count
CS_COUNT = 4 #Contact Sensors count
AG_COUNT = 6 #Accel and gyro axes

serialPort = "/dev/ttyACM0"

# Setting up of serial
ser = serial.Serial(serialPort, BAUD_RATE)

#Number of points per frame
maxLen = 150

# Initialization of windows
windows = {"winFs": pg.GraphicsWindow(), "winCs": pg.GraphicsWindow(), "winAG": pg.GraphicsWindow()}

# Assignment of window titles
windows["winFs"].setWindowTitle("Flex sensor readings")
windows["winCs"].setWindowTitle("Contact sensor readings")
windows["winAG"].setWindowTitle("Accelerometer and Gyroscope readings")


"""
Plots layout on the screen
Fs = Flex sensor
Cs = Contact sensor
A(axis) = Accelerometer
G(axis) = Gyroscope
"""

# Flex sensor window plots
pFs = []
for i in range(1,9):
	if i % 3 != 0:
		pFs.append(windows["winFs"].addPlot())
	else:
		windows["winFs"].nextRow()


# Contact sensor window plots
pCs = []
for i in range(1,6):
	if i % 3 != 0:
		pCs.append(windows["winCs"].addPlot())
	else:
		windows["winCs"].nextRow()

# Accelerometer and  gyroscope
pAG = [windows["winAG"].addPlot() for i in range(3)]
windows["winAG"].nextRow()
for i in range(3):
	pAG.append(windows["winAG"].addPlot())


# Customization of plots for flex
for sensor in pFs:
	sensor.setRange(yRange=(0,5))
	sensor.setTitle("Flex " + str(pFs.index(sensor)))
	sensor.setLabel(axis="left", text="Voltage", units="V")
	sensor.setLabel(axis="bottom", text="Time", units="s")

# Customization of plots for contact
for sensor in pCs:
	sensor.setRange(yRange=(-1,2))
	sensor.setTitle("Contact " + str(pCs.index(sensor)))
	sensor.setLabel(axis="left", text="Contact", units="")
	sensor.setLabel(axis="bottom", text="Time", units="s")


# Customization of plots for accel and gyroscope
for sensor in pAG:
	sensor.setRange(yRange=(0, 100))
	sensor.setLabel(axis="bottom", text="Time", units="s")
	if pAG.index(sensor) < 3:
		sensor.setTitle("Accel " + str(pAG.index(sensor)))
		sensor.setLabel(axis="left", text="Accel", units="")
	else:
		sensor.setTitle("Gyro " + str(pAG.index(sensor)))
		sensor.setLabel(axis="left", text="Gyro", units="")


# Initializing of data arrays
dataFs = np.zeros((FS_COUNT, maxLen))
dataCs = np.zeros((CS_COUNT, maxLen))
dataAG = np.zeros((AG_COUNT, maxLen))

# Initializing of curves/plots
curvesFs = [pFs[i].plot(dataFs[i]) for i in range(FS_COUNT)]
curvesCs = [pCs[i].plot(dataCs[i]) for i in range(CS_COUNT)]
curvesAG = [pAG[i].plot(dataAG[i]) for i in range(AG_COUNT)]

# 'x' or time initialization
ptr = 0

# Updates plots
def update():
	global ptr
	# Reading of the serial
	line = ser.readline().decode("utf-8")
	# Writing of the data from the serial
	print(line)

	# Moves plot to the left
	for i in range(FS_COUNT):
		dataFs[i][:-1] = dataFs[i][1:]
	for i in range(CS_COUNT):
		dataCs[i][:-1] = dataCs[i][1:]
	for i in range(AG_COUNT):
		dataAG[i][:-1] = dataAG[i][1:]


	# Stripping and splitting of serial data
	# data = [float(val) for val in line.strip().split(",")]
	data = []
	for val in line.strip().split(","):
		try:
			data.append(float(val))
		except ValueError:
			continue


	# Assigns new data from Serial
	for i in range(0, len(data)):
		if i < FS_COUNT:
			dataFs[i][-1] = data[i]
		elif i < FS_COUNT + CS_COUNT:
			dataCs[i-FS_COUNT][-1] = data[i]
		else:
			dataAG[i-(FS_COUNT+CS_COUNT)][-1] = data[i] 
	
	# Incrementing 'x'
	ptr += 1

	# Assignment and setting of values to the plot
	for i in range(len(curvesFs)):
		curvesFs[i].setData(dataFs[i])
		curvesFs[i].setPos(ptr,0)
	for i in range(len(curvesCs)):
		curvesCs[i].setData(dataCs[i])
		curvesCs[i].setPos(ptr,0)
	for i in range(len(curvesAG)):
		curvesAG[i].setData(dataAG[i])
		curvesAG[i].setPos(ptr,0)

def close():
	ser.flush()
	ser.close()  

update()
timer = pg.QtCore.QTimer()
timer.timeout.connect(update)
timer.start(50)

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
