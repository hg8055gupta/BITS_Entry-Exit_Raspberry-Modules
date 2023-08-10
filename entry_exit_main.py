import tkinter.font as tkFont
from tkinter import *
from PIL import ImageTk, Image
import tkinter.messagebox as tkMessageBox
from tktimepicker import AnalogPicker, AnalogThemes
import pickle
import os
import subprocess
from imutils import paths
import cv2
from pymongo import MongoClient
import pprint
from tkcalendar import *
import time
import datetime
from datetime import date as dt
from reportlab.pdfgen import canvas
from fpdf import FPDF
import pyqrcode
import png
import json
from escpos import *
from subprocess import call
from time import sleep
import pandas as pd
import requests
import urllib.request
import glob

client = MongoClient('localhost', 27017)
db = client.test
currentIdDB = db.currentId

root = Tk()
root.title("BITS Entry Exit System")

width = 640
height = 600
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width/2) - (width/2)
y = (screen_height/2) - (height/2)
root.geometry("%dx%d+%d+%d" % (width, height, x, y))

root.resizable(0, 0)

cwd = os.getcwd()

#=======================================VARIABLES=====================================
ADD_USERNAME = StringVar()
ADD_ID = StringVar()
ADD_DESTINATION = StringVar()
ADD_CONTACT_NO = StringVar()
ADD_VEHICLE_NO = StringVar()
ADD_IN_TIME = ""
ADD_EXPECTED_OUT_TIME = ""
ADD_PURPOSE_OF_VISIT = StringVar()
ADD_VISITOR_RELATION = StringVar()
DEL_ID = StringVar()
DEL_EXPECTED_OUT_TIME = ""
SEARCH_INPUT = StringVar()
SEARCH_FIELD = StringVar()
SearchCheckBoxInput = IntVar()
GenerateReportEntry = StringVar()
printpassContact = StringVar()
markexitContact = StringVar()
current_frame = Frame()
allUsers = {}
inUsers = {}
allUserList = []
searchedUserList = []
inUserList = []
currentId = {}
exitUserId = {}
exitUser = {}
entryUser = {}
lmain = None
qr_detected = False
cap = None
qr = ""
cancel = False
output = ""
image = Image.open(cwd + "/BITS-Pilani-Logo.png")
image2 = image.resize((100,100),Image.ANTIALIAS)
img = ImageTk.PhotoImage(image2)
connectApi = "http://172.20.10.3:8000/api"
imgBaseUrl = "http://172.20.10.3:8000/images"

#=======================================METHODS=======================================
def MainMenu():
	global current_frame, lbl_result1, cwd
	current_frame = Frame(root)
	panel = Label(current_frame, image = img)
	panel.grid(row=0,column=0)
	btn_show_users = Button(current_frame, text="Show All Users", font=('arial', 15), width=35, command=ToggleToShowAllUsers)
	btn_show_users.grid(row=2, pady=12)
	btn_show_users = Button(current_frame, text="Show Users Inside", font=('arial', 15), width=35, command=ToggleToShowInUsers)
	btn_show_users.grid(row=3, pady=12)
	btn_add_users = Button(current_frame, text="Entry", font=('arial', 15), width=35, command=ToggleToAddContact)
	btn_add_users.grid(row=4, pady=12)
	btn_del_users = Button(current_frame, text="Exit User With QR", font=('arial', 15), width=35, command=ToggleToQRCapture)
	btn_del_users.grid(row=5, pady=12)
	btn_del_users = Button(current_frame, text="Exit User With Contact", font=('arial', 15), width=35, command=ToggleToExitContact)
	btn_del_users.grid(row=6, pady=12)
	#btn_del_users = Button(current_frame, text="Reprint Pass", font=('arial', 15), width=35, command=ToggleToReprintPass)
	#btn_del_users.grid(row=6, pady=12)
	lbl_result1 = Label(current_frame, text="", font=('arial', 18))
	lbl_result1.grid(row=7, columnspan=2)
	btn_quit = Button(current_frame, text="Quit", font=('arial', 12), width=35, command=lambda : root.quit())
	btn_quit.grid(row=8, pady=12)
	
	current_frame.pack(side=TOP, pady=20)

def ShowAllUsers():
	global current_frame, lbl_result1, allUserList
	current_frame = Frame(root)
	allUserList = []
	getAllUserList()
	lbl_result1 = Label(current_frame, text="All Users", font=('arial', 18))
	lbl_result1.grid(row=1)
	
	listNodes = Listbox(current_frame, width=40, height=20, font=("Helvetica", 12))
	listNodes.grid(row=2)

	scrollbar = Scrollbar(current_frame, orient="vertical")
	scrollbar.config(command=listNodes.yview)
	scrollbar.grid(row=2, column=1, sticky=NS)

	listNodes.config(yscrollcommand=scrollbar.set)

	for name in allUserList:
		listNodes.insert(END, name)
	
	lbl_back = Label(current_frame, text="Back", fg="Blue", font=('arial', 12))
	lbl_back.grid(row=0, sticky=W)
	lbl_back.bind('<Button-1>', ToggleToMainMenu)
	current_frame.pack(side=TOP, pady=40)

