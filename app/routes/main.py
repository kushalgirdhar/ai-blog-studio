from flask import Blueprint, render_template, make_response, flash, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import or_

from app.extensions import db
from app.models.login_history import LoginHistory
from app.models.blog import BlogPost
from app.models.user import User
from app.models.comment import Comment
from app.forms import BlogPostForm, CommentForm, ProfileForm
from werkzeug.security import generate_password_hash
from db_copyright_checker import annotate_posts_with_copyright_info

main = Blueprint("main", __name__)


@main.route("/")
def home():

    public_posts = (
        BlogPost.query.filter_by(visibility="public")
        .order_by(BlogPost.created_at.desc())
        .all()
    )
    annotate_posts_with_copyright_info(public_posts)

    return render_template(
        "home.html", public_posts=public_posts, comment_form=CommentForm()
    )


@main.route("/dashboard")
@login_required
def dashboard():

    login_history = (
        LoginHistory.query.filter_by(user_id=current_user.id)
        .order_by(LoginHistory.login_time.desc())
        .all()
    )

    total_logins = len(login_history)

    blog_form = BlogPostForm()
    comment_form = CommentForm()
    my_posts = (
        BlogPost.query.filter(
            or_(
                BlogPost.created_by_id == current_user.id,
                BlogPost.visibility.in_(["public", "login_only"]),
            )
        )
        .order_by(BlogPost.created_at.desc())
        .all()
    )
    annotate_posts_with_copyright_info(my_posts)
    response = make_response(
        render_template(
            "dashboard.html",
            login_history=login_history,
            total_logins=total_logins,
            blog_form=blog_form,
            my_posts=my_posts,
            comment_form=comment_form,
        )
    )

    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"

    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    return response


@main.route("/profile", methods=["GET", "POST"])
@login_required
def profile():

    form = ProfileForm(obj=current_user)

    if form.validate_on_submit():

        new_username = form.username.data.strip()
        new_email = form.email.data.strip()
        new_password = form.password.data

        # Check username uniqueness
        existing_username = User.query.filter(
            User.username == new_username, User.id != current_user.id
        ).first()

        if existing_username:
            flash("Username already exists.", "error")
            return render_template("profile.html", form=form)

        # Check email uniqueness
        existing_email = User.query.filter(
            User.email == new_email, User.id != current_user.id
        ).first()

        if existing_email:
            flash("Email already exists.", "error")
            return render_template("profile.html", form=form)

        # Update username and email
        current_user.username = new_username
        current_user.email = new_email
        current_user.password_hash = generate_password_hash(new_password)

        # Update password
        current_user.password_hash = generate_password_hash(new_password)

        
        db.session.commit()

        flash("Profile updated successfully.", "success")

        return redirect(url_for("main.profile"))

    return render_template("profile.html", form=form)
