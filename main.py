from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from models import User, Blog
from app import app, db
import re
from hashutils import check_pw_hash
from datetime import datetime


@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index', 'blog']
    if request.endpoint not in allowed_routes and 'email' not in session and '/static/' not in request.path:
        return redirect('/login')


@app.route("/logout", methods=['POST'])
def logout():
    del session['email']
    return redirect('/login')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_pw_hash(password, user.pw_hash):
            session['email'] = email
            flash("Logged in")
            return redirect('/blog')
        elif user and user.pw_hash != password:
            flash('Incorrect password')
        elif email == '' and password == '':
            flash('Email and Password required')
        else:
            flash('User does not exist')

    return render_template('login.html', title='Blogz Login')


@app.route('/signup', methods=['POST', 'GET'])
def signup():

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']
        email = request.form['email']
        existing_user = User.query.filter_by(email=email).first()

        if email == '' and password == '' and verify == '':
            flash('Email and Password fields required')
            return render_template('signup.html', title='Blogz Signup')
        if existing_user or existing_user and password == '':
            flash('{} Already an account'.format(email))
            flash('Password required')
            return render_template('signup.html', title='Blogz Signup')
        if email == '':
            flash('Email field required')
            return render_template('signup.html', title='Blogz Signup')
        if not existing_user and password == '':
            flash('Password field required')
            return render_template('signup.html', title='Blogz Signup')
        if not existing_user and (len(password) < 3 or len(password) > 20) and password != verify:
            flash('Invalid Password')
            flash('Passwords do not match')
            return render_template('signup.html', title='Blogz Signup')
        if not existing_user and password != verify:
            flash('Passwords do not match')
            return render_template('signup.html', title='Blogz Signup')

        user = User(email=email, password=password)
        db.session.add(user)
        db.session.commit()
        session['email'] = email

        return redirect('/')

    return render_template('signup.html', title='Blogz Signup')


@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        owner = User.query.filter_by(email=session['email']).first()

        if title == '' or body == '':
            flash("The title or body can not be empty.")
            return redirect('/newpost')

        titles = Blog.query.filter_by(title=title).first()
        if not titles:
            new_blog = Blog(title, body, owner)
            db.session.add(new_blog)
            db.session.commit()
            return redirect('/blog?id={}'.format(new_blog.id))
        else:
            flash("A blog with the same title exists. Please choose a different title.")
            return redirect('/newpost')

    return render_template('newpost.html', title='Blogz Post')


@app.route('/', methods=['POST', 'GET'])
def index():
    users = User.query.all()
    return render_template('index.html', users=users, title='Blogz Home')


@app.route('/blog', methods=['POST', 'GET'])
def blog():    
    blog_id = request.args.get('id')
    user_id = request.args.get('user')

    blogs = Blog.query.order_by(Blog.pub_date.desc()).paginate(per_page=5)
    blog = Blog.query.filter_by(id=blog_id).first()
    user_blogs = Blog.query.order_by(Blog.pub_date.desc()).filter_by(owner_id=user_id).all()
    user_name = Blog.query.filter_by(owner_id=user_id).first()

    if blog_id:
        return render_template('blog.html', title="Blog", blog=blog)
    if user_blogs:
        return render_template('blog.html', title="Blog", blog_title=user_name.owner.email, user_blogs=user_blogs)
    else:
        return render_template('blog.html', title="Blogz", blogs=blogs, blog_title='Blogz')


if __name__ == "__main__":
    app.run()
