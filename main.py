import json
import os  # os hilft uns zu prüfen, ob die Datei schon existiert
import datetime
# No GUI for now!!!!
# Test Build 1 Ready for Pre- Alpha

currentdateandtime = datetime.datetime.now()

newidea = 0
databasetemp = {}
if os.path.exists("database.json"):
    with open("database.json", "r", encoding="utf-8") as file:
        try:
            databasetemp = json.load(file)
            if isinstance(databasetemp, list):
                databasetemp = {}
        except json.JSONDecodeError:
            databasetemp = {}


countofideas = len(databasetemp)
coid = countofideas + 1
print(str(coid))

nameofidea = input("Enter your Ideas Name: ")
descriptionofidea = input("Describe this Idea: ")
nid = nameofidea

currentdateandtime = datetime.datetime.now()
cdnt = currentdateandtime

databasetemp[f"Idea{coid}"] = {
    "Name of Idea": f'{nid}',
    "Description": f'{descriptionofidea}',
    "Date and Time": f'{cdnt}'
}

print(databasetemp)

if nid == "":
    print("No Idea saved")

else:

    print("Saved")


with open("database.json", "w") as file:
    json.dump(databasetemp, file, indent=4)
