@echo off 
echo ===== TASK MANAGEMENT APPLICATION ===== 
echo. 
call venv\Scripts\activate 
echo [INFO] Activating virtual environment... 
echo [INFO] Opening web browser... 
start "" http://localhost:5000 
echo [INFO] Application is running. Access http://localhost:5000 to use. 
echo [INFO] Press Ctrl+C to stop the application. 
echo. 
python app.py 
echo. 
call venv\Scripts\deactivate 
echo [INFO] Virtual environment deactivated. 
echo ===== APPLICATION CLOSED ===== 
pause 
