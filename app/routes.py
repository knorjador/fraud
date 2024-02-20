
import flask
import time
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
import sqlalchemy as sa
from datetime import datetime, timezone
from urllib.parse import urlsplit
from app import app, db
from app.models import Employee

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()

@app.route('/')
def index():
    return flask.render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        employee = db.session.scalar(sa.select(Employee).where(Employee.email == email))
        time.sleep(2)
        if email == "" or employee is None or not employee.check_password(password):
            return redirect(url_for('login', e='1'))
        else: 
            login_user(employee)
            return redirect(url_for('predict'))
    return flask.render_template('login.html')
  
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm = request.form['confirm']
        time.sleep(2)
        if email == "" or password == "" or confirm == "":
            return redirect(url_for('register', e='0'))
        if (password != confirm)
            return redirect(url_for('register', e='2'))
        employee = db.session.scalar(sa.select(Employee).where(Employee.email == email))
        if employee is None:
            employee = Employee(email=email)
            employee.set_password(password)
            db.session.add(employee)
            db.session.commit()
            return redirect(url_for('login'))
    return flask.render_template('register.html')

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if current_user.is_authenticated:
        return flask.render_template('predict.html', email=current_user.email)
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if current_user.is_authenticated:
        return flask.render_template('dashboard.html', email=current_user.email)
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))