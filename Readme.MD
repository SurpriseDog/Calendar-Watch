Not getting Evolution Gnome Calendar notifications on the desktop? Try this.

My script will automatically monitor the gnome-calendar database file for changes and send you a messagbox when events come up.


### Running

It should detect the calendar file automatically so you can just run the script with:

    ./calendar.watch.py

or you can point it at your `calendar.ics` file with:

    ./calendar.watch.py ~/.local/share/evolution/calendar/system/calendar.ics
