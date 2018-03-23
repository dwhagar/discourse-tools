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

After a considerable amount of work, this is finally finished.  The system makes a call for each individual user after
getting a user list, and it makes them all at once.  Playing with it for testing, I discovered that I hit the rate
limit.  Thus, some kind of throttling might need to be installed in the script.

Currently, the script can be run as a cron job, with the json file containing the API key and the default user that
admin calls (user list, etc) should be made with.  It relies on two custom user fields one for the Pushover User Key
and the other for the PushOver Application Key (also called an App Token or API Key).  This is to be configured by the
user.  Since I built this for myself, and I already had 2 custom fields, the fields for me are entries 2 and 3 in the
user information json output.  It is an array, so starts at index 0, thus would need to be adjusted.

I plan to add a lot of these as settings in the configuration json file, which is why there is no example up yet.

A large forum will, of course, take longer to run, for mine it takes about 5 seconds to go through all of my user
information, and most of that is getting each individual user's API information, it builds a list from that of users
who can receive push notifications and then only checks those users who have said information for their notification
data.

It ignores all entries that have been seen by the script (data is stored in a file under `data/username.last`)
as well as any that have not been seen by the script but are marked as seen by Discourse, this should allow for no
duplicate notifications to happen.  So far, since my forum is small, I don't hit the rate limit on normal usage, I have
the script running every 5 minutes for me.  However, the default rate limit is 60, I only have like around 40 users and
thus I will probably be adding some sort of rate limiting so the script pauses after 50 requests or some configurable
number, but that isn't included yet.