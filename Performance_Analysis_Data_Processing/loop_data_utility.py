# loop data handling and processing
# the code below helps calculate the daily, hourly average based on the data
# collected from WSDOT loop (https://tracflow.wsdot.wa.gov/contourdata/brainscan)
# Packages needed
import pandas as pd
from pandas import *
import numpy as np
import os
from datetime import *
import statistics as stat
import matplotlib.pyplot as plt
import matplotlib.ticker as plticker
import matplotlib
import csv
from zipfile import ZipFile

# after you download the data from WSDOT loop, you will receive some zip files
# the function below helps you unzip the file, check if the loop encounter with
# a large number of missing data issues based on your interested date period,
# and keep the .xlsx file only
# Note: The volume sheet under the excel file should look like below:
# column should follow: year-month-day hour:minute:second
# row (here we use hourly average) should follow: hour:minute:second
# row/column  2019-01-05 00:00:00, 2019-01-06 00:00:00, ...
# 0:00:00
# 1:00:00
# ...
# input:
#	   - filepath: file path you store the zip file
#	   - date1: start date
#	   - date2: end date
# output: .xlsx files from the zip file which have data based on your given
# date period
def raw_data_process(filepath, date1, date2):
	# get all the files under the given path
	folders = os.listdir(filepath)
	# check the zip file and unzip them all
	for i in folders:
		if i[-3:] == 'zip':
			zip = ZipFile(filepath+i)
			zip.extractall(path=filepath)

	files = os.listdir(filepath)
	# get current xlsx file and remove the .png file
	dtfiles = []
	index = 0
	for i in files:
		if i[-4:] == 'xlsx':
			dtfiles.append(filepath+i)
		if i[-3:] == 'png':
			os.remove(filepath+i)
		# if other files detected, print a caution, the other files which not
		# directly from the folder may cause some error for the other function
		# set up an index to detect such situation to avoid repeated print
		elif index == 0 and i[:-4]!='xlsx' and i[-3:]!='png':
				print('Caution: there are other files detected except the \
				zipped file in the given folder')
				print('Warning: other file may cause error for other functions')
				index = index + 1


	# check data and delete .xlsx fle with missing data only with the period
	# you are interested
	for excel in dtfiles:
		dt = pd.read_excel(excel, sheet_name='Volume')
		col =  list(dt.columns)
		a = 0
		for coln in col:
			try:
				if datetime.strptime(str(coln),'%Y-%m-%d %H:%M:%S') >= date1 and \
					datetime.strptime(str(coln),'%Y-%m-%d %H:%M:%S') <= date2:
					a = a+sum(dt[coln])
			except:
				print('Colume format error, check if colume name follows date \
				format: year-month-day hour:minute:second')
		if a < 0:
			os.remove(excel)

# data processing
# here we tide the data into ditrect format
# the output looks like {loopid:{time period:{datetime:[vol]}}} where vol is
# ordered by hour
# e.g., {'005es16186_MN':'BC':datetime(2019,1,5,0,0):[100, 200, 300,...]}
# create the dict followed by the format
def makeloopvol(periodlst, pathfile):
	# get current pathfile
	dtfiles = get_datafile(pathfile)
	loop_vol = {}
	for excel in dtfiles:
		# get the index of loop id from the .xlsx path
		# the loop id looks like 005es16186_MN where 005 is the route, 16186 is
		# the milepost for the loops
		# MN is the direction, in this example, MN stands form North bound
		if 'MN_' in excel:
			index = excel.index('N__')
		if 'MS_' in excel:
			index = excel.index('S__')
		loop_vol[excel[(index-12):(index+1)]] = {}
		for period in periodlst:
			loop_vol[excel[(index-12):(index+1)]][period] = {}
	return(loop_vol)

# get current .xlsx in the folder
def get_datafile(pathfile):
	files = os.listdir(pathfile)
	dtfiles = []
	for i in files:
		if i[-4:] == 'xlsx' and i[0]!='~':
			dtfiles.append(pathfile+i)
	return(dtfiles)

# if negative value is found for volume (regarding as missing value), convert
# them to zero
def convert_negative_val2(lst):
	a = 0
	tup = np.nonzero(lst)
	for i in tup:
		cklst = i
	for i in range(len(lst)):
		if lst[i] < 0:
			lst[i] = 0
	return(lst)

