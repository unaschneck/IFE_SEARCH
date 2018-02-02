# IFE parser and csv
import string
import re
import os

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
		fieldnames = ['year', 'month', 'day', 'hour', 'minute', 'second', 'millisecond', 'b1', 'b2', 'b3', 'btotal']
		writer = csv.DictWriter(txt_data, fieldnames=fieldnames)
		writer.writeheader() 
		for data in data_list:
			writer.writerow({'year': data[0], 'month': data[1], 'day': data[2], 'hour': data[3], 'second': data[4], 'millisecond': data[5], 'b1': data[6], 'b2': data[7], 'b3': data[8], 'btotal': data[9]})
	print("OUTPUT FILE SAVED AS '{0}'".format(output_filename))

########### IFE IDENTIFICATION CRITERIA

# FIRST CRITERIA: MAGNETIC FIELD ENHANCEMENT IS LARGER THAN 25% OF AMBIENT
def magEnhance():
	# define an ambient magnetic field magnitude over a four hour interval and compare the peak of |B| (where the derivative is zero)
	# to the ambient. 
	# Returns true if peak value is larger than (0.25)*(|B|avg)
	pass

# SECOND CRITERIA: EVENT LASTS LONGER THAN 10 MINUTES (measured over four hour intervals) 
def eventDur):
	# an event duration is defined as the time before and after a peak for |B| to return to the ambient (averaged over four hours)
	# field magnitude. 
	# Returns true if this duration is longer than 10 minutes.
	pass

# THIRD CRITERIA: CURENT SHEET IS PRESENT NEAR PEAK |B|
def jSheet():
	# a current sheet is present for a sharp rotation of at least one of the components. 
	# Return true if (i) at least one component of B changes from positive -> negative (or vv) within the duration of the event
	# (ii) and the change happens within a minute
	pass

# FOURTH CRITERIA: AT LEAST ONE MAGNETIC COMPONENT DOES NOT ROTATE DURING THE ENHANCEMENT
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
		
	outputCSV(filename, csv_data)
