from routes import app
from models import db
import os
import sqlite3

if __name__ == '__main__':
    # Thêm cột deadline vào bảng task và avatar vào bảng user nếu chưa tồn tại
    db_path = os.path.join(app.instance_path, 'database.db')
    if os.path.exists(db_path):
        try:
            # Kết nối đến database
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Kiểm tra xem cột deadline đã tồn tại chưa trong bảng task
            cursor.execute("PRAGMA table_info(task)")
            task_columns = [column[1] for column in cursor.fetchall()]
            
            # Nếu cột deadline chưa tồn tại, thêm vào
            if 'deadline' not in task_columns:
                cursor.execute("ALTER TABLE task ADD COLUMN deadline DATETIME")
                conn.commit()
                print("Đã thêm cột deadline vào bảng task")
            
            # Nếu cột category_id chưa tồn tại, thêm vào
            if 'category_id' not in task_columns:
                cursor.execute("ALTER TABLE task ADD COLUMN category_id INTEGER REFERENCES category(id)")
                conn.commit()
                print("Đã thêm cột category_id vào bảng task")
            
            # Kiểm tra xem cột avatar đã tồn tại chưa trong bảng user
            cursor.execute("PRAGMA table_info(user)")
            user_columns = [column[1] for column in cursor.fetchall()]
            
            # Nếu cột avatar chưa tồn tại, thêm vào
            if 'avatar' not in user_columns:
                cursor.execute("ALTER TABLE user ADD COLUMN avatar VARCHAR(200) DEFAULT 'default_avatar.png'")
                conn.commit()
                print("Đã thêm cột avatar vào bảng user")
            
            # Nếu cột is_blocked chưa tồn tại, thêm vào
            if 'is_blocked' not in user_columns:
                cursor.execute("ALTER TABLE user ADD COLUMN is_blocked BOOLEAN DEFAULT 0")
                conn.commit()
                print("Đã thêm cột is_blocked vào bảng user")
            
            # Kiểm tra xem bảng category đã tồn tại chưa
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='category'")
            if not cursor.fetchone():
                # Tạo bảng category nếu chưa tồn tại
                cursor.execute("""
                CREATE TABLE category (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(50) NOT NULL,
                    color VARCHAR(20) NOT NULL DEFAULT '#4caf50',
                    user_id INTEGER NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES user(id)
                )
                """)
                conn.commit()
                print("Đã tạo bảng category")
            
            conn.close()
        except Exception as e:
            print(f"Lỗi khi thêm cột: {e}")
    
    # Tạo thư mục instance nếu chưa tồn tại
    if not os.path.exists(app.instance_path):
        os.makedirs(app.instance_path)
    
    # Tạo thư mục static/uploads/avatars nếu chưa tồn tại
    avatars_dir = os.path.join(app.root_path, 'static', 'uploads', 'avatars')
    if not os.path.exists(avatars_dir):
        os.makedirs(avatars_dir)
    
    # Tạo bảng nếu chưa tồn tại
    with app.app_context():
        db.create_all()
    
    app.run(debug=True)
