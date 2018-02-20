# IFE parser and csv
import string
import re
import os
import numpy as np
from collections import namedtuple
from datetime import datetime
import matplotlib.pyplot as plt
from operator import itemgetter # find sequences of consecutive values
import itertools

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
		fieldnames = ['year', 'month', 'day', 'hour', 'minute', 'second', 'btotal', 'bx', 'by', 'bz']
		writer = csv.DictWriter(txt_data, fieldnames=fieldnames)
		writer.writeheader() 
		for data in data_list:
			print(data)
			writer.writerow({'year': data[0], 'month': data[1], 'day': data[2], 'hour': data[3], 'minute': data[4], 'second': data[5], 'btotal': data[6], 'bx': data[7], 'by': data[8], 'bz': data[9]})
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
	datetime_convert = [datetime.strptime(dt, '%Y-%m-%d %H:%M:%S.%f') for dt in datetime_lst] # convert datetime to format to use on x-axis
	(fig, ax) = plt.subplots(1, 1)

	import matplotlib.dates as mdates
	xfmt = mdates.DateFormatter('%Y-%m-%d %H:%M:%S.%f')
	ax.xaxis.set_major_formatter(xfmt)
	plt.plot(datetime_convert, b_total_list, color='black')
	plt.scatter(datetime_convert, b_total_list, color='black')

	plt.plot(datetime_convert, [0]*len(b_total_list), ':', color='black') # print at zeroes

	from scipy import stats # trimmed mean to remove percent_trim% of both ends of the mean
	percent_trim = 0.45
	trimmed_mean = stats.trim_mean(b_total_list, percent_trim)
	plt.plot(datetime_convert, [trimmed_mean]*len(b_total_list), '--', color='red') # print with mean

	################## Red line for regions above the cutoff 25%
	great_25 = []
	cutoff_percent = abs(trimmed_mean * .25)
	cutoff = trimmed_mean + cutoff_percent
	plt.plot(datetime_convert, [cutoff]*len(b_total_list), '--', color='green') # print with mean 25% cutoff

	print("trimmed mean = {0}".format(trimmed_mean))
	print("25% cutoff = {0}".format(cutoff))

	for event in b_total_list:
		if event >= cutoff:
			great_25.append(event)
		else:
			great_25.append(np.nan)

	################## Only hold greater than 25% value that last longer than x minutes
	#%Y-%m-%d %H:%M:%S.%f
	time_cutoff_in_minutes = 10
	time_cutoff = time_cutoff_in_minutes * 60
	print("time cutoff = {0} minutes".format(time_cutoff_in_minutes))
	# each row accounts for 1 second
	print("size of datetime: {0} seconds = {1:.2f} minutes".format(len(datetime_convert), float(float(len(datetime_convert))/60)))
	timer_cutoff_lst = list(great_25)
	timer_nan_groups = [timer_cutoff_lst[s] for s in np.ma.clump_unmasked(np.ma.masked_invalid(timer_cutoff_lst))] # groups of non-nan values

	event_totals = 0
	average_event = 0
	group_index = 0
	event_lst = []
	for i in range(len(timer_cutoff_lst)):
		if timer_cutoff_lst[i] is not np.nan:
			if group_index < len(timer_nan_groups):
				if len(timer_nan_groups[group_index]) <= time_cutoff:
					for j in range(i, i+len(timer_nan_groups[group_index])):
						#print(timer_cutoff_lst[j])
						timer_cutoff_lst[j] = np.nan
				else:
					event_totals += 1
					average_event += len(timer_nan_groups[group_index])
					event_lst.append(timer_nan_groups[group_index])
				i += len(timer_nan_groups[group_index]) # iterate down cutoff list to next section
				#print("jump {0} seconds to {1} of total {2}".format(len(timer_nan_groups[group_index]), i, len(timer_cutoff_lst)))
				group_index += 1
	print("total possible events = {0}".format(event_totals))
	if event_totals > 0:
		print("average possible event length {0:.4f} minutes".format((float(average_event) / event_totals)/60))

	plt.scatter(datetime_convert, timer_cutoff_lst, color='blue')
	plt.plot(datetime_convert, timer_cutoff_lst, color='blue') # overlay graph with regions that are above the cutoffs
	
	################## Point for the peak among the red lines for cutoff
	# find the max for each group of values that are above red
	import operator
	index_list = []
	max_print_list = []
	for sublist in event_lst:
		index, max_value = max(enumerate(sublist), key=operator.itemgetter(1))
		index_list.append(index)
		max_print_list.append(max_value)

	################## find the single max value for cutoff sections
	max_point = []
	for max_pt in great_25:
		if max_pt not in max_print_list:
			max_point.append(np.nan)
		else:
			max_point.append(max_pt)
	#assert no duplicates values in the code (should only be a list of max values), if not, is storing the same value in more than one place
	if np.count_nonzero(~np.isnan(max_point)) != len(max_print_list):
		print("WARNING: duplicates found, {0}!={1}".format(np.count_nonzero(~np.isnan(max_point)), len(max_print_list)))
	plt.scatter(datetime_convert, max_point, color='red')
	# Make adjacent lines to peak red
	red_adjacent = []
	red_adjacent = list(max_point)
	for i in range(len(red_adjacent)):
		if not np.isnan(max_point[i]):
			if (i-1) in range(0, len(b_total_list)): # add value if it is within the range of the given list (doesn't go out of index)
				red_adjacent[i-1] = b_total_list[i-1]
			if (i+1) in range(0, len(b_total_list)): # add value if it is within the range of the given list (doesn't go out of index)
				red_adjacent[i+1] = b_total_list[i+1]
	# creates list with max point (peak) and the left/right adjacent values as red
	plt.plot(datetime_convert, red_adjacent, color='red')

	################## Plot axis titles and format font size
	plt.title('Events: {0}'.format(os.path.basename(os.path.splitext(filename)[0])))
	plt.ylabel('|B| [nT]')
	plt.xlabel('Datetime (5 min. intervals)')
	plt.xticks(rotation=90)
	#plt.gcf().autofmt_xdate() # turn x-axis on side for easy of reading
	ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=5))
	ax.tick_params(axis='x', which='major', labelsize=3) # change size of font for x-axis
	plt.tight_layout() # fit x-axis title on bottom

	#plt.savefig('output_img/{0}.png'.format(os.path.basename(os.path.splitext(filename)[0])))
	#plt.show()
	return timer_cutoff_lst

