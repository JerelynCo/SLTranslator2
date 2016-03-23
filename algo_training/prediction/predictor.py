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

from sklearn.preprocessing import StandardScaler
from sklearn.externals import joblib
import string
import serial
import serial.tools.list_ports
import numpy as np

# for keyboard
from pykeyboard import PyKeyboard

# Predictors dictionary
predictors = {
    "svc": "SVC",
    "randomForest": "RandomForestClassifier",
}

# Arduino
serialPort = "/dev/ttyACM2"
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


counter = 0
while(1):
    row = ser.readline().decode("utf-8").strip()
    if "," in row:
        row = row.split(",")
        int_row = np.array([int(val) for val in row])

        if directory == "wo_g":
            int_row = int_row[:-3]

        if counter < len(letters_min_max.keys()):
        	if not checkUser(int_row[:5], counter):
        		ser.write(b'User does not pass')
        		break
            counter += 1

    if "enter" in row:
        prediction = predictor.predict(
            scaler.transform(int_row.reshape(1, -1)))
        k.type_string("%s" % (target_names[prediction]))

    if "space" in row:
        k.type_string(" ")

    else:
    	pass
