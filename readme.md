# discourse-tools

This project is simply a collection of various tools that I use with my discourse server.  There is nothing terribly
there is nothing terribly special about them other than the fact that I figured someone else might find them useful in 
some way.  The codes is badly commented and I'm horribly and documenting.

I also don't pretend that this is the best way to do these things, I use python a lot because I know it and it is
fairly easy for me to code in, thus that's what I use.  Please feel free to use what you find here or not.

## discord-tosser.py

This utility is designed to take data from Huginn via stdin, in the form of the JSON data from a webhook pushed event,
Huginn receives from Discourse and then sends to this script to process, the script then decides if the event should
get pushed out to Discord and which webhook to use, and other things like how to format the message.

The system uses the curl command rather than the library, mainly because I could test curl out via the command line
during testing, which made things easier for me during testing.

I will likely be refining the script as time goes on and it is not fully tested at the time of this commit, use with
caution.  The script could, I'm sure, be altered to take information from an http post request itself, but I frankly
don't know how to do that, hence Huginn receives the request, does minimal processing, and then executes the script.

## discourse-notifier.py

This is as yet to be written, my objective will be to use the Discoruse API to poll the forum for changes and then send
notifications out as needed, probably via PushOver, since that is what I personally use.