# IFE parser and csv
import string
import re
import os
import numpy as np
from collections import namedtuple
from datetime import datetime
import matplotlib.pyplot as plt

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

########### Convert string to datetime
def datetime_convert(csv_data):
	# covert to datetime format
	datetime_year = [int(col[0]) for col in csv_data]
	datetime_month = [int(col[1]) for col in csv_data]
	datetime_day = [int(col[2]) for col in csv_data]
	datetime_hour = [int(col[3]) for col in csv_data]
	datetime_minute = [int(col[4]) for col in csv_data]
	datetime_second = [int(col[5]) for col in csv_data]
	datetime_millisecond = [int(col[6]) for col in csv_data]

	dt = [] # datetime: '2009-6-8 23:59:27.0'
	for i in range(len(csv_data)):
		dt.append("{0}-{1}-{2} {3}:{4}:{5}.{6}".format(datetime_year[i],
																datetime_month[i],
																datetime_day[i],
																datetime_hour[i],
																datetime_minute[i],
																datetime_second[i],
											 					datetime_millisecond[i]))
	#print(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f'))
	return dt#[datetime.strptime(t, '%Y-%m-%d %H:%M:%S.%f') for t in dt] # convert to datetime

########### IFE IDENTIFICATION CRITERIA

## FIRST CRITERIA: MAGNETIC FIELD ENHANCEMENT IS LARGER THAN 25% OF AMBIENT
def magEnhance(datetime_list, b_total_list):
	'''
	define an ambient magnetic field magnitude over a four hour interval and compare the peak of |B| (where the derivative is zero)
	to the ambient. 
	Returns true if peak value is larger than (0.25)*(|B|avg)
	'''

	from scipy import stats # trimmed mean to remove percent_trim% of both ends of the mean
	percent_trim = 0.45
	trimmed_mean = stats.trim_mean(b_total_list, percent_trim)

	plt.plot(b_total_list, color='blue')
	trimmed_mean = stats.trim_mean(b_total_list, .15)
	plt.plot([trimmed_mean]*len(b_total_list), '--', color='red') # print with mean

	## Red line for regions above the cutoff 25%
	great_25 = []
	cutoff_percent = abs(trimmed_mean * .25)
	cutoff = trimmed_mean + cutoff_percent
	plt.plot([cutoff]*len(b_total_list), '--', color='green') # print with mean

	print("trimmed mean = {0}".format(trimmed_mean))
	print("cutoff = {0}".format(cutoff))
	for event in b_total_list:
		if event >= cutoff:
			great_25.append(event)
		else:
			great_25.append(np.nan)
	plt.plot(great_25, color='red')

	## Point for the peak among the red lines for cutoff
	# find the max for each group of values that are above red
	above_cutoff_groupings = [great_25[s] for s in np.ma.clump_unmasked(np.ma.masked_invalid(great_25))]
	import operator
	index_list = []
	max_print_list = []
	for sublist in above_cutoff_groupings:
		index, max_value = max(enumerate(sublist), key=operator.itemgetter(1))
		index_list.append(index)
		max_print_list.append(max_value)
	#print(above_cutoff_groupings)
	#print(index_list)
	#print(max_print_list)
	# find the single max value for cutoff sections
	max_point = []
	for max_pt in great_25:
		if max_pt not in max_print_list:
			max_point.append(np.nan)
		else:
			max_point.append(max_pt)
	#assert no duplicates values in the code (should only be a list of max values), if not, is storing the same value in more than one place
	if np.count_nonzero(~np.isnan(max_point)) != len(max_print_list):
		print("WARNING: duplicates found, {0}!={1}".format(np.count_nonzero(~np.isnan(max_point)), len(max_print_list)))
	plt.scatter(range(0, len(max_point)), max_point, color='red')

	plt.title('Events in IFE Search: {0}'.format(os.path.basename(os.path.splitext(filename)[0])))
	plt.ylabel('|B| [nT]')
	plt.xlabel('Datetime')
	#plt.savefig('output_img/{0}.png'.format(os.path.basename(os.path.splilstext(filename)[0])))
	plt.show()

	return max_point

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
	
	datetime_lst = datetime_convert(csv_data)

	b_total = [float(col[7]) for col in csv_data]
	b_x = [float(col[8]) for col in csv_data]
	b_y = [float(col[9]) for col in csv_data]
	b_z = [float(col[10]) for col in csv_data]

	# store data as grouped namedtuples
	#Person = collections.namedtuple('Person', 'name age gender')
	#bob = Person(name='Bob', age=30, gender='male')

	# store each value in its own list
	#ife_processing = namedtuple('ife_processing', 'datetime btotal bx by bz')
	#for i in range(len(csv_data)):
	#	ife_data = ife_processing(datetime=datetime_lst[i], btotal=b_total[i], bx=b_x[i], by=b_y[i], bz=b_z[i])
	#print(ife_processing)

	peaks_list = magEnhance(datetime_lst, b_total)

	#outputCSV(filename, ife_processing)

