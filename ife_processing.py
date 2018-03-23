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
import csv

# FORMAT FOR USE: python ife_tmp.py -F <FILENAME.TXT>
## FIRST CRITERIA: MAGNETIC FIELD ENHANCEMENT IS LARGER THAN 25% OF AMBIENT
## SECOND CRITERIA: EVENT LASTS LONGER THAN 10 MINUTES (measured over four hour intervals) 
## THIRD CRITERIA: CURENT SHEET IS PRESENT NEAR PEAK |B|

########### Pre-Processing File
def detectFileType(filename):
	# detect file type for pre-processing: ACE, STEREO, etc..
	pass

def readFile(filename):
	# read in file
	with open(filename, "r") as given_file:
		file_data = given_file.readlines()
		file_data = [row.replace("\r" , "") for row in file_data] # replace newline character with empty space
		file_data = [row.replace("\n" , "") for row in file_data]
	return file_data #returns file without newline characters

def breakIntoSubFiles(filename):
	sub_files = []
	sub_files.append(filename)
	return sub_files
	'''
	from subprocess import Popen, PIPE, call
	p1 = Popen(["cat", "{0}".format(filename)], stdout=PIPE)
	p2 = Popen(["wc", "-l"], stdin=p1.stdout, stdout=PIPE)
	p1.stdout.close()  # Allow p1 to receive a SIGPIPE if p2 exits.
	line_count = int(p2.communicate()[0])
	#print("line count = {0}\n".format(line_count))
	#determine_plot_interval1(line_count)
	max_line_count_before_killed = 999999
	time_per_x_plus_hour = 26316000000 # for overlap
	call(["sed", "-n", "-e", "{0},{1}p".format(1, time_per_x_plus_hour), filename], stdout=new_sub_file)
	counter = 1
	if line_count > max_line_count_before_killed:
		total_count = line_count
		start_index = 1
		end_index = time_per_x_plus_hour
		base_filename = "{0}_month".format(os.path.basename(os.path.splitext(filename)[0]))
		while(total_count > 0):
			weekly_filename = "{0}_{1}.txt".format(base_filename, counter)
			sub_files.append(weekly_filename)
			#print("greater than killed, split")
			#print("\nsed from {0} to {1}".format(start_index, end_index))
			# create file from start/end
			with open(weekly_filename, "w") as new_sub_file:
				#sed -n -e '1,999999p' AC_H3_MFI_23818.txt > ace_test_long.txt
				call(["sed", "-n", "-e", "{0},{1}p".format(start_index, end_index), filename], stdout=new_sub_file)
				#print("New file: {0}".format(weekly_filename))
			start_index += time_per_x_plus_hour
			end_index += time_per_x_plus_hour + 1 # some overlap in index
			if end_index > line_count:
				end_index = line_count
			total_count -= time_per_x_plus_hour
			counter += 1
	else:
		sub_files.append(filename)
	return sub_files # return the total number of files
	'''

def processCSVACEdata(graph_data):
	# store ACE data in list of list (all formats saved this way)
	'''
	start format: 03-04-2007 00:00:00.890  4.18300  3.18400  -2.33400  1.38100
	result stored as:
	['2009', '006', '08', '23', '59', '29', '000', '2.1987', '4.2269', '-1.0491', '4.8787'], 
	['2009', '006', '08', '23', '59', '30', '000', '2.1729', '4.1750', '-1.0475', '4.8217']]
	'''
	start_data = 0 # line the data starts on
	for i in range(len(graph_data)):
		graph_data[i] = re.sub("\s+", ",", graph_data[i].strip())
		if graph_data[i][0] != "#": # find where the commented out region ends (around 58)
			start_data = i
			break
	updated_graph_data = graph_data[start_data+3:] # start data when section isn't a comment (only data)
	
	ace_csv_data = [] # store each row as a list of list
	invalid_data_found = False

	for row in updated_graph_data: # format how the data is currently stored
		if row[0] != '#':
			#print(row)
			year = row[6:10]
			month = row[3:5]
			day = row[:2]
			hour = row[11:13]
			minute = row[14:16]
			second = row[17:19]
			millisecond = row[20:23]
			
			b_data = row[24:].split()  # magnetic field data
			#print(b_data)
			if b_data:
				if '-1.00000E+31' == b_data[0]:
					invalid_data_found = True
					btotal = np.nan 
					bx = np.nan 
					by = np.nan
					bz = np.nan
				else:
					btotal = b_data[0]
					bx = b_data[1] 
					by = b_data[2]
					bz = b_data[3]
				ace_csv_data.append([year, month, day, hour, minute, second, millisecond, btotal, bx, by, bz])
		
	if invalid_data_found: 
		print("LOG WARNING: Invalid data -1.00000E+31 found, converted to nan")
	return ace_csv_data # returns list of list of data

