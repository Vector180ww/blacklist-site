from flask import Flask, request, jsonify, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
import sqlite3
import base64

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Замени на свой секретный ключ

# Настройка Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Класс пользователя
class User(UserMixin):
    def __init__(self, id):
        self.id = id

# Загрузка пользователя
@login_manager.user_loader
def load_user(user_id):
    return User(user_id) if user_id == 'admin' else None

# Создание базы данных
def init_db():
    conn = sqlite3.connect('blacklist.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS employees 
                 (id INTEGER PRIMARY KEY, name TEXT, reason TEXT, photo BLOB)''')
    conn.commit()
    conn.close()

# Главная страница
@app.route('/')
def index():
    return app.send_static_file('index.html')

# Логин администратора
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'password':  # Замени на свои данные
            user = User('admin')
            login_user(user)
            return redirect(url_for('index'))
        return 'Неверный логин или пароль'
    return '''
        <form method="post">
            <p>Логин: <input type="text" name="username"></p>
            <p>Пароль: <input type="password" name="password"></p>
            <p><input type="submit" value="Войти"></p>
        </form>
    '''

# Выход
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Добавление сотрудника
@app.route('/add_employee', methods=['POST'])
def add_employee():
    name = request.form['name']
    reason = request.form['reason']
    photo = request.files.get('photo')

    conn = sqlite3.connect('blacklist.db')
    c = conn.cursor()
    
    if photo:
        photo_data = photo.read()
    else:
        photo_data = None

    c.execute("INSERT INTO employees (name, reason, photo) VALUES (?, ?, ?)", 
              (name, reason, photo_data))
    conn.commit()
    conn.close()
    
    return jsonify({"status": "success"})

# Удаление сотрудника (только для администратора)
@app.route('/delete_employee/<int:emp_id>', methods=['POST'])
@login_required
def delete_employee(emp_id):
    conn = sqlite3.connect('blacklist.db')
    c = conn.cursor()
    c.execute("DELETE FROM employees WHERE id = ?", (emp_id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "deleted"})

# Получение списка сотрудников
@app.route('/get_employees', methods=['GET'])
def get_employees():
    conn = sqlite3.connect('blacklist.db')
    c = conn.cursor()
    c.execute("SELECT id, name, reason, photo FROM employees")
    employees = c.fetchall()
    conn.close()

    result = []
    for emp in employees:
        emp_id, name, reason, photo = emp
        photo_url = None
        if photo:
            photo_url = "data:image/jpeg;base64," + base64.b64encode(photo).decode('utf-8')
        result.append({"id": emp_id, "name": name, "reason": reason, "photo": photo_url})
    
    return jsonify(result)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)