import json
import os  # os hilft uns zu prüfen, ob die Datei schon existiert
import datetime
# No GUI for now!!!!


currentdateandtime = datetime.datetime.now()

newidea = 0
# Ersetze deinen alten Lade-Block mit diesem:
databasetemp = {}
if os.path.exists("database.json"):
    with open("database.json", "r", encoding="utf-8") as file:
        try:
            databasetemp = json.load(file)
            # Falls die Datei eine Liste war, erzwingen wir ein Dictionary
            if isinstance(databasetemp, list):
                databasetemp = {}
        except json.JSONDecodeError:
            databasetemp = {}

# Testing
nameofidea = "Hi"
descriptionofidea = "Bye"

countofideas = len(databasetemp)
coid = countofideas + 1
print(str(coid))

nameofidea = input("Enter your Ideas Name: ")

nid = nameofidea

currentdateandtime = datetime.datetime.now()
cdnt = currentdateandtime
# Example
# 3. Deine Formel angewendet: Wir fügen das Dictionary direkt unter der Zahl ein
databasetemp[f"Idea{coid}"] = {
    "Name of Idea": f'{nid}',
    "Description": f'{descriptionofidea}',
    "Date and Time": f'{cdnt}'
}
# Wenn du jetzt das Haupt-Dictionary druckst:
print(databasetemp)

if nid == "":
    print("No Idea saved")

else:

    print("Saved")


with open("database.json", "w") as file:
    json.dump(databasetemp, file, indent=4)