def ShowInUsers():
	global current_frame, lbl_result1, inUserList
	current_frame = Frame(root)
	
	inUserList = []

	getInUserList()
	lbl_result1 = Label(current_frame, text="Users Inside", font=('arial', 18))
	lbl_result1.grid(row=1)
	
	listNodes = Listbox(current_frame, width=40, height=20, font=("Helvetica", 12))
	listNodes.grid(row=2)

	scrollbar = Scrollbar(current_frame, orient="vertical")
	scrollbar.config(command=listNodes.yview)
	scrollbar.grid(row=2, column=1, sticky=NS)

	listNodes.config(yscrollcommand=scrollbar.set)

	
	for name in inUserList:
		listNodes.insert(END, name)
	
	lbl_back = Label(current_frame, text="Back", fg="Blue", font=('arial', 12))
	lbl_back.grid(row=0, sticky=W)
	lbl_back.bind('<Button-1>', ToggleToMainMenu)
	current_frame.pack(side=TOP, pady=40)

def time_picker(time_input, check):
	global current_frame, ADD_IN_TIME, ADD_EXPECTED_OUT_TIME, dt
	ws = Tk()
	ws.title("TIME PICKER")
	ws.geometry("500x400")

	hour_string=StringVar()
	min_string=StringVar()
	last_value_sec = ""
	last_value = ""        
	f = ('Times', 20)

	def display_msg(time_input, check):
		global ADD_IN_TIME, ADD_EXPECTED_OUT_TIME
		date = cal.get_date()
		dateFormatted = date.split("/")
		finDate = dateFormatted[1].zfill(2) + "/" + dateFormatted[0].zfill(2) + "/" + "20" + dateFormatted[2] 
		m = min_sb.get()
		h = sec_hour.get()
		s = sec.get()
		if(check == 0):
			t = f"You entered BITS PILANI on {date} at {m}:{h}:{s}."
			ADD_IN_TIME = (date + '-' + m + '-' + h + '-' + s)
		else:
			if(check == 1):
				ADD_EXPECTED_OUT_TIME = finDate + '-' + m.zfill(2) + '-' + h.zfill(2) + '-' + s.zfill(2)
				date1_dt = datetime.datetime.strptime(ADD_IN_TIME, "%d/%m/%Y-%H-%M-%S")
				date2_dt = datetime.datetime.strptime(ADD_EXPECTED_OUT_TIME, "%d/%m/%Y-%H-%M-%S")
				if date2_dt <= date1_dt:
					tkMessageBox.showerror("Error", "Expected out time should be more than in time. Please select expected out time again!!")
					ADD_EXPECTED_OUT_TIME = ""
					DestroyFrame_time(ws)
					return
				t = f"You are expected to exit BITS PILANI on {finDate} at {m}:{h}:{s}."
				
				lbl_result1 = Label(current_frame, text=ADD_EXPECTED_OUT_TIME, font=('arial', 12))
				lbl_result1.grid(row=8, column=1, columnspan=1)
			
			else:
				t = f"You are exiting BITS PILANI on {finDate} at {m}:{h}:{s}."
				DEL_EXPECTED_OUT_TIME = finDate + '-' + m + '-' + h + '-' + s
		
		msg_display = Label(
			ws,
			text="",
			bg="#cd950c"
		)
		msg_display.config(text=t)
		
		msg_display.pack(pady=10)
		lbl_back = Label(ws, text="Back", fg="Blue", font=('arial', 12))
		lbl_back.place(x=40,y=20)
		destroy_funx = lambda q: DestroyFrame_time(ws)
		lbl_back.bind('<Button-1>', destroy_funx)
		   

	if last_value == "59" and min_string.get() == "0":
		hour_string.set(int(hour_string.get())+1 if hour_string.get() !="23" else 0)   
		last_value = min_string.get()

	if last_value_sec == "59" and sec_hour.get() == "0":
		min_string.set(int(min_string.get())+1 if min_string.get() !="59" else 0)
	if last_value == "59":
		hour_string.set(int(hour_string.get())+1 if hour_string.get() !="23" else 0)            
		last_value_sec = sec_hour.get()

	fone = Frame(ws)
	ftwo = Frame(ws)

	fone.pack(pady=10)
	ftwo.pack(pady=10)
	today = dt.today()
	curDate = today.strftime("%d/%m/%y")
	curDay = today.strftime("%d")
	curMonth = today.strftime("%m")
	curYear = today.year
	cal = Calendar(
		fone, 
		selectmode="day", 
		year=int(curYear), 
		month=int(curMonth),
		day=int(curDay)
		)
	cal.pack()

	min_sb = Spinbox(
		ftwo,
		from_=0,
		to=23,
		wrap=True,
		textvariable=hour_string,
		width=2,
		state="readonly",
		font=f,
		justify=CENTER
		)
	sec_hour = Spinbox(
		ftwo,
		from_=0,
		to=59,
		wrap=True,
		textvariable=min_string,
		font=f,
		width=2,
		justify=CENTER
		)

	sec = Spinbox(
		ftwo,
		from_=0,
		to=59,
		wrap=True,
		textvariable=sec_hour,
		width=2,
		font=f,
		justify=CENTER
		)

	min_sb.pack(side=LEFT, fill=X, expand=True)
	sec_hour.pack(side=LEFT, fill=X, expand=True)
	sec.pack(side=LEFT, fill=X, expand=True)

	msg = Label(
		ws, 
		text="Hour  Minute  Seconds",
		font=("Times", 12)
		)
	msg.pack(side=TOP)
	display_funx = lambda : display_msg(time_input, check)
	actionBtn =Button(
		ws,
		text="Set Time",
		padx=10,
		pady=10,
		command = display_funx
	)
	actionBtn.pack(pady=10)
	ws.mainloop()

