# IFE parser and csv
import string
import re
import os
import numpy as np

# FORMAT FOR USE: python ife_tmp.py -F <FILENAME.TXT>
########### Pre-Processing File
def readFile(filename):
	# read in file
	with open(filename, "r") as given_file:
		file_data = given_file.readlines()
		file_data = [row.replace("\r" , "") for row in file_data]
		file_data = [row.replace("\n" , "") for row in file_data]
	return file_data

########### Save Data as CSV
def outputCSV(filename, data_list):
	# save data from text as a csv
	given_file = os.path.basename(os.path.splitext(filename)[0]) # return only the filename and not the extension
	output_filename = "{0}_data.csv".format(given_file.upper())
	import csv
	with open(output_filename, 'w+') as txt_data:
		fieldnames = ['year', 'month', 'day', 'hour', 'minute', 'second', 'millisecond', 'btotal', 'bx', 'by', 'bz']
		writer = csv.DictWriter(txt_data, fieldnames=fieldnames)
		writer.writeheader() 
		for data in data_list:
			writer.writerow({'year': data[0], 'month': data[1], 'day': data[2], 'hour': data[3], 'second': data[4], 'millisecond': data[5], 'btotal': data[6], 'bx': data[7], 'by': data[8], 'bz': data[9]})
	print("OUTPUT FILE SAVED AS '{0}'".format(output_filename))

########### IFE IDENTIFICATION CRITERIA

## FIRST CRITERIA: MAGNETIC FIELD ENHANCEMENT IS LARGER THAN 25% OF AMBIENT
def magEnhance(b_total_list):
	'''
	define an ambient magnetic field magnitude over a four hour interval and compare the peak of |B| (where the derivative is zero)
	to the ambient. 
	Returns true if peak value is larger than (0.25)*(|B|avg)
	'''
	from scipy import stats # trimmed mean to remove percent_trim% of both ends of the mean
	percent_trim = 0.45
	trimmed_mean = stats.trim_mean(b_total_list, percent_trim)
	#print("original mean= {0}".format(np.mean(b_total_list)))
	#print("trimmed_mean = {0}".format(trimmed_mean))
	
	'''
	import matplotlib.pyplot as plt
	plt.plot(b_total_list, color='blue')
	trimmed_mean = stats.trim_mean(b_total_list, .15)
	plt.plot([trimmed_mean]*len(b_total_list), '--', color='red') # print with mean
	trimmed_mean = stats.trim_mean(b_total_list, .30)
	plt.plot([trimmed_mean]*len(b_total_list), '--', color='green') # print with mean
	trimmed_mean = stats.trim_mean(b_total_list, .45)
	plt.plot([trimmed_mean]*len(b_total_list), '--', color='yellow') # print with mean
	plt.show()
	'''
	return 

## SECOND CRITERIA: EVENT LASTS LONGER THAN 10 MINUTES (measured over four hour intervals) 
def eventDur():
	'''
	an event duration is defined as the time before and after a peak for |B| to return to the ambient (averaged over four hours)
	field magnitude. 
	Returns true if this duration is longer than 10 minutes.
	'''
	pass

## THIRD CRITERIA: CURENT SHEET IS PRESENT NEAR PEAK |B|
def jSheet():
	'''
	a current sheet is present for a sharp rotation of at least one of the components. 
	Return true if (i) at least one component of B changes from positive -> negative (or vv) within the duration of the event
	(ii) and the change happens within a minute
	'''
	pass

## FOURTH CRITERIA: AT LEAST ONE MAGNETIC COMPONENT DOES NOT ROTATE DURING THE ENHANCEMENT
def noRot():
	# a rotation of the magnetic field component is defined as when the component changes from positive -> negative (or vv)
	# Returns true if at least one component does not change sign within the event
	pass

if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser(description="flag format given as: -F <filename>")
	parser.add_argument('-F', '-filename', help="filename from data")
	args = parser.parse_args()

	filename = args.F

	if filename is None:
		print("\n\tWARNING: File not given, exiting...\n")
		exit()

	graph_data = readFile(filename)
	start_data = 0
	for i in range(len(graph_data)):
		graph_data[i] = re.sub("\s+", ",", graph_data[i].strip()) # replace all whitespace with commas in data
		if graph_data[i] == 'DATA:':
			start_data = i # save the index of the start of the data (typically 102)
	csv_data = graph_data[start_data+1:] # splice all data for just the graphable data (+1 to not include 'DATA:') 
	csv_data = [row.split(',') for row in csv_data]
	#for row in csv_data:
	#	print(row)

	#outputCSV(filename, csv_data)

	# store each value in its own list
	b_total = [float(col[7]) for col in csv_data]
	b_x = [float(col[8]) for col in csv_data]
	b_y = [float(col[9]) for col in csv_data]
	b_z = [float(col[10]) for col in csv_data]

	magEnhance(b_total)
