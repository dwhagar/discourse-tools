#!/usr/bin/env python3

import sys
import json
import subprocess
import os
import html

# Pull notification data from the system.
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

if len(sys.argv) > 1:
    fileName = sys.argv[1]
else:
    fileName = 'discourse-notifier.json'

cfg = json.load(open(fileName))

base = cfg["base"]
key = cfg["key"]
defaultUser = cfg["user"]
siteName = cfg["name"]

# Define our URL values and API key / user to use.
curlCmd = ["curl", "-sX", "GET"]
curlPost = ["curl", "-sH", "Content-Type: application/json", "-X", "POST", "-d"]
pushURL = "https://api.pushover.net/1/messages.json"

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

def getNotifications(userName):
    # Get current notifications for a user.
    url = constructURL("/notifications", userName)
    noticeData = getJSON(url)["notifications"]
    return noticeData

def getUsers():
    # Get a list of users, pull PushOver API data and grab notifications.
    url = constructURL("/admin/users/list/active")
    userData = getJSON(url)
    users = []

    for user in userData:
        if user["username"] != "discobot" and user["username"] != "system":
            data = getPushData(user["username"])
            if not data is None:
                data["notices"] = getNotifications(user["username"])
                users.append(data)

    return users

def main():
    # Get all users who have PushOver data from the forum.
    users = getUsers()

    # Make sure the data directory exists.
    if not os.path.isdir("data"):
        os.makedirs("data")

    if not os.path.isdir("logs"):
        os.makedirs("logs")

    for user in users:
        userFile = "data/" + user["user"] + ".last"
        userLog = "logs/" + user["user"] + ".log"

        # Establish which notice has last been sent.
        if not os.path.exists(userFile):
            lastNotice = 0
        else:
            with open(userFile) as f:
                lastNotice = int(next(f))

        # Built a list of notices to send out
        toSend = []

        for notice in user["notices"]:
            if (not notice["read"]) and (int(notice["id"]) > lastNotice):
                toSend.append(notice)

        # Update the last seen notification
        if len(user["notices"]) > 0:
            lastNotice = int(user["notices"][0]["id"])
            with open(userFile, 'w') as f:
                print(lastNotice, file=f)

        # Prepare to actually send out the notifications
        pushMessages = []

        if len(toSend) > 0:
            toSend = list(reversed(toSend))

            push = {}

            for notice in toSend:
                if notice["notification_type"] == 1: # Mention
                    push["message"] = "You were mentioned in " + notice["data"]["topic_title"] + " by " + notice["data"][
                        "display_username"] + "."
                elif notice["notification_type"] == 2 or notice["notification_type"] == 9: # Reply
                    push["message"] = "A reply to " + notice["data"]["topic_title"] + " was posted by " + notice["data"][
                        "display_username"] + "."
                elif notice["notification_type"] == 3: # Quoted
                    push["message"] = "You were quoted in " + notice["data"]["topic_title"] + " by " + notice["data"][
                        "display_username"] + "."
                elif notice["notification_type"] == 5: # Like
                    push["message"] = "Your post in " + notice["data"]["topic_title"] + " was liked by " + notice["data"][
                        "display_username"] + "."
                elif notice["notification_type"] == 6: # Private Message
                    push["message"] = "You received a private message from " + notice["data"]["display_username"]\
                                      + " called " + notice["data"]["topic_title"] + "."
                else:
                    push["message"] = None

                if not (push["message"] is None):
                    push["message"] = html.unescape(push["message"])
                    push["title"] = html.unescape(siteName + " : " + notice["data"]["topic_title"])
                    push["url"] = base + "/t/" + notice["slug"] + "/" + str(notice["topic_id"]) + "/" + str(notice["post_number"])
                    push["url_title"] = html.unescape(notice["data"]["topic_title"])
                    push["token"] = user["apiKey"]
                    push["user"] = user["userKey"]

                    pushString = json.dumps(push)
                    pushMessages.append(pushString)

        # Actually transmit the push notifications.
        if len(pushMessages) > 0:
            for message in pushMessages:
                curlFinal = curlPost[:]
                curlFinal.append(message)
                curlFinal.append(pushURL)
                rawOutput = subprocess.check_output(curlFinal)
                with open(userLog, 'w') as f:
                    print(rawOutput, file=f)

    return 0

main()