def AddContact():
	global current_frame, lbl_result1, ADD_CONTACT_NO
	current_frame = Frame(root)
	ADD_CONTACT_NO.set("")
	lbl_username = Label(current_frame, text="Contact No:", font=('arial', 12), bd=9)
	lbl_username.grid(row=1)
	username = Entry(current_frame, font=('arial', 12), textvariable=ADD_CONTACT_NO, width=15)
	username.grid(row=1, column=1)
	btn_login = Button(current_frame, text="Add", font=('arial', 14), width=30, command=UtilAddContact)
	btn_login.grid(row=3, columnspan=2, pady=16)
	lbl_back = Label(current_frame, text="Back", fg="Blue", font=('arial', 12))
	lbl_back.grid(row=0, sticky=W)
	lbl_back.bind('<Button-1>', ToggleToMainMenu)
	current_frame.pack(side=TOP, pady=80)

def AddUser():
	global current_frame, lbl_result1, ADD_EXPECTED_OUT_TIME, ADD_IN_TIME, ADD_ID, ADD_USERNAME, ADD_DESTINATION, ADD_CONTACT_NO, ADD_VEHICLE_NO,ADD_PURPOSE_OF_VISIT, ADD_VISITOR_RELATION, entryUser
	current_frame = Frame(root)
	response = (requests.post(connectApi + "/find", json = {"contact_no":ADD_CONTACT_NO.get()})).json()
	if not "docs" in response:
		ADD_VEHICLE_NO.set("")
		ADD_USERNAME.set("")
		ADD_DESTINATION.set("")
	else:
		tempList = response["docs"]
		entryUser = tempList[-1]
		ADD_VEHICLE_NO.set(entryUser["vehicle_no"])
		ADD_USERNAME.set(entryUser["name"])
		ADD_DESTINATION.set(entryUser["destination"])
	lbl_username = Label(current_frame, text="Username:", font=('arial', 12), bd=9)
	lbl_username.grid(row=1)
	lbl_username = Label(current_frame, text="Vehicle No:", font=('arial', 12), bd=9)
	lbl_username.grid(row=2)
	lbl_destination = Label(current_frame, text="Destination:", font=('arial', 12), bd=9)
	lbl_destination.grid(row=3)
	lbl_destination = Label(current_frame, text="Visitor Relation:", font=('arial', 12), bd=9)
	lbl_destination.grid(row=4)
	lbl_destination = Label(current_frame, text="Purpose:", font=('arial', 12), bd=9)
	lbl_destination.grid(row=5)
	username = Entry(current_frame, font=('arial', 12), textvariable=ADD_USERNAME, width=15)
	username.grid(row=1, column=1)
	username = Entry(current_frame, font=('arial', 12), textvariable=ADD_VEHICLE_NO, width=15)
	username.grid(row=2, column=1)
	ADD_ID.set(getNextId())
	destination = Entry(current_frame, font=('arial', 12), textvariable=ADD_DESTINATION, width=15)
	destination.grid(row=3, column=1)
	destination = Entry(current_frame, font=('arial', 12), textvariable=ADD_VISITOR_RELATION, width=15)
	destination.grid(row=4, column=1)
	
	helv36 = tkFont.Font(family='Helvetica', size=14)
	ADD_PURPOSE_OF_VISIT.set("Purpose for Visit")
	drop= OptionMenu(current_frame, ADD_PURPOSE_OF_VISIT, "Option 1", "Option 2","Option 3","Option 4","Option 5")
	drop.config(font=helv36)
	drop.grid(row=5, column = 1, sticky='NS')
	
	#destination = Entry(current_frame, font=('arial', 12), textvariable=ADD_PURPOSE_OF_VISIT, width=15)
	#destination.grid(row=5, column=1)
	in_funx = lambda : time_picker(ADD_IN_TIME, 0)
	btn_intime = Button(current_frame, text="In-Time", font=('arial', 12), width=14, command=currentTime)
	btn_intime.grid(row=6, columnspan=1, pady=8)
	out_funx = lambda : time_picker(ADD_EXPECTED_OUT_TIME, 1)
	btn_expectedouttime = Button(current_frame, text="Expected Out-Time", font=('arial', 12), width=14, command=out_funx)
	btn_expectedouttime.grid(row=6, column=1, columnspan=1, pady=8)
	lbl_result1 = Label(current_frame, text="", font=('arial', 12))
	lbl_result1.grid(row=7, columnspan=1)
	btn_login = Button(current_frame, text="Add", font=('arial', 14), width=30, command=ToggleToAddUserCam)
	btn_login.grid(row=9, columnspan=2, pady=16)
	lbl_back = Label(current_frame, text="Back", fg="Blue", font=('arial', 12))
	lbl_back.grid(row=0, sticky=W)
	lbl_back.bind('<Button-1>', ToggleToMainMenu)
	current_frame.pack(side=TOP, pady=80)
	
