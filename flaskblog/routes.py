import os
import secrets
from PIL import Image
from flaskblog import app, bcrypt, db
from flask import render_template, url_for, flash, redirect, request, abort
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm
from flaskblog.models import User, Post
from flask_login import login_user, logout_user, current_user, login_required


@app.route("/")
@app.route("/home")
def home():
    posts = Post.query.all()
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

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + ext
    picture_path = os.path.join(app.root_path, 'static/profile_images', picture_fn)
    resized_img = Image.open(form_picture)
    resized_img.thumbnail((200, 200))
    resized_img.save(picture_path)
    return picture_fn

@app.route("/account", methods=["POST", "GET"])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash(f"Changes were successfully executed!", "success")
        return redirect(url_for('account'))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
    user_image = url_for('static', filename='profile_images/' + current_user.image)   
    return render_template('account.html', title="Account", user_image=user_image,
                            form=form)    
    
@app.route("/post/new", methods=["POST", "GET"])
@login_required
def new_post():
    form = PostForm()    
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.post_content.data,
                    author=current_user)
        db.session.add(post)
        db.session.commit()
        flash("Your post has been created!", "success")
        return redirect(url_for('home'))
    return render_template('create_post.html', title="Create a post", form=form,
                            legend="Create a post")
    
@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template("post.html", title=post.title, post=post)
    
@app.route("/post/<int:post_id>/update", methods=["POST", "GET"])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.post_content.data
        db.session.commit()
        flash("Your post has been updated!", "success")
        return redirect(url_for('post', post_id=post.id))
    form.title.data = post.title
    form.post_content.data = post.content
    return render_template('create_post.html', title="Update a post", form=form,
                            legend="Update a post")    

@app.route("/post/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id):    
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash(f"Post has been deleted!", "success")
    return redirect(url_for('home'))

