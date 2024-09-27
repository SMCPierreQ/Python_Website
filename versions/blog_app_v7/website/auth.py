from flask import Blueprint, render_template, redirect, url_for, request, flash
from .import db
from .models import User
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .forms import RegistrationForm


auth = Blueprint("auth", __name__)


@auth.route("/login", methods=['GET', 'POST'])
def login():
    # If user is logged in, flash error and redirect to home page
    if current_user.is_authenticated:
        flash('You are logged in, to access this page you must log out. ',
              category='error')
        return redirect(url_for('views.home'))
    # If request is POST
    if request.method == "POST":
        # Checks entered email and password by user
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()
        if user:
            # If passwords match, flash success, login user, and redirect to home page
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                # If passwords don't match, flash error
                flash('Incorrect password, try again.', category='error')
        else:
            # If email doesn't exist in database
            flash('Email does not exist.', category='error')
    # Render login page for route
    return render_template("login.html", user=current_user)


@auth.route("/signup", methods=['GET', 'POST'])
def sign_up():
    # If user is logged in, flash error and redirect to home page
    if current_user.is_authenticated:
        flash('You are logged in, to access this page you must log out. ',
              category='error')
        return redirect(url_for('views.home'))
    # Use user registration form from forms.py
    form = RegistrationForm()
    if form.validate_on_submit():
        # If form inputs are satisfied, hash password and set user information for database
        hashed_password = generate_password_hash(
            (form.password.data), method='pbkdf2:sha256')
        user = User(username=form.username.data,
                    email=form.email.data, password=hashed_password)
        # Add user to database and save (commit)
        db.session.add(user)
        db.session.commit()
        # Flash success message and redirect user to login page.
        flash('Your account has been created!', 'success')
        return redirect(url_for('auth.login'))
    # Render signup page for route
    return render_template('signup.html', form=form, user=current_user)


@auth.route("/logout", methods=['GET', 'POST'])
@login_required
def logout():
    # Log out user and redirect to login page.
    logout_user()
    return redirect(url_for("auth.login"))
