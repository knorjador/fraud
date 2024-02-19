
import flask
from flask import render_template
from app import app

@app.route('/')
def index():
    return flask.render_template('index.html')

@app.route('/login')
def login():
    return flask.render_template('login.html')

@app.route('/register')
def register():
    return flask.render_template('register.html')

@app.route('/dashboard')
def dashboard():
    return flask.render_template('dashboard.html')

@app.route('/predict')
def predict():
    return flask.render_template('predict.html')