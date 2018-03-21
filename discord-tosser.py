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

# Define our Discord Webhook URL's
discordHooks = {
    "announce": "https://discordapp.com/api/webhooks/360583927473111040/PaMUhckgEuqIyVAVLAywm1MpXZER0ou8aeJAvFcohNfp72gz_Cabe2wVJsUzs7CQjPTO",
    "phoenix": "https://discordapp.com/api/webhooks/360589282974498816/W2KdBwaquBDZOvs0fZZLCw09Z4axE2P1kzBg7mE8P9EEkans_EYZ7yY59wDM7w0mq5V7",
    "requests": "https://discordapp.com/api/webhooks/360594033833148416/DiF685mPHGewp1Si8CuszwEWEG58EmYnAS8_IYUMeD2W3faHkEXNzyTevugRRHiEqxWx",
    "bu": "https://discordapp.com/api/webhooks/361246798922121219/VwSpqaUopNXdlwbapDJXiMjmcubjaL-5423TYQ05oY3f6uUbXuPe3sguW3rVO_cXz2KH",
    "as": "https://discordapp.com/api/webhooks/361248219105329154/0HMaJ_tZLEf7V5zFR0qBhAbiKia0Flf0bSE_it0JMcmcRvhBO1vX3IFCT-2Nx4kUA5eQ",
    "eos": "https://discordapp.com/api/webhooks/361248777404940288/kAy20j6SdIoYzpbfDNEi1AhKWtoHaCU_xdyavKxafSUxLTO8xPFMRU3nP306PUkEitte",
    "burning": "https://discordapp.com/api/webhooks/361260772573315072/6QFGMcJG1pQ1Rm49zvZx72M57sgmYndBguc9SKg4tEO-9GOcV_IdmgbyhcFY5nRIxn1H",
    "rants": "https://discordapp.com/api/webhooks/373667490255077378/bqobZDF976tyWhqxn8jSmnmX9oolsbYBwaRrVd9cutb1TbONqr6qBY9yb_pzzcQkM8Kr",
    "media": "	https://discordapp.com/api/webhooks/373991743596789761/cKPNwuvUCZhUPeKaydkJshqhOfiR1HSBC8cOAbkNUJun11rnJam19kPrKuSt9x7EoOME",
    "unlikely": "https://discordapp.com/api/webhooks/377213149205626885/OQse51I970avHYxkzxLx86a4oRMAHQlcNJDpjp5z-Xa8-FL4izCKGAScIZkHmsp6_qDh",
    "founders": "https://discordapp.com/api/webhooks/408468333113901067/NdCwrCfvbvYbbggPZXqXO3BvS1bpvhxOuRaLlEZglf28pwUBqm32KuQvtNieDaQ8UZAY",
    "admin": "https://discordapp.com/api/webhooks/425469745463164929/efLpccqfO8M8hEt9UugDGHZt-oNtTb2AxlOH4OBUSgc2vnHtGoWZhBPwjZvhaQkRHZ2b"
}

# Define some group ID's
discordIDs = {
    "creative": "<@&367415080121532417>",
    "looking": "<@&363809658529644546>",
    "staff": "<@&244280246793142272>",
    "players": "<@&243867690068869120>",
    "eos": "<@&360905173612101632>",
    "bu": "<@&360904957932732417>",
    "as": "<@&360905351849181187>"
}


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