#!/bin/bash

# If you have the 'tidy' program installed, uncomment lines 36 and 48 for a formattted output. 
# Tidy can be installed on ubuntu with 'sudo apt-get install tidy'

# If you want to get the button mode telemetry, use the Plus feed url instead - https://go.spidertracks.com/api/aff/feed/plus
URL="https://go.spidertracks.com/api/aff/feed"

# user and password should be you account details you use to log in to go.spidertracks.com. 
USER="acasado@acm.org"
PASSWORD="spider123"
# Identity should be your organisation or AFF feed name. This is not required, but is used to help with support enquiries. 
IDENTITY="Club de Planeadores de Vitacura"
# Change the "15 minutes ago" to suit as required
NOW=$(date --utc +"%Y-%m-%dT%H:%M:%SZ" --date "5 minutes ago")

BODY=$( cat <<EOF
<?xml version="1.0" encoding="UTF-8" ?>
<data xmlns="https://aff.gov/affSchema" sysId="$IDENTITY" rptTime="$NOW" version="2.23">
	<msgRequest to="Spidertracks" from="$IDENTITY" msgType="Data Request" subject="Async" dateTime="$NOW">
		<body>$NOW</body>
	</msgRequest>
</data>
EOF
)

echo "           ======= Details ======="
echo "URL: $URL"
echo "user: $USER"
echo "identity: $IDENTITY"
echo "Date: $NOW"
echo

echo "           ======= Request ======="

echo $BODY | tidy -xml -iq
echo

echo "           ======= Response ======="
curl $URL \
	-X POST \
	-s \
	-A "STL Curl Client" \
	-u "$USER":"$PASSWORD" \
	-H "Content-Type: application/xml" \
	-d "$BODY" \
	-s \
	-k | tidy -xml -iq -w 80
echo

