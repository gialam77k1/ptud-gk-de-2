# Hệ thống Quản lý Công việc
## Thông tin sinh viên 
- Tên : Nguyễn Gia Lâm
- STT : 36
- MSSV : 22685611

## Giới thiệu

Đây là một hệ thống quản lý công việc được xây dựng bằng Python Flask, cho phép người dùng theo dõi và quản lý các nhiệm vụ của mình. Hệ thống hỗ trợ phân quyền người dùng, quản lý tiến độ công việc và thông báo deadline.

## Tính năng

- **Quản lý người dùng**: Phân quyền admin và user thông thường
- **Quản lý công việc**: Tạo, xem, cập nhật và xóa công việc
- **Theo dõi tiến độ**: Hiển thị tỷ lệ hoàn thành công việc theo người dùng
- **Thông báo deadline**: Cảnh báo về các công việc đang trễ hạn
- **Giao diện trực quan**: Sử dụng Bootstrap để tạo giao diện thân thiện với người dùng

## Công nghệ sử dụng

- **Backend**: Python Flask
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Database**: SQLite/PostgreSQL
- **Authentication**: Flask-Login
- **Template Engine**: Jinja2

## Cài đặt

### Yêu cầu hệ thống

- Python 3.8+
- pip

### Các bước cài đặt


1. Clone repository:
```
git clone https://github.com/gialam77k1/ptud-gk-de-2.git
cd ptud-gk-de-2
```

2. Tạo môi trường ảo:
```
python -m venv venv
venv\Scripts\activate
```
## Chạy bằng file shell script
```
.\run.ps1
```
## Chạy từng lệnh
3. Cài đặt dependencies:
```
python.exe -m pip install --upgrade pip
```
```
pip install -r requirements.txt
```

4. Khởi chạy ứng dụng:
```
flask run
```



## Sử dụng

1. Truy cập ứng dụng tại địa chỉ `http://localhost:5000`
2. Đăng nhập với tài khoản admin mặc định:
   - Username: admin
   - Password: admin123
3. Thêm người dùng mới và quản lý công việc
