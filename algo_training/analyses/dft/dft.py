import argparse
import pandas as pd
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("filename", help="Indicate the filename to solve", type=str)
args = parser.parse_args()

data = pd.read_csv(args.filename)

def dft(column):
	global dft_vector 
	dft_vector = np.empty(0)
	col_size = len(column)
	for k in range(col_size):
		dft = 0
		for n in range(col_size):
			dft += column[n] * complex(np.cos(-2 * k * n * np.pi/col_size), np.sin(-2 * k * n * np.pi/col_size))
		dft_vector = np.append(dft_vector, dft)
	


dft(data.ix[:,0].values)
data['real'] = [i.real for i in dft_vector]
data['imag'] = [i.imag for i in dft_vector]
data['mag'] = [np.absolute(i) for i in dft_vector]

data.to_csv("output.csv")