# get loop volume
def get_loop(t1, t2, dt, day, period, loopid, loop_vol, date):
	if date >= t1 and date <= t2:
		volst = convert_negative_val2(list(dt[day]))
		if volst != None:
			loop_vol[loopid][period][date] = []
			loop_vol[loopid][period][date] = volst
	return(loop_vol)

def excel_processing(pathfile, periodlst, time_bond, loop_vol):
	dtfiles = get_datafile(pathfile)
	for excel in dtfiles:
		dt = pd.read_excel(excel, sheet_name='Volume')
		# get the index of loop id from the .xlsx path
		if 'MN_' in excel:
			index = excel.index('N__')
		if 'MS_' in excel:
			index = excel.index('S__')
		loopid = excel[(index-12):(index+1)]
		daylst = list(dt.columns)
		hourlst = list(dt.index)
		# check data availability during befor closure period
		for day in daylst:
			date = datetime.strptime(str(day),'%Y-%m-%d %H:%M:%S')
			loop_vol = get_loop(time_bond[0], time_bond[1], dt, day, \
			periodlst[0], loopid, loop_vol, date)
			loop_vol = get_loop(time_bond[2], time_bond[3], dt, day, \
			periodlst[1], loopid, loop_vol, date)
			loop_vol = get_loop(time_bond[4], time_bond[5], dt, day, \
			periodlst[2], loopid, loop_vol, date)
	return(loop_vol)

#get latitude and longitude for each loop
def get_loop_location(loopvol, pathfile):
	dtfiles = get_datafile(pathfile)
	# create a loc direct to stire lat, lon for each loop id
	loc = {}
	for i in loopvol:
		loc[i] = []
	for j in dtfiles:
		dt = pd.read_excel(j, sheet_name='Metadata')
		if 'N_' in j:
			index = j.index('N__')
		if 'S_' in j:
			index = j.index('S__')
		loc[j[(index-12):(index+1)]] = list(dt.iloc[0][1:])
	return(loc)

# calculate the value
# calculate daily average by loop within a week (by day, mor_peak, eve_peak)
# calculate daily average (by Sat, Sun, Mon,...) by day
def CalVol(loopvoldict, t1, t2, d1, d2):
	wkavg_loop = {}
	davg_loop = {}
	for lpid in loopvoldict:
		# create dict to store daily and weekly average
		wkavg_loop[lpid] = {}
		davg_loop[lpid] = {}
		pdlst = list(loopvoldict[lpid].keys())
		for pd in pdlst:
			wkavg_loop[lpid][pd] = 0
			davg_loop[lpid][pd] = {}
			date_time = list(loopvoldict[lpid][pd].keys())
			# call the CalWeekAvg function to calculate the weekday traffic
			# volume average for each loop id
			wkavg_loop[lpid][pd] = CalWeekAvg(loopvoldict, date_time, lpid, \
			pd, t1, t2, d1, d2)
			# call the CaldailyAvg function to calculate the daily traffic
			#volume average for each loop id
			davg_loop[lpid][pd] = CaldailyAvg(loopvoldict, date_time, lpid, \
			pd, t1, t2, d1, d2)
	return(wkavg_loop, davg_loop)

def CalWeekAvg(loopdict, datetime, loopid, period, t1, t2, d1, d2):
	vol = 0
	n = 0
	for day in datetime:
		if day.weekday() >= d1 and day.weekday() <= d2:
			loopvol = loopdict[loopid][period][day][t1:t2]
			vol = vol + sum(loopvol)
			n = n + len(np.nonzero(loopvol)[0])
	if n == 0:
		#uncomment for the code below to check detailed id information
		#identified with missing data
		#print('loopid:', loopid, 'has identified with missing data when \
		#calculating weekly average at', period, 'period')
		avg = 0
	else:
		avg = round(vol/n, 3)
	#return the average traffic volume based on given daily and hourly bound
	return(avg)

def CaldailyAvg(loopdict, datetime, loopid, period, t1, t2, d1, d2):
	DailyAvg = {}
	for day in datetime:
		# the bound defined for different days
		if day.weekday() >= d1 and day.weekday() <= d2:
			DailyAvg[day] = []
			loopvol = loopdict[loopid][period][day][t1:t2]
			vol = sum(loopvol)
			n = len(np.nonzero(loopvol)[0])
			if n == 0:
				#uncomment for the code below to check detailed id information
				#identified with missing data
				#print('loopid:', loopid, ' has identified with missing data \
				#when calculating daily average at ', period, ' period')
				avg = 0
			else:
				avg = round(vol/n, 3)

			DailyAvg[day].append(round(vol,3))
			DailyAvg[day].append(n)
			DailyAvg[day].append(avg)
	#return a list which contains the total loop vol, number of n calculated
	# in the loops,
	#and the calculated average
	return(DailyAvg)

