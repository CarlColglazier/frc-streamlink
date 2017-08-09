import tbapy
import streamlink
from datetime import date
from datetime import datetime
from streamlink_cli.main import main
import sys
import os

# TODO: Have users generate this and save it to a config file.
KEY = "gEN1xmBqEzAUCaswA17nmryJLqCKlMSybW6EkG4AHw4WHt4QXRsnAF86KehFC0eY"
tba = tbapy.TBA(KEY)
NOW = datetime.combine(date.today(), datetime.min.time())

def active(start, end):
    """
    Returns true if the current date is between the start and end.
    """
    start_time = datetime.strptime(start, "%Y-%m-%d")
    end_time = datetime.strptime(end, "%Y-%m-%d")
    return start_time <= NOW <= end_time

def get_live_events():
    """
    Get the events which are currently being played.
    These are the ones that are most likely to have a stream.
    """
    status = tba.status()
    events = tba.events(status["current_season"])
    return [item for item in events if active(item.start_date, item.end_date)]

def format_link(stream):
    """
    Convert the JSON structure to a url.
    Currently supported:
    - twitch
    """
    if stream["type"] == "twitch":
        return "https://twitch.tv/{}".format(stream["channel"])
    return "https://{}.com/{}".format(stream["type"], stream["channel"])

def stream_list():
    """
    List the streams which are currently live.
    """
    i = 1
    events = get_live_events()
    if len(events) == 0:
        print("No streams currently online")
        sys.exit()
    for event in events:
        print("{:-2}. {:10} - {}".format(i, event.key, event.name))
        i += 1
    index = 0
    while index is 0:
        print("Select an event (ex: 1): ")
        selection = input()
        if 0 < int(selection) <= len(events):
            index = int(selection)
    event = events[index - 1]
    return [format_link(item) for item in event.webcasts]

if __name__ == "__main__":
    links = stream_list()
    for link in links:
        qualities = list(streamlink.streams(link))
        q = None
        while q is None:
            print("Select a stream quality: ")
            print(" ".join(qualities))
            i = input()
            if i in qualities:
                q = i
        print("streamlink {} {}".format(link, q))
        old_sys_argv = sys.argv
        sys.argv = [old_sys_argv[0]] + [link,q]
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
        main()
