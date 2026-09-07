import datetime
import tkinter
import json
import sys
import os


file_path = "results.json"


if os.path.exists(file_path):
    



print("Got an Idea? Write it down")

idea = input("Enter your idea: ")
description = input("Describe your idea: ")
date = datetime.datetime.now()
idea_number = total_lines + 1
ideadict = {"ID":idea_number, "Idea": idea, "Description": description}
json_string = json.dumps(ideadict, indent=2)

print(json_string)

print(ideadict)
if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
    with open('result.json', 'r') as read_file_save:
        savefileforstopoverwrite = json.load(read_file_save)


        writefiletosave =  str(savefileforstopoverwrite)  + str(ideadict)

        writetojson = json.dumps(writefiletosave, indent=2)

        with open(file_path, 'w') as fp:
            json.dump(writetojson, fp, indent=2)

else:
    with open(file_path, 'w') as fp:
            json.dump(json_string, fp, indent=2)

