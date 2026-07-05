@echo off

echo Hello, i am your IdeaPad Setup Assistant, i'll help you with the Installation Process, so lets get Started!
echo -- Windows Setup only --
pause

set /p chosen_path_of_installation=Enter your desired Path, where IdeaPad should be installed and Press Enter (if left blank it gets installed in Documents):


if "%chosen_path_of_installation%"=="" (
    set chosen_path_of_installation=%USERPROFILE%\Documents
    echo Installation Path now is %USERPROFILE%\Documents
) else (
echo Installation Path now is %chosen_path_of_installation%
)



mkdir "%chosen_path_of_installation%\Idea Pad"
curl -L -o "%chosen_path_of_installation%\Idea Pad\Idea.Pad.2.0.exe" "https://github.com/JojoNeedsPizza/IdeaPad/releases/download/Prerelease1.0/Idea.Pad.2.0.exe"
curl -L -o "%chosen_path_of_installation%\Idea Pad\idea_daemon.exe" "https://github.com/JojoNeedsPizza/IdeaPad/releases/download/Prerelease1.0/Idea.Pad.2.0.exe"

echo Do you want, that the IdeaBar gets added to the Autostart?
echo.
echo Enter "1" if yes or "2" if not
set /p autostart_y_n=Enter your pick and press ENTER:
if "%autostart_y_n%"=="1" (
curl -L -o "%chosen_path_of_installation%\Idea Pad\settings.json" "https://raw.githubusercontent.com/JojoNeedsPizza/IdeaPad/refs/heads/main/setup/Autostartoptions/Autostarttrue/settings.json"
) else (
curl -L -o "%chosen_path_of_installation%\Idea Pad\settings.json" "https://raw.githubusercontent.com/JojoNeedsPizza/IdeaPad/refs/heads/main/setup/Autostartoptions/Autostartfalse/settings.json"
)

echo.
echo Allright, ur all set, Idea Pad is ready to use, have fun and Never forget an Idea ever again
echo -Developed by JojoNeedsPizza
pause