#!/usr/bin/python
"""
################################################################################
# Copyright (c) 2017 Robert Hill.  All rights reserved.
################################################################################
        NAME:
        create_test_files.py

        DESCRIPTION:
	A script to quickly generate the test files required for 
	the unique file name script

        HISTORY:
        06/09/17 -RH
        Initial creation

################################################################################
"""

################################################################################
# IMPORT
################################################################################
import argparse,os,time

################################################################################
# CONSTANT
################################################################################
test_folder_count = 30

# Find our arguments
parser = argparse.ArgumentParser(description = "Script to create a bunch of test files for the unique file script")
parser.add_argument('-t', '--target',   default="target", help = "The path to the source folder")
args = parser.parse_args()

# Create a bunch of test files in the target folder
for i in range(0, test_folder_count):
	os.chdir(args.target)
	test_name_format = "Test{0}File{0}.MOV".format(i)
	with open(test_name_format, 'a'):
		os.utime(test_name_format, None)
		time.sleep(1)
