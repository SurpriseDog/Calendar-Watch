#!/usr/bin/python3
# Send messages to the user in GUI space

import os
import sys
import time
import shutil
import subprocess
from importlib.util import find_spec
# Must be a standalone script to work with gc.py



# Import PyQt and fallback on tkinter otherwise
if find_spec("PyQt5"):
    import PyQt5.QtCore as qcore
    import PyQt5.QtWidgets as qwidgets
    import PyQt5.QtGui as qgui

elif find_spec("tkinter"):
    import tkinter as tk
else:
    print("Unable to import PyQt5 or tkinter")
    print("Please install with: pip3 install PyQt5 tkinter")


def quote(text):
    "Wrap a string in the minimum number of quotes to be quotable"
    for q in ('"', "'", "'''"):
        if q not in text:
            break
    else:
        return repr(text)
    if "\n" in text:
        q = "'''"
    return q + text + q



################################################################################


def notify(*text):
    '''Use notify send to send a transient message
    uid = User ID Example: 1000'''
    cmd = ['notify-send', quote(' '.join(text))]
    return subprocess.run(cmd, check=False).returncode


def popup(*text, question=False, timeout=99999999):
    '''Popup a text or question in userland and return True if click okay.
    True  = Accept
    False = Reject
    Other = Return Code'''
    text = ' '.join(text)
    if question:
        cmd = "zenity --question --timeout=" + str(timeout)
    else:
        cmd = "zenity --info --timeout=" + str(timeout)

    cmd = cmd.split() + ['--text=' + text]
    print(cmd)
    return subprocess.run(cmd, check=False).returncode


def tk_box(msg, wrap=640, title='Info'):
    "Messagebox with tkinter"
    root = tk.Tk()
    root.title(title)
    lbl = tk.Label(root, font=("Arial", 12), text=msg, wraplength=wrap)
    lbl.pack(padx=10, pady=20)
    button = tk.Button(root, text="Okay", command=root.destroy, width=10, font=("Arial", 12))
    button.pack(pady=10, padx=40)
    root.update()
    root.lift()
    time.sleep(len(msg)/64)
    root.mainloop()


def pqbox(msg, wrap=640, title='Info', margin=20):
    "Messagebox with PyQt"
    if "QT_LOGGING_RULES" not in os.environ:
        os.environ["QT_LOGGING_RULES"] = "qt5ct.debug=false"

    app = qwidgets.QApplication(sys.argv)
    window = qwidgets.QWidget()
    window.resize(wrap + margin * 2, 200)
    window.move(app.desktop().screen().rect().center() - window.rect().center())

    label = qwidgets.QLabel(window)
    font = qgui.QFont()
    font.setFamily("Arial")
    font.setPointSize(14)
    label.setFont(font)

    label.move(margin, margin)
    label.setFixedWidth(wrap)
    label.setWordWrap(True)
    label.setAlignment(qcore.Qt.AlignCenter)
    label.setText(msg)
    label.adjustSize()      # Do this or the .height() will be wrong
    # txtsize = label.fontMetrics().boundingRect(label.text())
    # lbl_height = math.ceil(txtsize.width() / wrap) * txtsize.height()
    # print(lbl_height, label.height())

    button = qwidgets.QPushButton(window)
    button.setText("Okay")
    button.clicked.connect(app.quit)

    pos = window.rect().center() - button.rect().center()
    button.move(pos.x(), label.y() + label.height() + margin)
    window.resize(window.width(), button.y() + button.height() + margin)

    window.setWindowTitle(title)
    window.show()
    app.exec_()


def msgbox(*args, wrap=640, throwerr=False):
    '''
    Popup message box, requires PyQT, tkinter or zenity.
    Guaranteed not to break, even if third party libraries not installed.
    returns False if message was not delivered to desktop
    '''
    msg = ' '.join(list(map(str, args)))

    if "PyQt5" in sys.modules:
        pqbox(msg, wrap)

    elif "tkinter" in sys.modules:
        tk_box(msg, wrap)


    elif shutil.which('zenity'):
        cmd = ['zenity', '--width', str(len(msg)*10), '--info', '--timeout=99999999', '--text='+quote(msg)]
        ret = subprocess.run(cmd, check=False)
        return not bool(ret.returncode)


    else:
        print("\nInstall PyQt5, tkinter or zenity to get this message on the desktop:")
        print(msg)
        if throwerr:
            raise ValueError("Cannot show msgbox")
        return False

    return True




################################################################################
if __name__ == "__main__":
    MSG = ' '.join(sys.argv[1:])
    msgbox(MSG)
