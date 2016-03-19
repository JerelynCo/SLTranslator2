"""
* Make sure predictor directory is present
* Run and install missing libraries (most likely sklearn is missing)
* Change arduino port if necessary
* Report to Je if any errors found
* Edit 
"""

from sklearn.preprocessing import StandardScaler
from sklearn.externals import joblib
import string
import serial
import serial.tools.list_ports
import numpy as np


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

# File names
classifier_fn = "RandomForestClassifier.pkl"  # Change this if needed

scaler_fn = "scaler.pkl"

dir_base = "prediction_new/"
dir_scaler = dir_base + "scaler/"
dir_classifiers = dir_base + "classifiers/"


# Target names
target_names = [i for i in string.ascii_uppercase]

# Setting up of serial
ser = serial.Serial(serialPort, BAUD_RATE)

# Loading scaler
scaler = joblib.load(dir_scaler + directory + scaler_fn)
predictor = joblib.load(dir_classifiers + directory + classifier_fn)

while(1):
    row = ser.readline().decode("utf-8").strip().split(",")
    int_row = np.array([int(val) for val in row])

    if directory == "wo_g":
        int_row = int_row[:-3]

    prediction = predictor.predict(scaler.transform(int_row.reshape(1, -1)))
    print("%s: %s" % (row, target_names[prediction]))