# calculate hourly average of traffic volume
def CalHourAvg(loopvoldict, d1, d2):
	loop_list = list(loopvoldict.keys())
	# create dict for hourly average calculation
	avg_lp_hr = {} # dict for hourly average of each loop
	avg_hr = {} # dict for hourly average based on all loops
	periodlst = {}
	for pd in loopvoldict[loop_list[0]]:
		avg_lp_hr[pd] = {}
		avg_hr[pd] = {}
		periodlst[pd] = {}
	#get hourly volume from the selected date
	for pd in periodlst:
		for lpid in loop_list:
			daylst = list(loopvoldict[loop_list[0]][pd].keys())
			periodlst[pd][lpid] = {}
			for h in range(24):
				periodlst[pd][lpid][h] = []
				for d in daylst:
					if d.weekday()>= d1 and d.weekday()<=d2:
						periodlst[pd][lpid][h].append(round(loopvoldict[lpid]\
						[pd][d][h],3))

	for pd in periodlst:
		for lpid in loop_list:
			avg_lp_hr[pd][lpid] = {}
			avg_hr[pd] = {}
			for h in range(24):
				avg_lp_hr[pd][lpid][h] = []
				avg_hr[pd][h] = []
				sum_vol = round(sum(periodlst[pd][lpid][h]),3)
				num = len(np.nonzero(periodlst[pd][lpid][h])[0])
				# calculate the sum of hourly traffic volume for a specific loop
				# calculate the total avaiable data count
				avg_lp_hr[pd][lpid][h].append(sum_vol)
				avg_lp_hr[pd][lpid][h].append(num)
				if num == 0:
					avg_lp_hr[pd][lpid][h].append(0)
				else:
					# calculate the daily average
					avg_lp_hr[pd][lpid][h].append(round(sum_vol/num, 3))

	for pd in periodlst:
		for i in range(len(loop_list)):
			for h in range(24):
				if i == 0:
					avg_hr[pd][h] = list(avg_lp_hr[pd][loop_list[i]][h][:2])
				else:
					avg_hr[pd][h][0] = avg_hr[pd][h][0] + avg_lp_hr[pd][loop_list[i]][h][0]
					avg_hr[pd][h][1] = avg_hr[pd][h][1] + avg_lp_hr[pd][loop_list[i]][h][1]

	for pd in periodlst:
		for i in range(24):
			avg = round(avg_hr[pd][i][0]/avg_hr[pd][i][1],3)
			avg_hr[pd][i].append(avg)

	return(avg_lp_hr, avg_hr)

# calculated the hourly average traffic volume based on different day of
# all available loops
def getAvgHrbyDay(loopvoldict):
	loop_list = list(loopvoldict.keys())
	# create dict for hourly average calculation
	hrplotlst = {} # dict for hourly average of each loop
	periodlst = {}
	for pd in loopvoldict[loop_list[0]]:
		hrplotlst[pd] = {}
		periodlst[pd] = {}

	for pd in periodlst:
		daylst = list(loopvoldict[loop_list[0]][pd].keys())
		for d in daylst:
			periodlst[pd][d] = {}
			for i in range(24):
				periodlst[pd][d][i] = []
	for lpid in loop_list:
		for pd in periodlst:
			daylst = list(loopvoldict[lpid][pd].keys())
			for d in daylst:
				for i in range(24):
					periodlst[pd][d][i].append(loopvoldict[lpid][pd][d][i])

	for pd in periodlst:
		for d in list(periodlst[pd].keys()):
			hrplotlst[pd][d] = []
			for i in range(24):
				sum_vol = sum(periodlst[pd][d][i])
				n = len(np.nonzero(periodlst[pd][d][i])[0])
				if n == 0:
					avg = 0
				else:
					avg = round(sum_vol/n, 3)
				hrplotlst[pd][d].append(avg)
	return(hrplotlst)

