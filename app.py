from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:3306/blogz'
app.config['SQLALCHEMY_ECHO'] = True
# STATIC_URL = '/static/'
db = SQLAlchemy(app)
app.secret_key = 'uahfkahdlfhuhkn8392uh'