from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'billy_burgers_secret')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///billy.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# MODELOS
class Registro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(10)) # ingreso / gasto
    descripcion = db.Column(db.String(100))
    monto = db.Column(db.Float)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

class Empleado(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50))
    sueldo = db.Column(db.Float)

with app.app_context():
    db.create_all()

# RUTAS
@app.route('/')
def login():
    return render_template('login.html')

@app.route('/auth', methods=['POST'])
def auth():
    if request.form.get('user') == 'admin' and request.form.get('password') == 'admin':
        session['admin'] = True
        return redirect(url_for('dashboard'))
    return "Error"

@app.route('/dashboard')
def dashboard():
    if not session.get('admin'): return redirect(url_for('login'))
    ingresos = db.session.query(db.func.sum(Registro.monto)).filter(Registro.tipo == 'ingreso').scalar() or 0
    gastos = db.session.query(db.func.sum(Registro.monto)).filter(Registro.tipo == 'gasto').scalar() or 0
    registros = Registro.query.order_by(Registro.fecha.desc()).limit(10).all()
    return render_template('dashboard.html', ingresos=ingresos, gastos=gastos, total=ingresos-gastos, registros=registros)

# API PARA TELEGRAM
@app.route('/api/telegram', methods=['POST'])
def telegram():
    data = request.json
    nuevo = Registro(tipo=data['tipo'], monto=data['monto'], descripcion=data['desc'])
    db.session.add(nuevo)
    db.session.commit()
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
