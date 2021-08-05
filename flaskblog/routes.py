import os
import secrets
from PIL import Image
from flaskblog import app, bcrypt, db, mail
from flask import render_template, url_for, flash, redirect, request, abort
from flaskblog.forms import (RegistrationForm, LoginForm, UpdateAccountForm, PostForm,
                             RequestResetForm, ResetPasswordForm)
from flaskblog.models import User, Post
from flask_login import login_user, logout_user, current_user, login_required
from flask_mail import Message


@app.route("/")
@app.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
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


@app.route("/user/<string:username>/posts")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
            .order_by(Post.date_posted.desc())\
            .paginate(page=page, per_page=5)
    return render_template("user_posts.html", posts=posts, user=user,
                            title=f"{username}'s Posts")


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password reset request', sender='goldenpelmeni@gmail.com', 
                   recipients=[user.email])
    msg.body = f"""To reset you password visit: \n
                   {url_for('reset_password', token=token, _external=True)}"""
    mail.send(msg)
    

@app.route("/reset_password", methods=["POST", "GET"])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('Reset request has been sent to your email account!', 'success')
        return redirect(url_for('login'))
    return render_template("reset_request.html", title='Reset password', form=form)
    
    
@app.route("/reset_password/<token>", methods=["POST", "GET"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if not user:
        flash('that is an invalid or expired token!', 'alert-fail')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_pas = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user.password = hashed_pas
        db.session.commit()
        flash(f"Password has been updated!", "success")
        return redirect(url_for("login"))
    return render_template("reset_password.html", title='Reset password', form=form)    
    
    
@app.errorhandler(404)
def error_404(error):
    return render_template("errors/404.html", title='Wannabe page not found', error=error) 
    
    
@app.errorhandler(403)
def error_403(error):
    return render_template("errors/403.html", title="You don't have permission!", error=error) 
    
    
@app.errorhandler(500)
def error_500(error):
    return render_template("errors/500.html", title='Something snapped', error=error)         
    