'''global current_frame, lbl_result1, SEARCH_FIELD, SEARCH_INPUT, current_frame, SearchCheckBoxInput
	
	current_frame = Frame(root)
	
	helv36 = tkFont.Font(family='Helvetica', size=14)
	
	SEARCH_FIELD.set("Select the Filter for Searching")

	drop= OptionMenu(current_frame, SEARCH_FIELD, "Contact Number", "Vehicle Number","User Id","In-Date (dd/mm/yyyy)","Out-Date (dd/mm/yyyy)")
	drop.config(font=helv36)
	
	SearchCheckBoxInput.set(0)
	
	c1 = Checkbutton(current_frame, text='Show Only Users Inside',variable=SearchCheckBoxInput, onvalue=1, offvalue=0)
	
	lbl_result1 = Label(current_frame, text="", font=('arial', 10))
	lbl_result1.grid(row=4)
	
	lbl_result1 = Label(current_frame, text="", font=('arial', 10))
	lbl_result1.grid(row=5)
	
	username = Entry(current_frame, font=('arial', 12), textvariable=SEARCH_INPUT, width=15)
	username.grid(row=6, columnspan = 2)
	
	lbl_result1 = Label(current_frame, text="", font=('arial', 10))
	lbl_result1.grid(row=1)
	
	lbl_result1 = Label(current_frame, text="", font=('arial', 10))
	lbl_result1.grid(row=2)

	drop.grid(row=3, columnspan = 2, sticky='NS')
	
	lbl_back = Label(current_frame, text="Back", fg="Blue", font=('arial', 12))
	lbl_back.grid(row=0, sticky=W)
	
	lbl_result1 = Label(current_frame, text="", font=('arial', 10))
	lbl_result1.grid(row=7, columnspan=1)
	
	btn_login = Button(current_frame, text="Search", font=('arial', 14), width=30, command=UtilSearchUser)
	btn_login.grid(row=8, columnspan=2, pady=16)
	lbl_back.bind('<Button-1>', ToggleToMainMenu)
	c1.grid(row = 7, columnspan = 2)
	current_frame.pack(side=TOP, pady=80)
'''

def AddUserCam():
	global current_frame, cap, lmain, ADD_ID, button_capture, button_quit, cancel, output, cwd
	current_frame = Frame(root)
		
	cancel = False
	output = cwd + "/dataset/"

	try:
		os.makedirs(output, exist_ok = True)
		print("[INFO] directory created successfully")
	except OSError as error:
		print("[INFO] directory already exist")
	
	cap = cv2.VideoCapture(0)
	
	if not cap.isOpened():
		print("Error opening video")
		ToggleToMainMenu()
	
	capWidth = cap.get(3)
	capHeight = cap.get(4)
	
	success, frame = cap.read()
	if not success:
		if camIndex == 0:
			sys.exit(1)
		else:
			success, frame = cap.read()
			if not success:
				sys.exit(1)
				
	current_frame.bind('<Escape>', ToggleToMainMenuCam)
	lmain = Label(current_frame, compound=CENTER, anchor=CENTER, relief=RAISED)
	button_capture = Button(current_frame, text="Capture", command=prompt_ok)
	button_quit = Button(current_frame, text="Quit", command=ToggleToMainMenuCam)

	lmain.pack()
	button_capture.place(bordermode=INSIDE, relx=0.5, rely=0.9, anchor=CENTER, width=300, height=50)
	button_capture.focus()
	button_quit.place(bordermode=INSIDE, relx=0.9, rely=0.9, anchor=E, width=100, height=25)

	show_frame_add_user()
	
def show_frame_add_user():
	global prevImg, button_capture, origImg, lmain, frame, cancel

	_, frame = cap.read()
	imgtk = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)))
	lmain.imgtk = imgtk
	lmain.configure(image=imgtk)
	current_frame.pack()
	if not cancel:
		lmain.after(5, show_frame_add_user)
	
def save(event = 0):
	global frame, output, cap, ADD_ID
	
	cap.release()
	p = output + "/" + ADD_ID.get() + ".png"
	cv2.imwrite(p, frame)
	UtilAddUser()
	
def resume(event = 0):
	global button1, button2, button_capture, lmain, cancel, current_frame

	cancel = False

	button1.place_forget()
	button2.place_forget()

	current_frame.bind('<Return>', prompt_ok)
	button_capture.place(bordermode=INSIDE, relx=0.5, rely=0.9, anchor=CENTER, width=300, height=50)
	button_quit.place(bordermode=INSIDE, relx=0.9, rely=0.9, anchor=E, width=100, height=25)
	lmain.after(5, show_frame_add_user)
	