def retrieveFromExistingCSV(existing_csv):
	csv_data = [] # store each row as a list of list
	# match format: ['2006', '04', '14', '17', '09', '01', '121', '10.2030', '1.90300', '-9.81400', '-2.04100']
	# ([year, month, day, hour, minute, second, millisecond, btotal, bx, by, bz])
	with open(existing_csv, 'r') as csv_file:
		reader = csv.reader(csv_file, delimiter=',')
		next(reader, None) # skip headers
		csv_data = [row for row in reader]
	return csv_data

########### Save Data as CSV
def outputCSV(filename, data_list):
	# save data from text as a csv 
	given_file = os.path.basename(os.path.splitext(filename)[0]) # return only the filename and not the extension
	output_filename = "{0}_data.csv".format(given_file.upper())
	with open(output_filename, 'w+') as txt_data:
		fieldnames = ['year', 'month', 'day', 'hour', 'minute', 'second', 'millisecond', 'btotal', 'bx', 'by', 'bz']
		writer = csv.DictWriter(txt_data, fieldnames=fieldnames)
		writer.writeheader() 
		for data in data_list:
			if '+31' not in data:
				writer.writerow({'year': data[0],
								 'month': data[1], 
								 'day': data[2], 
								 'hour': data[3], 
								 'minute': data[4], 
								 'second': data[5], 
								 'millisecond': data[6], 
								 'btotal': data[7], 
								 'bx': data[8], 
								 'by': data[9], 
								 'bz': data[10]})
	print("DATA SAVED AS '{0}'".format(output_filename))

########### Convert string to datetime
def datetime_convert(csv_data):
	# covert to datetime format
	#for col in csv_data:
	#	print(col[6])
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
	print("Date range of data: '{0}' to '{1}'\n".format(dt[0], dt[len(dt)-1]))
	return dt#[datetime.strptime(t, '%Y-%m-%d %H:%M:%S.%f') for t in dt] # convert to datetime

