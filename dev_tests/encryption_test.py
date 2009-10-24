#!/usr/bin/python

import RSA, traceback, sys

from struct import unpack

def toBytes(value):
	"Turns a string into a list of byte values"
	return unpack('%sB' % len(value), value)

print('Making RSA Key...')
k = RSA.keygen(61, 53)
PubKey = (k[0], k[1])
PrivateKey = (k[0], k[2])

PubKey_OtherGuy = (k[0], k[1]) # The public key of the other guy, initially set to 0
PubKey_string = k[3]

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
	global PubKey
	#if len(PubKey_OtherGuy) == 0: 
	#	raise ValueError
	ciphertext = []
	for temp in string:
		ciphertext.append(RSA.rsa(temp, PubKey, None))
	ciphertext_string = TupleToString(tuple(ciphertext))
	return ciphertext_string

def decrypt(string):
	global PrivateKey
	cleartext = ''
	tuple_string = StringToTuple(string)
	for temp in tuple_string:
		cleartext = cleartext + chr(RSA.rsa(temp, None, PrivateKey, decrypt=True))
	return str(cleartext)
		



regular_string = 'hi there'
try:
	signed_string = sign(toBytes(regular_string))
	print 'Signed String :', signed_string
	encrypted_string = encrypt(toBytes(signed_string))
	print 'Encrypted String :', encrypted_string
except:
	traceback.print_exc()
	sys.exit(1)

try:
	decrypted_string = decrypt(encrypted_string)
	print 'Decrypted String :', decrypted_string
	unsigned_string = unsign(decrypted_string)
	print 'Unsigned string :', unsigned_string
	
except:
	PrintToScreen('You didnt get a Public Key from the "other guy"')
	

	
print unsigned_string

import os

os.system("pause")
