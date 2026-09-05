from datetime import datetime, timezone

from app.extensions import db


class BlogPost(db.Model):
    __tablename__ = "blog_posts"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    created_by_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    created_by = db.relationship(
        "User",
        backref="created_blog_posts"
    )

    visibility = db.Column(
        db.String(20),
        nullable=False,
        default="private"
    )


    title = db.Column(
        db.String(200),
        nullable=False
    )

    short_description = db.Column(
        db.String(500),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=False
    )

    photo = db.Column(
        db.String(255),
        nullable=True
    )


    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )