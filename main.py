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


Idea + coid = {




}

if nid == "":
    print("No Idea saved")

else:
    print("Your Idea: " + str(nid))
    print("Saved")