########### IFE IDENTIFICATION CRITERIA
def multiplePlot(buffer_size, datetime_list, bx, by, bz, btotal, sub_title, buffer_b):
	# plot all four values if they create an event
	# share the x axis among all four graphs
	# four subplots sharing both x/y axes
	print("\nSub-graphs for bx, by, bz, btotal graph saved {0}_event{1}.png, saved to output_img".format(os.path.basename(os.path.splitext(filename)[0]), sub_title))
	fig = plt.figure()
	fig.set_figheight(18)
	fig.set_figwidth(16)
	datetime_convert = [datetime.strptime(dt, '%Y-%m-%d %H:%M:%S.%f') for dt in datetime_list] # convert datetime to format to use on x-axis
	pre_buffer_datetime = datetime_convert # save a local copy, to use a the title (even after updated with the buffer)
	
	if buffer_b: # is not None (None when graphing 'overall')
		# buffer_b is a tuple: (bx_groups, by_groups, bz_groups, bt_groups, total_datetime)
		full_bx = buffer_b[0]
		full_by = buffer_b[1]
		full_bz = buffer_b[2]
		full_bt =  buffer_b[3]
		total_time =  buffer_b[4]
		add_buffer_to_both_sides = int(len(bx)*buffer_size)
		print("added {0} minutes buffer to either side of the found event".format(float(add_buffer_to_both_sides)/60))
		new_start_with_buffer = total_time.index(datetime_convert[0]) - add_buffer_to_both_sides
		if new_start_with_buffer < 0: # either move back x or start at the beginning
			new_start_with_buffer = 0
		new_end_with_buffer = total_time.index(datetime_convert[len(datetime_convert)-1]) + add_buffer_to_both_sides
		if new_end_with_buffer > len(total_time):
			new_end_with_buffer = len(total_time)
		#print("index: without buffer = ({0}, {1}), with buffer = ({2}, {3})".format(total_time.index(datetime_convert[0]), total_time.index(datetime_convert[len(datetime_convert)-1]), new_start_with_buffer, new_end_with_buffer))
		
		# NEW B VALUES WITH THE ADDED BUFFER
		datetime_convert = total_time[new_start_with_buffer:new_end_with_buffer]
		bx = full_bx[new_start_with_buffer:new_end_with_buffer]
		by = full_by[new_start_with_buffer:new_end_with_buffer]
		bz = full_bz[new_start_with_buffer:new_end_with_buffer]
		btotal = full_bt[new_start_with_buffer:new_end_with_buffer]
	
	import matplotlib.dates as mdates
	xfmt = mdates.DateFormatter('%Y-%m-%d %H:%M:%S.%f')
	ax1 = plt.subplot(411)
	ax1.xaxis.set_major_formatter(xfmt)
	plt.setp(ax1.get_xticklabels(), fontsize=6)
	plt.plot(datetime_convert, bx, color='red')
	ax1.set_title('Bx')
	plt.ylabel("[nT]")
	plt.setp(ax1.get_xticklabels(), visible=False)

	ax2 = plt.subplot(412, sharex=ax1, sharey=ax1)
	ax2.set_title('By')
	ax2.plot(datetime_convert, by, color='green')
	plt.ylabel("[nT]")
	plt.setp(ax2.get_xticklabels(), visible=False)

	ax3 = plt.subplot(413, sharex=ax1, sharey=ax1)
	ax3.set_title('Bz')
	ax3.plot(datetime_convert, bz, color='blue')
	plt.ylabel("[nT]")
	plt.setp(ax3.get_xticklabels(), visible=False)

	# b_total does not share the same y axis as the others
	ax4 = plt.subplot(414, sharex=ax1)
	ax4.set_title('B_total')
	ax4.plot(datetime_convert, btotal, color='black')
	y_max = np.nanmax(np.asarray(btotal)[np.asarray(btotal) != -np.nan]) + 1 # ignore nan when finding min/max
	y_min = np.nanmin(np.asarray(btotal)[np.asarray(btotal) != -np.nan]) - 1 # ignore nan when finding min/max
	ax4.set_ylim([y_min, y_max])
	plt.ylabel("[nT]")
	
	#f.subplots_adjust(hspace=0)
	plt.setp([a.get_xticklabels() for a in fig.axes[:-1]], visible=False)
	plt.xticks(rotation=90)
	#plt.gcf().autofmt_xdate() # turn x-axis on side for easy of reading
	if sub_title is 'overall':
		time_interval = len(datetime_convert) / 3600 # hour
		time_print = "Hourly"
		ax1.xaxis.set_major_locator(mdates.MinuteLocator(interval=time_interval))
		if time_interval == 0: # is less than an hour long
			time_interval = len(datetime_convert) / 60
			ax1.xaxis.set_major_locator(mdates.MinuteLocator(interval=1))
			time_print = "Minute"
		print("(x-axis) multi HOUR time interval = {0}".format(time_interval))
		plt.xlabel('Datetime: {0} ({1} intervals)'.format(time_print, time_interval))
	else:
		time_interval = len(datetime_convert) / 60 # 1 minute
		print("(x-axis) multi MINUTE time interval = {0}".format(time_interval))
		plt.xlabel('Datetime: Mintues ({0} intervals)'.format(time_interval))
		ax1.xaxis.set_major_locator(mdates.MinuteLocator(interval=1))

	ax1.tick_params(axis='x', which='major', labelsize=7) # change size of font for x-axis
	plt.tight_layout(rect=[0, 0, 1, 0.97]) # fit x-axis/y-axi/title around the graph (left, bottom, right, top)
	plt.suptitle('Event {0}: {1} to {2}'.format(sub_title, pre_buffer_datetime[0], pre_buffer_datetime[len(pre_buffer_datetime)-1]))
	plt.savefig('output_img/{0}/{1}_event{2}.png'.format(os.path.basename(os.path.splitext(filename)[0]), os.path.basename(os.path.splitext(filename)[0]), sub_title))
	#plt.show()

