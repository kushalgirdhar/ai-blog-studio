from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from flask_wtf.file import FileAllowed, FileField
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])

    password = PasswordField("Password", validators=[DataRequired()])

    submit = SubmitField("Login")


class RegisterForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=3, max=80)]
    )

    email = StringField("Email", validators=[DataRequired(), Email()])

    password = PasswordField("Password", validators=[DataRequired(), Length(min=8)])

    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(),
            EqualTo("password", message="Passwords must match."),
        ],
    )

    submit = SubmitField("Create Account")


class BlogPostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(max=200)])


    short_description = StringField(
        "Short Description", validators=[DataRequired(), Length(max=500)]
    )

    description = TextAreaField("Description", validators=[DataRequired()])
    
    visibility = SelectField(
        "Visibility",
        choices=[
            ("private", "Private"),
            ("public", "Public"),
            ("login_only", "Login Only"),
        ],
        default="private",
    )

    photo = FileField(
        "Photo",
        validators=[
            FileAllowed(
                ["jpg", "jpeg", "png", "webp"],
                "Only JPG, JPEG, PNG, and WEBP images are allowed.",
            )
        ],
    )

    submit = SubmitField("Create Post")

class CommentForm(FlaskForm):

    content = TextAreaField(
        "Comment",
        validators=[
            DataRequired(),
            Length(max=2000)
        ]
    )

    submit = SubmitField("Post Comment")

class ProfileForm(FlaskForm):

    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Length(min=3, max=80)
        ]
    )

    email = StringField(
        "Email",
        validators=[
            DataRequired(),
            Email()
        ]
    )

    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=8)
        ]
    )

    submit = SubmitField("Update Profile")