#
# functions to handle the GitHub GIST facilities

#
import zlib
from base64 import urlsafe_b64encode as b64e, urlsafe_b64decode as b64d

def obscure(data: bytes) -> bytes:
    return b64e(zlib.compress(data, 9))

def unobscure(obscured: bytes) -> bytes:
    return zlib.decompress(b64d(obscured))
import requests
import json

GITHUB_API="https://api.github.com"			# the URL base
def geturlbyfilename(user, filename):			# get the GitHub GIST URL by filesname of given user
    req = requests.get(GITHUB_API+'/users/%s/gists' % user) # get the list
    r =req.json()					# convert the json data to dict
    for g in r:						# scan all the results
        files=g['files'] 				# get the files names
        if filename in files: 				# check thet the file is on the list
           filedata=files[filename]
           return(filedata['raw_url']) 			# return the URL
    return ("")

def getgistsid(urlraw, user):				# extract the gist ID from the URL

    p1=urlraw.find(user)+len(user)+1			# look for ht user
    p2=urlraw[p1:].find('/') 				# find te end if the glist id
    return (urlraw[p1:p1+p2])				# return the GIST ID


def updategist (user, filename, API_TOKEN, description, content):	# update a GIST in gitHub
    headers={'Authorization':'token %s'%API_TOKEN} 	# the authorization, use the API token
    params={'scope':'gist'}				# build the payload
    payload={"description": description,"public":True,"files":{filename:{"content":content}}}
    urlraw=geturlbyfilename(user, filename)		# get the URL using the file name for that user
    if urlraw != "":					# if found ???
       gist_id=getgistsid(urlraw, user)			# get the GIST ID
       url=GITHUB_API+"/gists/"+gist_id			# place it on the URL
       res=requests.patch(url,headers=headers,params=params,data=json.dumps(payload)) # and update
    else:
       #form a request URL				# if not create the GIST
       url=GITHUB_API+"/gists"				# set the URL
       res=requests.post(url,headers=headers,params=params,data=json.dumps(payload)) # create the GIST
    return (res)					# return the response
    
