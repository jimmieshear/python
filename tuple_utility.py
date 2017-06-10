#!/usr/bin/python
"""
################################################################################
# Copyright (c) 2017 Robert Hill. All rights reserved.
################################################################################
	NAME: TupleUtility.py

	DESCRIPTION:
	A utility class that can provide a tuple-ized version of a file 
	descriptor. The utility can return the highest version in the target
	folder.

	History:		
	04/20/17 -RH
	Initial Creation
		Logging is verbose since clients don't always have a way to
		express what happened if the script should not work properly

		*Note that .dmg might be changing in the future. macOS no longer
		uses HFS, and is moving to APFS, which has no concept of whole
		disk volumes. It uses containers, like a lot of modern file
		systems. 

################################################################################
"""

################################################################################
# Imports
################################################################################

# Common Imports
import os,sys,argparse,logging,re

################################################################################
# Logging 
################################################################################

log = logging.getLogger('Utilities')
log.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s', "%Y-%m-%d %H:%M:%S")

logger1 = logging.FileHandler('/tmp/utilities.log')
logger1.setLevel(logging.DEBUG)
logger1.setFormatter(formatter)
log.addHandler(logger1)

################################################################################
# Classes
################################################################################
class ExecuteScript(object):
	def __init__(self, args):
		self.args = args

	def return_highest_tuple_for_path(self):

		# Check arguments to script
		if (self.args.path == "path"):
			self.usage()
			sys.exit(0)

		tu = TupleUtility()
		# Snapshot path folder
		my_versions = os.listdir(self.args.path)
		log.debug("ExecuteScript:return_highest_tuple_for_path: my_versions: {0}".format(my_versions))

		# Check if the version passed in starts with a digit
		for my_version in my_versions:
			# This Regex matches a 3 tuple version
			my_temp_match = re.search(r'\b(?<!\.)((?:\d{1,3}))(?:\.\d{1,2}){0,2}(?:\..mg)', my_version)
			my_match = None
			if my_temp_match is not None:	
				my_match = my_temp_match.group()
				log.debug("ExecuteScript:return_highest_tuple_for_path: my_temp_match : {0}".format(my_match))
			else:
				# Skip, regex found "none" type
				continue
	
			log.debug("ExecuteScript:return_highest_tuple_for_path: my_match: {0}".format(my_match))

			# Tuplize
			my_tuple_version = tu.tuplize_version(my_match)
			log.debug("ExecuteScript:return_highest_tuple_for_path: my_tuple_version: {0}".format(my_tuple_version))

			if (my_tuple_version):
				# Check if tuple is higher or lower than current "highest_version"
				if tu.highest_version:
					my_return = tu.compare_tuples(tu.highest_version, my_tuple_version)
					# higher than current "Highest", set property to new version
					if (my_return is -1):
						# Normalize back to string
						tu.highest_version = my_tuple_version
						tu.highest_name = my_version
						log.debug("ExecuteScript:return_highest_tuple_for_path: tu.highest_version: {0}, tu.highest_name {1}".format(my_tuple_version,my_version))
				else:
					# No highest version set
					tu.highest_version = my_tuple_version
					tu.highest_name = my_version
					log.debug("ExecuteScript:return_highest_tuple_for_path: tu.highest_version: {0}, tu.highest_name {1}".format(my_tuple_version,my_version))
			else:
				# Not a valid tuple skip
				continue

		# Return highest version
		if not self.args.name:
			my_join_version = '.'.join(map(str,tu.highest_version))
			print my_join_version
		else:
			print tu.highest_name
	
class TupleUtility(object):
	"""
	TupleUtility: Class to encapsulate the tuple utility functions
	"""

	def __init__(self):
		self._highest_version = None
		self._highest_name = None

	# PROPERTIES
	@property
	def highest_version(self):
		return self._highest_version

	@highest_version.setter
	def highest_version(self, higher_version):
		self._highest_version = higher_version
		log.debug("TupleUtility:highest_version setter higher_version: {0}".format(higher_version))

	@property
	def highest_name(self):
		return self._highest_name

	@highest_name.setter
	def highest_name(self, higher_name):
		self._highest_name = higher_name
		log.debug("TupleUtility:highest_name setter higher_name: {0}".format(higher_name))


	# FUNCTIONS	
	def tuplize_version(self, version):
		"""
		tuplize_version: A quick way to split the version out 
		"""
		if version.endswith('mg'):
			version = version[:-4] # ext are always 4 characters
		my_tuple_version = [int(x) for x in re.sub(r'(\.0+)*$','',version).split(".")]
		log.debug("TupleUtility:tuplize_version: tuple will return my_tuple_version:{0}".format(my_tuple_version))

		return my_tuple_version

	def is_valid_tuple(self, version):
		"""
		is_valid_tuple: Restricts the versions we look at. Currently the versioning fits this spec:
		Version-999.99.99	== OK
		Version-1.1.1		== OK
		
		A Versions first tuple can go from	0 - 999
		A Versions second tuple can go from	0 - 99
		A Versions third tuple can go from	0 - 99
		NOTE: I left this here, as I figured it might provide utility to other classes.
			The regex in the Execute class takes care of this functionality, but a
			script may not have the same params
		"""

		# Positional arguments
		if not len(str(version[0])) < 4:
			log.debug("TupleUtility:is_valid_tuple: tuple is invalid {0}, skipping".format(version[0]))
			return False

		if len(version) > 1:
			if not len(str(version[1])) < 3:
				log.debug("TupleUtility:is_valid_tuple: tuple is invalid {0}, skipping".format(version[1]))
				return False

		if len(version) == 3:
			if not len(str(version[2])) < 3:
				log.debug("TupleUtility:is_valid_tuple: tuple is invalid {0}, skipping".format(version[2]))
				return False
		return True

	def compare_tuples(self, first_tuple,second_tuple):
		"""
		CompareTuples: requires two tuples and will compare them, returning -1 (higher), 1 (lower), 0 (even)
		"""

		log.debug("TupleUtility:compareTuples: Subroutine entry with variables my_first_tuple:{0} and my_second_tuple:{1}".format(first_tuple,second_tuple))
		my_cmp = cmp(first_tuple, second_tuple)
		return my_cmp

	def usage(self):
		print ("A class that can return the highest version from a list of versions to the script")
		print ("<required> '-p' or '--path'	Location of files that you wish to have scanned")
		print ("<default>			User wants output of just the version, like 123.4.5.")
		print ("<optional> '-n' or '--name'	User wants output of name and version, like what was handed into the script ex. Build-123.4.5.dmg")

################################################################################
# RUN AS SCRIPT
################################################################################
if __name__ == "__main__":

	# ARGS
	parser = argparse.ArgumentParser(description = "Script to return highest version given a list of versions")

	parser.add_argument('-p', '--path',		default="path", help = "Path to the directory")
	parser.add_argument('-n', '--name',		action="store_true",  help = "Return output as name of file instead of just version")
	args = parser.parse_args()

	ExecuteScript(args).return_highest_tuple_for_path()
