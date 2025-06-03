import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import SocketIO, join_room, leave_room, emit
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'comisiones-marinas-secure-key-2025-jun-03'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Configurar Socket.IO con Redis y soporte para WebSocket
socketio = SocketIO(app, 
                    cors_allowed_origins="*",
                    async_mode='eventlet',
                    message_queue='redis://red-d0vichggjchc7386t3rg:6379/0',
                    transports=['websocket', 'polling'],  # Permitir WebSocket primero
                    allow_upgrades=True)  # Permitir upgrade a WebSocket

# Modelo de usuario
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='user')
    active = db.Column(db.Boolean, default=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Formulario de login
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# Inicializar SQLite para mensajes
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  room TEXT,
                  username TEXT,
                  message TEXT,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

# Guardar mensaje en SQLite
def save_message(room, username, message):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("INSERT INTO messages (room, username, message) VALUES (?, ?, ?)",
              (room, username, message))
    conn.commit()
    conn.close()

# Obtener mensajes de SQLite
def get_messages(room):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT username, message FROM messages WHERE room = ? ORDER BY timestamp", (room,))
    messages = c.fetchall()
    conn.close()
    return messages

# Crear administrador por defecto
with app.app_context():
    db.create_all()
    if not User.query.filter_by(email='admin@comisionesmarinas.es').first():
        admin = User(email='admin@comisionesmarinas.es', role='admin', active=True)
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()

init_db()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Rutas
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data) and user.active:
            login_user(user)
            return redirect(url_for('index'))
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/comisiones/')
@login_required
def comisiones():
    return render_template('comisiones.html')

@app.route('/comisiones/<int:id>')
@login_required
def comision(id):
    messages = get_messages(f'comision_{id}')
    return render_template('comision.html', comision_id=id, messages=messages)

@app.route('/comisiones/crear', methods=['GET', 'POST'])
@login_required
def crear_comision():
    if request.method == 'POST':
        # Aquí iría tu lógica para crear una nueva comisión
        # Por ahora, simulamos un éxito
        return redirect(url_for('comision', id=1))
    return render_template('comision_crear.html')

@app.route('/temas/<int:id>')
@login_required
def tema(id):
    messages = get_messages(f'tema_{id}')
    return render_template('tema.html', tema_id=id, messages=messages)

@app.route('/temas/crear/<int:comision_id>', methods=['GET', 'POST'])
@login_required
def crear_tema(comision_id):
    if request.method == 'POST':
        # Aquí iría tu lógica para crear un nuevo tema
        # Por ahora, simulamos un éxito
        return redirect(url_for('comision', id=comision_id))
    return render_template('tema_crear.html', comision_id=comision_id)

@app.route('/admin/')
@login_required
def admin():
    return render_template('admin.html')

@app.route('/admin/temas')
@login_required
def admin_temas():
    return render_template('admin_temas.html')

@app.route('/temas/<int:id>/aprobar', methods=['POST'])
@login_required
def aprobar_tema(id):
    # Aquí iría tu lógica para aprobar un tema
    # Por ahora, simulamos un éxito
    return redirect(url_for('tema', id=id))

# Eventos de Socket.IO
@socketio.on('connect')
def handle_connect():
    print(f'Usuario conectado: {current_user.email if current_user.is_authenticated else "Anónimo"}')
    emit('server_message', {'msg': 'Conexión establecida'})

@socketio.on('disconnect')
def handle_disconnect():
    print(f'Usuario desconectado: {current_user.email if current_user.is_authenticated else "Anónimo"}')

@socketio.on('join')
def on_join(data):
    room = data['room']
    join_room(room)
    print(f'Usuario se unió a la sala: {room}')
    messages = get_messages(room)
    for username, message in messages:
        emit('message', {'username': username, 'message': message}, room=request.sid)
    emit('server_message', {'msg': f'Usuario se unió a {room}'}, room=room)

@socketio.on('leave')
def on_leave(data):
    room = data['room']
    leave_room(room)
    print(f'Usuario salió de la sala: {room}')
    emit('server_message', {'msg': f'Usuario salió de {room}'}, room=room)

@socketio.on('message')
def handle_message(data):
    room = data['room']
    message = data['message']
    username = current_user.email if current_user.is_authenticated else 'Anónimo'
    print(f'Mensaje en {room}: {username}: {message}')
    save_message(room, username, message)
    emit('message', {'username': username, 'message': message}, room=room)

def create_app():
    return app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    socketio.run(app, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)
