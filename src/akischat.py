#!/usr/bin/python

#-------------------------------------------------------------------------------------------------
# Name: Akiscode Chat
# Author: Stephen Akiki
# Website: http://akiscode.com
# Language: Python
# Usage: 
#	python akischat.py 
# Dependencies:
#	---
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
#    Thanks to Stephen Akiki (http://akiscode.com/code/chat) for peer-to-peer chat code
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

import os, thread, socket, traceback, urllib, sys, getopt

import RSA # Custom Lib

from struct import unpack

#-------------------CONSTANTS-------------------------

def usage():
	print 'Usage'

# This was going to be a wrapper function so we could use a GUI but the GUI idea fell through
#   and i'm to lazy to change it
def PrintToScreen(str):
	print str

LOCAL_IP = socket.gethostbyname(socket.gethostname()) # Gets local IP address

IP_ADDRESS_LIST = [] # Holds all the IP addresses

vlock = thread.allocate_lock() # Thread lock for IP_ADDRESS_LIST

NICKNAME_DICT = {LOCAL_IP:LOCAL_IP}

PORT = 7721 # Port to send packets on

DEBUG = 1


PrintToScreen('Making RSA Key...')
k = RSA.keygen(61, 53)
PubKey = (k[0], k[1])
PrivateKey = (k[0], k[2])

PubKey_OtherGuy = () # The public key of the other guy, initially set to 0
PubKey_string = k[3]

def toBytes(value):
	"Turns a string into a list of byte values"
	return unpack('%sB' % len(value), value)
	

def TupleToString(temp_tuple):
	temp_string = ''
	for k in temp_tuple:
		temp_string = temp_string + str(k) + '|' 
		
	return temp_string

def StringToTuple(string):
	temp_tuple = tuple(string.split('|'))
	temp_list = []
	for k in temp_tuple:
		if k == '':
			continue
		temp_list.append(int(k))
	
	return tuple(temp_list)
	
def sign(string):
	global PrivateKey
	ciphertext = []
	for temp in string:
		ciphertext.append(RSA.rsa(temp, PrivateKey, None))
	ciphertext_string = TupleToString(tuple(ciphertext))
	return ciphertext_string
	
def unsign(string):
	global PubKey_OtherGuy
	cleartext = ''
	tuple_string = StringToTuple(string)
	for temp in tuple_string:
		cleartext = cleartext + chr(RSA.rsa(temp, None, PubKey_OtherGuy, decrypt=True))
	return str(cleartext)

def encrypt(string):
	global PubKey_OtherGuy
	if len(PubKey_OtherGuy) == 0: 
		raise ValueError
	ciphertext = []
	for temp in string:
		ciphertext.append(RSA.rsa(temp, PubKey_OtherGuy, None))
	ciphertext_string = TupleToString(tuple(ciphertext))
	return ciphertext_string

def decrypt(string):
	global PrivateKey
	cleartext = ''
	tuple_string = StringToTuple(string)
	for temp in tuple_string:
		cleartext = cleartext + chr(RSA.rsa(temp, None, PrivateKey, decrypt=True))
	return str(cleartext)
		


def GetInput():
	data = raw_input().rstrip()
	return str(data)

# Used to print out info that I need during debugging.
def dbg(string):
	global DEBUG
	if DEBUG == 1:
		print '-----DEBUG-----: ' + str(string)
	else:
		pass



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
	global vlock
	global NICKNAME_DICT

	PrintToScreen(('Nick: '+NICKNAME_DICT[LOCAL_IP], 'Local IP:'+LOCAL_IP, 'Port:'+str(PORT), IP_ADDRESS_LIST))

	while 1:
		d = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		d.bind(('', PORT))
		while 1:
			data, addr = d.recvfrom(1024)
			if not data: break
			if not addr[0] in IP_ADDRESS_LIST and addr[0] != LOCAL_IP:
				vlock.acquire()  # Lock global list to not corrupt memory
				IP_ADDRESS_LIST.append(addr[0])
				NICKNAME_DICT[addr[0]] = addr[0]
				vlock.release() # Release lock
				SendSyncSuggestion()

			if data[:16] == r'\sync_suggestion':
				SyncRequest()
				PrintToScreen(NICKNAME_DICT[addr[0]] + ' has joined.')
				continue

			if data[:5] == r'\quit':
				vlock.acquire()
				IP_ADDRESS_LIST.remove(addr[0])
				del NICKNAME_DICT[addr[0]]
				vlock.release()
				

			if data[:13] == r'\sync_request':
				dbg('got sync request') # Debug Only
				SyncData()
				continue	

			if data[:10] == r'\sync_data':
				dbg('got sync data')
				TEMP_IP_ADDR_LIST = str(data[11:]).split('|')
				dbg(TEMP_IP_ADDR_LIST) # Debug Only
				for temp_ip in TEMP_IP_ADDR_LIST:
					if not temp_ip in IP_ADDRESS_LIST and temp_ip != LOCAL_IP:
						vlock.acquire()  # Lock global list to not corrupt memory
						IP_ADDRESS_LIST.append(temp_ip)
						vlock.release() # Release lock
				continue

			if data[:10] == r'\nick_data':
				dbg('got nick sync data')
				TEMP_NICKNAME_LIST = str(data[11:]).split(';')
				dbg('TEMP_NICKNAME_LIST = ' + str(TEMP_NICKNAME_LIST))
				for temp_nick in TEMP_NICKNAME_LIST:
					dbg('temp_nick = '+ temp_nick)
					small_list = temp_nick.split('|')
					dbg(small_list)
					dbg('key: ' + small_list[0] + 'value: ' + small_list[1])
					vlock.acquire() # lock thread access to variable
					NICKNAME_DICT[small_list[0]] = small_list[1] # IP Address key, actual value for values
					vlock.release() # release lock
				continue

			if data[:7] == r'\pubkey':
				global PubKey_OtherGuy, PubKey_string
				if len(PubKey_OtherGuy) != 0:
					continue
				PubKey_OtherGuy = tuple(map(int, data[8:-1].split(','))) # Take string and turn it into a tuple full of ints
				try:

					e = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
					e.sendto('\pubkey'+PubKey_string, (addr[0], PORT))
					e.close()
				except:
	
					dbg(str(('\pubkey'+ PubKey_string, addr[0], PORT)))
					PrintToScreen('Could not send Public Key to: ' + addr[0])
				continue				


			if data[:10] == r'\encrypted':
				try:
					data = decrypt(data[10:])
				except:
					PrintToScreen('Cannot decrypt message')
					if DEBUG == 1:
						traceback.print_exc()
					continue
				try:
					data = unsign(data)
				except:
					PrintToScreen('Cannot unsign message.  The message was most likely not sent by the person you think it is (Man in the Middle attack possible)')
					if DEBUG == 1:
						traceback.print_exc()
					continue
					
				PrintToScreen(NICKNAME_DICT[addr[0]] + '**: ' + str(data))

				continue

			PrintToScreen(NICKNAME_DICT[addr[0]] + ': ' + str(data))

		d.close()

