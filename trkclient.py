#!/usr/bin/python3
import socket
import signal
from telnetlib import *
from time import sleep
#########################################################################
# This script ins installed on the OGN station in order to send the status of the OGN trackers to the management server
#########################################################################

def signal_term_handler(signal, frame):
    print('got SIGTERM ... shutdown orderly')
    sock.close()
    sys.exit(0)


# ......................................................................#
signal.signal(signal.SIGTERM, signal_term_handler)
# ......................................................................#

server="CASADOUBUNTU.local"				# server to send the TRK status messages
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)# create the sock
errorc = 0
while errorc < 100:					# while not too many errors
	try:
		sock.connect((server, 50000))		# try to connect
		break
	except:
		if errorc > 100:
			exit(0)
			print ("Error connecting ...")
		sleep(5)
		errorc += 1

print("Socket connected to: ", server, ":", 50000)	# report that is connected
hostname = socket.gethostname()				# get the name of the OGN station
							# logon to OGN APRS network

login = 'L: user '+hostname+' vers V1.0'		# prepare the login message
login=login.encode(encoding='utf-8', errors='strict')	# convert it to bytes
sock.send(login)a					# send the login
data = sock.recv(1024)					# receive the reply
print('Received', repr(data))				# and report it

tn = Telnet('localhost', 50001)				# create the telent instance
station=':'
count=1
while True:						# for ever 
	try:
		r=tn.read_until(b'\n').decode('UTF-8')	# read char by char untile new line
	except KeyboardInterrupt:			# in case of Crtl-C close
		print("Keyboard input received, end of program, shutdown")
		print("Msgs sent:", count)
		sock.close()
		exit(0)
	except:						# any other error
		print("Msgs sent:", count)
		sock.close()
		exit(0)
	sdr=r.find(">OGNSDR")				# find the TCP/IP indicator
	if sdr > 0:					# if dound
		station=r[8:sdr]                	# get the OGN staion name
		print("S:", station, r[sdr+8:])		# report it
		continue				# keep reading chars
	khz=r.find('kHz')				# look if it is one of the lines that we need
	if khz == -1 :
		continue
	if r[khz+4:khz+6] != '3:':			# it is for a OGN tracker ???
		continue
	ident = r[khz+6:khz+12]				# get the ident
	rr= r[khz+13:]
	sc=rr.find(':')
	body=rr[sc+2:]
	msg="M:"+station+':'+ident+':'+body
	msg=msg.encode('utf-8')				# convert to bytes
	if station != ':':
		try:
			print ("<--", msg)
			sock.sendall(msg)		# send it to the management server
		except KeyboardInterrupt:		# if Ctrl-C 
			print("Keyboard input received, end of program, shutdown")
			print("Msgs sent:", count)
			sock.close()
			exit(0)
		except:
			print("Msgs sent:", count)
			sock.close()
			exit(0)
		count +=1
		data = sock.recv(1024)			# receive the ack
		#print('--> Received', repr(data), count)
		print('--> Received', data.decode('UTF-8'), count) # and report it
#########################################################################################################################
