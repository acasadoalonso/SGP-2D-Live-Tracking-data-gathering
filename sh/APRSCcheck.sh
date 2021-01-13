#!/bin/sh
pnum=$(pgrep aprsc)
if [ $? -ne 0 ] # if aprsc is  not running
then
 # restart aprsc
    logger -t $0 "aprsc seems down, restarting"
    sudo service aprsc start
    logger -t $0 $(pgrep aprsc) 
else
    logger -t $0 "aprsc seems up. "$(pgrep aprsc) 
fi

