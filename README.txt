Python files

################################################################################
# unique_name_for_copy.py
################################################################################
This is a script I use to copy my camera files from my different video cameras
to my computer. I needed a way to change something abstract like "PRM0002.mp4" 
into something more concrete like a date and time. The script relies on having 
a correct date and time set on the camera. 

################################################################################
# sprinklerdetector.py
################################################################################
A script I use with my Opensprinkler to detect water leaks using a flow control
system. The script runs on a scheduler, with a check every few minutes. If the
system is not scheduled to water, and the flow sensor is reporting water running
then a second check is run to determine if it's not a false alarm (someone using
the faucet). Raising the alert level each time.

################################################################################
# tuple_utility.py
################################################################################
A portion of a script I use from time to time to scan directories for the latest
version of a build. This assume 3 tuple versions (especially the regex), which
are normal for Apple style builds. The script will scan a directory of files 
(typically dmgs) and return the highest tuple version.
