# AI Blog Studio 🚀

A production-ready Flask web application combining user authentication, PostgreSQL database management, interactive blogging, and an offline, rule-based **Image-to-Blog Text Generator** powered by classical Computer Vision (OpenCV, Pillow, NumPy, Tesseract OCR, and Jinja2 templates).

Authenticated authors can upload images to automatically generate well-crafted blog drafts (title, short description, and full description) derived from measurable visual features — zero external API keys, zero cloud latency, and 100% deterministic local execution.

---

## 🌟 Key Features

### 📸 Rule-Based Image-to-Blog AI Engine (`image_to_blog`)
- **Dominant Palette Extraction:** K-Means clustering (`cv2.kmeans`) determines dominant colors and matches them to perceptual human color names.
- **Lighting & Temperature Analysis:** Computes mean luminance, tonal contrast, and warm/cool color ratios.
- **Texture & Edge Complexity:** Evaluates sharpness using Laplacian variance and visual density via Canny edge detection.
- **Composition & Rule of Thirds:** Analyzes aspect ratios (landscape/portrait/square) and 3x3 grid edge distribution to identify visual focal points.
- **EXIF Metadata Extraction:** Reads camera make, model, focal length, exposure time, f-number, and ISO if available.
- **Embedded Text OCR:** Detects and transcribes readable text using Tesseract OCR.
- **Dynamic Phrasing & Jinja2 Templates:** Synthesizes extracted metrics into natural, varied descriptions and structured drafts.

### ✍️ Blog & Content Management
- Create, preview, edit, and publish rich blog posts.
- **Draft Assistance:** AI-generated blog drafts populate the form for author review and editing before publishing.
- **Visibility Controls:** Set posts to `Public`, `Login Only`, or `Private`.
- **Media Handling:** Secure upload pipeline with UUID renaming, file type validation, and responsive container rendering.

### 🔐 Authentication & User Accounts
- Secure registration and login with bcrypt password hashing.
- Session-based authentication with `Flask-Login` and login history tracking.
- Author dashboard displaying personal posts, total engagement, and quick-action modals.

### 💬 Community & Comments
- Interactive commenting system with role-based permissions.
- Public posts support anonymous or logged-in discussions; private posts restrict access to post authors.

### 🛡️ Security & Reliability
- Strict CSRF protection with `Flask-WTF`.
- Secure file upload handling (`werkzeug.utils.secure_filename` + UUID hashing).
- SQL injection prevention via SQLAlchemy ORM parameterized queries.

---

## 🏗️ Architecture & Project Structure

```text
ai-blog-studio/
├── app/
│   ├── models/                 # SQLAlchemy database models
│   │   ├── blog.py             # BlogPost schema
│   │   ├── comment.py          # Comment schema
│   │   ├── login_history.py    # Authentication log schema
│   │   └── user.py             # User account schema
│   ├── routes/                 # Flask Blueprints
│   │   ├── auth.py             # Login, registration, logout
│   │   ├── blog.py             # Post creation, editing, AI generate endpoint, comments
│   │   └── main.py             # Home page, dashboard, profile
│   ├── services/
│   │   └── ai_service.py       # Integration service calling image_to_blog engine
│   ├── static/
│   │   ├── style.css           # Custom styling and responsive design
│   │   └── uploads/blog/       # Uploaded post images
│   ├── templates/              # Jinja2 HTML templates
│   │   ├── auth/               # Login & Register views
│   │   ├── blog/               # Blog creation and view templates
│   │   ├── dashboard.html      # User control panel
│   │   └── home.html           # Public discovery feed
│   ├── extensions.py           # Database & LoginManager instances
│   ├── forms.py                # WTForms schemas with CSRF validation
│   └── __init__.py             # Flask application factory
│
├── image_to_blog/              # Standalone Image-to-Blog CV Engine
│   ├── __init__.py             # Public module export
│   ├── api.py                  # Single public entrypoint: generate_blog_text()
│   ├── config.py               # Color palettes, threshold ranges, phrase banks
│   ├── ingestion.py            # Image loader, format normalizer & corruption validator
│   ├── features/               # Feature extractors
│   │   ├── color.py            # K-Means dominant colors & Euclidean naming
│   │   ├── light.py            # Mean brightness, contrast std dev, warmth ratio
│   │   ├── texture.py          # Laplacian sharpness & Canny edge density
│   │   ├── composition.py      # Orientation & 3x3 focal region detector
│   │   ├── metadata.py         # EXIF camera metadata parser
│   │   └── text_ocr.py         # Tesseract OCR reader & text cleaner
│   ├── phrasing.py             # Feature-to-phrase mapping & mood synthesis
│   ├── templates/              # Jinja2 text templates
│   │   ├── title.j2            # Title template
│   │   ├── short_description.j2 # Summary template
│   │   └── long_description.j2  # Multi-sentence detailed body template
│   └── generator.py            # End-to-end pipeline orchestrator
│
├── migrations/                 # Alembic database migration scripts
├── tests/                      # Automated unit and integration test suite
│   └── test_image_to_blog.py   # Test suite for CV extractors and pipeline
├── config.py                   # Application environment configuration
├── requirements.txt            # Python dependencies
├── run.py                      # Application entrypoint
└── README.md
```

---

## ⚙️ Prerequisites

- **Python:** 3.10+ (tested on Python 3.12 & 3.14)
- **PostgreSQL:** 14+ running locally or remotely
- **Tesseract OCR:** System binary required for text detection
  - **Ubuntu/Debian:** `sudo apt update && sudo apt install -y tesseract-ocr`
  - **macOS (Homebrew):** `brew install tesseract`
  - **Windows:** Download installer from [UB-Mannheim Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)

---

## 🚀 Quickstart & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/<your-username>/ai-blog-studio.git
cd ai-blog-studio
```

### 2. Create and Activate Virtual Environment
```bash
python3 -m venv myenv
source myenv/bin/activate  # On Windows: myenv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory:
```env
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your_strong_secret_key_here
DATABASE_URL=postgresql://username:password@localhost:5432/blog_db
```

### 5. Initialize the Database
```bash
flask db upgrade
```

### 6. Run the Development Server
```bash
python run.py
```
Visit `http://127.0.0.1:5000` in your web browser.

---

## 🧪 Running Automated Tests

Run the comprehensive test suite verifying ingestion, color clustering, lighting, composition, OCR, and template generation:

```bash
python -m unittest tests/test_image_to_blog.py
```

---

## 🌐 Production Deployment

### Gunicorn WSGI Server
Run behind Gunicorn:
```bash
gunicorn --workers 4 --bind 127.0.0.1:8000 "run:app"
```

### Systemd Service (`/etc/systemd/system/aiblog.service`)
```ini
[Unit]
Description=AI Blog Studio Flask Application
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/ai-blog-studio
Environment="PATH=/var/www/ai-blog-studio/myenv/bin"
ExecStart=/var/www/ai-blog-studio/myenv/bin/gunicorn --workers 4 --bind 127.0.0.1:8000 run:app
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## 📌 Technical Notes & Limitations

- **Visual Properties Descriptor:** The `image_to_blog` generator describes measurable visual properties (colors, lighting, texture, composition, orientation, and embedded text). It does not use heavy deep learning models or perform semantic object classification (e.g. identifying dog breeds or specific landmarks).
- **Human-in-the-Loop:** AI-generated outputs serve as starting drafts. Authors always retain full control to edit, refine, or rewrite before saving.

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).