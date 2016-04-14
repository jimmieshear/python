#!/usr/bin/python

"""
################################################################################
# Copyright (c) 2016 Robert Hill
################################################################################
	NAME: 
	unique_name_for_copy.py

	DESCRIPTION:
	Will generate a time_stamp based name 

	HISTORY:
	02/11/16 -RH
	Initial creation

################################################################################
"""

import os.path,time,argparse,logging,datetime,subprocess,sys
from subprocess import Popen

################################################################################
# LOGGING
################################################################################
log = logging.getLogger('uniquename')
log.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

logger1 = logging.FileHandler('/tmp/uniquename.log')
logger1.setLevel(logging.DEBUG)
logger1.setFormatter(formatter)
log.addHandler(logger1)

################################################################################
# Classes
################################################################################

class ExecutePlan(object):
	def __init__(self, args):
		self.args = args
		self.source_files = None

	def run(self):
		# Check args
		if (self.args.source == "source" or self.args.dest == "dest"):
			self.usage()
			sys.exit(0)

		# Snapshot source folder
		self.source_files = os.listdir(self.args.source)
		log.debug("ExecutePlan:run: self.source_files eq {0}".format(self.source_files))

		ut = MoveCameraFiles(self.args,self.source_files)
		ut.is_mov_file()
		ut.get_mov_count()
		if (ut.items_count > 0):
			ut.move_files_with_final_name()

	def usage(self):
		print("Script to injest mov files from a camera card and copy them with a file name")
		print("<required> '-s' or '--source' The path to the source mov files")
		print("<required> '-d' or '--dest' The path to the destination folder")



class MoveCameraFiles(object):
	def __init__(self,args,source_file):
		self.args = args
		self.source_files = source_file
		self.mov_list = []
		self.items_count = None

	def is_mov_file(self):
		# Validate each file is a .mov file, and append to the list
		for i in self.source_files:
			# Drift camera
			if not i.endswith("_thm.mp4") and i.endswith(".mp4"):
				self.mov_list.append(i)
				log.debug("MoveCameraFiles:is_mov_file: appended to self.mov_list {0}".format(i))
			# Bullet HD Camera for motorcycle
			if i.endswith(".MOV"):
				self.mov_list.append(i)
				log.debug("MoveCameraFiles:is_mov_file: appended to self.mov_list {0}".format(i))
			# GoPro 4
			if i.endswith(".MP4"):
				self.mov_list.append(i)
				log.debug("MoveCameraFiles:is_mov_file: appended to self.mov_list {0}".format(i))

	def get_mov_count(self):
		# Get the number of items we will work on
		try:
			self.items_count = len(self.mov_list)
			log.debug("MoveCameraFiles:get_mov_count: count is {0}".format(self.items_count))
		except:
			log.debug("MoveCameraFiles:get_mov_count: count is None")

	def move_files_with_final_name(self):
		# Move the files to the destination
		current_count = self.items_count
		print("Working on {0} files".format(self.items_count))

		# itterate over the mov list
		for i in self.mov_list:
			os.chdir(self.args.source)
			my_date_time = time.ctime(os.path.getctime(i))
			log.debug("MoveCameraFiles:move_files_with_final_name: my_date_time {0}".format(my_date_time))
			formatted_time = self.format_date_time(my_date_time)

			# Ditto results to final destination
			my_ditto_cmd = "/usr/bin/ditto '{0}/{1}' '{2}/{3}'".format(self.args.source,i,self.args.dest,formatted_time)
			log.debug("MoveCameraFiles:move_files_with_final_name: executing cmd {0}".format(my_ditto_cmd))

			# Check destination name and create a destination path
			my_dest_path = os.path.abspath("{0}/{1}".format(self.args.dest,formatted_time))

			# Maybe the user is trying to run this on the same files? 
			if os.path.exists(my_dest_path):
				current_count -= 1
				print("Duplicate destination file found {0}, skipping!".format(my_dest_path))
			else:
				# Execute the copy
				print("\nWorking on {0}, item {1} of {2}.".format(i,current_count,self.items_count))
				print("Will save file as {0} in destination {1}.".format(formatted_time,self.args.dest))
				current_count -= 1 
				self.execute_cmd(my_ditto_cmd)

	def execute_cmd(self,cmd,terminal=None):
		try:
			output = Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
			# Capture out and err in case we need to handle a issue
			if (terminal):
				for line in iter(output.stdout.readline, ''):
					print line.rstrip()
			(stdout,sterr) = output.communicate()
			log.debug("RunCommand:execute_cmd: Output from {0} is {1}".format(cmd, stdout))

		except TypeError as e:
			log.error("RunCommand:execute_cmd: Received error {0} from cmd {1}".format(e,cmd))
		except NSURLErrorDomain as e:
			log.error("RunCommand:execute_cmd: Received error {0} from cmd {1}".format(e,cmd))

		return(stdout,sterr)

	@staticmethod	
	def format_date_time(the_ctime):
		# Get the create time for the files in the mov_list
		my_date_time = datetime.datetime.strptime(the_ctime, "%a %b %d %H:%M:%S %Y")
		log.debug("MoveCameraFiles:format_date_time: time is {0}".format(my_date_time))
		my_format = "%m%d%Y_%H%M%S"
		my_final_date_time = my_date_time.strftime(my_format)
		log.debug("MoveCameraFiles:format_date_time: formatted time is {0}".format(my_final_date_time))
		my_final_formatted = "{0}.mp4".format(my_final_date_time)
		log.debug("MoveCameraFiles:format_date_time: final formatted time is {0}".format(my_final_formatted))
		return(my_final_formatted)

################################################################################
# RUN AS A SCRIPT
################################################################################
if __name__ == "__main__":

	# Find our arguments
	parser = argparse.ArgumentParser(description = "Script to injest mov files from a camera card and copy them with a file name")

	parser.add_argument('-s', '--source',	default="source", help = "The path to the source mov files")
	parser.add_argument('-d', '--dest',	default="dest", help = "The path to the destination folder")
	args = parser.parse_args()

	ExecutePlan(args).run()
