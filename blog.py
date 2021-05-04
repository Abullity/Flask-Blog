from flask import Flask, render_template, url_for, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from forms import RegistrationForm, LoginForm
from datetime import datetime
import WebData as data


app = Flask(__name__)
app.config['SECRET_KEY'] = 'bb886a5e4478122cd1739dffd1138fec'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///site.db"
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image = db.Column(db.String(20), nullable=False, default="default.jpg")
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref="author", lazy=True)
    
    def __repr__(self):
        return f"User {self.id}('{self.username}', '{self.email}', '{self.image}')"
    

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime(), nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def __repr__(self):
        return f"Post {self.id}('{self.title}', '{self.date_posted}')"
    
    
@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html", posts=data.posts)
    
@app.route("/about")
def about():
    return render_template("about.html", title="About Wannabe Twitter")   

@app.route("/register", methods=["POST", "GET"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f"Account created for {form.username.data}!", "success")
        return redirect(url_for("home"))
    return render_template("register.html", title="Create Account", form=form)
    
@app.route("/login", methods=["POST", "GET"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.username.data == "admin" and form.password.data == "admin"[::-1]:
            flash(f"Signed in as {form.username.data}!", "success login-feedback")
            return redirect(url_for("home"))
        else:
            flash(f"Incorrect user or password!", "fail login-feedback")
    return render_template("login.html", title="Sign in wannabe account", form=form)
    
        
if __name__ == '__main__':
    app.run(debug=True)
    
