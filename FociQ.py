# -*- coding: utf-8 -*-
"""
Created on Tue Sep 25 12:48:39 2018

@author: Phil Honl
"""
wd = ""
import os
import sys
import threading
import time
import subprocess
from tkinter import *
import tkinter.scrolledtext as ScrolledText
import tkinter.font as tkFont
from tkinter import filedialog
import config
import evaluation
import datetime

folders = []
files = []
print("Working in directory: " + wd)


class App:
    
    def __init__(self, master):
        
       
        def updateLog(text):
            #Updates log window with given text
            self.user_log.configure(state="normal")
            text = text + "\n"
            self.user_log.insert(END, text)
            self.user_log.see("end")
            self.user_log.configure(state="disabled")
            pass
        
        def choosePath(event=None):
            #Opens file dialog to search 
            global dirname
            print("Select a directory.")
            dirname = filedialog.askdirectory(initialdir=os.getcwd(),title='Please select a directory')
            if len(dirname) > 0:
                print ("Chose" + str(dirname))
            else: 
                print ("No directory selected.. Using config.")
            self.path_field_image.delete("1.0", END) 
            self.path_field_image.insert(CURRENT, dirname)   
            updateLog("Updated Path to: " + dirname)
                       
        def startThread():
            #starts a thread which starts ImageJ
             config.writeCfg(os.getcwd(), dirname, self.noise_field.get("1.0", END+"-1c"), self.noise_field_r.get("1.0", END+"-1c"), self.background_field.get("1.0", END+"-1c"), self.background_field_r.get("1.0", END+"-1c"), self.channel_green.get(), self.channel_red.get())
             updateLog("Saving parameters...")
             updateLog("Starting IJ macro...")
             global t
             t = threading.Thread(target=startIj())
             t.start()

        def startIj():
            #start ImageJ in new subprocess with given params
            global child, start_time_ij
            start_time_ij = datetime.datetime.now().replace(microsecond=0)
            child = subprocess.Popen(["java", "-jar", "ij.jar", "-m", "foci.ijm"])            #,  "-m", "foci.ijm"
            t1 = threading.Thread(target=startEvaluation)
            t1.start()
                        
        def startEvaluation():
            #start evaluation of files after IJ is done locating foci
            while child.poll() is None:
                time.sleep(1)
            updateLog("IJ done...")
            updateLog("Starting evaluation...")
            evaluation.scanFolders(dirname)
            computation_time = datetime.datetime.now().replace(microsecond=0) - start_time_ij
            updateLog("Finished after " + str(computation_time) +". Check Results folder!")
            
            
        def checkIJ():
            #checks if IJ jar is in path of FociQ
            return "ij" in os.listdir(os.getcwd())
            
        
        def checkInput(path):
            #check if paths and ij.jar exists and starts thread
            if os.path.exists(path) and "ij.jar" in os.listdir(os.getcwd()):
                startThread()
            elif not os.path.exists(path):
                updateLog("Error: path does not exist.")
            elif not "ij.jar" in os.listdir(os.getcwd()):
                updateLog("Error: ij.jar not found.")
                
        global dirname
        dirname = config.readCfg(os.getcwd())[4]
        #master settings
        self.master = master
        master.title("FociQ")
        master.geometry('650x380')
        #master.configure(background='grey')
        self.font = tkFont.Font(family="courier", size=8)
        #Path text label and input label
        self.choose_label = Label(master, text = "Image path: ")
        self.choose_label.grid(column = 0, row = 0, sticky = W, padx = 10)
        self.path_field_image =Text(root, height = 1, width =100)
        self.path_field_image.grid(column = 0, row = 1, padx = 10, columnspan = 7, sticky = W)
        self.path_field_image.insert(CURRENT, config.readCfg(os.getcwd())[4])
        #Choose path btn
        self.choose_btn = Button(root, text="...", command = choosePath)
        self.choose_btn.grid(column = 8, row = 1, sticky = W, padx = 10)
        #Noise text label and input label
        self.noise_label = Label(master, text = "Noise (Find Maxima): ")
        self.noise_label.grid(column = 0, row = 3, sticky = W, padx = 10, columnspan=1)
        self.noise_field_label = Label(master, text = "Green Channel: ", fg = "green")
        self.noise_field_label.grid(column = 0, row = 4, sticky = W, padx = 10, columnspan=1)
        self.noise_field = Text(root, height = 1, width = 10)
        self.noise_field.insert(CURRENT, config.readCfg(os.getcwd())[0])
        self.noise_field.grid(column = 1, row = 4, sticky = W, padx = 0)
        self.noise_field_label_r = Label(master, text = "Red Channel: ", fg = "red")
        self.noise_field_label_r.grid(column = 2, row = 4, sticky = W, padx = 10, columnspan=1)
        self.noise_field_r = Text(root, height = 1, width = 10)
        self.noise_field_r.insert(CURRENT, config.readCfg(os.getcwd())[2])
        self.noise_field_r.grid(column = 3, row = 4, sticky = W, padx = 0)
        
        #Background subtraction radius text label and input label
        self.background_label = Label(master, text = "Background Subtraction Radius: ")
        self.background_label.grid(column = 0, row = 5, sticky = W, padx = 10, columnspan=1)
        self.background_field_label = Label(master, text = "Green Channel:", padx = 10, fg = "green")
        self.background_field_label.grid(column = 0, row = 6, sticky = W, padx = 0, columnspan=1)
        self.background_field = Text(root, height = 1, width = 10)
        self.background_field.insert(CURRENT, config.readCfg(os.getcwd())[1])
        self.background_field.grid(column = 1, row = 6, sticky = W, padx = 0)
        
        self.background_field_label_r = Label(master, text = "Red Channel:", padx = 10, fg = "red")
        self.background_field_label_r.grid(column = 2, row = 6, sticky = W, padx = 0)
        self.background_field_r = Text(root, height = 1, width = 10)
        self.background_field_r.insert(CURRENT, config.readCfg(os.getcwd())[3])
        self.background_field_r.grid(column = 3, row = 6, sticky = W, padx = 0)

        #Checkbox for Channels 
        self.channel_green =  IntVar(value=config.readCfg(os.getcwd())[5])
        self.channel_red = IntVar(value=config.readCfg(os.getcwd())[6])
        self.channel_box_label = Label(master, text = "Foci Channels:")
        self.channel_box_label.grid(column = 0, row = 7, sticky = W, padx = 10)
        self.channel_box_green = Checkbutton(master, text = "Green", variable=self.channel_green, fg = "green")
        self.channel_box_green.grid(column = 0, row = 8, sticky = W, padx = 10)
        self.channel_box_Red = Checkbutton(master, text = "Red", variable=self.channel_red, fg = "red")
        self.channel_box_Red.grid(column = 0, row = 9, sticky = W, padx = 10)
        #User log text and input label
        self.user_log_label = Label(master, text = "Log:")
        self.user_log_label.grid(column = 0, row = 10, sticky = W, padx = 10)
        self.user_log = ScrolledText.ScrolledText(root, height = 5, width = 95, font = self.font)
        self.user_log.grid(column = 0, row = 11, sticky = W, padx = 10, columnspan = 5)
        self.user_log.configure(state="disabled")
        updateLog("Ready...")
        #Execute button for foci counting
        self.start_btn = Button(root, text="Go!", command = lambda : checkInput(dirname))
        self.start_btn.grid(column = 0, row = 12, sticky = W, padx = 10, pady = 10)
        
        self.version = Label(master, text = "1.1.0")
        self.version.grid(column = 6, row = 15, sticky = E)

root = Tk()
root.iconbitmap("icon.ico")
root.grid_columnconfigure(1, weight=1)
gui = App(root)
root.mainloop()
