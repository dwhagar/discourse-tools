#!/usr/bin/env python3

import sys
import json
import subprocess
from dateutil.parser import parse

# Define our URL values and API key / user to use.
curlCmd = "curl -sX GET "
curlPost = "curl -s -X POST -d "

base = "https://forum.moltenaether.com"
key = "b8dce6591ad59c414ef7bd6a03eb0030fc3c7677f63e54dd5b74fd561f6285b8"
user = "cyclops"
auth = "?api_key=" + key + "&api_username=" + user
suffix = ".json" + auth

def getJSON(curlString):
    # Retrieve JSON data.
    curlList = curlString.split()
    rawOutput = subprocess.check_output(curlList)
    jData = json.loads(str(rawOutput, 'utf-8'))
    return jData

def main():

    return 0

main()