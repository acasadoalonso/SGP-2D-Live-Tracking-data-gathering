import socket
import signal
from telnetlib import *
from time import sleep
#########################################################################


def signal_term_handler(signal, frame):
    print('got SIGTERM ... shutdown orderly')
    sock.close()
    sys.exit(0)


# ......................................................................#
signal.signal(signal.SIGTERM, signal_term_handler)
# ......................................................................#

server="CASADOUBUNTU.local"
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
errorc = 0
while errorc < 100:
	try:
		sock.connect((server, 50000))
		break
	except:
		if errorc > 100:
			exit(0)
			print ("Error connecting ...")
		sleep(5)
		errorc += 1

print("Socket connected to: ", server, ":", 50000)
hostname = socket.gethostname()
					# logon to OGN APRS network

login = 'L: user '+hostname+' vers V1.0' 
login=login.encode(encoding='utf-8', errors='strict')
sock.send(login)
data = sock.recv(1024)
print('Received', repr(data))



tn = Telnet('localhost', 50001)
station=':'
count=1
while True:
	try:
		r=tn.read_until(b'\n').decode('UTF-8')
	except KeyboardInterrupt:
		print("Keyboard input received, end of program, shutdown")
		print("Msgs sent:", count)
		sock.close()
		exit(0)
	except:
		print("Msgs sent:", count)
		sock.close()
		exit(0)
	sdr=r.find(">OGNSDR")
	if sdr > 0:
		station=r[8:sdr]                
		print("S:", station, r[sdr+8:])
		continue
	khz=r.find('kHz')
	if khz == -1 :
		continue
	if r[khz+4:khz+6] != '3:':
		continue
	ident = r[khz+6:khz+12]
	rr= r[khz+13:]
	sc=rr.find(':')
	body=rr[sc+2:]
	msg="M:"+station+':'+ident+':'+body
	msg=msg.encode('utf-8')
	if station != ':':
		try:
			print ("<--", msg)
			sock.sendall(msg)
		except KeyboardInterrupt:
			print("Keyboard input received, end of program, shutdown")
			print("Msgs sent:", count)
			sock.close()
			exit(0)
		except:
			print("Msgs sent:", count)
			sock.close()
			exit(0)
		count +=1
		data = sock.recv(1024)
		#print('--> Received', repr(data), count)
		print('--> Received', data.decode('UTF-8'), count)

