@echo off
echo Starting EduChrono Backend...
uvicorn app.main:app --reload
pause
