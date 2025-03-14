from flask import Flask, render_template, redirect, url_for, request, flash, send_from_directory, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Task, Category
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import uuid

app = Flask(__name__)
app.config.from_object('config.Config')
db.init_app(app)
login_manager = LoginManager(app)

# Cấu hình upload file
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads', 'avatars')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Danh sách màu mặc định cho danh mục
DEFAULT_COLORS = [
    '#4caf50',  # Xanh lá
    '#2196f3',  # Xanh dương
    '#f44336',  # Đỏ
    '#ff9800',  # Cam
    '#9c27b0',  # Tím
    '#795548',  # Nâu
    '#607d8b',  # Xám xanh
    '#e91e63',  # Hồng
    '#009688',  # Xanh ngọc
    '#ffeb3b',  # Vàng
]

# Tạo tài khoản admin cố định nếu chưa tồn tại
def create_admin_account():
    with app.app_context():
        print("Đang kiểm tra tài khoản admin...")
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            print("Không tìm thấy tài khoản admin, đang tạo mới...")
            hashed_password = generate_password_hash('admin123')
            admin = User(username='admin', password=hashed_password, role='admin')
            db.session.add(admin)
            db.session.commit()
            print("Đã tạo tài khoản admin mặc định")
        else:
            # Nếu tài khoản admin tồn tại nhưng không có quyền admin, cập nhật quyền
            if admin.role != 'admin':
                print(f"Tài khoản admin đã tồn tại nhưng không có quyền admin, đang cập nhật...")
                admin.role = 'admin'
                db.session.commit()
                print(f"Đã cập nhật tài khoản {admin.username} thành admin")
            else:
                print(f"Đã tìm thấy tài khoản admin: {admin.username}, role: {admin.role}")

