import os
from uuid import uuid4

from flask import Blueprint, redirect, url_for, flash, current_app, request
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models.blog import BlogPost
from app.forms import BlogPostForm, CommentForm
from app.models.comment import Comment

blog = Blueprint("blog", __name__)


@blog.route("/dashboard/blog/create", methods=["POST"])
@login_required
def create_blog():

    form = BlogPostForm()

    if form.validate_on_submit():

        photo_path = None

        if form.photo.data:

            upload_folder = os.path.join(
                current_app.root_path, "static", "uploads", "blog"
            )

            os.makedirs(upload_folder, exist_ok=True)

            original_filename = secure_filename(form.photo.data.filename)

            extension = os.path.splitext(original_filename)[1].lower()

            unique_filename = f"{uuid4().hex}{extension}"

            file_path = os.path.join(upload_folder, unique_filename)

            form.photo.data.save(file_path)

            photo_path = f"uploads/blog/{unique_filename}"

        post = BlogPost(
            title=form.title.data,
            short_description=form.short_description.data,
            description=form.description.data,
            photo=photo_path,
            created_by_id=current_user.id,
            visibility=form.visibility.data,
        )

        db.session.add(post)
        db.session.commit()

        flash("Blog post created successfully.", "success")

    else:

        flash("Please check the blog form.", "error")

    return redirect(url_for("main.dashboard"))


@blog.route("/blog/<int:post_id>/comment", methods=["POST"])
def add_comment(post_id):

    post = BlogPost.query.get_or_404(post_id)

    form = CommentForm()

    # Get the page from which the comment was submitted
    redirect_to = request.form.get("redirect_to", "home")

    if not form.validate_on_submit():
        flash("Please enter a valid comment.", "error")

        if redirect_to == "dashboard":
            return redirect(url_for("main.dashboard"))

        return redirect(url_for("main.home"))

    # Check whether the user is allowed to comment
    if post.visibility == "private":

        if not current_user.is_authenticated:
            return redirect(url_for("auth.login"))

        if post.created_by_id != current_user.id:
            return "You are not allowed to comment on this post.", 403

    elif post.visibility == "login_only":

        if not current_user.is_authenticated:
            return redirect(url_for("auth.login"))

    elif post.visibility == "public":

        pass

    else:
        return "Invalid post visibility.", 400

    # Store only the user ID
    if current_user.is_authenticated:
        user_id = current_user.id
    else:
        user_id = None

    comment = Comment(
        post_id=post.id,
        user_id=user_id,
        content=form.content.data,
    )

    db.session.add(comment)
    db.session.commit()

    flash("Comment added successfully.", "success")

    # Redirect back to the page where the comment was submitted
    if redirect_to == "dashboard":
        return redirect(url_for("main.dashboard"))

    return redirect(url_for("main.home"))
