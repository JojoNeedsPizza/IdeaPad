@echo off

echo Hello, i am your IdeaPad Setup Assistant, i'll help you with the Installation Process, so lets get Started!
echo -- Windows Setup only --
pause

set /p chosen_path_of_installation=Enter your desired Path, where IdeaPad should be installed and Press Enter (if left blank it gets installed in Documents):
::echo %chosen_path_of_installation%

if "%chosen_path_of_installation%"=="" (
    set chosen_path_of_installation=%USERPROFILE%\Documents
    echo Installation Path now is %USERPROFILE%\Documents
) else (
echo path
)

pause

mkdir "%chosen_path_of_installation%\Idea Pad"
curl -L -o "%chosen_path_of_installation%\Idea Pad\Idea.Pad.2.0.exe" "https://github.com/JojoNeedsPizza/IdeaPad/releases/download/Prerelease1.0/Idea.Pad.2.0.exe"
curl -L -o "%chosen_path_of_installation%\Idea Pad\idea_daemon.exe" "https://github.com/JojoNeedsPizza/IdeaPad/releases/download/Prerelease1.0/Idea.Pad.2.0.exe"

echo Do you want, that the IdeaBar gets in the Autostart?

