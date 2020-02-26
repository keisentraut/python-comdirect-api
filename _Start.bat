
@echo off

cls

REM Please start the program in your mapped folder e.g. C: or D: 
set direc="%cd%"
echo %time% Work on %direc%...

if not exist %direc%\%datei% echo File not found! STOP! && pause && exit

echo %time% Check if all Python components are installed...
echo ------------------------------------------------------------------------
pip install -r requirements.txt
echo ------------------------------------------------------------------------

echo %time% Start...

python %direc%\start.py %direc%

echo %time% Finished!

pause
