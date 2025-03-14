@echo off
echo ===== TASK MANAGEMENT APPLICATION SETUP =====
echo.

REM Kiểm tra Python đã được cài đặt chưa
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed. Please install Python before running this script.
    echo You can download Python at: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python found.
echo.

REM Kiểm tra virtualenv đã được cài đặt chưa
python -m pip show virtualenv > nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Installing virtualenv...
    python -m pip install virtualenv
    if %errorlevel% neq 0 (
        echo [ERROR] Unable to install virtualenv.
        pause
        exit /b 1
    )
)

echo [OK] Virtualenv installed.
echo.

REM Kiểm tra môi trường ảo đã tồn tại chưa
if not exist "venv" (
    echo [INFO] Creating virtual environment...
    python -m virtualenv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Unable to create virtual environment.
        pause
        exit /b 1
    )
) else (
    echo [OK] Virtual environment already exists.
)
echo.

REM Kích hoạt môi trường ảo
echo [INFO] Activating virtual environment...
call venv\Scripts\activate
if %errorlevel% neq 0 (
    echo [ERROR] Unable to activate virtual environment.
    pause
    exit /b 1
)
echo [OK] Virtual environment activated.
echo.

REM Kiểm tra file requirements.txt
if not exist "requirements.txt" (
    echo [INFO] requirements.txt not found. Creating default file...
    echo flask==2.0.1 > requirements.txt
    echo flask-sqlalchemy==2.5.1 >> requirements.txt
    echo flask-login==0.5.0 >> requirements.txt
    echo werkzeug==2.0.1 >> requirements.txt
    echo.
)

REM Cài đặt các gói từ requirements.txt
echo [INFO] Installing required packages...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Unable to install required packages.
    pause
    exit /b 1
)
echo [OK] Required packages installed.
echo.

REM Kiểm tra file app.py
if not exist "app.py" (
    echo [ERROR] app.py not found. Please check your project structure.
    pause
    exit /b 1
)

REM Tạo file run_app.bat để chạy ứng dụng
echo @echo off > run_app.bat
echo echo ===== TASK MANAGEMENT APPLICATION ===== >> run_app.bat
echo echo. >> run_app.bat
echo call venv\Scripts\activate >> run_app.bat
echo echo [INFO] Activating virtual environment... >> run_app.bat
echo echo [INFO] Opening web browser... >> run_app.bat
echo start "" http://localhost:5000 >> run_app.bat
echo echo [INFO] Application is running. Access http://localhost:5000 to use. >> run_app.bat
echo echo [INFO] Press Ctrl+C to stop the application. >> run_app.bat
echo echo. >> run_app.bat
echo python app.py >> run_app.bat
echo echo. >> run_app.bat
echo call venv\Scripts\deactivate >> run_app.bat
echo echo [INFO] Virtual environment deactivated. >> run_app.bat
echo echo ===== APPLICATION CLOSED ===== >> run_app.bat
echo pause >> run_app.bat

REM Khởi động ứng dụng và mở trình duyệt
echo ===== STARTING APPLICATION =====
echo.
echo [INFO] Opening web browser...
echo [INFO] Application is running. Access http://localhost:5000 to use.
echo [INFO] Press Ctrl+C to stop the application.
echo.

REM Mở trình duyệt web
start "" http://localhost:5000

REM Chạy ứng dụng
python app.py

REM Khi ứng dụng dừng, hỏi người dùng có muốn thoát khỏi môi trường ảo không
echo.
set /p deactivate_choice="Do you want to deactivate the virtual environment? (Y/N): "
if /i "%deactivate_choice%"=="Y" (
    call venv\Scripts\deactivate
    echo [INFO] Virtual environment deactivated.
) else (
    echo [INFO] Still in virtual environment. Type 'deactivate' to exit when needed.
)

echo.
echo ===== COMPLETED =====
pause 