## SECOND CRITERIA: EVENT LASTS LONGER THAN 10 MINUTES (measured over four hour intervals) 
def eventDur(datetime_lst, b_total):
	'''
	an event duration is defined as the time before and after a peak for |B| to return to the ambient (averaged over four hours)
	field magnitude. 
	Returns true if this duration is longer than 10 minutes.
	'''
	pass

## THIRD CRITERIA: CURENT SHEET IS PRESENT NEAR PEAK |B|
def jSheet(datetime_list, events_list, b_val):
	'''
	a current sheet is present for a sharp rotation of at least one of the components. 
	Return true if (i) at least one component of B changes from positive -> negative (or vv) within the duration of the event
	(ii) and the change happens within a minute
	'''
	time_cutoff_in_minutes = 10
	time_cutoff = time_cutoff_in_minutes * 60
	print("jsheet time cutoff = {0} minutes".format(time_cutoff_in_minutes))
	#print(events_list)
	
	group_nonnan_index = [x for x in range(len(events_list)) if events_list[x] is not np.nan]
	#print("\time non nan ={0}".format(group_nonnan_index))

	timestamps_index = [] # list of lists of values in consecutive order: [[1,2,3],[7,8],[11]]
	for k, g in itertools.groupby(enumerate(group_nonnan_index), lambda x: x[1]-x[0]):
		consec_order = list(map(itemgetter(1), g))
		if len(consec_order) <= time_cutoff:
			timestamps_index.append(consec_order)
	#print(timestamps_index)

	#store the events that take place in the time cutofft
	jsheet_timecutoff_events = []
	jsheet_index = []
	for index in timestamps_index:
		timespan_sublist = [b_val[i] for i in index]
		if not all(i >= 0 for i in timespan_sublist) and not all(i <= 0 for i in timespan_sublist):
			jsheet_index.append(index)
			jsheet_timecutoff_events.append(timespan_sublist)

	#print(jsheet_timecutoff_events)
	#print(jsheet_index)
	print("found jsheet events = {0}".format(len(jsheet_timecutoff_events)))
	b_plot_jsheet = [np.nan]*len(datetime_list)

	for (index, value) in zip(jsheet_index, jsheet_timecutoff_events):
		#print(index, value)
		for i in range(len(index)):
			b_plot_jsheet[index[i]] = value[i]
	#print(b_plot_jsheet)
	#return b_plot_jsheet
	return jsheet_index

