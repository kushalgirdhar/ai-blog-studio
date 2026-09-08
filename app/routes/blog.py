import os
from uuid import uuid4

from datetime import datetime, timezone
from flask import (
    Blueprint,
    redirect,
    url_for,
    flash,
    current_app,
    request,
    render_template,
    jsonify,
    abort,
)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.services.ai_service import generate_blog_from_image
from db_copyright_checker import check_blog_draft_copyright
import tempfile
from app.extensions import db
from app.models.blog import BlogPost
from app.forms import BlogPostForm, CommentForm
from app.models.comment import Comment

blog = Blueprint("blog", __name__)


@blog.route("/dashboard/blog/create", methods=["GET"])
@login_required
def create_blog_page():
    form = BlogPostForm()
    return render_template("blog/create.html", form=form)


@blog.route("/dashboard/blog/create", methods=["POST"])
@login_required
def create_blog():

    form = BlogPostForm()

    if form.validate_on_submit():

        photo_path = None

        if form.photo.data and hasattr(form.photo.data, "filename") and form.photo.data.filename:

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


@blog.route("/blog/<int:post_id>/edit", methods=["GET", "POST"])
@login_required
def edit_blog(post_id):
    post = BlogPost.query.get_or_404(post_id)

    # Restrict edit access strictly to the post creator
    if post.created_by_id != current_user.id:
        flash("You are not authorized to edit this post.", "error")
        return redirect(url_for("main.dashboard"))

    form = BlogPostForm(obj=post)

    if form.validate_on_submit():
        post.title = form.title.data
        post.short_description = form.short_description.data
        post.description = form.description.data
        post.visibility = form.visibility.data

        if form.photo.data and hasattr(form.photo.data, "filename") and form.photo.data.filename:
            upload_folder = os.path.join(
                current_app.root_path, "static", "uploads", "blog"
            )
            os.makedirs(upload_folder, exist_ok=True)
            original_filename = secure_filename(form.photo.data.filename)
            extension = os.path.splitext(original_filename)[1].lower()
            unique_filename = f"{uuid4().hex}{extension}"
            file_path = os.path.join(upload_folder, unique_filename)
            form.photo.data.save(file_path)
            post.photo = f"uploads/blog/{unique_filename}"

        post.updated_at = datetime.now(timezone.utc)
        db.session.commit()

        flash("Blog post updated successfully.", "success")
        redirect_to = request.form.get("redirect_to", "dashboard")
        if redirect_to == "home":
            return redirect(url_for("main.home"))
        return redirect(url_for("main.dashboard"))

    # Compute copyright and plagiarism report for the post against other posts and reference docs
    try:
        existing_posts = BlogPost.query.filter(BlogPost.id != post.id).with_entities(
            BlogPost.id, BlogPost.title, BlogPost.short_description, BlogPost.description
        ).all()
        extra_corpus = {}
        for p in existing_posts:
            extra_corpus[f"db_post_{p.id}_full"] = f"{p.title}\n{p.short_description}\n{p.description}"
            if p.title:
                extra_corpus[f"db_post_{p.id}_title"] = p.title
            if p.short_description:
                extra_corpus[f"db_post_{p.id}_short"] = p.short_description
            if p.description:
                extra_corpus[f"db_post_{p.id}_desc"] = p.description

        copyright_report = check_blog_draft_copyright(
            title=post.title or "",
            short_description=post.short_description or "",
            description=post.description or "",
            extra_corpus=extra_corpus,
        )
    except Exception as e:
        current_app.logger.exception(f"Error computing copyright check for edit post {post_id}: {e}")
        copyright_report = {
            "is_flagged": False,
            "has_plagiarism": False,
            "has_copyright": False,
            "plagiarism_phrases": [],
            "copyright_phrases": [],
            "matched_phrases": [],
            "max_similarity": 0.0,
            "summary_message": "No overlap detected.",
        }

    return render_template("blog/edit.html", form=form, post=post, copyright_check=copyright_report)


