import datetime
import tkinter

print("Got an Idea? Write it down")

idea = input("Enter your idea: ")
description = input("Describe your idea: ")
Date = datetime.datetime.now()

idea = {"Idea": idea, "Description": description }

