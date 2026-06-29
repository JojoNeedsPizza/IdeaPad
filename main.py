import json
# No GUI for now!!!!
newidea = 0


with open("database.json", "r", encoding="utf-8") as file:
    idea_list = json.load(file)


# Testing
nameofidea = "Hi"
descriptionofidea = "Bye"

countofideas = len(idea_list)

coid = countofideas
print(str(coid))

newidea = input("Enter your Idea: ")

nid = newidea

datenbank = {}
# Example
# 3. Deine Formel angewendet: Wir fügen das Dictionary direkt unter der Zahl ein
datenbank[f"Idea{coid}"] = {
    "Name of Idea": f'{nameofidea}',
    "Description": f'{descriptionofidea}'
}
# Wenn du jetzt das Haupt-Dictionary druckst:
print(datenbank)

if nid == "":
    print("No Idea saved")

else:
    print("Your Idea: " + str(nid))
    print("Saved")



