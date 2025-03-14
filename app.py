# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Đảm bảo thư mục uploads tồn tại
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Định nghĩa các mô hình
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='user')  # 'admin' hoặc 'user'
    avatar = db.Column(db.String(200), default='default.png')
    tasks = db.relationship('Task', backref='user', lazy=True)
    is_active = db.Column(db.Boolean, default=True)
    
    # Override phương thức is_active của UserMixin nếu cần
    def get_is_active(self):
        return self.is_active

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'in_progress', 'completed'
    created = db.Column(db.DateTime, default=datetime.now)
    deadline = db.Column(db.DateTime)
    finished = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Tạo các bảng trong cơ sở dữ liệu
with app.app_context():
    db.create_all()
    # Tạo admin nếu chưa tồn tại
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            password=generate_password_hash('admin123'),
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            if not user.is_active:
                flash('Tài khoản đã bị khóa. Vui lòng liên hệ quản trị viên.', 'danger')
                return redirect(url_for('login'))
                
            login_user(user)
            flash('Đăng nhập thành công!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Tên đăng nhập hoặc mật khẩu không đúng!', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists', 'danger')
            return redirect(url_for('register'))
        
        new_user = User(
            username=username,
            password=generate_password_hash(password),
            role='user'
        )
        
        # Xử lý avatar nếu có
        if 'avatar' in request.files:
            file = request.files['avatar']
            if file and allowed_file(file.filename):
                filename = secure_filename(f"{username}_{file.filename}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                new_user.avatar = filename
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Đăng ký thành công! Bây giờ bạn có thể đăng nhập.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    # Lấy danh sách công việc của người dùng hiện tại
    if current_user.role == 'admin':
        tasks = Task.query.all()
        users = User.query.all()
    else:
        tasks = Task.query.filter_by(user_id=current_user.id).all()
        users = None
    
    # Đếm số công việc trễ hạn
    overdue_tasks = Task.query.filter(
        Task.user_id == current_user.id,
        Task.status != 'completed',
        Task.deadline < datetime.now()
    ).count()
    
    # Truyền đối tượng datetime.now() cho template
    return render_template('dashboard.html', tasks=tasks, users=users, overdue_tasks=overdue_tasks, now=datetime.now)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        if 'avatar' in request.files:
            file = request.files['avatar']
            if file and allowed_file(file.filename):
                filename = secure_filename(f"{current_user.username}_{file.filename}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                
                # Xóa avatar cũ nếu không phải avatar mặc định
                if current_user.avatar != 'default.png':
                    try:
                        old_avatar_path = os.path.join(app.config['UPLOAD_FOLDER'], current_user.avatar)
                        if os.path.exists(old_avatar_path):
                            os.remove(old_avatar_path)
                    except Exception as e:
                        print(f"Error removing old avatar: {e}")
                
                current_user.avatar = filename
                db.session.commit()
                flash('Avatar đã được cập nhật thành công!', 'success')
        
        return redirect(url_for('profile'))
    
    return render_template('profile.html')

@app.route('/task/new', methods=['GET', 'POST'])
@login_required
def new_task():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        deadline_str = request.form.get('deadline')
        
        if not title:
            flash('Tiêu đề không được bỏ trống', 'danger')
            return redirect(url_for('new_task'))
        
        # Parse deadline từ string sang datetime
        deadline = None
        if deadline_str:
            try:
                deadline = datetime.fromisoformat(deadline_str)
            except ValueError:
                flash('Định dạng deadline không hợp lệ', 'danger')
                return redirect(url_for('new_task'))
        
        task = Task(
            title=title,
            description=description,
            status='pending',
            deadline=deadline,
            user_id=current_user.id
        )
        
        db.session.add(task)
        db.session.commit()
        
        flash('Công việc đã được tạo thành công!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('new_task.html')

@app.route('/task/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    
    # Kiểm tra quyền truy cập
    if task.user_id != current_user.id and current_user.role != 'admin':
        flash('Bạn không có quyền chỉnh sửa công việc này', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        task.title = request.form.get('title')
        task.description = request.form.get('description')
        task.status = request.form.get('status')
        
        deadline_str = request.form.get('deadline')
        if deadline_str:
            try:
                task.deadline = datetime.fromisoformat(deadline_str)
            except ValueError:
                flash('Định dạng deadline không hợp lệ', 'danger')
                return redirect(url_for('edit_task', task_id=task_id))
        
        # Nếu status là completed và chưa có thời gian hoàn thành
        if task.status == 'completed' and not task.finished:
            task.finished = datetime.now()
        # Nếu status không còn là completed thì reset thời gian hoàn thành
        elif task.status != 'completed':
            task.finished = None
        
        db.session.commit()
        flash('Công việc đã được cập nhật thành công!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('edit_task.html', task=task)

@app.route('/task/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    
    # Kiểm tra quyền truy cập
    if task.user_id != current_user.id and current_user.role != 'admin':
        flash('Bạn không có quyền xóa công việc này', 'danger')
        return redirect(url_for('dashboard'))
    
    db.session.delete(task)
    db.session.commit()
    
    flash('Công việc đã được xóa thành công!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/admin/users')
@login_required
def admin_users():
    if current_user.role != 'admin':
        flash('Bạn không có quyền truy cập trang này', 'danger')
        return redirect(url_for('dashboard'))
    
    users = User.query.all()
    # Thêm datetime.now() vào ngữ cảnh render template
    from datetime import datetime
    return render_template('user_admin.html', users=users, now=datetime.now)

@app.route('/admin/users/<int:user_id>/toggle-status', methods=['GET'])
@login_required
def toggle_user_status(user_id):
    if current_user.role != 'admin':
        flash('Bạn không có quyền thực hiện hành động này', 'danger')
        return redirect(url_for('dashboard'))
    
    user = User.query.get_or_404(user_id)
    
    # Không cho phép admin khóa chính mình
    if user.id == current_user.id:
        flash('Bạn không thể khóa tài khoản của chính mình', 'danger')
        return redirect(url_for('admin_users'))
    
    # Đảo trạng thái is_active
    user.is_active = not user.is_active
    
    # Lưu vào CSDL
    db.session.commit()
    
    status_message = "khóa" if not user.is_active else "mở khóa"
    flash(f'Đã {status_message} người dùng {user.username} thành công', 'success')
    
    return redirect(url_for('admin_users'))

@app.route('/admin/users/<int:user_id>/delete', methods=['GET'])
@login_required
def delete_user(user_id):
    if current_user.role != 'admin':
        flash('Bạn không có quyền thực hiện hành động này', 'danger')
        return redirect(url_for('dashboard'))
    
    user = User.query.get_or_404(user_id)
    
    # Không cho phép admin xóa chính mình
    if user.id == current_user.id:
        flash('Bạn không thể xóa tài khoản của chính mình', 'danger')
        return redirect(url_for('admin_users'))
    
    # Lưu tên người dùng để hiển thị thông báo
    username = user.username
    
    # Có thể cần xử lý các công việc liên quan
    # Option 1: Xóa tất cả công việc liên quan đến người dùng
    # Task.query.filter_by(user_id=user.id).delete()
    
    # Option 2: Chuyển công việc sang tài khoản admin hoặc một người dùng khác
    # tasks = Task.query.filter_by(user_id=user.id).all()
    # for task in tasks:
    #     task.user_id = admin_user_id  # ID của một admin hoặc người dùng khác
    
    # Xóa người dùng
    db.session.delete(user)
    db.session.commit()
    
    flash(f'Đã xóa người dùng {username} thành công', 'success')
    
    return redirect(url_for('admin_users'))

@app.route('/admin/users/<int:user_id>')
@login_required
def user_detail(user_id):
    if current_user.role != 'admin':
        flash('Bạn không có quyền truy cập trang này', 'danger')
        return redirect(url_for('dashboard'))
    
    user = User.query.get_or_404(user_id)
    from datetime import datetime
    
    return render_template('user_detail.html', user=user, now=datetime.now)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)