"""
* Make sure predictor directory is present
* Run and install missing libraries (most likely sklearn is missing)
* Change arduino port if necessary
* Report to Je if any errors found
* Edit


** Install the following for windows:
* pywin32
* pyHook

* Install: https://github.com/SavinaRoja/PyUserInput
"""
import RPi.GPIO as GPIO
from sklearn.preprocessing import StandardScaler
from sklearn.externals import joblib
import string
import serial
import serial.tools.list_ports as port
import numpy as np
import pygame

# RPi GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

RLed = 17
YLed = 27
GLed = 22

GPIO.setup(RLed, GPIO.OUT)
GPIO.setup(YLed, GPIO.OUT)
GPIO.setup(GLed, GPIO.OUT)

# audio
pygame.init()

# for keyboard
from pykeyboard import PyKeyboard

# Predictors dictionary
predictors = {
    "svc": "SVC",
    "randomForest": "RandomForestClassifier",
}

# Arduino
for comport in port.comports():
        if "ACM" in comport[0]:
                serialPort = comport[0]

# Arduino
# serialPort = "/dev/ttyACM2"
BAUD_RATE = 9600

# "Group"
directory = "all/"  # Change this if needed
directory = "wo_g/"

# File names
# classifier_fn = "RandomForestClassifier.pkl"  # Change this if needed
classifier_fn = "SVC.pkl"

scaler_fn = "scaler.pkl"

# dir_base = "prediction/"
dir_scaler = "scaler/"
dir_classifiers = "classifiers/"


# Target names
target_names = [i for i in string.ascii_uppercase]

# Setting up of serial
ser = serial.Serial(serialPort, BAUD_RATE)

# Loading scaler
scaler = joblib.load(dir_scaler + directory + scaler_fn)
predictor = joblib.load(dir_classifiers + directory + classifier_fn)


k = PyKeyboard()

letters_min_max = [[[-107, -21, -124, -127, -102], [38, 150, 49, 31, 39]],
                   [[-102, -13, -9, -116, -101], [34, 118, 114, 53, 15]],
                   [[-106, -20, -126, -127, -111], [38, 100, 27, 62, 6]]]

keys = ["Z", "H", "G"]


def checkUser(row, counter):
    for i in range(5):
        for j in range(5):
            if letters_min_max[i][0][j] <= row[i] <= letters_min_max[i][1][j]:
                return True  # within range
            else:
                return False  # out of range

print("Starting serial reading now...")
letter = ""
# counter = 0
while(1):
    row = ser.readline().decode("utf-8").strip()
    if "," in row:
        row = row.split(",")
        int_row = np.array([int(val) for val in row])

        if directory == "wo_g/":
            int_row = int_row[:-3]

        # if counter < len(letters_min_max.keys()):
        # 	if not checkUser(int_row[:5], counter):
        # 		ser.write(b'User does not pass')
        # 		break
        # 	counter += 1

    if "enter" in row:
        prediction = predictor.predict(
            scaler.transform(int_row.reshape(1, -1)))
        letter = target_names[prediction]
        k.type_string("%s" % letter)
        if letter is "B":
                GPIO.output(RLed, 1)
                GPIO.output(GLed, 0)
                GPIO.output(YLed, 0)
        if letter is "G":
                GPIO.output(RLed, 0)
                GPIO.output(GLed, 1)
                GPIO.output(YLed, 0)
        if letter is "W":
                GPIO.output(RLed, 0)
                GPIO.output(GLed, 0)
                GPIO.output(YLed, 1)
        
        letter_sound = pygame.mixer.Sound("audio/" + letter +".wav")
        letter_sound.play()
        
    if "space" in row:
        k.type_string(" ")

    else:
    	pass