# Gọi hàm tạo admin khi khởi động ứng dụng
with app.app_context():
    create_admin_account()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            # Kiểm tra xem tài khoản có bị khóa không
            if user.is_blocked:
                return render_template('index.html', error="Tài khoản của bạn đã bị khóa!")
            
            login_user(user)
            
            # Nếu là admin, chuyển hướng đến trang quản lý admin
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            
            # Nếu là user thông thường, chuyển hướng đến dashboard
            return redirect(url_for('dashboard'))
        else:
            return render_template('index.html', error="Tên đăng nhập hoặc mật khẩu không đúng!")
    
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = 'user'  # Đặt mặc định là user
        
        # Kiểm tra xem username đã tồn tại chưa
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return render_template('register.html', error="Tên đăng nhập đã tồn tại!")
        
        # Tạo user mới
        hashed_password = generate_password_hash(password)
        user = User(username=username, password=hashed_password, role=role)
        db.session.add(user)
        db.session.commit()
        
        # Đăng nhập người dùng sau khi đăng ký
        login_user(user)
        return redirect(url_for('dashboard'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        print(f"Đang xử lý đăng nhập cho user: {username}")
        user = User.query.filter_by(username=username).first()
        
        if user:
            print(f"Tìm thấy user: {user.username}, role: {user.role}")
            if check_password_hash(user.password, password):
                print("Mật khẩu chính xác")
                # Kiểm tra xem tài khoản có bị khóa không
                if user.is_blocked:
                    print("Tài khoản bị khóa")
                    return render_template('index.html', error="Tài khoản của bạn đã bị khóa!")
                
                login_user(user)
                print("Đăng nhập thành công")
                
                # Nếu là admin, chuyển hướng đến trang quản lý admin
                if user.role == 'admin':
                    print("Chuyển hướng đến trang admin")
                    return redirect(url_for('admin_dashboard'))
                
                # Nếu là user thông thường, chuyển hướng đến dashboard
                print("Chuyển hướng đến trang dashboard")
                return redirect(url_for('dashboard'))
            else:
                print("Mật khẩu không chính xác")
        else:
            print("Không tìm thấy user")
        
        return render_template('index.html', error="Tên đăng nhập hoặc mật khẩu không đúng!")
    
    # Chuyển hướng đến trang chủ thay vì hiển thị trang login riêng biệt
    return redirect(url_for('index'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Decorator để kiểm tra quyền admin
def admin_required(f):
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    # Lấy tất cả các task của admin và sắp xếp theo deadline
    tasks = Task.query.filter_by(user_id=current_user.id).order_by(
        # Đặt các task không có deadline xuống cuối
        Task.deadline.is_(None).asc(),
        # Sắp xếp các task có deadline từ gần nhất đến xa nhất
        Task.deadline.asc()
    ).all()
    
    # Tính số lượng task đã quá hạn
    now = datetime.now()
    overdue_count = 0
    for task in tasks:
        if task.deadline and task.deadline < now and task.status == 'Pending':
            overdue_count += 1
    
    return render_template('admin/dashboard.html', tasks=tasks, overdue_count=overdue_count)

@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    users = User.query.filter(User.role != 'admin').all()
    
    # Tính số lượng task đã quá hạn
    now = datetime.now()
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    overdue_count = 0
    for task in tasks:
        if task.deadline and task.deadline < now and task.status == 'Pending':
            overdue_count += 1
    
    return render_template('admin/users.html', users=users, overdue_count=overdue_count)

@app.route('/admin/block_user/<int:user_id>')
@login_required
@admin_required
def admin_block_user(user_id):
    user = User.query.get_or_404(user_id)
    
    # Không cho phép khóa tài khoản admin
    if user.role == 'admin':
        return redirect(url_for('admin_users'))
    
    user.is_blocked = True
    db.session.commit()
    return redirect(url_for('admin_users'))

@app.route('/admin/unblock_user/<int:user_id>')
@login_required
@admin_required
def admin_unblock_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_blocked = False
    db.session.commit()
    return redirect(url_for('admin_users'))

@app.route('/admin/delete_user/<int:user_id>')
@login_required
@admin_required
def admin_delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    # Không cho phép xóa tài khoản admin
    if user.role == 'admin':
        return redirect(url_for('admin_users'))
    
    # Xóa tất cả các task của user
    Task.query.filter_by(user_id=user.id).delete()
    
    # Xóa tất cả các category của user
    Category.query.filter_by(user_id=user.id).delete()
    
    # Xóa user
    db.session.delete(user)
    db.session.commit()
    
    return redirect(url_for('admin_users'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Lấy tất cả các task của người dùng và sắp xếp theo deadline
    # Các task không có deadline sẽ được đặt ở cuối danh sách
    tasks = Task.query.filter_by(user_id=current_user.id).order_by(
        # Đặt các task không có deadline xuống cuối
        Task.deadline.is_(None).asc(),
        # Sắp xếp các task có deadline từ gần nhất đến xa nhất
        Task.deadline.asc()
    ).all()
    
    # Tính số lượng task đã quá hạn
    now = datetime.now()
    overdue_count = 0
    for task in tasks:
        if task.deadline and task.deadline < now and task.status == 'Pending':
            overdue_count += 1
    
    return render_template('dashboard.html', tasks=tasks, overdue_count=overdue_count)

@app.route('/add_task', methods=['POST'])
@login_required
def add_task():
    title = request.form['title']
    deadline_str = request.form.get('deadline')
    
    task = Task(title=title, user_id=current_user.id)
    
    if deadline_str and deadline_str.strip():
        try:
            deadline = datetime.fromisoformat(deadline_str)
            task.deadline = deadline
        except ValueError:
            # Nếu định dạng không hợp lệ, bỏ qua
            pass
    
    db.session.add(task)
    db.session.commit()
    flash('Nhiệm vụ đã được thêm thành công!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/complete_task/<int:task_id>')
@login_required
def complete_task(task_id):
    task = Task.query.get(task_id)
    if task and task.user_id == current_user.id:
        task.status = 'Completed'
        task.finished_at = db.func.current_timestamp()
        db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        # Kiểm tra xem có file được tải lên không
        if 'avatar' not in request.files:
            return render_template('profile.html', user=current_user, error="Không có file nào được chọn")
        
        file = request.files['avatar']
        
        # Nếu người dùng không chọn file
        if file.filename == '':
            return render_template('profile.html', user=current_user, error="Không có file nào được chọn")
        
        # Nếu file hợp lệ
        if file and allowed_file(file.filename):
            # Tạo tên file an toàn với UUID để tránh trùng lặp
            filename = secure_filename(file.filename)
            file_extension = filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
            
            # Lưu file
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(file_path)
            
            # Cập nhật avatar trong database
            current_user.avatar = unique_filename
            db.session.commit()
            
            return redirect(url_for('profile'))
        else:
            return render_template('profile.html', user=current_user, error="Chỉ chấp nhận file ảnh (png, jpg, jpeg, gif)")
    
    return render_template('profile.html', user=current_user)

@app.route('/uploads/avatars/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/categories')
@login_required
def categories():
    categories = Category.query.filter_by(user_id=current_user.id).all()
    return render_template('categories.html', categories=categories, default_colors=DEFAULT_COLORS)

@app.route('/add_category', methods=['POST'])
@login_required
def add_category():
    name = request.form['name']
    color = request.form['color']
    
    # Kiểm tra xem tên danh mục đã tồn tại chưa
    existing_category = Category.query.filter_by(name=name, user_id=current_user.id).first()
    if existing_category:
        return redirect(url_for('categories', error="Tên danh mục đã tồn tại!"))
    
    category = Category(name=name, color=color, user_id=current_user.id)
    db.session.add(category)
    db.session.commit()
    
    return redirect(url_for('categories'))

@app.route('/edit_category/<int:category_id>', methods=['POST'])
@login_required
def edit_category(category_id):
    category = Category.query.filter_by(id=category_id, user_id=current_user.id).first_or_404()
    
    name = request.form['name']
    color = request.form['color']
    
    # Kiểm tra xem tên danh mục đã tồn tại chưa (trừ danh mục hiện tại)
    existing_category = Category.query.filter(
        Category.name == name,
        Category.user_id == current_user.id,
        Category.id != category_id
    ).first()
    
    if existing_category:
        return redirect(url_for('categories', error="Tên danh mục đã tồn tại!"))
    
    category.name = name
    category.color = color
    db.session.commit()
    
    return redirect(url_for('categories'))

@app.route('/delete_category/<int:category_id>')
@login_required
def delete_category(category_id):
    category = Category.query.filter_by(id=category_id, user_id=current_user.id).first_or_404()
    
    # Cập nhật các task thuộc danh mục này về null
    Task.query.filter_by(category_id=category.id).update({Task.category_id: None})
    
    db.session.delete(category)
    db.session.commit()
    
    return redirect(url_for('categories'))

@app.route('/reset_admin_password')
def reset_admin_password():
    admin = User.query.filter_by(username='admin').first()
    if admin:
        admin.password = generate_password_hash('admin123')
        admin.role = 'admin'  # Đảm bảo tài khoản có quyền admin
        db.session.commit()
        return render_template('index.html', message="Đã đặt lại mật khẩu cho tài khoản admin thành 'admin123'")
    else:
        return render_template('index.html', error="Không tìm thấy tài khoản admin!")

@app.route('/edit_task/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    
    # Tính số lượng task đã quá hạn
    now = datetime.now()
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    overdue_count = 0
    for t in tasks:
        if t.deadline and t.deadline < now and t.status == 'Pending':
            overdue_count += 1
    
    if request.method == 'POST':
        title = request.form['title']
        deadline_str = request.form.get('deadline')
        
        task.title = title
        
        if deadline_str and deadline_str.strip():
            try:
                deadline = datetime.fromisoformat(deadline_str)
                task.deadline = deadline
            except ValueError:
                # Nếu định dạng không hợp lệ, bỏ qua
                pass
        else:
            task.deadline = None
        
        db.session.commit()
        flash('Nhiệm vụ đã được cập nhật thành công!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('edit_task.html', task=task, overdue_count=overdue_count)
