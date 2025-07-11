from flask import Flask, render_template, request, redirect, url_for, flash, Response, send_from_directory
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin
from flask_bcrypt import Bcrypt
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, RadioField, TextAreaField, SelectField, FileField
from wtforms.validators import DataRequired, Email
from werkzeug.utils import secure_filename
import sqlite3
import pandas as pd
from io import BytesIO
import os

app = Flask(__name__)
app.secret_key = "مفتاح-سري-معقد-وطويل-تغيّره-لهذا-المشروع"

bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

DATABASE = 'students.db'
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class User(UserMixin):
    def __init__(self, id_, username, password_hash):
        self.id = id_
        self.username = username
        self.password_hash = password_hash

def get_user(username):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password_hash FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return User(*row)
    return None

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password_hash FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return User(*row)
    return None

class LoginForm(FlaskForm):
    username = StringField('اسم المستخدم', validators=[DataRequired()])
    password = PasswordField('كلمة المرور', validators=[DataRequired()])
    submit = SubmitField('دخول')

class RegistrationForm(FlaskForm):
    full_name = StringField('الاسم الكامل', validators=[DataRequired()])
    email = StringField('البريد الإلكتروني', validators=[DataRequired(), Email()])
    country = StringField('الدولة', validators=[DataRequired()])
    university = SelectField('اختر الجامعة', choices=[
        ("Bahcesehir University", "Bahçeşehir University"),
        ("Istanbul Aydın University", "Istanbul Aydın University"),
        ("Istanbul Okan University", "Istanbul Okan University"),
        ("Altınbaş University", "Altınbaş University"),
        ("Istanbul Medipol University", "Istanbul Medipol University"),
        ("Istanbul Bilgi University", "Istanbul Bilgi University"),
        ("Istanbul Kültür University", "Istanbul Kültür University"),
        ("Istanbul Gelişim University", "Istanbul Gelişim University"),
        ("Beykent University", "Beykent University"),
        ("Üsküdar University", "Üsküdar University"),
        ("Istanbul Arel University", "Istanbul Arel University"),
        ("Istinye University", "Istinye University"),
        ("Nişantaşı University", "Nişantaşı University"),
        ("Maltepe University", "Maltepe University"),
        ("Istanbul Ticaret University", "Istanbul Ticaret University"),
    ], validators=[DataRequired()])
    major = StringField('التخصص', validators=[DataRequired()])
    language = RadioField('لغة الدراسة', choices=[('English','إنجليزي'), ('Turkish','تركي')], validators=[DataRequired()])
    notes = TextAreaField('ملاحظات إضافية')
    cv = FileField('رفع السيرة الذاتية (pdf, doc, docx)')
    submit = SubmitField('إرسال')

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT,
            email TEXT,
            country TEXT,
            university TEXT,
            major TEXT,
            language TEXT,
            notes TEXT,
            cv_filename TEXT
        )
    ''')
    conn.commit()
    conn.close()

def create_admin_user():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", ("osama",))
    if cursor.fetchone() is None:
        pw_hash = bcrypt.generate_password_hash("osama1108@").decode('utf-8')
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", ("osama", pw_hash))
        conn.commit()
    conn.close()
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = get_user(form.username.data)
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash('تم تسجيل الدخول بنجاح.', 'success')
            return redirect(url_for('admin'))
        else:
            flash('اسم المستخدم أو كلمة المرور غير صحيحة.', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('تم تسجيل الخروج بنجاح.', 'success')
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
def index():
    form = RegistrationForm()
    if form.validate_on_submit():
        cv_filename = None
        if form.cv.data:
            file = form.cv.data
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                cv_filename = filename
            else:
                flash("امتداد الملف غير مسموح. الرجاء رفع ملف pdf, doc, أو docx فقط.", "danger")
                return redirect(url_for('index'))

        data = (
            form.full_name.data,
            form.email.data,
            form.country.data,
            form.university.data,
            form.major.data,
            form.language.data,
            form.notes.data,
            cv_filename
        )
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO students (full_name, email, country, university, major, language, notes, cv_filename)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', data)
        conn.commit()
        conn.close()

        flash(f"تم استلام طلبك بنجاح {form.full_name.data}!", "success")
        return redirect(url_for('index'))

    return render_template('form.html', form=form)

@app.route('/admin')
@login_required
def admin():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT id, full_name, email, country, university, major, language, notes, cv_filename FROM students ORDER BY id DESC')
    students = cursor.fetchall()
    conn.close()
    return render_template('admin.html', students=students)

@app.route('/delete/<int:student_id>', methods=['POST'])
@login_required
def delete(student_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM students WHERE id = ?', (student_id,))
    conn.commit()
    conn.close()
    flash("تم حذف الطلب بنجاح.", "success")
    return redirect(url_for('admin'))

@app.route('/export')
@login_required
def export():
    conn = sqlite3.connect(DATABASE)
    df = pd.read_sql_query('SELECT * FROM students', conn)
    conn.close()

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Students')
    output.seek(0)

    return Response(output,
     mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    headers={"Content-Disposition":"attachment;filename=students.xlsx"})

@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    init_db()
    create_admin_user()
    app.run(debug=True)