def prompt_ok(event = 0):
	global cancel, button_capture, button1, button2, button_quit, current_frame
	cancel = True

	button_capture.place_forget()
	button_quit.place_forget()
	button1 = Button(current_frame, text="Good Image!", command=save)
	button2 = Button(current_frame, text="Try Again", command=resume)
	button1.place(anchor=CENTER, relx=0.2, rely=0.9, width=150, height=50)
	button2.place(anchor=CENTER, relx=0.8, rely=0.9, width=150, height=50)
	button1.focus()
	
def currentTime():
	global ADD_IN_TIME, current_frame
	current_time = datetime.datetime.now()
	today = dt.today()
	d1 = today.strftime("%d/%m/%Y")
	ADD_IN_TIME = (str(d1) + '-' + str(current_time.hour).zfill(2) + '-' + str(current_time.minute).zfill(2) + '-' + str(current_time.second).zfill(2))
	lbl_result1 = Label(current_frame, text=ADD_IN_TIME, font=('arial', 12))
	lbl_result1.grid(row=8, columnspan=1)

def DelUser():
	global current_frame, lbl_result1, exitUser, exitUserId, root
	Username = "NA"
	ContactNo = "NA"
	VehicleNo = "NA"
	Destination = "NA"
	InTime = "NA"
	OutTime = "NA"
	Purpose = "NA"
	Relation = "NA"
	if getDelUser():
		Username = exitUser["name"]
		Destination = exitUser["destination"]
		InTime = exitUser["in_time"]
		if exitUser["vehicle_no"] != "":
			VehicleNo = exitUser["vehicle_no"]
		ContactNo = exitUser["contact_no"]
		Purpose = exitUser["purpose"]
		if exitUser["relation"] != "":
			Relation = exitUser["relation"]
		current_time = datetime.datetime.now()
		today = dt.today()
		d1 = today.strftime("%d/%m/%Y")
		exit_time = (str(d1) + '-' + (str(current_time.hour)).zfill(2) + '-' + (str(current_time.minute)).zfill(2) + '-' + (str(current_time.second)).zfill(2)) 
		OutTime = exit_time
	
	current_frame = Frame(root)
	lbl_username = Label(current_frame, text="Username:", font=('arial', 12), bd=9)
	lbl_username.grid(row=1)
	lbl_username = Label(current_frame, text="Contact No:", font=('arial', 12), bd=9)
	lbl_username.grid(row=2)
	lbl_username = Label(current_frame, text="Vehicle No:", font=('arial', 12), bd=9)
	lbl_username.grid(row=3)
	lbl_destination = Label(current_frame, text="Destination:", font=('arial', 12), bd=9)
	lbl_destination.grid(row=4)
	lbl_destination = Label(current_frame, text="Purpose:", font=('arial', 12), bd=9)
	lbl_destination.grid(row=5)
	lbl_destination = Label(current_frame, text="Relation:", font=('arial', 12), bd=9)
	lbl_destination.grid(row=6)
	username = Label(current_frame, font=('arial', 12), text=Username, width=15)
	username.grid(row=1, column=1)
	username = Label(current_frame, font=('arial', 12), text=ContactNo, width=15)
	username.grid(row=2, column=1)
	destination = Label(current_frame, font=('arial', 12), text=VehicleNo, width=15)
	destination.grid(row=3, column=1)
	destination = Label(current_frame, font=('arial', 12), text=Destination, width=15)
	destination.grid(row=4, column=1)
	destination = Label(current_frame, font=('arial', 12), text=Purpose, width=15)
	destination.grid(row=5, column=1)
	destination = Label(current_frame, font=('arial', 12), text=Relation, width=15)
	destination.grid(row=6, column=1)
	lbl_username = Label(current_frame, text="In Time", font=('arial', 10), bd=9)
	lbl_username.grid(row=7, column = 0)
	lbl_destination = Label(current_frame, text="Out Time", font=('arial', 10), bd=9)
	lbl_destination.grid(row=7, column=1)
	username = Label(current_frame, font=('arial', 10), text=InTime, width=15)
	username.grid(row=8, column=0)
	destination = Label(current_frame, font=('arial', 10), text=OutTime, width=15)
	destination.grid(row=8, column=1)
	
	if Username == "NA":
		btn_login = Button(current_frame, text="Try Again", font=('arial', 14), width=35, command=ToggleToQRCapture)
		btn_login.grid(row=9, columnspan=2, pady=20)
	else:
		btn_login = Button(current_frame, text="Mark Exit", font=('arial', 14), width=35, command=UtilDelUser)
		btn_login.grid(row=9, columnspan=2, pady=20)
		
	lbl_back = Label(current_frame, text="Back", fg="Blue", font=('arial', 12))
	lbl_back.grid(row=0, sticky=W)
	lbl_back.bind('<Button-1>', ToggleToMainMenu)
	current_frame.pack(side=TOP, pady=80)
		
