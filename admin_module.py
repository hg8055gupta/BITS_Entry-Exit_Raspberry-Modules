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
root.title("BITS Entry Exit System Admin Module")

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
connectApi = "http://172.18.19.242:8000/api"
imgBaseUrl = "http://172.18.19.242:8000/images"

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
	btn_del_users = Button(current_frame, text="Search User", font=('arial', 15), width=35, command=ToggleToSearchUser)
	btn_del_users.grid(row=4, pady=12)
	btn_del_users = Button(current_frame, text="Generate Monthly Report", font=('arial', 15), width=35, command=ToggleToGenerateReport)
	btn_del_users.grid(row=5, pady=12)
	btn_del_users = Button(current_frame, text="Generate Daily Report", font=('arial', 15), width=35, command=ToggleToGenDailyReport)
	btn_del_users.grid(row=6, pady=12)
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

def SearchUser():
	global current_frame, lbl_result1, SEARCH_FIELD, SEARCH_INPUT, current_frame, SearchCheckBoxInput
	
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

def showSearchUser():
	global current_frame, lbl_result1, searchedUserList
	current_frame = Frame(root)
	
	lbl_result1 = Label(current_frame, text="Searched Users", font=('arial', 18))
	lbl_result1.grid(row=1)
	
	listNodes = Listbox(current_frame, width=40, height=15, font=("Helvetica", 12))
	listNodes.grid(row=2)

	scrollbar = Scrollbar(current_frame, orient="vertical")
	scrollbar.config(command=listNodes.yview)
	scrollbar.grid(row=2, column=1, sticky=NS)

	listNodes.config(yscrollcommand=scrollbar.set)

	for name in searchedUserList:
		listNodes.insert(END, name)
	
	lbl_back = Label(current_frame, text="Back", fg="Blue", font=('arial', 12))
	lbl_back.grid(row=0, sticky=W)
	lbl_back.bind('<Button-1>', ToggleToMainMenu)
	current_frame.pack(side=TOP, pady=40)
        
def GenerateReport():
	global current_frame, lbl_result1,GenerateReportEntry
	current_frame = Frame(root)
	lbl_username = Label(current_frame, text="", font=('arial', 12), bd=9)
	lbl_username.grid(row=1)
	lbl_username = Label(current_frame, text="Month and Year (mm/yyyy)", font=('arial', 12), bd=9)
	lbl_username.grid(row=2)
	GenerateReportEntry.set("")
	username = Entry(current_frame, font=('arial', 12), textvariable=GenerateReportEntry, width=15)
	username.grid(row=2, column=1)
	
	btn_login = Button(current_frame, text="Generate", font=('arial', 14), width=30, command=UtilGenerateReport)
	btn_login.grid(row=7, columnspan=2, pady=14)
	lbl_back = Label(current_frame, text="Back", fg="Blue", font=('arial', 12))
	lbl_back.grid(row=0, sticky=W)
	lbl_back.bind('<Button-1>', ToggleToMainMenu)
	current_frame.pack(side=TOP, pady=80)

def DestroyFrame(event=None):
	global current_frame
	current_frame.destroy()

def ToggleToMainMenu(event=None):
	DestroyFrame()
	MainMenu()

def ToggleToShowAllUsers(event=None):
	DestroyFrame()
	ShowAllUsers()

def ToggleToGenDailyReport():
	UtilGenDailyReport()
	tkMessageBox.showinfo("Success", "Report for today generated successfully.")
	

def ToggleToGenerateReport():
	DestroyFrame()
	GenerateReport()

def ToggleToShowInUsers(event=None):
	DestroyFrame()
	ShowInUsers()
	
def ToggleToShowSearchUser(event=None):
	DestroyFrame()
	showSearchUser()
	
def ToggleToSearchUser(event=None):
	DestroyFrame()
	SearchUser()

MainMenu()

#========================================UTIL FUNCTIONS===================================
def UtilGenDailyReport():
	global cwd
	today = dt.today()
	d1 = today.strftime("%d/%m/%Y")
	querySearch = d1 + "-"
	response = (requests.post(connectApi + "/find", json = {"in_time" : {"$regex": querySearch}})).json()
	
	if not "docs" in response:
		df = pd.DataFrame([])
	else:
		cursor = response["docs"]
		df =  pd.DataFrame(list(cursor))
	if df.empty:
		tkMessageBox.showerror("Error", "No user visited today. Couldn't generate a report!\nPlease try again.")
		return
	df.pop('_id')
	df = df[['name', 'id', 'contact_no', 'destination', 'in_time', 'out_time', 'vehicle_no', 'purpose', 'relation', 'in_campus']]
	oldName = cwd + "/" + "Report.xlsx"
	oldName_csv = cwd + "/" + "Report.csv"
	File = d1
	nameSplit = File.split("/")
	tempName = nameSplit[0] + "-" + nameSplit[1] + "-" + nameSplit[2]
	fileName = cwd + "/" + tempName + "-DailyReport.xlsx"
	fileName_csv = cwd + "/" + tempName + "-DailyReport.csv"
	df.to_excel("Report.xlsx")
	df.to_csv("Report.csv", index=False)
	os.rename(oldName, fileName)
	os.rename(oldName_csv, fileName_csv)
	
