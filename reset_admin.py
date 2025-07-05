import sqlite3
from flask_bcrypt import Bcrypt

DATABASE = 'students.db'
bcrypt = Bcrypt()

def reset_admin_user():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # حذف المستخدم القديم admin لو موجود
    cursor.execute("DELETE FROM users WHERE username = ?", ("admin",))

    # حذف المستخدم الجديد لو موجود عشان ما يتكرر
    cursor.execute("DELETE FROM users WHERE username = ?", ("osama",))

    # إنشاء مستخدم جديد osama مع كلمة سر (ايميلك)
    password = "osama1108@"  # غيّرها لبريدك الحقيقي
    pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", ("osama", pw_hash))

    conn.commit()
    conn.close()
    print("تم حذف المستخدم القديم وإنشاء المستخدم الجديد بنجاح.")

if __name__ == '__main__':
    reset_admin_user()
