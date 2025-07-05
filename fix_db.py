import sqlite3

DATABASE = 'students.db'

def add_cv_column():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE students ADD COLUMN cv_filename TEXT")
        conn.commit()
        print("✅ تم إضافة العمود 'cv_filename' بنجاح.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("⚠️ العمود 'cv_filename' موجود مسبقًا.")
        else:
            print("❌ حدث خطأ:", e)
    finally:
        conn.close()

if __name__ == "__main__":
    add_cv_column()