def UtilGenerateReport():
	global GenerateReportEntry, allUsersDB, cwd
	if len(GenerateReportEntry.get()) == 0:
		tkMessageBox.showerror("Error", "Enter the month and year!!")
		ToggleToGenerateReport()
	else:
		querySearch = "/" + GenerateReportEntry.get() + "-"
		response = (requests.post(connectApi + "/find", json = {"in_time" : {"$regex": querySearch}})).json()
		if not "docs" in response:
			df = pd.DataFrame([])
		else:
			cursor = response["docs"]
			df =  pd.DataFrame(list(cursor))
		if df.empty:
			tkMessageBox.showerror("Error", "No user visited this month. Couldn't generate a report!\nPlease try again.")
			return
		df.pop('_id')
		df = df[['name', 'id', 'contact_no', 'destination', 'in_time', 'out_time', 'vehicle_no', 'purpose', 'relation', 'in_campus']]
		oldName = cwd + "/" + "Report.xlsx"
		oldName_csv = cwd + "/" + "Report.csv"
		File = GenerateReportEntry.get()
		nameSplit = File.split("/")
		tempName = nameSplit[0] + "-" + nameSplit[1]
		fileName = cwd + "/" + tempName + "-monthReport.xlsx"
		fileName_csv = cwd + "/" + tempName + "-monthReport.csv"
		df.to_excel("Report.xlsx")
		df.to_csv("Report.csv", index=False)
		os.rename(oldName, fileName)
		os.rename(oldName_csv, fileName_csv)
		tkMessageBox.showinfo("Success", "Report for " + GenerateReportEntry.get() + " month generated successfully.")
	
def UtilSearchUser():
	global searchedUserList, allUsersDB, SEARCH_FIELD, SEARCH_INPUT, SearchCheckBoxInput
	if (SEARCH_FIELD.get() == "Select the Filter for Searching"):
		tkMessageBox.showerror("Error", "Select some Filter for Searching!!")
		ToggleToSearchUser()
		return
	elif len(SEARCH_INPUT.get()) == 0:
		tkMessageBox.showerror("Error", "Enter the value of the filter selected!!")
		ToggleToSearchUser()
		return
	searchedUserList = []
	if(SearchCheckBoxInput.get() == 0):
		if (SEARCH_FIELD.get() == "Contact Number"):
			response = (requests.post(connectApi + "/find", json = {"contact_no" : SEARCH_INPUT.get()})).json()
			if not "docs" in response:
				searchedUser = []
			else:
				searchedUser = response["docs"]
		elif (SEARCH_FIELD.get() == "Vehicle Number"):
			response = (requests.post(connectApi + "/find", json = {"vehicle_no" : SEARCH_INPUT.get()})).json()
			if not "docs" in response:
				searchedUser = []
			else:
				searchedUser = response["docs"]
		elif (SEARCH_FIELD.get() == "User Id"):
			response = (requests.post(connectApi + "/find", json = {"id" : SEARCH_INPUT.get()})).json()
			if not "docs" in response:
				searchedUser = []
			else:
				searchedUser = response["docs"]
		elif (SEARCH_FIELD.get() == "In-Date (dd/mm/yyyy)"):
			response = (requests.post(connectApi + "/find", json = {"in_time" : {"$regex": SEARCH_INPUT.get()}})).json()
			if not "docs" in response:
				searchedUser = []
			else:
				searchedUser = response["docs"]
		else:
			response = (requests.post(connectApi + "/find", json = {"out_time" : {"$regex": SEARCH_INPUT.get()}})).json()
			if not "docs" in response:
				searchedUser = []
			else:
				searchedUser = response["docs"]
	else:
		if (SEARCH_FIELD.get() == "Contact Number"):
			response = (requests.post(connectApi + "/find", json = {"contact_no" : SEARCH_INPUT.get(), "in_campus" : True})).json()
			if not "docs" in response:
				searchedUser = []
			else:
				searchedUser = response["docs"]
		elif (SEARCH_FIELD.get() == "Vehicle Number"):
			response = (requests.post(connectApi + "/find", json = {"vehicle_no" : SEARCH_INPUT.get(), "in_campus" : True})).json()
			if not "docs" in response:
				searchedUser = []
			else:
				searchedUser = response["docs"]
		elif (SEARCH_FIELD.get() == "User Id"):
			response = (requests.post(connectApi + "/find", json = {"id" : SEARCH_INPUT.get(), "in_campus" : True})).json()
			if not "docs" in response:
				searchedUser = []
			else:
				searchedUser = response["docs"]
		elif (SEARCH_FIELD.get() == "In-Date (dd/mm/yyyy)"):
			response = (requests.post(connectApi + "/find", json = {"in_time" : {"$regex": SEARCH_INPUT.get()}, "in_campus" : True})).json()
			if not "docs" in response:
				searchedUser = []
			else:
				searchedUser = response["docs"]
		else:
			response = (requests.post(connectApi + "/find", json = {"out_time" : {"$regex": SEARCH_INPUT.get()}, "in_campus" : True})).json()
			if not "docs" in response:
				searchedUser = []
			else:
				searchedUser = response["docs"]
	for user in searchedUser:
		searchedUserList.append(user["name"] + " (" + user["in_time"] + ", " + user["out_time"] + ")")
	
	SEARCH_INPUT.set("")
	ToggleToShowSearchUser()

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
#========================================INITIALIZATION===================================
if __name__ == '__main__':
	root.mainloop()