def QRCapture():
	global current_frame, cap, lmain
	current_frame = Frame(root)
	
	cap = cv2.VideoCapture(0)
	
	if not cap.isOpened():
		print("Error opening video")
		ToggleToMainMenu()
	capWidth = cap.get(3)
	capHeight = cap.get(4)
	
	success, frame = cap.read()
	if not success:
		if camIndex == 0:
			sys.exit(1)
		else:
			success, frame = cap.read()
			if not success:
				sys.exit(1)
				
	lmain = Label(current_frame, compound=CENTER, anchor=CENTER, relief=RAISED)
	button_quit = Button(current_frame, text="Quit", command=ToggleToMainMenuCam)

	lmain.pack()
	button_quit.place(bordermode=INSIDE, relx=0.9, rely=0.9, anchor=E, width=100, height=25)
	
	show_frame()
	
def show_frame():
	global button_capture, qr, lmain, current_frame, cap
	_, frame = cap.read()
	qr = read_qr_code(frame)
	if qr != "":
		cap.release()
		ToggleToDelUser()

	else:
		imgtk = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)))
		lmain.imgtk = imgtk
		lmain.configure(image=imgtk)
		current_frame.pack()
		lmain.after(5, show_frame)
	
def read_qr_code(frame):
    try:
        detect = cv2.QRCodeDetector()
        value, points, straight_qrcode = detect.detectAndDecode(frame)
        value = value.split(",")[0]
        return value
    except:
        return ""
    
def download_image(url, file_path, file_name):
    full_path = file_path + file_name + '.png'
    urllib.request.urlretrieve(url, full_path)

def MarkExitContact():
	global current_frame, lbl_result1, markexitContact
	current_frame = Frame(root)
	lbl_username = Label(current_frame, text="", font=('arial', 12), bd=9)
	lbl_username.grid(row=1)
	lbl_username = Label(current_frame, text="Contact Number", font=('arial', 12), bd=9)
	lbl_username.grid(row=2)
	printpassContact.set("")
	username = Entry(current_frame, font=('arial', 12), textvariable=markexitContact, width=15)
	username.grid(row=2, column=1)
	
	btn_login = Button(current_frame, text="Mark Exit", font=('arial', 14), width=30, command=UtilMarkExitContact)
	btn_login.grid(row=7, columnspan=2, pady=14)
	lbl_back = Label(current_frame, text="Back", fg="Blue", font=('arial', 12))
	lbl_back.grid(row=0, sticky=W)
	lbl_back.bind('<Button-1>', ToggleToMainMenu)
	current_frame.pack(side=TOP, pady=80)

def DestroyFrame_time(ws, event=None):
	ws.destroy()

def DestroyFrame(event=None):
	global current_frame
	current_frame.destroy()

def ToggleToMainMenu(event=None):
	DestroyFrame()
	MainMenu()
	
def ToggleToMainMenuCam(event=None):
	global cap
	cap.release()
	DestroyFrame()
	MainMenu()

def ToggleToShowAllUsers(event=None):
	DestroyFrame()
	ShowAllUsers()

def ToggleToShowInUsers(event=None):
	DestroyFrame()
	ShowInUsers()

def ToggleToAddUser(event=None):
	DestroyFrame()
	AddUser()

def ToggleToAddContact(event=None):
	DestroyFrame()
	AddContact()

def ToggleToAddUserCam(event=None):
	DestroyFrame()
	AddUserCam()

def ToggleToDelUser(event=None):
	DestroyFrame()
	DelUser()
	
def ToggleToQRCapture(event=None):
	DestroyFrame()
	QRCapture()

def ToggleToExitContact(event=None):
	DestroyFrame()
	MarkExitContact()

def ToggleToMarkExitCamera(event=None):
	DestroyFrame()
	MarkExitCamera()

MainMenu()

#========================================UTIL FUNCTIONS===================================
def getDelUser():
	global exitUserDB, exitUserId, exitUser, inUsers, allUsersDB
	response = (requests.post(connectApi + "/find", json = {"id": qr, "in_campus": True})).json()
	if not "docs" in response:
		tkMessageBox.showerror("Error", "User not in BITS Pilani Campus.\nTry again.")
		return False
	user = response["docs"]
	exitUser = user[0]
	return True

def UtilMarkExitContact():
	global markexitContact, ADD_CONTACT_NO, ADD_DESTINATION, ADD_EXPECTED_OUT_TIME, ADD_ID, ADD_IN_TIME, ADD_VEHICLE_NO, ADD_USERNAME, cwd, ADD_PURPOSE_OF_VISIT, ADD_VISITOR_RELATION
	
	response = (requests.post(connectApi + "/find", json = {"contact_no" : markexitContact.get()})).json()
	if not "docs" in response:
		tkMessageBox.showerror("Error", "Invalid Contact.\nTry again.")
		ToggleToExitContact()
		return
	
	user = response["docs"]
	if (len(user)==0):
		tkMessageBox.showerror("Error", "User not in BITS Pilani campus.\nTry again.")
		return
		
	current_time = datetime.datetime.now()
	today = dt.today()
	d1 = today.strftime("%d/%m/%Y")
	exit_time = (str(d1) + '-' + str(current_time.hour) + '-' + str(current_time.minute) + '-' + str(current_time.second)) 
	user = user[-1]
	if user["in_campus"] == False:
		tkMessageBox.showerror("Error", "User not in BITS Pilani.\nTry again.")
		ToggleToExitContact()
		return
	user["in_campus"]= False
	user["out_time"] = exit_time
	response = (requests.post(connectApi + "/add-data", json = user)).json()
	tkMessageBox.showinfo("Success", " Exit marked successfully.")
	markexitContact.set("")
	ToggleToMainMenu()