def multiplePlot(datetime_list, bx, by, bz, btotal, counter):
	# plot all four values if they create an event
	# share the x axis among all four graphs

	# four subplots sharing both x/y axes
	f, (ax1, ax2, ax3, ax4) = plt.subplots(4, sharex=True, sharey=True)
	datetime_convert = [datetime.strptime(dt, '%Y-%m-%d %H:%M:%S.%f') for dt in datetime_list] # convert datetime to format to use on x-axis
	ax1.set_title('Events: {0}-{1}'.format(datetime_convert[0], datetime_convert[len(datetime_convert)-1]))
	import matplotlib.dates as mdates
	xfmt = mdates.DateFormatter('%Y-%m-%d %H:%M:%S.%f')
	ax1.xaxis.set_major_formatter(xfmt)
	ax1.set_title('Bx')
	ax1.plot(datetime_convert, bx, color='red')
	#plt.ylabel("[nT]")
	
	ax2.set_title('By')
	ax2.plot(datetime_convert, by, color='green')
	
	ax3.set_title('Bz')
	ax3.plot(datetime_convert, bz, color='blue')
	
	ax4.set_title('B_total')
	ax4.plot(datetime_convert, btotal, color='black')
	
	#f.subplots_adjust(hspace=0)
	plt.setp([a.get_xticklabels() for a in f.axes[:-1]], visible=False)
	plt.savefig('output_img/{0}_{1}.png'.format(os.path.basename(os.path.splitext(filename)[0]), counter))
	#plt.show()

## FOURTH CRITERIA: AT LEAST ONE MAGNETIC COMPONENT DOES NOT ROTATE DURING THE ENHANCEMENT
def noRot():
	# a rotation of the magnetic field component is defined as when the component changes from positive -> negative (or vv)
	# Returns true if at least one component does not change sign within the event
	pass