def magEnhance(datetime_list, b_total_list, bx, by, bz, percent_cutoff, percent_mean_trimmed, time_cutoff_in_minutes, change_mean_every_x_hours, buffer_size):
	'''
	define an ambient magnetic field magnitude over a four hour interval and compare the peak of |B| (where the Maxative is zero)
	to the ambient. 
	Returns true if peak value is larger than (0.25)*(|B|avg)
	'''
	datetime_convert = [datetime.strptime(dt, '%Y-%m-%d %H:%M:%S.%f') for dt in datetime_lst] # convert datetime to format to use on x-axis
	print("size of datetime: {0} seconds = {1:.2f} minutes = {2:.3f} hours \n".format(len(datetime_convert), float(float(len(datetime_convert))/60), float(float(len(datetime_convert))/3600)))
	# original values: (bx_groups, by_groups, bz_groups, bt_groups, total_datetime) -> for plotting sub events (buffer)
	original_values = (list(bx), list(by), list(bz), list(b_total_list), list(datetime_convert)) # create a static version of the original values
	(fig, ax) = plt.subplots(1, 1, figsize=(25, 16))

	import matplotlib.dates as mdates
	xfmt = mdates.DateFormatter('%Y-%m-%d %H:%M:%S.%f')
	ax.xaxis.set_major_formatter(xfmt) # feed in datetimes to x axis
	plt.plot(datetime_convert, b_total_list, color='black')
	#plt.scatter(datetime_convert, b_total_list, color='black')

	plt.plot(datetime_convert, [0]*len(b_total_list), ':', color='black') # print at zeroes

	from scipy import stats # trimmed mean to remove percent_trim% of both ends of the mean
	b_total_x_hours = np.asarray(b_total_list) # for finding the ambient magnetic field
	# 1 row is 1 second, 1 hour = 3600 rows
	b_total_x_hours = np.asarray(b_total_list) # convert to np for split
	split_time = change_mean_every_x_hours*60*60 # in seconds
	print("from {1} hours in split into the total {0} hours".format(float(float(len(datetime_convert))/3600), change_mean_every_x_hours))
	b_total_x_means = np.array_split(b_total, float(len(b_total))/float(split_time))
	b_total_x_means = [list(x) for x in b_total_x_means]
	print("split_time {0}, out of {1} = {2} different means (rounded to {3})".format(split_time, len(b_total), float(len(b_total))/float(split_time), len(b_total_x_means)))

	trimed_mean_lst = [] # stores the mean and the time it stays that length
	mean_to_print = []
	for subtime in b_total_x_means:
		mean_found = stats.trim_mean(subtime, percent_mean_trimmed)
		mean_to_print.append(mean_found)
		trimed_mean_lst.append([mean_found]*len(subtime))
	print("trimmed mean: \n{0}".format(mean_to_print))
	graph_trimmed_mean = [j for i in trimed_mean_lst for j in i] # compress parts into a single list to graph
	#trimmed_mean = stats.trim_mean(b_total_list, percent_mean_trimmed)
	#print("{0} == {1}".format(len(trimed_mean_lst), len([trimmed_mean]*len(b_total_list))))
	plt.plot(datetime_convert, graph_trimmed_mean, '--', color='red') # print with mean trimmed x percent from either side
	
	################## Red line for regions above the cutoff 25%
	greater_percent_cutoff = [] # will be a x mean values of time/change_mean_every_x_hours
	cutoff_percent_list = []
	cuttoff_to_print = []
	for submean in trimed_mean_lst:
		cutoff_found_per_mean = abs(submean[0] * percent_cutoff) #25% (can be reverted back)
		cuttoff_to_print.append(submean[0] + cutoff_found_per_mean)
		cutoff_percent_list.append([submean[0] + cutoff_found_per_mean]*len(submean))
	cutoff_percent_list = [j for i in cutoff_percent_list for j in i] # compress parts into a single list to graph
	print("{0}% cutoff: \n{1}".format(percent_cutoff*100, cuttoff_to_print))
	plt.plot(datetime_convert, cutoff_percent_list, '--', color='green') # print with mean 25% cutoff
	
	for event_index in range(len(b_total_list)):
		if b_total_list[event_index] >= cutoff_percent_list[event_index]:
			greater_percent_cutoff.append(b_total_list[event_index])
		else:
			greater_percent_cutoff.append(np.nan)

	################## Only hold greater than 25% value that last longer than x minutes
	#%Y-%m-%d %H:%M:%S.%f
	time_cutoff = time_cutoff_in_minutes * 60
	print("time cutoff = {0} minutes".format(time_cutoff_in_minutes))
	# each row accounts for 1 second
	timer_cutoff_lst = list(greater_percent_cutoff)
	timer_nan_groups = [timer_cutoff_lst[s] for s in np.ma.clump_unmasked(np.ma.masked_invalid(timer_cutoff_lst)) if len(timer_cutoff_lst[s]) > time_cutoff]
	# groups of non-nan values (groups any value above the cutoff that lasts longer than the cutoff)

	average_event = 0
	group_index = 0
	date_index = [] # stores the range of index values where the cuttoff is satisfed, used for printing date range
	
	print_date_values = []
	bx_print = []
	by_print = []
	bz_print = []
	btotal_print = []
	for date_index, timer_index, x, y, z, t in zip(datetime_lst, timer_cutoff_lst, bx, by, bz, b_total):
		if timer_index is np.nan:
			print_date_values.append(np.nan)
			bx_print.append(np.nan)
			by_print.append(np.nan)
			bz_print.append(np.nan)
			btotal_print.append(np.nan)
		else:
			print_date_values.append(date_index)
			bx_print.append(x)
			by_print.append(y)
			bz_print.append(z)
			btotal_print.append(t)

	# to print for each sub-graph
	bx_groups = [bx_print[s] for s in np.ma.clump_unmasked(np.ma.masked_invalid(bx_print)) if len(bx_print[s]) > time_cutoff]
	by_groups = [by_print[s] for s in np.ma.clump_unmasked(np.ma.masked_invalid(by_print)) if len(by_print[s]) > time_cutoff]
	bz_groups = [bz_print[s] for s in np.ma.clump_unmasked(np.ma.masked_invalid(bz_print)) if len(bz_print[s]) > time_cutoff]
	bt_groups = [btotal_print[s] for s in np.ma.clump_unmasked(np.ma.masked_invalid(btotal_print)) if len(btotal_print[s]) > time_cutoff]

	#plot_sub_plots at the end

	plt.plot(datetime_convert, timer_cutoff_lst, color='blue') # overlay graph with regions that are above the cutoffs
	#plt.scatter(datetime_convert, timer_cutoff_lst, color='blue')
	
	################## Point for the peak among the red lines for cutoff
	# find the max for each group of values that are above red
	import operator
	index_list = []
	max_print_list = []
	for sublist in bt_groups:
		index, max_value = max(enumerate(sublist), key=operator.itemgetter(1))
		index_list.append(index)
		max_print_list.append(max_value)

	################## find the single max value for cutoff sections
	max_point = []
	for max_pt in greater_percent_cutoff:
		if max_pt not in max_print_list:
			max_point.append(np.nan)
		else:
			max_point.append(max_pt)
	#assert no duplicates values in the code (should only be a list of max values), if not, is storing the same value in more than one place
	if np.count_nonzero(~np.isnan(max_point)) != len(max_print_list):
		print("\nLOG WARNING: duplicates max peaks found, {0}!={1}".format(np.count_nonzero(~np.isnan(max_point)), len(max_print_list)))
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
	plt.xticks(rotation=90)
	#plt.gcf().autofmt_xdate() # turn x-axis on side for easy of reading
	time_interval = len(datetime_convert) / 3600 # hour
	time_print = "Hourly"
	ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=time_interval))
	if time_interval == 0: # is less than an hour long
		time_interval = len(datetime_convert) / 60
		ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=1))
		time_print = "Minute"
	plt.xlabel('Datetime: {0} ({1} intervals)'.format(time_print, time_interval))
	print("mag time interval = {0}".format(time_interval))
	#plt.xlabel('Datetime: {0} ({1} intervals)'.format(time_print, time_interval))
	ax.tick_params(axis='x', which='major', labelsize=7) # change size of font for x-axis
	plt.tight_layout(rect=[0, 0, 1, 0.97]) # fit x-axis/y-axi/title around the graph (left, bottom, right, top)

	print("\nEvents graph saved {0}.png, saved to output_img".format(os.path.basename(os.path.splitext(filename)[0])))
	plt.savefig('output_img/{0}/{1}.png'.format(os.path.basename(os.path.splitext(filename)[0]),os.path.basename(os.path.splitext(filename)[0]), os.path.splitext(filename)[0]))

	#plt.show()
	# original values: (bx_groups, by_groups, bz_groups, bt_groups, total_datetime)
	plot_sub_events(print_date_values, time_cutoff, timer_nan_groups, bx_groups, by_groups, bz_groups, bt_groups, original_values, buffer_size)
	return timer_cutoff_lst

