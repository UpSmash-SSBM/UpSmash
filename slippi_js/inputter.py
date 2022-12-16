from tkinter import *
from tkinter import filedialog
from flask import Flask, render_template, request
import socket
import os

SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 4096 # send 4096 bytes each time step
host = "192.168.1.101"
# the port, let's use 5001
port = 5001

def callback():
    # function using allows the user to pick a file of filetype
    filename = filedialog.askopenfilename(initialdir = '/', title = 'Select a File',filetypes = (('Slippi files','*.slp*'),('all files','*.*')))
    label_file_explorer.configure(text='File Opened: '+ filename)
    # this will send the slp file to Flask
    filesize = os.path.getsize(filename)
    # create the client socket
    s = socket.socket()
    print(f"[+] Connecting to {host}:{port}")
    s.connect((host, port))
    print("[+] Connected.")
    # send the filename and filesize
    s.send(f"{filename}{SEPARATOR}{filesize}".encode())

root = Tk() 
root.title('Melee Stat Tracker')
root.geometry('900x600')
bg = PhotoImage(file = os.path.dirname(__file__) + '\\fixtures\SSBU-Pokémon_Stadium.png')
label1 = Label(root, image = bg, anchor=CENTER)
label1.place(x = 0, y = 0)
label_file_explorer = Label(root, width = 65, height = 2, fg = 'white', bg = 'gray')
button_browse = Button(root, text = 'Browse', command = callback)
button_exit = Button(root, text = 'Exit', command = exit)

# place the buttons where they need to go
label_file_explorer.place(x = 315, y= 300, anchor = CENTER)
button_browse.place(x = 600, y = 290, anchor = CENTER)
button_exit.place(x = 600, y = 315, anchor = CENTER)

# keep the window open
root.mainloop()
#newlabel = root.Label(test = "Upload Slippi .SLP: ")