@blog.route("/blog/<int:post_id>/regenerate", methods=["POST"])
@login_required
def regenerate_blog_post(post_id):
    post = BlogPost.query.get_or_404(post_id)

    # Restrict regeneration strictly to the post creator
    if post.created_by_id != current_user.id:
        return jsonify({"error": "You are not authorized to regenerate this post."}), 403

    uploaded_photo = request.files.get("photo")
    temp_path = None
    target_image_path = None

    try:
        if uploaded_photo and uploaded_photo.filename:
            suffix = os.path.splitext(secure_filename(uploaded_photo.filename))[1].lower()
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                uploaded_photo.save(temp_file.name)
                temp_path = temp_file.name
                target_image_path = temp_path
        elif post.photo:
            full_photo_path = os.path.join(current_app.root_path, "static", post.photo)
            if os.path.exists(full_photo_path):
                target_image_path = full_photo_path

        if not target_image_path:
            return jsonify({"error": "No image available to analyze for regeneration."}), 400

        # Build corpus excluding current post
        existing_posts = BlogPost.query.filter(BlogPost.id != post.id).with_entities(
            BlogPost.id, BlogPost.title, BlogPost.short_description, BlogPost.description
        ).all()
        extra_corpus = {}
        for p in existing_posts:
            extra_corpus[f"db_post_{p.id}_full"] = f"{p.title}\n{p.short_description}\n{p.description}"
            if p.title:
                extra_corpus[f"db_post_{p.id}_title"] = p.title
            if p.short_description:
                extra_corpus[f"db_post_{p.id}_short"] = p.short_description
            if p.description:
                extra_corpus[f"db_post_{p.id}_desc"] = p.description

        blog_data = generate_blog_from_image(target_image_path, extra_corpus=extra_corpus)

        return jsonify(
            {
                "title": blog_data.get("title", ""),
                "short_description": blog_data.get("short_description", ""),
                "description": blog_data.get("description", ""),
                "copyright_check": blog_data.get("copyright_check", {}),
            }
        )
    except Exception as e:
        current_app.logger.exception(f"Regeneration failed for post {post_id}: {e}")
        return jsonify({"error": "Unable to regenerate blog at this time."}), 500
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


@blog.route("/dashboard/blog/generate", methods=["POST"])
@login_required
def generate_blog():
    image = request.files.get("photo")

    if not image:
        return jsonify({"error": "Please upload an image."}), 400

    temp_path = None

    try:
        # Create a temporary file for AI processing
        suffix = os.path.splitext(secure_filename(image.filename))[1].lower()

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            image.save(temp_file.name)
            temp_path = temp_file.name

        # Gather existing database posts as reference corpus for duplication checking
        existing_posts = BlogPost.query.with_entities(
            BlogPost.id, BlogPost.title, BlogPost.short_description, BlogPost.description
        ).all()
        extra_corpus = {
            f"database_post_{p.id}": f"{p.title}\n{p.short_description}\n{p.description}"
            for p in existing_posts
        }
        extra_corpus = {}
        for p in existing_posts:
            extra_corpus[f"db_post_{p.id}_full"] = f"{p.title}\n{p.short_description}\n{p.description}"
            if p.title:
                extra_corpus[f"db_post_{p.id}_title"] = p.title
            if p.short_description:
                extra_corpus[f"db_post_{p.id}_short"] = p.short_description
            if p.description:
                extra_corpus[f"db_post_{p.id}_desc"] = p.description

        # Generate blog using AI and verify copyright / duplication
        blog_data = generate_blog_from_image(temp_path, extra_corpus=extra_corpus)

        return jsonify(
            {
                "title": blog_data.get("title", ""),
                "short_description": blog_data.get("short_description", ""),
                "description": blog_data.get("description", ""),
                "copyright_check": blog_data.get("copyright_check", {}),
            }
        )

    except Exception:
        current_app.logger.exception("AI blog generation failed")

        return jsonify({"error": "Unable to generate blog at this time."}), 500

    finally:
        # Delete temporary image after AI processing
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


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