def plot_sub_events(print_date_values, time_cutoff, timer_nan_groups,  bx_groups, by_groups, bz_groups, bt_groups, orignal_total_values, buffer_size):
	print_dates = []
	append_date = []
	for i in print_date_values:
		if i is not np.nan:
			append_date.append(i)
		else:
			if append_date != []:
				print_dates.append(append_date)
				append_date = []
	average_event = 0
	event_counter = 0
	sub_plot_times = []
	for print_dates_all_ranges in print_dates:
		if len(print_dates_all_ranges) > time_cutoff: # one minute
			event_counter += 1
			average_event += len(print_dates_all_ranges)
			sub_plot_times.append(print_dates_all_ranges)
			print("Possible event from '{0}' to '{1}', for {2} seconds or {3:.4f} minutes".format(print_dates_all_ranges[0], print_dates_all_ranges[-1], len(print_dates_all_ranges), float(len(print_dates_all_ranges))/60.0))

	if event_counter > 0:
		print("\nFound {0} events with a {1} minutes cutoff".format(event_counter, time_cutoff/60))
		print("average possible event length {0:.4f} minutes\n".format((float(average_event) / event_counter/60)))
		## if event found, print log data for time span
		if len(timer_nan_groups) != event_counter:
			print("ERROR: {0} != {1}, TOTAL EVENTS PRINTED DO NOT MATCH THE GROUPS ABOVE THE CUTOFF".format(event_counter, len(timer_nan_groups)))
		for i in range(len(sub_plot_times)):
			multiplePlot(buffer_size, sub_plot_times[i], bx_groups[i], by_groups[i], bz_groups[i], bt_groups[i], i+1, orignal_total_values)
			find_jsheet_derivatives(buffer_size, sub_plot_times[i], bx_groups[i], by_groups[i], bz_groups[i], bt_groups[i], i+1, orignal_total_values)

