#!/usr/bin/python3
import rsa
import argparse
from Keys import *

DK=[]
print ("\nGenerate the files for OGNdecode program")
print ("========================================\n")
pgmver='V1.0'
parser = argparse.ArgumentParser(description="OGN Generate the encrypting keys for OGNDECODE")
parser.add_argument('-p',  '--print',  required=False, dest='prt',   action='store', default=False)
parser.add_argument('-ke', '--keyencrypt',  required=False, dest='keyencrypt', action='store', default="keyfile.encrypt")
parser.add_argument('-k',  '--keyfile',   required=False, dest='keys',  action='store', default="keyfile")

# --------------------------------------#
args  = parser.parse_args()
prt   = args.prt
keyfileencrypted = args.keyencrypt
keyfilename      = args.keys

# --------------------------------------#

#
privkey = getprivatekey('keypriv.PEM')
publkey = getpublickey('keypubl.PEM')
key=getkeyfile(keyfilename)
print ("Orig Key from file:     ", key)
signature=getsignature(key,'keypriv.PEM')
print ("Signature:              ", signature)
DK=getkeys(DK,key)
print ("HEXGet keys:            ", DK) 
for h in DK:
    print (hex(h))
DECKEY = getdeckey(keyfilename)
i=0
while i < len(DECKEY):
   kk= DECKEY[i:i+1]
   print (kk)
   i += 1
print ("DecKey to use:          ", DECKEY.decode('utf-8'), "Length:",  len( DECKEY.decode('utf-8')))
# RSA tests
crypto=rsa.encrypt(key, publkey)
print ("DecKey encrypted:       ",crypto, "\n\n")

with open(keyfileencrypted, mode='wb') as keyfile:
     keyfile.write(crypto)

print ("Decrypted Key:          ", rsa.decrypt(crypto, privkey))
k2=getkeyfromencryptedfile(keyfileencrypted, privkey)
print ("Key back from file:     ", k2)
print ("The KEY is:             ", rsa.verify(k2, signature, publkey))
print ("DecKey to use:          ", DECKEY)
