#!/usr/bin/python3
from Crypto.PublicKey import RSA
from Crypto.PublicKey import DSA
from Crypto.PublicKey import ECC
from Crypto.Hash      import SHA256
from Crypto.Hash      import MD5
from Crypto.Signature import DSS, pss
from Crypto.Random    import get_random_bytes
from Crypto.Cipher    import AES, PKCS1_OAEP


import binascii
import json
RSAkeylen = 3072
DSAkeylen = 3072

def getsignature(message, privkey, pemfile):		# sign a message providing either the privete key or the PEM file
        if pemfile:
           privkey=getprivatekey(pemfile)
        else:
           privkey = RSA.import_key(privkey)
        h  = SHA256.new(message)
        return(pss.new(privkey).sign(h))

def valsignature(message, signature, pubkey, pemfile):	# validate a signature providing either the private key or the PEM file
        if pemfile:
           pubkey=getpublickey(pemfile)
        else:
           pubkey = RSA.import_key(pubkey)
        h = SHA256.new(message)
        verifier = pss.new(pubkey)
        try:
           verifier.verify(h, signature)
           return (True)
        except ValueError:
           return (False)


def getfromencryptedfile(kfile, privkey):		# get the data form an encrypted file providing the private key
	with open(kfile, mode='rb') as keyfile:
     		data = keyfile.read()
	cipher_rsa = PKCS1_OAEP.new(privkey)
	return(cipher_rsa.decrypt(data))

def getprivatekey(pemfile):				# get the private key form a PEM file
	
	with open(pemfile,  mode='rb') as privatefile:
     		keydata = privatefile.read().decode('ascii').rstrip('\n')
	privkey = RSA.import_key(keydata)
	return(privkey)

def getpublickey(pemfile):				# get the public key from a PEM file
	with open(pemfile, mode='rb') as privatefile:
     		keydata = privatefile.read().decode('ascii').rstrip('\n')
	publkey = RSA.import_key(keydata)
	return(publkey)


def RSAgenkeypair(keylen):				# gen a RSA key pair public/private
	keyPair     = RSA.generate(keylen)
	pubKey      = keyPair.publickey()
	pubKeyPEM   = pubKey.exportKey()
	privKeyPEM  = keyPair.exportKey()
	return(pubKeyPEM.decode('ascii'), privKeyPEM.decode('ascii'))


	return(pubKeyPEM.decode('ascii'), privKeyPEM.decode('ascii'))

##########

def ECCgenkeypair():
	keyPair = ECC.generate(curve='P-256')
	pubKey  = keyPair.public_key()
	privKeyPEM = keyPair.export_key(format='PEM')
	publKeyPEM = pubKey.export_key(format='PEM')
	return(publKeyPEM, privKeyPEM)

##########
def DSAgenkeypair(DSAkeylen):
	keyPair    = DSA.generate(DSAkeylen)
	pubKey     = keyPair.publickey()
	pubKeyPEM  = pubKey.export_key()
	privKeyPEM = keyPair.export_key()
	return(pubKeyPEM.decode('ascii'), privKeyPEM.decode('ascii'))


##########
def RSAgenlistofkp(listofkp,limit,keylen=RSAkeylen):			# gen a list of key pairs
        idx=1
        while idx <= limit:
           kp=RSAgenkeypair(keylen)
           pubk=kp[0]
           prik=kp[1]
           #print (prik,"\n\n", pubk)
           kp={}
           kp['index']=str(idx)
           kp['private_key']=prik
           kp['public_key']=pubk
           listofkp.append(kp)
           idx += 1
        return(listofkp)
##########
def ECCgenlistofkp(listofkp,limit):
   idx=1
   while idx < limit:
      kp=ECCgenkeypair()
      pubk=kp[0]
      prik=kp[1]
      kp={}
      kp['index']=str(idx)
      kp['private_key']=prik
      kp['public_key']=pubk
      listofkp.append(kp)
      idx += 1
   return(listofkp)

##########
def DSAgenlistofkp(listofkp,limit, keylen=DSAkeylen):
   idx=1
   while idx < limit:
      kp=DSAgenkeypair(keylen)
      pubk=kp[0]
      prik=kp[1]
      #print (prik,"\n\n", pubk)
      kp={}
      kp['index']=str(idx)
      kp['private_key']=prik
      kp['public_key']=pubk
      listofkp.append(kp)
      idx += 1
   return(listofkp)
def MD5getdigest (message):
      h = MD5.new()
      h.update(message)
      return (h.hexdigest())

def SHAgetdigest (message):
      h = SHA256.new()
      h.update(message)
      return (h.hexdigest())

