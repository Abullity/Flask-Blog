from flask import Flask, render_template, url_for, flash, redirect
from forms import RegistrationForm, LoginForm
import WebData as data


app = Flask(__name__)
app.config['SECRET_KEY'] = 'bb886a5e4478122cd1739dffd1138fec'


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
    
