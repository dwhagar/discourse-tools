#!/usr/bin/env python3

import sys
import json
import subprocess
from dateutil.parser import parse

## TODO: Notification Types - 1 is an @Mention, 2 is a reply, 5 is a Like
## TODO: URL for notifications is notifications.js?api_key=blah&api_username=someone

if len(sys.argv) > 1:
    fileName = sys.argv[1]
else:
    fileName = 'discourse-notifier.json'

cfg = json.load(open(fileName))

base = cfg["base"]
key = cfg["key"]
defaultUser = cfg["user"]

# Define our URL values and API key / user to use.
curlCmd = ["curl", "-sX", "GET"]
curlPost = ["curl", "-s", "-X", "POST", "-d"]

def constructURL(call, userName = None):
    # Construct a call URL to retrieve information from the forum.
    if userName is None:
        userName = defaultUser

    auth = "?api_key=" + key + "&api_username=" + userName
    suffix = ".json" + auth
    return base + call + suffix

def getJSON(url):
    # Retrieve JSON data.
    curlList = curlCmd[:]
    curlList.append(url)
    rawOutput = subprocess.check_output(curlList)
    jData = json.loads(str(rawOutput, 'utf-8'))
    return jData

def getPushData(userName):
    # Gets any pushOver data from the system for a specific user.
    url = constructURL("/users/" + userName)
    userData = getJSON(url)

    # Get PushOver Keys
    userKey = userData["user"]["user_fields"]["3"]
    apiKey = userData["user"]["user_fields"]["4"]

    if (userKey is None) or (apiKey is None):
        data = None
    else:
        data = {
            "user":userName,
            "userKey":userKey,
            "apiKey":apiKey
        }

    return data

def getUsers():
    # Get a list of users.
    url = constructURL("/admin/users/list/active")
    userData = getJSON(url)
    users = []

    for user in userData:
        if user["username"] != "discobot" and user["username"] != "system":
            data = getPushData(user["username"])
            if not data is None:
                users.append(data)

    return users

def main():
    # Get all users who have PushOver data from the forum.
    users = getUsers()

    

    return 0

main()