def derivative_pair(y_pair):
	#print("Y: {0}".format(y_pair))
	slope = y_pair[1]-y_pair[0]#/1 # x2-x1 always 1 (1 second between pairs)
	return slope

def find_jsheet_derivatives(buffer_size, datetime_list, bx, by, bz, btotal, sub_title, buffer_b):
	# produce a list of derivative for the range of points found in the event identified
	der_bx = []
	der_by = []
	der_bz = []
	datetime_pair = []
	datetime_convert = [datetime.strptime(dt, '%Y-%m-%d %H:%M:%S.%f') for dt in datetime_list] # convert datetime to format to use on x-axis

	if buffer_b: # is not None (None when graphing 'overall')
		# buffer_b is a tuple: (bx_groups, by_groups, bz_groups, bt_groups, total_datetime)
		full_bx = buffer_b[0]
		full_by = buffer_b[1]
		full_bz = buffer_b[2]
		full_bt =  buffer_b[3]
		total_time =  buffer_b[4]
		add_buffer_to_both_sides = int(len(bx)*buffer_size)
		print("added {0} minutes buffer to either side of the found event".format(float(add_buffer_to_both_sides)/60))
		new_start_with_buffer = total_time.index(datetime_convert[0]) - add_buffer_to_both_sides
		if new_start_with_buffer < 0: # either move back x or start at the beginning
			new_start_with_buffer = 0
		new_end_with_buffer = total_time.index(datetime_convert[len(datetime_convert)-1]) + add_buffer_to_both_sides
		if new_end_with_buffer > len(total_time):
			new_end_with_buffer = len(total_time)
		#print("index: without buffer = ({0}, {1}), with buffer = ({2}, {3})".format(total_time.index(datetime_convert[0]), total_time.index(datetime_convert[len(datetime_convert)-1]), new_start_with_buffer, new_end_with_buffer))
		
		# NEW B VALUES WITH THE ADDED BUFFER
		datetime_convert = total_time[new_start_with_buffer:new_end_with_buffer]
		bx = full_bx[new_start_with_buffer:new_end_with_buffer]
		by = full_by[new_start_with_buffer:new_end_with_buffer]
		bz = full_bz[new_start_with_buffer:new_end_with_buffer]
		#btotal = full_bt[new_start_with_buffer:new_end_with_buffer]


	for i in xrange(0, len(by), 2): # create pairs from each list
		pair = bx[i:i+2]
		if len(pair) > 1: # do not find the derivative of a single trailing point
			der_bx.append(derivative_pair(pair))
			datetime_pair.append(datetime_convert[i])

	for i in xrange(0, len(bx), 2): # create pairs from each list
		pair = by[i:i+2]
		if len(pair) > 1: # do not find the derivative of a single trailing point
			der_by.append(derivative_pair(pair))

	for i in xrange(0, len(bz), 2): # create pairs from each list
		pair = bz[i:i+2]
		if len(pair) > 1: # do not find the derivative of a single trailing point
			der_bz.append(derivative_pair(pair))

	#print("Bx:\n{0}".format(der_bx))
	#print("By:\n{0}".format(der_by))
	#print("Bz:\n{0}".format(der_bz))

	# plot b values if they create an event
	# share the x axis among all four graphs

	print("bx {0}, by {1}, bz {2}, date {3}\n".format(len(der_bx), len(der_by), len(der_bz), len(datetime_pair)))
	fig, (ax1, ax2, ax3) = plt.subplots(3, sharex=True, sharey=True, figsize=(16, 16))
	
	import matplotlib.dates as mdates
	xfmt = mdates.DateFormatter('%Y-%m-%d %H:%M:%S.%f')
	ax1.xaxis.set_major_formatter(xfmt)
	ax1.set_title('Bx')
	ax1.set_ylabel("[nT]")
	ax1.plot(datetime_pair, der_bx, color='red')
	
	ax2.set_title('By')
	ax2.set_ylabel("[nT]")
	ax2.plot(datetime_pair, der_by, color='green')
	
	ax3.set_title('Bz')
	ax3.set_ylabel("[nT]")
	ax3.plot(datetime_pair, der_bz, color='blue')
	

	plt.setp([a.get_xticklabels() for a in fig.axes[:-1]], visible=False)
	plt.suptitle('Derivatives of Event {0}: {1} to {2}'.format(sub_title, datetime_convert[0], datetime_convert[len(datetime_convert)-1]))
	plt.xticks(rotation=90)
	time_interval = len(datetime_convert) / 60 # 1 minute
	print("dev time interval = {0}".format(time_interval))
	plt.xlabel('Datetime: Every 2 Mintues ({0} intervals)'.format(time_interval))
	ax1.xaxis.set_major_locator(mdates.MinuteLocator(interval=1))
	print("time interval = {0}".format(time_interval))
	ax1.tick_params(axis='x', which='major', labelsize=7) # change size of font for x-axis
	plt.tight_layout(rect=[0, 0, 1, 0.97]) # fit x-axis/y-axi/title around the graph (left, bottom, right, top)
	print("Derivatives for the event for bx, by, and bz graph saved {0}_event{1}_DER.png, saved to output_img".format(os.path.basename(os.path.splitext(filename)[0]), sub_title))
	plt.savefig('output_img/{0}/{1}_event{2}_DERIVATIVE.png'.format(os.path.basename(os.path.splitext(filename)[0]), os.path.basename(os.path.splitext(filename)[0]), sub_title))
	
	#plt.show()

	# find min/max and ignore nan values
	#np.nanmax(np.asarray(btotal)[np.asarray(btotal) != -np.nan]) 
	der_bx_max = np.nanmax(np.asarray(der_bx)[np.asarray(der_bx) != -np.nan]) 
	der_by_max = np.nanmax(np.asarray(der_by)[np.asarray(der_by) != -np.nan]) 
	der_bz_max = np.nanmax(np.asarray(der_bz)[np.asarray(der_bz) != -np.nan]) 

	der_bx_min = np.nanmin(np.asarray(der_bx)[np.asarray(der_bx) != -np.nan]) 
	der_by_min = np.nanmin(np.asarray(der_by)[np.asarray(der_by) != -np.nan]) 
	der_bz_min = np.nanmin(np.asarray(der_bz)[np.asarray(der_bz) != -np.nan]) 

	print("BX: \nMax: {0} at {1}\nMin: {2} at {3}".format(der_bx[der_bx.index(der_bx_max)], datetime_convert[der_bx.index(der_bx_max)],
														  der_bx[der_bx.index(der_bx_min)], datetime_convert[der_bx.index(der_bx_min)]))
	print("BY: \nMax: {0} at {1}\nMin: {2} at {3}".format(der_by[der_by.index(der_by_max)], datetime_list[der_by.index(der_by_max)],
														  der_by[der_by.index(der_by_min)], datetime_convert[der_by.index(der_by_min)]))
	print("BZ: \nMax: {0} at {1}\nMin: {2} at {3}".format(der_bz[der_bz.index(der_bz_max)], datetime_convert[der_bz.index(der_bz_max)],
														  der_bz[der_bz.index(der_bz_min)], datetime_convert[der_bz.index(der_bz_min)]))

