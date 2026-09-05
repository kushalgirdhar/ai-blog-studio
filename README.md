# AI-Powered Flask Blog Platform

A production-oriented Flask web application with user authentication, PostgreSQL database integration, blog management, comments, image uploads, and AI-assisted blog content generation using Google's Gemini Vision AI.

The application allows authenticated users to create blog posts by uploading an image. Gemini analyzes the image and generates a title, short description, and long description. The generated content is displayed as a draft so the user can review and edit it before publishing.

> AI generates the content — the user always has the final decision to publish.

---

## Features

### Authentication
- User registration
- User login and logout
- Password hashing
- Session-based authentication
- Login history tracking
- Protected dashboard
- Profile management

### Blog Management
- Create blog posts
- Upload blog images
- Image validation
- Unique image filenames
- Public, Login Only, and Private visibility
- User-based blog ownership
- Blog timestamps
- Edit generated AI content before publishing

### AI-Assisted Blog Creation
- Upload an image
- AI analyzes the image using Gemini Vision
- Automatically generates:
  - Blog title
  - Short description
  - Long description
- Generated content is shown in the form
- User can edit the generated content
- AI never publishes a blog automatically
- Blog is saved only after the user clicks "Post Blog"

### Comments
- Comments on blog posts
- Anonymous comments on public posts
- Logged-in comments linked to user accounts
- Usernames retrieved from the users table
- Inline comments
- Comment visibility based on blog visibility

### Security
- Password hashing
- CSRF protection
- Environment variables for secrets
- Secure file names
- File type validation
- Upload restrictions
- Authentication-protected routes
- Database foreign keys
- Server-side form validation

### Database
- PostgreSQL
- SQLAlchemy ORM
- Flask-Migrate
- Alembic migrations
- User relationships
- Blog ownership relationships
- Comment relationships
- Login history

### Production Setup
- Gunicorn WSGI server
- Apache2 reverse proxy
- systemd service
- PostgreSQL database
- Environment-based configuration

---

## Technology Stack

### Backend
- Python
- Flask
- Flask-SQLAlchemy
- Flask-Login
- Flask-WTF
- Flask-Migrate
- Gunicorn

### Database
- PostgreSQL
- SQLAlchemy
- Alembic

### AI
- Google Gemini API
- Gemini Vision / Multimodal AI
- Structured JSON AI responses

### Image Processing
- Pillow
- Werkzeug Secure Filename

### Frontend
- HTML
- Jinja2 Templates
- JavaScript
- CSS

### Server
- Apache2
- Gunicorn
- systemd

---

## Project Architecture

```text
New Project/
│
├── app/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── login_history.py
│   │   ├── blog.py
│   │   └── comment.py
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── main.py
│   │   └── blog.py
│   │
│   ├── static/
│   │   ├── style.css
│   │   └── uploads/
│   │       └── blog/
│   │
│   ├── templates/
│   │   ├── dashboard.html
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── home.html
│   │   └── profile.html
│   │
│   ├── forms.py
│   ├── extensions.py
│   └── __init__.py
│
├── migrations/
│
├── myenv/
│
├── .env
├── .gitignore
├── config.py
├── requirements.txt
└── run.py