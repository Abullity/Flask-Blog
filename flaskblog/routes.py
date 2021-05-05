from flaskblog import app, bcrypt, db
from flask import render_template, url_for, flash, redirect, request
from flaskblog.forms import RegistrationForm, LoginForm
from flaskblog.models import User, Post
from flaskblog.DummyData import posts
from flask_login import login_user, logout_user, current_user, login_required

    
@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html", posts=posts)
    
@app.route("/about")
def about():
    return render_template("about.html", title="About Wannabe Twitter")   

@app.route("/register", methods=["POST", "GET"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pas = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(username=form.username.data, email=form.email.data, password=hashed_pas)
        db.session.add(user)
        db.session.commit()
        flash(f"Account created for {form.username.data}!", "success")
        return redirect(url_for("home"))
    return render_template("register.html", title="Create Account", form=form)
    
@app.route("/login", methods=["POST", "GET"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash(f"Logged in as {form.username.data}!", "success")
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash(f"Incorrect user or password!", "fail login-feedback")
    return render_template("login.html", title="Sign in wannabe account", form=form)
       
@app.route("/logout")
def logout():    
    logout_user()
    flash(f"Successfully logged out!", "success")
    return redirect(url_for('home'))

@app.route("/account")
@login_required
def account():    
    return render_template('account.html', title="Account")    
