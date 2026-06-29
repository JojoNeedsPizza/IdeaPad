import json
import os  # os hilft uns zu prüfen, ob die Datei schon existiert
import datetime
from pick import pick
# No GUI for now!!!!
# Test Build 1 Ready for Pre- Alpha

logotext = r"""



  ######         ##                      ######:                   ##            . ####:              .####.             #####:    ########  ##:  :## 
  ######         ##                      #######:                  ##            #######:             ######             #######   ########  ##    ## 
    ##           ##                      ##   :##                  ##            #:.   ##            :##  ##:            ##  :##:  ##        :##  ##: 
    ##      :###.##   .####:    :####    ##    ##   :####     :###.##                  ##            ##:  :##            ##   :##  ##        :##  ##: 
    ##     :#######  .######:   ######   ##   :##   ######   :#######                 :#             ##    ##            ##   .##  ##         ## .##  
    ##     ###  ###  ##:  :##   #:  :##  #######:   #:  :##  ###  ###                 ##             ## ## ##            ##    ##  #######    ##::##  
    ##     ##.  .##  ########    :#####  ######:     :#####  ##.  .##               .##:             ## ## ##            ##    ##  #######    ##::##  
    ##     ##    ##  ########  .#######  ##        .#######  ##    ##              .##:              ##    ##            ##   .##  ##         :####:  
    ##     ##.  .##  ##        ## .  ##  ##        ## .  ##  ##.  .##             :##:               ##:  :##            ##   :##  ##         .####.  
    ##     ###  ###  ###.  :#  ##:  ###  ##        ##:  ###  ###  ###            :##:         ##     :##  ##:            ##  :##:  ##          ####   
  ######   :#######  .#######  ########  ##        ########  :#######            ########     ##      ######             #######   ########    ####   
  ######    :###.##   .#####:    ###.##  ##          ###.##   :###.##            ########     ##      .####.             #####:    ########     ##    


                                               Made by JojoNeedsPizza  --Still in developement                                                                                                       
"""
main_menu_ui_title = r"""
---------------------------------------------------
|                  Main Menu                      |
---------------------------------------------------
"""

add_new_idea = r"""
---------------------------------------------------
|              Add a new Idea                     |
---------------------------------------------------
"""

show_all_ideas = r"""
---------------------------------------------------
|                Show all Ideas                   |
---------------------------------------------------
"""



#---------------------------------------------------
#|              Add a new Idea                     |
#---------------------------------------------------
def add_idea():
    print(add_new_idea)
    currentdateandtime = datetime.datetime.now()
    databasetemp = {}
    if os.path.exists("database.json"):
        with open("database.json", "r", encoding="utf-8") as file:
            try:
               databasetemp = json.load(file)

            except json.JSONDecodeError:
                databasetemp = {}

            if isinstance(databasetemp, list):
                databasetemp = {}


    countofideas = len(databasetemp)
    coid = countofideas + 1
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

    if nid == "":
        print("No Idea saved")

    else:
       with open("database.json", "w") as file:
        json.dump(databasetemp, file, indent=4)
        print("Idea Saved Successfully!")

#---------------------------------------------------
#|                Show all Ideas                   |
#---------------------------------------------------
def show_ideas():











# --------------------------------------------------
#|                  Main Menu                      |
#---------------------------------------------------

def main_menu():
 print(main_menu_ui_title)
 titel = "\n(Use the Arrow Keys to steer and press Enter to select)"
 optionen = ["1. Add a new Idea", "2. Show Ideas", "3. Exit Program"]
 option, index = pick(optionen, titel, indicator="=>", default_index=0)
 if index == 0:
    add_idea()
 elif index == 1:
    show_ideas()
 elif index == 2:
    print("Goodbye!")