def CalallDayAvg(Avglst):
	loop_list = list(Avglst.keys())
	periodlst = list(Avglst[loop_list[0]].keys())
	#create dict to store the data
	allDayAvg = {}
	for pd in periodlst:
		allDayAvg[pd] = {}
	for pd in periodlst:
		daylst = list(Avglst[loop_list[0]][pd].keys())
		for d in daylst:
			allDayAvg[pd][d] = []
	for i in range(len(loop_list)):
		for pd in periodlst:
			daylst = list(Avglst[loop_list[i]][pd].keys())
			for d in daylst:
				if i == 0:
					allDayAvg[pd][d] = list(Avglst[loop_list[i]][pd][d])
				else:
					allDayAvg[pd][d][0] = allDayAvg[pd][d][0]+Avglst[loop_list[i]][pd][d][0]
					allDayAvg[pd][d][1] = allDayAvg[pd][d][1]+Avglst[loop_list[i]][pd][d][1]

	for pd in periodlst:
		daylst = list(allDayAvg[pd].keys())
		for d in daylst:
			if allDayAvg[pd][d][1] == 0:
				allDayAvg[pd][d][2] = 0
			else:
				avg = round(allDayAvg[pd][d][0]/allDayAvg[pd][d][1],3)
				allDayAvg[pd][d][2] = avg
	return(allDayAvg)

def move_figure(f, x, y):
	"""Move figure's upper left corner to pixel (x, y)"""
	backend = matplotlib.get_backend()
	if backend == 'TkAgg':
		f.canvas.manager.window.wm_geometry("+%d+%d" % (x, y))
	elif backend == 'WXAgg':
		f.canvas.manager.window.SetPosition((x, y))
	else:
		# This works for QT and GTK
		# You can also use window.setGeometry
		f.canvas.manager.window.move(x, y)


def plothr(legendlst, loopvoldict):
	plotdata = getAvgHrbyDay(loopvoldict)
	x = list(range(168))
	fig = plt.figure()
	ax = fig.add_axes([0.8, 0.8, 1, 1]) # main axes
	move_figure(fig, 500, 500)
	
	#tide data so the day starts on Monday
	y = {}
	i = 0
	for p in plotdata:
		y[p] = []
		i = i + 1
		for d in plotdata[p]:
			if d.weekday()>=5:
				pass
			else:
				y[p].extend(plotdata[p][d])
		for d in plotdata[p]:
			if d.weekday()>=5:
				y[p].extend(plotdata[p][d])
		if i == 3:
			ax.plot(x, y[p], 'r--')
		else:
			ax.plot(x, y[p])

	ax.set_title('Hourly average traffic volume based on WSDOT loop data', fontsize=15)
	ax.set_xlabel('Date', fontsize=15)
	ax.set_xticks([0, 24, 48, 72, 96, 120, 144])
	ax.set_xticklabels(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'], fontsize=13)
	ax.set_ylabel("Average traffic volume", fontsize=15)

	ax.grid(which='major', linestyle='--')
	ax.grid(which='minor', linestyle=':')
	plt.legend(legendlst, loc='lower left', bbox_to_anchor=(1., 0.5), fontsize=13)
	plt.show()

def hourlyplot(y1, y2, y3, notes, legendlst):
	x =  list(range(24))
	fig = plt.figure()
	ax = fig.add_axes([0.8, 0.8, 1, 1]) # main axes
	mngr = plt.get_current_fig_manager()
	mngr.window.setGeometry(50,100,640, 545)
	ax.plot(x, y1)
	ax.plot(x, y2,'.-')
	ax.plot(x, y3,'r--')

	ax.set_title('Average traffic volume based on Sensys data by hour' + notes, fontsize = 16)
	ax.set_xlabel('Hour', fontsize = 16)
	ax.set_ylabel("Traffic volume", fontsize = 16)

	ax.grid(which='major', linestyle='--')
	ax.grid(which='minor', linestyle=':')
	plt.legend(legendlst, loc='lower left', bbox_to_anchor=(1., 0.5), fontsize=12)

	plt.show()

def tidedictandplot(dicts, notes, legendlst):
	hrdic = {'BC':[],'AC':[],'AO2':[]}
	for pd in dicts:
		for hr in dicts[pd]:
			hrdic[pd].append(dicts[pd][hr][2])
	hourlyplot(hrdic['BC'],hrdic['AC'],hrdic['AO2'], notes, legendlst)