def determine_plot_interval(datetime_convert):
	# determine the interval for the graph to plot
	time_print = 'Minute'
	time_interval = 1
	print("datetime = {0}".format(len(datetime_convert)))
	level_of_crowdness = 20 # per interval
	# total seconds / seconds in x
	total_minutes = len(datetime_convert) / 60
	print("total_minutes = {0}".format(total_minutes))
	
	if total_minutes > level_of_crowdness:
		total_hours = len(datetime_convert) / 3600
		print("total_hours =   {0}".format(total_hours))
		if total_hours > level_of_crowdness:
			total_days = len(datetime_convert) / 86400
			print("total_days =    {0}".format(total_days))
			if total_days > level_of_crowdness:
				total_weeks = len(datetime_convert) / 604800
				print("total_weeks =   {0}".format(total_weeks))
				if total_weeks > level_of_crowdness:
					total_months = len(datetime_convert) / 2.628e+6
					print("total_months =  {0}".format(total_months))
					if total_months > level_of_crowdness:
						total_years = len(datetime_convert) / 3.154e+7
						print("total_years =   {0}".format(total_years))


	'''
	time_interval = len(datetime_convert) / 3600 # hour
	time_print = "Hourly"
	ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=time_interval))
	if time_interval == 0: # is less than an hour long
		time_interval = len(datetime_convert) / 60
		ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=1))
		time_print = "Minute"
	plt.xlabel('Datetime: {0} ({1} intervals)'.format(time_print, time_interval))
	print("mag time interval = {0}".format(time_interval))
	plt.xlabel('Datetime: {0} ({1} intervals)'.format(time_print, time_interval))
	'''

	#print("\ntime_print = {0}".format(time_print))
	#print("time_interval = {0}".format(time_interval))
	return (time_print, time_interval)

