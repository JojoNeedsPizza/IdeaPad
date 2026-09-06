import datetime
import tkinter
import json
import sys
import os
print("Got an Idea? Write it down")

idea = input("Enter your idea: ")
description = input("Describe your idea: ")
date = datetime.datetime.now()

ideadict = {"Idea": idea, "Description": description}


print(ideadict)
if os.path.exists("./result.json") and os.path.getsize("./result.json") > 0:
    with open('result.json', 'r') as read_file_save:
        savefileforstopoverwrite = json.load(read_file_save)

        writefiletosave =  str(savefileforstopoverwrite) + "\n" + str(ideadict)

        print(writefiletosave)

        with open('result.json', 'w') as fp:
            json.dump(writefiletosave, fp)

else:
    with open('result.json', 'w') as fp:
            json.dump(ideadict, fp)

