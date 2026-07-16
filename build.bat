@echo off
echo Installing dependencies...
pip install -r requirements.txt
pip install pyinstaller

echo.
echo Building SlapPC.exe ...
pyinstaller ^
  --onefile ^
  --windowed ^
  --icon=assets\icon.ico ^
  --name=SlapPC ^
  --add-data="sounds;sounds" ^
  --add-data="assets;assets" ^
  --hidden-import=sounddevice ^
  --hidden-import=sounddevice._sounddevice ^
  --hidden-import=pygame ^
  --hidden-import=pystray ^
  --hidden-import=PIL ^
  --hidden-import=customtkinter ^
  slappc.py

echo.
echo Done! Your EXE is in: dist\SlapPC.exe
pause
