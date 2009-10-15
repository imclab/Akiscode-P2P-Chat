#!/usr/bin/python

#-------------------------------------------------------------------------------------------------
# Name: Akiscode Chat
# Author: Stephen Akiki
# Website: http://akiscode.com
# Language: Python
# Usage: 
#	python akischat.py 
#		 OR
#       python akischat.py --GUI
# Dependencies:
#	python-tk package - for GUI
# Thanks to:
#	---
# Disclaimer:
#	By using this program you do so at your own risk. I assume no liability
#	for anything that happens to you because you used this program.
#	
#	Enjoy
#
# License - GNU GPL (See LICENSE.txt for full text):
#-------------------------------------------------------------------------------------------------
#    If you want to use this code (in compliance with the GPL) then you should
#    include this somewhere in your code comments header:
#
#    Thanks to Stephen Akiki (http://akiscode.com/code/chat) for sparknotes downloader code
#-------------------------------------------------------------------------------------------------
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#-------------------------------------------------------------------------------------------------
# Copyright (C) 2009 Stephen Akiki. All rights reserved.
#-------------------------------------------------------------------------------------------------

import os, thread, socket, traceback

#-------------------CONSTANTS-------------------------

LOCAL_IP = socket.gethostbyname(socket.gethostname()) # Gets local IP address

IP_ADDRESS_LIST = [] # Holds all the IP addresses

PORT = 7721 # Port to send packets on

DEBUG = 1
#-----------------------------------------------------

# Used to print out info that I need during debugging.
def dbg(string):
	global DEBUG
	if DEBUG == 1:
		print '-----DEBUG-----: ' + str(string)
	else:
		pass

# This is a wrapper function so we can abstract away how we print the characters, either to the 
#   command line or the GUI
def PrintToScreen(str):
	print str


def SendText(str):
	global PORT
	for ip_addr in IP_ADDRESS_LIST:
		try:
			d = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			d.sendto(str, (ip_addr, PORT))
			d.close()
		except:
			PrintToScreen('Could not send to: ' + ip_addr)
			dbg((str, ip_addr, PORT))
			if DEBUG == 1:
				traceback.print_exc()
			else:
				pass



