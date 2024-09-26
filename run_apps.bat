@echo off
REM Activate the virtual environment
call venv\Scripts\activate.bat

REM Start the transcription service
start cmd /k python transcript.py

REM Start the report service
start cmd /k python report.py

REM Start the main Flask app
start cmd /k python main.py

REM Keep the script running
pause