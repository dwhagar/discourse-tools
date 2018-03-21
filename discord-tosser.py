#!/usr/bin/env python3

import sys
import json
import subprocess
from dateutil.parser import parse

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

# Define our URL values and API key / user to use.
curlCmd = "curl -sX GET "
curlPost = "curl -s -X POST -d "

auth = "?api_key=" + key + "&api_username=" + user
suffix = ".json" + auth


def getJSON(curlString):
    # Retrieve JSON data.
    curlList = curlString.split()
    rawOutput = subprocess.check_output(curlList)
    jData = json.loads(str(rawOutput, 'utf-8'))
    return jData


def getCategory(topicID):
    # Initialize our return value.
    catName = "Uh..."

    # Get the topic's category ID
    curlTopic = curlCmd + base + "/t/" + str(topicID) + suffix
    topicData = getJSON(curlTopic)
    catID = topicData["category_id"]

    # Get the data on all categories.
    curlCategory = curlCmd + base + "/site" + suffix
    catList = getJSON(curlCategory)
    catData = catList["categories"]
    for cat in catData:
        if cat["id"] == catID:
            catName = cat["name"]
            break

    return catName


def buildMessage(sendPing, pingID, pingMsg, postedBy, postedTo):
    # Helps to build messages for posting to Discord
    if sendPing:
        if pingID is None:
            message = pingMsg
        else:
            message = pingID + pingMsg
    else:
        message = "A reply has been posted by "

    message = message + postedBy + " to " + postedTo + " UTC."
    message = message.replace("  ", " ")

    return message


def main():
    # There should never be more than just the one line, but just in case it is
    # going to be stored in memory anyway, save time later.

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

    if jsonData["deleted_at"] != "nil":
        wasDeleted = True
    if (jsonData["updated_at"] != jsonData["created_at"]) and (jsonData["post_number"] > 1):
        wasEdited = True
    if jsonData["cooked"] == "":
        noText = True

    if not (wasDeleted or wasEdited or noText):
        name = getCategory(jsonData["topic_id"])
        postURL = base + "/t/" + jsonData["topic_slug"] + "/" + str(jsonData["topic_id"]) + "/" + str(
            jsonData["post_number"])
        message = "Uh..."

        if jsonData["post_number"] == 1:
            sendPing = True
        else:
            sendPing = False

        postedDate = parse(jsonData["updated_at"])

        if jsonData["name"] == "":
            postedBy = jsonData["username"]
        else:
            postedBy = jsonData["name"] + " (" + jsonData["username"] + ")"

        postedTo = jsonData["topic_title"] + " on " + postedDate.strftime("%l:%M%p on %A, %B %d, %Y")

        if name == "News and Announcements":
            message = buildMessage(sendPing, discordIDs["players"],
                                   ", a new announcement has been posted by ",
                                   postedBy,
                                   postedTo)
            hookURL = discordHooks["announce"]
        elif name == "Angelic Sins":
            message = buildMessage(sendPing, discordIDs["as"],
                                   ", a topic has been started by ",
                                   postedBy,
                                   postedTo)
            hookURL = discordHooks["as"]
        elif name == "Blazing Umbra":
            message = buildMessage(sendPing, discordIDs["bu"],
                                   ", a topic has been started by ",
                                   postedBy,
                                   postedTo)
            hookURL = discordHooks["bu"]
        elif name == "Embers of Soteria":
            message = buildMessage(sendPing, discordIDs["eos"],
                                   ", a topic has been started by ",
                                   postedBy,
                                   postedTo)
            hookURL = discordHooks["eos"]
        elif name == "Phoenix Nebula":
            message = buildMessage(sendPing, discordIDs["creative"],
                                   ", a topic has been started by ",
                                   postedBy,
                                   postedTo)
            hookURL = discordHooks["phoenix"]
        elif name == "Rants":
            message = buildMessage(sendPing, None,
                                   "A topic has been started by ",
                                   postedBy,
                                   postedTo)
            hookURL = discordHooks["rants"]
        elif name == "Media":
            message = buildMessage(sendPing, None,
                                   "A topic has been started by ",
                                   postedBy,
                                   postedTo)
            hookURL = discordHooks["media"]
        elif name == "Staff":
            message = buildMessage(sendPing, discordIDs["staff"],
                                   ", a topic has been started by ",
                                   postedBy,
                                   postedTo)
            hookURL = discordHooks["admin"]
        elif name == "Requests":
            message = buildMessage(sendPing, discordIDs["looking"],
                                   ", a topic has been started by ",
                                   postedBy,
                                   postedTo)
            hookURL = discordHooks["requests"]
        elif name == "Founders Hall":
            message = buildMessage(sendPing, None,
                                   "A topic has been started by ",
                                   postedBy,
                                   postedTo)
            hookURL = discordHooks["founders"]
        elif name == "Characters":
            message = buildMessage(sendPing, discordIDs["staff"],
                                   ", a new character bio has been posted by ",
                                   postedBy,
                                   postedTo)
            hookURL = discordHooks["phoenix"]
        elif name == "Unlikely Kingdoms":
            message = buildMessage(sendPing, discordIDs["players"],
                                   ", a topic has been started by ",
                                   postedBy,
                                   postedTo)
            hookURL = discordHooks["unlikely"]
        else:
            hookURL = ""

        if hookURL == "":
            return 1

        message = message + " " + postURL

        postList = curlPost.split()
        postList.append('{"content": "' + message + '"}')
        postList.append("-H")
        postList.append("Content-Type: application/json")
        postList.append(hookURL)
        rawOutput = subprocess.check_output(postList)
        print(rawOutput)

        return 0

main()