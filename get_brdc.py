#!/usr/bin/python

'''
Author: 	Joanna Mazer
Github: 	https://github.com/joannamazer
Date:   	04/26/2018
About:		Input options for day/month/year to fetch the corresponding GPS broadcast ephemeris file. Creates directory "/ephemeris" for all output files.
'''

import ftplib
import sys
import base64
import datetime
import argparse
import os
from utils.unlzw import unlzw # to unzip *.Z compressed unix file



# config options: -d (day), -m (month), -y(year)
# default values: today's date [datetime.datetime.now()]
def parse_input_arguments(day, month, year):
	date = datetime.date(year, month, day)
	description = "DEFAULT: [" + str(date) + "]"
	parser = argparse.ArgumentParser(prog='get_brcd_data.py', description=description)
	parser.add_argument('-d', metavar='DATE', type=int, default=day, help='[dd]')
	parser.add_argument('-m', metavar='MONTH', type=int, default=month, help='[mm]')
	parser.add_argument('-y', metavar='YEAR', type=int, default=year, help='[yyyy]')
	args = parser.parse_args()
#	parser.print_help()

	if args.d:
		day = args.d
	if args.m:
		month = args.m
	if args.y:
		year = args.y
	date = datetime.date(year, month, day)
	return date


def main(argv):

	now = datetime.datetime.now()
	day = now.day
	month = now.month
	year = now.year
	data_directory = "ephemeris/"

	date = parse_input_arguments(day, month, year); # update date to match default or user input values
	print "\nRetreiving broadcast ephemeris file for date: " + str(date)

	ftp = ftplib.FTP('cddis.gsfc.nasa.gov', 'anonymous','anonymous') # guest access to server content
	ftp.cwd("/gnss/data/daily") # daily GPS broadcast ephemeris files

	data_path = '{0:%Y}/{0:%j}/{0:%y}n/'.format(date)
	ftp.cwd(data_path)

	ephem_file = 'brdc{0:%j}0.{0:%y}n'.format(date)
	ephem_file_zipped = ephem_file + str(".Z")
	retr_filename = "RETR " + str(ephem_file_zipped)

	filedata = open(ephem_file_zipped, 'wb') # open/create local binary file
	ftp.retrbinary(retr_filename, filedata.write) # return .Z file
	filedata.close()
	ftp.quit() # quit access to server


	if not os.path.isdir(data_directory): # check if directory exists
		os.mkdir(data_directory)

	with open(ephem_file_zipped, 'r') as f_in: # open local .Z file for decompression
		with open(str(data_directory) + str(ephem_file), 'w+') as f_out: # open/create local file for decompression
			compressed = f_in.read()
			decompressed = unlzw(compressed)
			f_out.write(decompressed)

	print "Output file saved in directory: ephemeris/"

	if os.path.isfile(ephem_file_zipped): # remove compressed .Z file
	    os.remove(ephem_file_zipped)
	else:
	    print("Error: %s file not found" % ephem_file_zipped)

if __name__ == "__main__":
	main(sys.argv[1:])