def UtilDelUser():
	global exitUser, exitUserDB, inUsers, exitUserId
	response = (requests.post(connectApi + "/find", json = {"id": qr})).json()
	user = response["docs"]
	if (len(user)==0):
		tkMessageBox.showerror("Error", "User not in BITS Pilani campus.\nTry again.")
		return
	current_time = datetime.datetime.now()
	today = dt.today()
	d1 = today.strftime("%d/%m/%Y")
	exit_time = (str(d1) + '-' + str(current_time.hour) + '-' + str(current_time.minute) + '-' + str(current_time.second)) 
	user = user[-1]
	user["in_campus"]= False
	user["out_time"] = exit_time
	response = (requests.post(connectApi + "/add-data", json = user)).json()
	tkMessageBox.showinfo("Success", " Exit marked successfully.")
	ToggleToMainMenu()

def UtilAddContact():
	global ADD_CONTACT_NO
	if len(ADD_CONTACT_NO.get())!=10:
		tkMessageBox.showerror("Error", "Invalid Contact!!")
		ToggleToAddContact()
	else:
		ToggleToAddUser()
	

def UtilAddUser():
	global ADD_USERNAME, ADD_ID, ADD_DESTINATION, ADD_EXPECTED_OUT_TIME, ADD_IN_TIME, inUsers, allUsers, ADD_CONTACT_NO, ADD_VEHICLE_NO, allUsersDB, ADD_PURPOSE_OF_VISIT, ADD_VISITOR_RELATION, cwd
	if len(ADD_USERNAME.get()) == 0 or len(ADD_ID.get()) == 0 or len(ADD_DESTINATION.get()) == 0 or len(ADD_IN_TIME) == 0 or len(ADD_EXPECTED_OUT_TIME) == 0 or len(ADD_CONTACT_NO.get()) == 0  or len(ADD_PURPOSE_OF_VISIT.get()) == 0:
		tkMessageBox.showerror("Error", "Some field is empty!!")
		ToggleToAddUser()
	else:
		aa = {
			"id" : ADD_ID.get(), 
			"name" : ADD_USERNAME.get(),
			"contact_no" : ADD_CONTACT_NO.get(),
			"vehicle_no" : ADD_VEHICLE_NO.get(),
			"destination" : ADD_DESTINATION.get(),
			"in_time" : ADD_IN_TIME,
			"out_time" : ADD_EXPECTED_OUT_TIME,
			"purpose" : ADD_PURPOSE_OF_VISIT.get(),
			"relation" : ADD_VISITOR_RELATION.get(),
			"in_campus" : True
		}
		response = requests.post(connectApi + "/add-data", json = aa)
		if not (response.status_code == 200):
			tkMessageBox.showerror("Error", "Couldn't make an entry!\nPlease try again.")
		
		tkMessageBox.showinfo("Success", ADD_USERNAME.get() + " added successfully.")
		url = connectApi + "/upload"
		files = {'image': open(cwd + "/dataset/" + ADD_ID.get() + ".png", 'rb')}
		requests.post(url, files=files)
		removingfiles = glob.glob(cwd + "/dataset/" + ADD_ID.get() + ".png")
		for i in removingfiles:
			os.remove(i)
		printPass()
		clearAddUserVariables()
		ToggleToAddContact()

