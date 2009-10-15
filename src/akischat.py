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

import os, thread, socket, traceback, urllib

#-------------------CONSTANTS-------------------------

LOCAL_IP = socket.gethostbyname(socket.gethostname()) # Gets local IP address
GLOBAL_IP = ''
try:
	GLOBAL_IP = urllib.urlopen('http://akiscode.com/ip_addr').read() # Gets Global IP
except:
	GLOBAL_IP = '---'


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


def ListenToSocket():
	global PORT
	global LOCAL_IP
	global IP_ADDRESS_LIST

	PrintToScreen(('Local IP:'+LOCAL_IP, 'Global IP:'+GLOBAL_IP, 'Port:'+str(PORT), IP_ADDRESS_LIST))

	while 1:
		d = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		d.bind(('', PORT))
		while 1:
			data, addr = d.recvfrom(1024)
			if not data: break
			if not addr[0] in IP_ADDRESS_LIST and addr[0] != LOCAL_IP:
				IP_ADDRESS_LIST.append(addr[0])
				SendSyncSuggestion()

			if data[:16] == r'\sync_suggestion':
				SyncRequest()

			if data[:13] == r'\sync_request':
				dbg('got sync request') # Debug Only
				SyncData()

			if data[:10] == r'\sync_data':
				dbg('got sync data')
				TEMP_IP_ADDR_LIST = str(data[11:]).split('|')
				dbg(TEMP_IP_ADDR_LIST) # Debug Only
				for temp_ip in TEMP_IP_ADDR_LIST:
					if not temp_ip in IP_ADDRESS_LIST and temp_ip != LOCAL_IP:
						IP_ADDRESS_LIST.append(temp_ip)

			PrintToScreen(addr[0] + ': ' + str(data))

		d.close()

def SendSyncSuggestion():
	SendText('\sync_suggestion')

def SyncRequest():
	SendText('\sync_request')

def SyncData():
	global IP_ADDRESS_LIST
	dbg(('\sync_data ' + '|'.join(IP_ADDRESS_LIST)))  # Debug Only
	SendText('\sync_data ' + '|'.join(IP_ADDRESS_LIST))


def Input(str):
	global LOCAL_IP
	global IP_ADDRESS_LIST

	if str[:4] == r'\add':
		if not str[5:] in IP_ADDRESS_LIST and str[5:] != LOCAL_IP:
			IP_ADDRESS_LIST.append(str[5:])
			SendSyncSuggestion()
			return 0

	if str[:3] == r'\ip': # Display all ip address you currently have
		PrintToScreen(IP_ADDRESS_LIST)
		return 0

	if str[:7] == r'\whoami': # Whats your IP address?
		PrintToScreen(LOCAL_IP)
		return 0

	if str[:16] == r'\sync_suggestion' or str[:13] == r'\sync_request' or str[:10] == r'\sync_data':
		return 0


	SendText(str)

if __name__ == "__main__":
	thread.start_new_thread(ListenToSocket, ())

	while 1:
		Input(raw_input().rstrip())