if __name__ == '__main__':
	start_time = datetime.now() #starts a timer for run (~3-5 minutes per month)

	import argparse
	parser = argparse.ArgumentParser(description="flag format given as: -F <filename>") # ex. python ife_processing.py -F ACE_WITH_AN_EVENT.txt
	parser.add_argument('-F', '-filename', help="filename from data")
	args = parser.parse_args()

	filename = args.F #stores argument as filename
	if filename is None: # if you run script without a file, will give you a warning and not run
		print("\n\tWARNING: File not given, exiting...\n")
		exit()

	# if the file is longer than a week, it will be broken apart into sub_files
	# break into subfiles
	total_files_to_run = breakIntoSubFiles(filename)
	# if not broken down, this variables = 0
	#print("Total time to run = {0}".format(total_files_to_run))
	if len(total_files_to_run) > 1:
		print("Total weeks worth of time to run = {0}".format(len(total_files_to_run)))
	
	if len(total_files_to_run) > 1:
		# run each sub file indivudally 
		for file_sub in total_files_to_run:
			os.system('./run_each_sub_data.sh {0}'.format(file_sub)) #runs sub-files recursively
	else:
		print("\nProcessing: {0}".format(filename)) 
		graph_data = readFile(filename) 
		# processing for ACE data
		# make new directory
		if not os.path.exists('output_img/{0}'.format(os.path.basename(os.path.basename(os.path.splitext(filename)[0])))):
			os.makedirs('output_img/{0}'.format(os.path.basename(os.path.basename(os.path.splitext(filename)[0]))))
		
		output_filename = "{0}_data.csv".format(os.path.basename(os.path.splitext(filename)[0]).upper()) # stores data
		#print("{0} exists {1}".format(output_filename, os.path.isfile(output_filename)))
		if not os.path.isfile(output_filename): # if csv doesn't already exist, generate it
			#print("does not exist, generate")
			csv_data = processCSVACEdata(graph_data)
			outputCSV(filename, csv_data)
		else: # use exising csv to generate graph
			#print("does exist, retrieve existing")
			csv_data = retrieveFromExistingCSV(output_filename)

		'''STEREO DATA
		for i in range(len(graph_data)):
			graph_data[i] = re.sub("\s+", ",", graph_data[i].strip()) # replace all whitespace with commas in data
			# for stereo data
			if graph_data[i] == 'DATA:':
				start_data = i # save the index of the start of the data (typically 102)
		csv_data = graph_data[start_data+1:] # splice all data for just the graphable data (+1 to not include 'DATA:') 
		csv_data = [row.split(',') for row in csv_data]
		outputCSV(filename, csv_data)
		'''
		datetime_lst = []
		datetime_lst = datetime_convert(csv_data)
		determine_plot_interval(datetime_lst) #TODO

		b_x = [float(col[8]) for col in csv_data]
		b_y = [float(col[9]) for col in csv_data]
		b_z = [float(col[10]) for col in csv_data]
		b_total = [float(col[7]) for col in csv_data]

		# values subject to change
		percent_cutoff_value = .25 #%
		percent_trimmed_from_mean = 0.45 #%
		time_cutoff_in_minutes = 30 # minutes
		update_mean_every_x_hours = 4 # hours
		buffer_size = .30 #% add x seconds around any event found as a buffer

		# plot total event split into parts
		multiplePlot(buffer_size, datetime_lst, b_x, b_y, b_z, b_total, "overall", None)

		# find possible events
		possible_events = magEnhance(datetime_lst,
									 b_total,
									 b_x,
									 b_y,
									 b_z,
									 percent_cutoff_value,
									 percent_trimmed_from_mean,
									 time_cutoff_in_minutes,
									 update_mean_every_x_hours,
									 buffer_size) # finds possible events for a given set of constants 
		
	print("\nGraphing ran for {0}".format(datetime.now() - start_time))
	#plt.show()

