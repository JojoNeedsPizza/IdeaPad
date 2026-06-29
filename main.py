import json
import datetime
# No GUI for now!!!!


currentdateandtime = datetime.datetime.now()

newidea = 0


with open("database.json", "r", encoding="utf-8") as file:
    idea_list = json.load(file)


# Testing
nameofidea = "Hi"
descriptionofidea = "Bye"

countofideas = len(idea_list)

coid = countofideas
print(str(coid))

nameofidea = input("Enter your Ideas Name: ")

nid = nameofidea

currentdateandtime = datetime.datetime.now()
cdnt = currentdateandtime
databasetemp = {}
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
    print("Your Idea: " + str(nid))
    print("Saved")



