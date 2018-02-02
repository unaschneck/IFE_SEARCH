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