def printPass():
	global ADD_CONTACT_NO, ADD_DESTINATION, ADD_EXPECTED_OUT_TIME, ADD_ID, ADD_IN_TIME, ADD_VEHICLE_NO, ADD_USERNAME, cwd, ADD_PURPOSE_OF_VISIT, ADD_VISITOR_RELATION, imgBaseUrl
	ID = ADD_ID.get()
	name = ADD_USERNAME.get()
	contact = ADD_CONTACT_NO.get()
	vehicle_no = ADD_VEHICLE_NO.get()
	if (vehicle_no == ""):
		vehicle_no = "NA"
	in_time = ADD_IN_TIME
	out_time = ADD_EXPECTED_OUT_TIME
	destination = ADD_DESTINATION.get()
	purpose = ADD_PURPOSE_OF_VISIT.get()
	relation = ADD_VISITOR_RELATION.get()
	if (relation == ""):
		relation = "NA"
	
	url = imgBaseUrl + "/" + ADD_ID.get() + ".png"
	download_image(url, cwd + "/dataset/", ID)
	
	print("\nStatus => Printer Working!")
	# Define character design and font sizes for each line.
	thermal_printer = None 
	command_thermal_printer = []
	command_thermal_printer.append("sudo lsof /dev/usb/lp0")
	command_thermal_printer.append("sudo chmod 666 /dev/usb/lp0")
	command_thermal_printer.append("printf '\x1B\x45\x01' > /dev/usb/lp0")
	command_thermal_printer.append("printf '\x1D\x42\x01' > /dev/usb/lp0")
	command_thermal_printer.append("printf '\x1D\x21\x12' > /dev/usb/lp0")
	command_thermal_printer.append("echo ' BITS ENTRY-EXIT PASS \\n' > /dev/usb/lp0")
	# inverse
	command_thermal_printer.append("printf '\x1D\x42\x10' > /dev/usb/lp0")
	# char size
	command_thermal_printer.append("printf '\x1D\x21\x01' > /dev/usb/lp0")
	command_thermal_printer.append("echo 'ID: " + ID + "' > /dev/usb/lp0")
	command_thermal_printer.append("echo 'Name: " + name + "' > /dev/usb/lp0")
	command_thermal_printer.append("echo 'Contact No: " + contact + "' > /dev/usb/lp0")
	command_thermal_printer.append("echo 'Vehicle No: " + vehicle_no + "' > /dev/usb/lp0")
	command_thermal_printer.append("echo 'Destination: " + destination + "' > /dev/usb/lp0")
	command_thermal_printer.append("echo 'Purpose: " + purpose + "' > /dev/usb/lp0")
	command_thermal_printer.append("echo 'Visitor Relation: " + relation + "' > /dev/usb/lp0")
	command_thermal_printer.append("echo 'In Time: " + in_time + "' > /dev/usb/lp0")
	command_thermal_printer.append("echo 'Expected Out Time: " + out_time + "\\n' > /dev/usb/lp0")

	command_thermal_printer.append("echo 'Please Show this Pass at BITS PILANI Main Gate' > /dev/usb/lp0")
	
	
	# Print each line via the serial port.
	for i in range(len(command_thermal_printer)):
		call([command_thermal_printer[i]], shell=True)
		sleep(0.25)
	# Print QR Code w/ Settings
	if thermal_printer is None:
		thermal_printer = printer.File("/dev/usb/lp0")
	#thermal_printer = printer.File("/dev/usb/lp0")
	thermal_printer.image(cwd + "/dataset/" + ID + ".png")
	thermal_printer.qr(str(str(ID) + "," + str(name)), size=16, model=2)
	thermal_printer.cut()
	removingfiles = glob.glob(cwd + "/dataset/" + ID + ".png")
	for i in removingfiles:
		os.remove(i)
	
def clearAddUserVariables():
	global ADD_USERNAME, ADD_ID, ADD_DESTINATION, ADD_IN_TIME, ADD_EXPECTED_OUT_TIME, ADD_CONTACT_NO, ADD_VEHICLE_NO, ADD_PURPOSE_OF_VISIT, ADD_VISITOR_RELATION
	
	ADD_USERNAME.set("")
	ADD_ID.set("")
	ADD_DESTINATION.set("")
	ADD_CONTACT_NO.set("")
	ADD_VEHICLE_NO.set("")
	ADD_PURPOSE_OF_VISIT.set("")
	ADD_VISITOR_RELATION.set("")
	ADD_IN_TIME = ""
	ADD_EXPECTED_OUT_TIME = ""
	saveId()

def getAllUserList():
	global allUserList, allUsers, allUsersDB, connectApi
	response = (requests.post(connectApi + "/find", json = {})).json()
	if not "docs" in response:
		tempList = []
	else:
		tempList = response["docs"]
	for user in tempList:
		displaylist = user["name"] + " (" + user["in_time"] + ", " + user["out_time"] + ")"
		allUserList.append(displaylist)
	return
	
def getInUserList():
	global inUserList, inUsers, allUsersDB
	
	response = (requests.post(connectApi + "/find", json = {"in_campus":True})).json()
	if not "docs" in response:
		print(response)
	else:
		tempList = response["docs"]
		for user in tempList:
			displaylist = user["name"] + " (" + user["in_time"] + ", " + user["out_time"] + ")"
			inUserList.append(displaylist)
		
	return
	
def getNextId():
	global currentIdDB, date, currentId
	
	today = dt.today()
	currentId = currentIdDB.find_one()
	if currentId is None:
		currentId = {}
		currentId["date"] = today.strftime("%Y%m%d")
		currentId["id"] = 1
	else:
		date = today.strftime("%Y%m%d")
		if date == currentId["date"]:
			currentId["id"] = currentId["id"] + 1
		else:
			currentId["date"] = today.strftime("%Y%m%d")
			currentId["id"] = 1
	
	return str(currentId["date"]) + str(currentId["id"]).zfill(4)



def saveId():
	global currentId, currentIdDB
	
	currentIdDB.drop()
	currentIdDB.insert_one(dict(currentId))

#========================================INITIALIZATION===================================
if __name__ == '__main__':
	root.mainloop()
