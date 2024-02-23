
import os
import flask
import time
import sklearn
import pickle
import pandas as pd
import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib.pyplot as plt
from io import BytesIO
from flask import render_template, flash, redirect, url_for, request, Response
from flask_login import login_user, logout_user, current_user, login_required
import sqlalchemy as sa
from datetime import datetime, timezone
from urllib.parse import urlsplit
from app import app, db
from app.models import Employee, Transaction

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('predict'))
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
        if (password != confirm):
            return redirect(url_for('register', e='2'))
        employee = db.session.scalar(sa.select(Employee).where(Employee.email == email))
        if employee is None:
            employee = Employee(email=email)
            employee.set_password(password)
            db.session.add(employee)
            db.session.commit()
            return redirect(url_for('login'))
    return flask.render_template('register.html')

def processPrediction(data):
    loaded_model = pickle.load(open("model.pkl", "rb"))
    result = loaded_model.predict(data)
    return result[0]

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        kind = request.form['kind']
        amount = request.form['amount']
        oldbalanceOrg = request.form['oldbalanceOrg']
        newbalanceOrg = request.form['newbalanceOrg']
        newbalanceDest = request.form['newbalanceDest']
        step = request.form['step']
        nameOrg = request.form['nameOrg']
        nameDest = request.form['nameDest']
        oldbalanceDest = request.form['oldbalanceDest']

        if (amount == "" or oldbalanceOrg == "" or newbalanceOrg == "" or newbalanceDest == ""):
            return redirect(url_for('predict', e='3'))

        kind = int(request.form['kind'])
        amount = float(request.form['amount'])
        oldbalanceOrg = float(request.form['oldbalanceOrg'])
        newbalanceOrg = float(request.form['newbalanceOrg'])
        newbalanceDest = float(request.form['newbalanceDest'])
        step = 0 if step == "" else int(request.form['step'])
        nameOrg = request.form['nameOrg']
        nameDest = request.form['nameDest']
        oldbalanceDest = 0.0 if oldbalanceDest == "" else float(request.form['oldbalanceDest'])

        type_cashout = (kind == 1)
        type_transfer = (kind == 4)

        result = processPrediction([[amount, type_cashout, type_transfer, oldbalanceOrg, newbalanceOrg, newbalanceDest]])

        transaction = Transaction(
            kind=kind,
            amount=amount, 
            oldbalanceOrg=oldbalanceOrg, 
            newbalanceOrg=newbalanceOrg,
            newbalanceDest=newbalanceDest,
            step=step,
            nameOrg=nameOrg,
            nameDest=nameDest,
            oldbalanceDest=oldbalanceDest, 
            fraud=result,
            employee_id=current_user.id
        )
        db.session.add(transaction)
        db.session.commit()

        time.sleep(2)
        return redirect(url_for('dashboard'))

    if current_user.is_authenticated:
        return flask.render_template('predict.html', email=current_user.email)
    return redirect(url_for('index'))


@app.route('/plot.png')
def plot():
    no_fraud = int(request.args.get('n', 50))
    fraud = int(request.args.get('y', 50))

    try:
        fig, ax = plt.subplots()
        labels = ['Non fraude', 'Fraude']
        sizes = [no_fraud, fraud]
        colors = ['#1F95A7', 'lightcoral']
        plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
        plt.title('Répartition des transactions')
        plt.axis('equal')
        plt.legend(labels, title='Légende', loc='upper right')

        img_stream = BytesIO()
        plt.savefig(img_stream, format='png')
        img_stream.seek(0)

        return Response(img_stream, content_type='image/png')
    except Exception as e:
        return str(e)

@app.route('/dashboard')
def dashboard():
    if current_user.is_authenticated:
        query = (
            db.session.query(Transaction)
            .filter_by(employee_id=current_user.id)
            .order_by(sa.desc(Transaction.timestamp))
        )
        transactions = query.all()
        no_fraud = 0
        fraud = 0
        total_transactions = 0
        total_amount = 0
        total_fraud = 0
        for x in transactions:
            total_transactions += 1
            total_amount += x.amount
            if x.fraud == False:
                no_fraud += 1 
            else: 
                fraud += 1
                total_fraud += x.amount
        img_url = url_for('plot', n=no_fraud, y=fraud)
        return flask.render_template('dashboard.html', email=current_user.email, transactions=transactions, img_url=img_url, fraud=fraud, total_amount=total_amount, total_fraud=total_fraud, total_transactions=total_transactions)
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