def SendSyncSuggestion():
	SendText('\sync_suggestion')

def SyncRequest():
	SendText('\sync_request')

def SyncData():
	global IP_ADDRESS_LIST
	dbg(('\sync_data ' + '|'.join(IP_ADDRESS_LIST)))  # Debug Only
	SendText('\sync_data ' + '|'.join(IP_ADDRESS_LIST))
	dbg((r'\nick_data ' + ";".join(["%s|%s" % (k, v) for k, v in NICKNAME_DICT.items()])))
	SendText(r'\nick_data ' + ";".join(["%s|%s" % (k, v) for k, v in NICKNAME_DICT.items()]))



def Input(input_string):
	global LOCAL_IP
	global IP_ADDRESS_LIST
	global NICKNAME_DICT
	global vlock
	global PubKey
	global PubKey_string
	global PubKey_OtherGuy
	global PORT

	if input_string[:4] == r'\add':
		if not input_string[5:] in IP_ADDRESS_LIST and input_string[5:] != LOCAL_IP:
			vlock.acquire() # Lock global list to not corrupt memory
			IP_ADDRESS_LIST.append(input_string[5:])
			NICKNAME_DICT[input_string[5:]] = input_string[5:]
			vlock.release() # Release lock
			SendSyncSuggestion()
			return 0

	if input_string[:5] == r'\eadd': # Encrypted Add
		print '***Encrypted Mode***'
		print 'Sending _only_ to ' + input_string[6:] 
		try:
			d = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			d.sendto('\pubkey'+PubKey_string, (input_string[6:], PORT))
			d.close()
		except:

			dbg(str(('\pubkey'+ PubKey_string, input_string[6:], PORT)))
			PrintToScreen('Could not send to: ' + input_string[6:])
			print '***END Encrypted Mode***'
			return 0
		while 1:
			EInput = GetInput()
			try:
				EInput = sign(toBytes(EInput))
			except:
				PrintToScreen('Could not sign input')
				print '***END Encrypted Mode***'
				return 0
			try:
				EEInput = encrypt(toBytes(EInput))
			except ValueError:
				PrintToScreen('You have not received a public key from the person you are connecting.  You probably entered the IP address wrong')
				print '***END Encrypted Mode***'
				return 0
			except:
				PrintToScreen('Could not encrypt input')
				if DEBUG == 1:
					traceback.print_exc()
				print '***END Encrypted Mode***'
				return 0
				
			if EInput[:5] == r'\quit':
				PubKey_OtherGuy = ()
				print '***END Encrypted Mode***'
				return 0
			try:
				e = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
				e.sendto(r'\encrypted'+ EEInput, (input_string[6:], PORT))
				e.close()
			except:
				PrintToScreen('Could not send encrypted message to: ' + input_string[6:])
				if DEBUG == 1:
					traceback.print_exc()
				print '***END Encrypted Mode***'
				return 0
		return 0

	if input_string[:5] == r'\quit':
		SendText(NICKNAME_DICT[LOCAL_IP] + ' has quit.')
		sys.exit(1)
		return 0

	if input_string[:5] == r'\nick':
		if len(IP_ADDRESS_LIST) == 0:
			PrintToScreen('You need to connect to someone first')
		else:
			NICKNAME_DICT[LOCAL_IP] = input_string[6:]
			SendSyncSuggestion()

	if input_string[:3] == r'\ip': # Display all ip address you currently have
		PrintToScreen(IP_ADDRESS_LIST)
		return 0

	if input_string[:7] == r'\whoami': # Whats your IP address?
		PrintToScreen('Nick: ' + NICKNAME_DICT[LOCAL_IP] + ' Local IP: ' +LOCAL_IP)
		print NICKNAME_DICT

	SendText(input_string)



def MakeMainMenu():
	global LOCAL_IP
	root = Tk()
	root.title(title + '(' + versionstring + ') - Stephen Akiki')
	root.minsize(500, 400)

	w = Label(root, text=LOCAL_IP)
	w.grid(row=0)


	root.mainloop()

if __name__ == "__main__":
	thread.start_new_thread(ListenToSocket, ())
	while 1:
		Input(GetInput())
		

