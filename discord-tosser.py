#!/usr/bin/env python3

import sys
import json
import os
import requests
from dateutil.parser import parse

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

if len(sys.argv) > 1:
    fileName = sys.argv[1]
else:
    fileName = 'discord-tosser.json'

cfg = json.load(open(fileName))

base = cfg["base"]
key = cfg["key"]
user = cfg["user"]

discordHooks = {}
discordIDs = {}

for hook in cfg["hook-urls"]:
    discordHooks[hook["name"]] = hook["url"]

for uid in cfg["ids"]:
    discordIDs[uid["name"]] = uid["id"]

auth = "?api_key=" + key + "&api_username=" + user
suffix = ".json" + auth

def getJSON(url):
    # Retrieve JSON data.
    getRequest = requests.get(url)
    if getRequest.status_code == 200 and getRequest.json() != {}:
        jData = getRequest.json()
    else:
        with open("logs/tosser-errors.txt", 'w') as f:
            print(getRequest.status_code, getRequest.text, file=f)
        jData = {}

    return jData

def getCategory(topicSlug, topicID):
    # Initialize our return value.
    catName = "Uh..."

    # Get the topic's category ID
    topicURL = base + "/t/" + topicSlug + "/" + str(topicID) + suffix
    topicData = getJSON(topicURL)
    catID = topicData["category_id"]

    # Get the data on all categories.
    siteURL = base + "/site" + suffix
    catList = getJSON(siteURL)
    catData = catList["categories"]
    for cat in catData:
        if cat["id"] == catID:
            catName = cat["name"]
            break

    return catName

def main():
    # There should never be more than just the one line, but just in case it is
    # going to be stored in memory anyway, save time later.

    if not os.path.isdir("logs"):
        os.makedirs("logs")

    data = []

    for line in sys.stdin:
        stringData = line
        stringData = stringData.replace("=>", ":")
        stringData = stringData.replace("nil", "\"nil\"")
        data.append(json.loads(stringData))

    if len(data) == 0:
        return 1

    jsonData = data[0]

    # Now to make some decisions on what to do.
    wasDeleted = False
    wasEdited = False
    noText = False
    autoLocked = False

    if jsonData["deleted_at"] != "nil":
        wasDeleted = True
    if jsonData["updated_at"] != jsonData["created_at"]:
        wasEdited = True
    if jsonData["cooked"] == "":
        noText = True
    if jsonData["cooked"].find("topic was automatically closed") > -1:
        autoLocked = True

    if not (wasDeleted or wasEdited or noText or autoLocked):
        name = getCategory(jsonData["topic_slug"], jsonData["topic_id"])
        postURL = base + "/t/" + jsonData["topic_slug"] + "/" + str(jsonData["topic_id"]) + "/" + str(
            jsonData["post_number"])

        if jsonData["post_number"] == 1:
            isReply = False
        else:
            isReply = True

        postedDate = parse(jsonData["updated_at"])

        if jsonData["name"] == "":
            postedBy = jsonData["username"]
        else:
            postedBy = jsonData["name"] + " (" + jsonData["username"] + ")"

        postedTo = jsonData["topic_title"] + " at " + postedDate.strftime("%l:%M%p on %A, %B %d, %Y")

        for topic in cfg["discourse-map"]:
            if name == topic["name"]:
                if topic["tag"] is None:
                    sendPing = False
                else:
                    sendPing = True

                if not isReply:
                    if sendPing:
                        message = discordIDs[topic["tag"]] + ", a new message was posted by "
                    else:
                        message = "A new message was posted by "
                else:
                    message = "A reply has been posted by "

                message = message + postedBy + " to " + postedTo + " UTC."
                message = message.replace("  ", " ")
                message = message.replace(" .", ".")

                if not (topic["hook"] is None or topic["hook"] == ""):
                    hookURL = discordHooks[topic["hook"]]
                    message = message + " " + postURL

                    data = {"content":message}

                    if len(message) > 0:
                        r = requests.post(hookURL, json=data)
                        with open("logs/tosser-log.txt", 'w') as f:
                            print(r.status_code, r.text, file=f)

                    return 0

                else:
                    return 1

    return 0

main()