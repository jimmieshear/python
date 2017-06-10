#!/usr/bin/python
"""
################################################################################
# Copyright (c) 2016 Robert Hill
################################################################################
	NAME: 
	unique_name_for_copy.py

	DESCRIPTION:
	Will generate a time_stamp based name.

	HISTORY:
	02/11/16 -RH
	Initial creation

	06/09/17 -RH
	Added function to rename files in a target directory. This is for
	items that are already imported and just need renaming.

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
# CLASSES
################################################################################

class ExecutePlan(object):
	def __init__(self, args):
		self.args = args
		self.source_files = None

	def run(self):
		if (self.args.inplace):
			if (self.args.source == "source"):
				self.usage()
				sys.exit(0)
		elif (self.args.source == "source" or self.args.dest == "dest"):
			self.usage()
			sys.exit(0)

		# Snapshot source folder
		self.source_files = os.listdir(self.args.source)
		log.debug("ExecutePlan:run: self.source_files eq {0}".format(self.source_files))

		items_count = len(self.source_files)
		if (self.args.inplace and items_count > 0):
			rcf = RenameCameraFiles(self.args,self.source_files)
			rcf.rename_camera_file()
		elif (items_count > 0):
			ut = MoveCameraFiles(self.args,self.source_files)
			ut.move_files_with_final_name()

	def usage(self):
		if (self.args.inplace):
			print("Script to injest mov files from a camera card and copy them with a file name")
			print("<required> '-s' or '--source' The path to the source mov files")
		else:
			print("Script to injest mov files from a camera card and copy them with a file name")
			print("<required> '-s' or '--source' The path to the source mov files")
			print("<required> '-d' or '--dest' The path to the destination folder")


class CameraFile(object):
	"""
	CameraFile -- A class that will validate if a file is supported or not and add
			the files to a property list
	"""
	def __init__(self,source_files):
		self.args = args
		self.source_files = source_files
		self._movie_file = []

	# PROPERTIES
	@property
	def movie_files(self):
		return self._movie_file

	@movie_files.setter
	def movie_files(self, movie_file):
		self._movie_file.append(movie_file)
		return self._movie_file

	def is_mov_file(self):
		# Call before using the property getter for movie_files
		for i in self.source_files:
			# Drift camera
			if not i.endswith("_thm.mp4") and i.endswith(".mp4"):
				log.debug("MoveCameraFiles:is_mov_file: mp4 {0}".format(i))
				self.movie_files = i
			# Bullet HD Camera for motorcycle
			elif i.endswith(".MOV"):
				log.debug("MoveCameraFiles:is_mov_file: .MOV {0}".format(i))
				self.movie_files = i
			# GoPro 4
			elif i.endswith(".MP4"):
				log.debug("MoveCameraFiles:is_mov_file: .MP4 {0}".format(i))
				self.movie_files = i

	@staticmethod	
	def format_date_time(the_ctime):
		# Get the create time for the files in the mov_list
		my_date_time = datetime.datetime.strptime(the_ctime, "%a %b %d %H:%M:%S %Y")
		my_format = "%m%d%Y_%H%M%S"
		my_final_date_time = my_date_time.strftime(my_format)
		my_final_formatted = "{0}.mp4".format(my_final_date_time)
		log.debug("MoveCameraFiles:format_date_time: final formatted time is {0}".format(my_final_formatted))
		return(my_final_formatted)

class RenameCameraFiles(object):
	"""
	RenameCameraFiles -- A class to rename the files instead of copy
	"""
	def __init__(self,args,source_files):
		self.args = args
		self.source_files = source_files

	def rename_camera_file(self):
		cf = CameraFile(self.source_files)

		# Creates the list of movie files from the source files list
		cf.is_mov_file()

		original_count = len(cf.movie_files)
		current_count = original_count
		print("Working on {0} files".format(original_count))

		for i in cf.movie_files:
			os.chdir(self.args.source)
			my_date_time = time.ctime(os.path.getctime(i))
			formatted_time = cf.format_date_time(my_date_time)
			log.debug("MoveCameraFiles:formatted_time:  {0}".format(formatted_time))

			print("\nWorking on {0} of {1}.".format(current_count,original_count))
			print("Will rename file from {0} to {1}".format(i,formatted_time))

			os.rename(i, formatted_time)
			current_count -= 1

class MoveCameraFiles(object):
	"""
	MoveCameraFiles -- A class to copy and name the file 
	"""
	def __init__(self,args,source_files):
		self.args = args
		self.source_files = source_files
		self.mov_list = []

	def move_files_with_final_name(self):
		cf = CameraFile(self.source_files)

		# Creates the list of movie files from the source files list
		cf.is_mov_file()

		original_count = len(cf.movie_files)
		current_count = original_count
		print("Working on {0} files".format(original_count))

		# Change dir to source folder
		os.chdir(self.args.source)

		# itterate over the mov list
		for i in cf.movie_files:
			my_date_time = time.ctime(os.path.getctime(i))
			formatted_time = cf.format_date_time(my_date_time)
			log.debug("MoveCameraFiles:formatted_time:  {0}".format(formatted_time))

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
				print("\nWorking on {0}, item {1} of {2}.".format(i,current_count,original_count))
				print("Will save file as {0} in destination {1}.".format(formatted_time,self.args.dest))
				current_count -= 1 
				self.execute_cmd(my_ditto_cmd)

	# Add a remove sources command at some point

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


################################################################################
# RUN AS A SCRIPT
################################################################################
if __name__ == "__main__":

	# Find our arguments
	parser = argparse.ArgumentParser(description = "Script to injest mov files from a camera card and copy them with a file name")

	parser.add_argument('-s', '--source',	default="source", help = "The path to the source mov files")
	parser.add_argument('-d', '--dest',	default="dest", help = "The path to the destination folder")
	parser.add_argument('-p', '--inplace',	action="store_true", help = "Change the files in place, this is for an already imported item you just want to change the name of")
	args = parser.parse_args()

	ExecutePlan(args).run()
