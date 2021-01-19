#!/bin/sh
pnum=$(pgrep aprsc)
if [ $? -ne 0 ] # if aprsc is  not running
then
 # restart aprsc
    logger -t $0 "APRSC seems down, restarting"
    sudo service aprsc start
    sleep 5
    logger -t $0 "New APRSC: "$(pgrep aprsc) 
else
    logger -t $0 "APRSC seems up. "$(pgrep aprsc) 
fi

