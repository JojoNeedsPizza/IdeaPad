import json
# No GUI for now!!!!
newidea = 0


with open("database.json", "r", encoding="utf-8") as file:
    idea_list = json.load(file)


countofideas = len(idea_list)

coid = countofideas
print(str(coid))

newidea = input("Enter your Idea: ")

nid = newidea


# 3. Deine Formel angewendet: Wir fügen das Dictionary direkt unter der Zahl ein
["neues_dict" + str(coid)] = {
    "Name of Idea": "Smart Trash Can",
    "Description": "Ein Mülleimer, der Chips-Tüten automatisch scannt und nachbestellt."
}

# Wenn du jetzt das Haupt-Dictionary druckst:
print(datenbank)

if nid == "":
    print("No Idea saved")

else:
    print("Your Idea: " + str(nid))
    print("Saved")



