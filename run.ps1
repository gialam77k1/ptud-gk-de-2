# Đặt lại chính sách của PowerShell trên Windows để đảm bảo chạy được file script
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force

# Kiểm tra python đã được tải chưa và phiên bản phù hợp không
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Python is not installed. Please install Python 3.10 or newer." -ForegroundColor Red
    exit 1
}

Write-Host "Found Python: $pythonVersion" -ForegroundColor Green

# Kiểm tra và xóa môi trường ảo cũ nếu tồn tại
if (Test-Path .\venv) {
    Write-Host "Removing existing virtual environment..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force .\venv
}

# Tạo môi trường ảo tên venv
Write-Host "Creating virtual environment..." -ForegroundColor Green
try {
    python -m venv venv
    if (-not $?) { throw "Failed to create virtual environment" }
} catch {
    Write-Host "Error: Failed to create virtual environment. Error: $_" -ForegroundColor Red
    exit 1
}

# Kích hoạt môi trường ảo
Write-Host "Activating virtual environment..." -ForegroundColor Green
try {
    .\venv\Scripts\activate
    if (-not $?) { throw "Failed to activate virtual environment" }
} catch {
    Write-Host "Error: Failed to activate virtual environment. Error: $_" -ForegroundColor Red
    exit 1
}

# Kiểm tra môi trường ảo đã được kích hoạt chưa
if (-not $env:VIRTUAL_ENV) {
    Write-Host "Error: Virtual environment activation failed" -ForegroundColor Red
    exit 1
}

# Nâng cấp pip
Write-Host "Upgrading pip..." -ForegroundColor Green
try {
    python.exe -m pip install --upgrade pip
    if (-not $?) { throw "Failed to upgrade pip" }
} catch {
    Write-Host "Error: Failed to upgrade pip. Error: $_" -ForegroundColor Red
    exit 1
}

# Tải các thư viện cần thiết
Write-Host "Installing dependencies..." -ForegroundColor Green
try {
    # Kiểm tra xem có file requirements.txt không
    if (Test-Path .\requirements.txt) {
        pip install -r requirements.txt
    } else {
        # Nếu không có file requirements.txt, cài đặt các gói cần thiết
        pip install flask flask-sqlalchemy flask-migrate flask-login
    }
    
    if (-not $?) { throw "Failed to install dependencies" }
} catch {
    Write-Host "Error: Failed to install dependencies. Error: $_" -ForegroundColor Red
    exit 1
}

Write-Host "
Installation completed successfully!" -ForegroundColor Green
Write-Host "
Starting Flask application...
" -ForegroundColor Cyan

# Thiết lập biến môi trường Flask nếu cần thiết
$env:FLASK_APP = "app.py"  # Đổi tên file này nếu file chính của bạn khác
$env:FLASK_DEBUG = "1"     # Bật chế độ debug

# Start Flask application
try {
    Write-Host "Running Flask with 'flask run --debug'..." -ForegroundColor Green
    flask run --debug
    if (-not $?) { throw "Failed to start Flask application" }
} catch {
    Write-Host "Error: Failed to start Flask application. Error: $_" -ForegroundColor Red
    exit 1
}