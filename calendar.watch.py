#!/usr/bin/python3
# Look at gnome-calendar file and send msgbox for each event that is in the current window
# Usage: ./calendar.watch.py
# or: ./calendar.watch.py <filename>

import os
import sys
import time
import subprocess

from datetime import datetime as dada
from sd.common import DotDict, fmt_time, local_time



def convert(string):
    "Convert two types of timestring into utc"
    string = string.rstrip('Z').split('T')
    # print('\n\n', string)
    date = dada.strptime(string[0], '%Y%m%d')
    # print(date)
    ts = date.timestamp()
    if len(string) > 1:
        date = dada.strptime(string[1], '%H%M%S')
        # print(date)
        ts += (date - dada(1900, 1, 1)).seconds
    return int(ts)


class Event:
    "Event from calendar.ics"
    def __init__(self, data):
        self.data = data
        if data.dtstart:
            self.start = convert(data.dtstart)
            self.end = convert(data.dtend)
        else:
            self.start = convert(data.start)
            self.end = convert(data.end)
        self.triggered = False

    def msg(self,):
        subprocess.Popen(['sd/msgbox.py', self.data.summary])
        print('msg sent:', self.data.summary)
        self.triggered = True

    def print(self,):
        print(self.data.summary)
        print(self.start, local_time(self.start))
        print(self.end, local_time(self.end))
        print(self.data.uid)
        # print(self.data)

    def __eq__(self, other):
        return self.data == other.data

    def __repr__(self,):
        return self.data.summary


def parse_line(data, line):
    "Parse a line in calendar.ics for symbols and return value after symbol"
    symbols = {'LAST-MODIFIED:':'modified',
               'UID:':'uid',
               'DTSTART;VALUE=DATE:':'start',
               'DTSTART;TZID=':'start_flag',
               'DTEND;TZID=':'end_flag',
               'DTEND;VALUE=DATE:':'end',
               'SUMMARY:':'summary',
              }
    for key in symbols:
        if line.startswith(key):
            data[symbols[key]] = line.split(key)[1]
            return True
    return False


def read_calendar(path, events, modified):
    "Read calendar if the file has been modified and return True"

    if os.path.getmtime(path) > modified:
        print("\n\nCalendar Modified")
        modified = os.path.getmtime(path)
        seen_events = []
        with open(path) as f:
            data = DotDict()
            for line in f.readlines():
                line = line.strip()
                if parse_line(data, line):
                    continue
                if data.start_flag:
                    data.dtstart = line
                    del data.start_flag
                elif data.end_flag:
                    data.dtend = line
                    del data.end_flag
                elif line == 'END:VEVENT':
                    uid = data.uid
                    e = Event(data)
                    seen_events.append(uid)
                    if uid not in events:
                        print('\n\n')
                        e.print()
                    if uid in events and events[uid] == e:
                        print('Skipping existing event:', e)
                    else:
                        # Skip existing events
                        events[uid] = e
                    data = DotDict()

        # Remove events that no longer exist
        for uid in list(events.keys()):
            if uid not in seen_events:
                del events[uid]
        return modified
    return False


def next_event(events):
    "Scan events for the next timestamp coming up"
    upcoming = 0
    now = time.time()
    best = None
    for event in events.values():
        if not upcoming or event.start < upcoming:
            if event.end > now and not event.triggered:
                upcoming = event.start
                best = event
    if upcoming and upcoming > now:
        print('upcoming in', fmt_time(upcoming - now), ':', best)
    return upcoming


def trigger(events):
    "Send off messages"
    now = time.time()
    for event in events.values():
        if event.start <= now <= event.end and not event.triggered:
            event.msg()


def main():
    if sys.argv[1:]:
        path = sys.argv[1]
    else:
        path = os.path.join(os.path.expanduser('~'), '.local/share/evolution/calendar/system/calendar.ics')
    if not os.path.exists(path):
        print('Cannot find:', path)
        return False

    events = DotDict()      # uid -> Event
    modified = 0            # Last time calendar file was modified
    upcoming = 0            # timestamp of upcoming event
    while True:
        ret = read_calendar(path, events, modified)
        now = time.time()
        if ret:
            modified = ret
            print('\n\n')
            upcoming = next_event(events)
            if upcoming < now:
                trigger(events)
                upcoming = next_event(events)

        if upcoming and 0 < upcoming - now < 600:
            delay = upcoming - now + 1
            print("Sleeping", fmt_time(delay))
            time.sleep(delay)
            trigger(events)
        else:
            time.sleep(600)

if __name__ == "__main__":
    main()
