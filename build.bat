@echo off
pyinstaller --onefile --windowed --add-data "icon.png;." --add-data "background.png;." --icon=icon.png broadcast_me.py