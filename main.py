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
                                                GitHub: https://github.com/JojoNeedsPizza/IdeaPad
                                                Profile: https://github.com/JojoNeedsPizza                                                                                                       
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

def clear_terminal():
    # Führt den passenden Terminal-Befehl für dein Betriebssystem aus
    os.system('cls' if os.name == 'nt' else 'clear')

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
        input("\nPress ENTER to return to the main menu...")
        return

    else:
       with open("database.json", "w") as file:
        json.dump(databasetemp, file, indent=4)
        print("Idea Saved Successfully!")
        input("\nPress ENTER to return to the main menu...")




#---------------------------------------------------
#|                Show all Ideas                   |
#---------------------------------------------------
def show_ideas():
    print(show_all_ideas)
    databasetemp = {}
    if os.path.exists("database.json"):
        with open("database.json", "r", encoding="utf-8") as file:
            try:
                databasetemp = json.load(file)
            except json.JSONDecodeError:
                pass

    # 2. Prüfen, ob die Datenbank leer ist
    if not databasetemp:
        print("Es wurden noch keine Ideen gespeichert! Schnapp dir einen Kaffee und werd kreativ. ☕")
        return

    # 3. Jede Idee einzeln und hübsch formatiert ausgeben
    for idea_id, data in databasetemp.items():
        print(f"💡 [{idea_id}]")
        print(f"   Name:        {data.get('Name of Idea', 'Unbekannt')}")
        print(f"   Beschreibung:{data.get('Description', 'Keine Beschreibung')}")
        print(f"   Gespeichert: {data.get('Date and Time', '-')}")
        print("-" * 35)  # Trennlinie zwischen den Ideen
    input("\nPress ENTER to return to the main menu...")











# --------------------------------------------------
#|                  Main Menu                      |
#---------------------------------------------------

def main_menu():
    while True:
        clear_terminal()


        titel = r"""
        


  ######         ##                      ######:                   ##            . ####:              .####.             
  ######         ##                      #######:                  ##            #######:             ######            
    ##           ##                      ##   :##                  ##            #:.   ##            :##  ##:            
    ##      :###.##   .####:    :####    ##    ##   :####     :###.##                  ##            ##:  :##            
    ##     :#######  .######:   ######   ##   :##   ######   :#######                 :#             ##    ##             
    ##     ###  ###  ##:  :##   #:  :##  #######:   #:  :##  ###  ###                 ##             ## ## ##             
    ##     ##.  .##  ########    :#####  ######:     :#####  ##.  .##               .##:             ## ## ##             
    ##     ##    ##  ########  .#######  ##        .#######  ##    ##              .##:              ##    ##              
    ##     ##.  .##  ##        ## .  ##  ##        ## .  ##  ##.  .##             :##:               ##:  :##            
    ##     ###  ###  ###.  :#  ##:  ###  ##        ##:  ###  ###  ###            :##:         ##     :##  ##:              
  ######   :#######  .#######  ########  ##        ########  :#######            ########     ##      ######               
  ######    :###.##   .#####:    ###.##  ##          ###.##   :###.##            ########     ##      .####.               


                                               Made by JojoNeedsPizza  --Still in developement
                                                GitHub: https://github.com/JojoNeedsPizza/IdeaPad
                                                Profile: https://github.com/JojoNeedsPizza  
                                                
                                                
                                                
                                                ---------------------------------------------------
                                                |                  Main Menu                      |
                                                ---------------------------------------------------
                                                
                                                (Use the Arrow Keys to steer and press Enter to select)
        """
        optionen = ["1. Add a new Idea", "2. Show Ideas", "3. Exit Program"]
        option, index = pick(optionen, titel, indicator="=>", default_index=0)
        if index == 0:
          add_idea()
        elif index == 1:
           show_ideas()
        elif index == 2:
           print("Goodbye!")
           break



# Show Ideas Func = show_ideas()
# Main Menu Func = main_menu()
# Add New Idea Func = add_idea()

# Dieser Befehl sorgt dafür, dass das Menü beim Starten anspringt
if __name__ == "__main__":
    main_menu()
