import ideabase

# No GUI for now!!!!
idb = ideabase.idbase

newidea = 0

newidea = input("Enter your Idea: ")

nid = newidea

if nid == "":
    print("No Idea saved")

else:
    print(nid)
    print("Idea Saved")
