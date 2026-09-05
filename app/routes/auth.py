from flask import Blueprint, render_template, redirect, url_for, flash, make_response

from flask_login import login_user, logout_user, current_user

from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db
from app.models.login_history import LoginHistory
from app.models.user import User
from app.forms import LoginForm, RegisterForm

auth = Blueprint("auth", __name__)


# =========================
# LOGIN
# =========================


@auth.route("/login", methods=["GET", "POST"])
def login():

    # If already logged in, don't show login page
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = LoginForm()

    if form.validate_on_submit():

        username = form.username.data
        password = form.password.data

        # Find user by username
        user = User.query.filter_by(username=username).first()

        # Check username and password
        if user and check_password_hash(user.password_hash, password):

            # Create login session
            login_user(user)

            # Record login history
            history = LoginHistory(user_id=user.id)

            db.session.add(history)
            db.session.commit()

            # Go to dashboard
            return redirect(url_for("main.dashboard"))

        # Invalid credentials
        flash("Invalid username or password.", "error")

    # Prevent browser from caching login page
    response = make_response(render_template("login.html", form=form))

    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"

    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    return response


# =========================
# REGISTER
# =========================


@auth.route("/register", methods=["GET", "POST"])
def register():

    # Don't allow already logged-in users
    # to open registration unnecessarily
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = RegisterForm()

    if form.validate_on_submit():

        username = form.username.data
        email = form.email.data
        password = form.password.data

        # Check existing username
        existing_username = User.query.filter_by(username=username).first()

        if existing_username:
            flash("Username already exists.", "error")

            return render_template("register.html", form=form)

        # Check existing email
        existing_email = User.query.filter_by(email=email).first()

        if existing_email:
            flash("Email already exists.", "error")

            return render_template("register.html", form=form)

        # Create new user
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
        )

        db.session.add(user)
        db.session.commit()

        # Automatically login the new user
        login_user(user)

        # Record signup as the first login
        history = LoginHistory(user_id=user.id)

        db.session.add(history)
        db.session.commit()

        # Directly go to dashboard
        return redirect(url_for("main.dashboard"))

    return render_template("register.html", form=form)


# =========================
# LOGOUT
# =========================


@auth.route("/logout")
def logout():

    logout_user()

    # After logout, user must login again
    return redirect(url_for("auth.login"))