if __name__ == '__main__':
	start_time = datetime.now()

	import argparse
	parser = argparse.ArgumentParser(description="flag format given as: -F <filename>")
	parser.add_argument('-F', '-filename', help="filename from data")
	args = parser.parse_args()

	filename = args.F
	if filename is None:
		print("\n\tWARNING: File not given, exiting...\n")
		exit()
		
	# processing for STEREO data
	# TODO: other data lsformats
	graph_data = readFile(filename)
	start_data = 0
	for i in range(len(graph_data)):
		graph_data[i] = re.sub("\s+", ",", graph_data[i].strip()) # replace all whitespace with commas in data
		if graph_data[i] == 'DATA:':
			start_data = i # save the index of the start of the data (typically 102)
	csv_data = graph_data[start_data+1:] # splice all data for just the graphable data (+1 to not include 'DATA:') 
	csv_data = [row.split(',') for row in csv_data]
	#outputCSV(filename, csv_data)
	
	datetime_lst = datetime_convert(csv_data)

	b_x = [float(col[8]) for col in csv_data]
	b_y = [float(col[9]) for col in csv_data]
	b_z = [float(col[10]) for col in csv_data]
	b_total = [float(col[7]) for col in csv_data]
	#multiplePlot(datetime_lst, b_x, b_y, b_z, b_total)

	possible_events = magEnhance(datetime_lst, b_total) # finds possible events for a given time frame
	
	print("\nbx")
	bx_jsheet_events = jSheet(datetime_lst, possible_events, b_x) # filter possible events for neg/pos change
	bx_jsheet_events = [item for sublist in bx_jsheet_events for item in sublist] # flatten
	#print(bx_jsheet_events)
	
	print("\nby")
	by_jsheet_events = jSheet(datetime_lst, possible_events, b_y) # filter possible events for neg/pos change
	by_jsheet_events = [item for sublist in by_jsheet_events for item in sublist] # flatten
	#print(by_jsheet_events)

	print("\nbz")
	bz_jsheet_events = jSheet(datetime_lst, possible_events, b_z) # filter possible events for neg/pos change
	bz_jsheet_events = [item for sublist in bz_jsheet_events for item in sublist] # flatten
	#print(bz_jsheet_events)

	print("\n")

	# Determine where the x, y, z share timestamps during the events
	bxy_shared = []
	for x in bx_jsheet_events:
		if x in by_jsheet_events:
			bxy_shared.append(x)

	byz_shared = []
	for y in by_jsheet_events:
		if y in bz_jsheet_events:
			byz_shared.append(y)

	bzx_shared = []
	for z in bz_jsheet_events:
		if z in bx_jsheet_events:
			bzx_shared.append(z)
	
	timestamps_index = [] # list of lists of values in consecutive order: [[1,2,3],[7,8],[11]]
	if bxy_shared and not byz_shared and not bzx_shared:
		for k, g in itertools.groupby(enumerate(bxy_shared), lambda x: x[1]-x[0]):
			consec_order = list(map(itemgetter(1), g))
			timestamps_index.append(consec_order)
	if byz_shared and not bzx_shared and not bxy_shared:
		for k, g in itertools.groupby(enumerate(byz_shared), lambda x: x[1]-x[0]):
			consec_order = list(map(itemgetter(1), g))
			timestamps_index.append(consec_order)
	if bzx_shared and not bxy_shared and not byz_shared:
		for k, g in itertools.groupby(enumerate(bzx_shared), lambda x: x[1]-x[0]):
			consec_order = list(map(itemgetter(1), g))
			timestamps_index.append(consec_order)
	
	# check that bx and by are changing signs
	# update timestamp index
	remove_elements = [] # elements where the averages is not opposite, to be removed
	for updated_time in timestamps_index:
		# see if a list of value is increasing or decreasing
		x_average = sum(list(itemgetter(*updated_time)(b_x))) / len(updated_time)
		y_average = sum(list(itemgetter(*updated_time)(b_y))) / len(updated_time)
		if (x_average > 0) and (y_average > 0): # if x is pos and y is pos (remove)
			remove_elements.append(updated_time)
		if (x_average < 0) and (y_average < 0): # if x is neg and y is neg (remove)
			remove_elements.append(updated_time)

	#print(remove_elements)
	#print(len(timestamps_index))
	timestamps_index = [x for x in timestamps_index if x not in remove_elements]
	#print(len(timestamps_index))
	counter = 0
	for sub_graph in timestamps_index:
		counter += 1 # increment data figure counter
		multiplePlot(list(itemgetter(*sub_graph)(datetime_lst)),
					list(itemgetter(*sub_graph)(b_x)),
					list(itemgetter(*sub_graph)(b_y)),
					list(itemgetter(*sub_graph)(b_z)),
					list(itemgetter(*sub_graph)(b_total)),
					counter)
	print("graphing {0} sub graphs for each interval".format(counter))

	print("\nGraphing ran for {0}".format(datetime.now() - start_time))

