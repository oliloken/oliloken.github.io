@echo off
cd /d "%~dp0"
echo Building photo list...
python build_gallery.py || py build_gallery.py
echo.
pause
