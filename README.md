# AI Blog Studio 🚀

A production-ready Flask web application combining user authentication, PostgreSQL database management, interactive blogging, an offline **Image-to-Blog Text Generator**, and an automated **Copyright & Plagiarism Detection System**.

Authenticated authors can upload images to automatically generate rich, context-aware blog drafts (title, short description, and full narrative) derived from visual features and grammar templates — complete with real-time duplication and plagiarism analysis against existing database posts and reference corpora.

---

## 👨‍💻 Author & Contact

- **Author:** Kushal Girdhar
- **GitHub:** [@kushalgirdhar](https://github.com/kushalgirdhar)
- **Repository:** [https://github.com/kushalgirdhar/ai-blog-studio](https://github.com/kushalgirdhar/ai-blog-studio)

---

## 🧠 AI & Technology Stack Breakdown

The application uses an offline, privacy-first, zero-cloud-cost AI architecture composed of three dedicated subsystems:

### 1. Image Processing & Computer Vision
Extracts measurable visual features, perceptual metrics, color palettes, and embedded text directly from uploaded images.

- **`pillow` (`PIL`)** — Loads, validates image integrity, checks dimensions, converts color spaces (RGB/RGBA/Grayscale), and parses EXIF camera metadata (camera model, exposure, ISO, focal length).
- **`opencv` (`cv2`)** — Advanced image analysis including Laplacian variance (sharpness), Canny edge detection (visual density & texture), K-Means color clustering, and HSV channel thresholding for scene classification.
- **`numpy`** — Fast array math, matrix slicing, and vector transformations supporting Pillow and OpenCV operations.
- **`color thief`** — Converts RGB values to human-readable color names and extracts dominant color palettes.
- **`pytesseract` & `Tesseract OCR`** — Reads text that physically appears inside the image (such as signs, labels, and logos).

---

### 2. Text Generation & Storytelling
Synthesizes visual features into rich, natural narrative stories with high combinatorial variety.

- **`Tracery`** — Grammar-based generative text engine producing over 1,000,000+ unique, context-specific narrative combinations across diverse scene categories (rainforest waterfalls, futuristic tech/holograms, coastal seascapes, urban architecture, sunsets, and mountain vistas).
- **`jinja2`** — Sentence templates with dynamic word slots and structured formatting for blog titles, short summaries, and multi-paragraph drafts.

---

### 3. Copyright & Plagiarism Detection
Compares generated and edited blog drafts against the live database of published posts and local reference archives.

- **`scikit-learn`** — The core machine learning library that actually does the detection. Specifically two functions from it:
  - **`TfidfVectorizer`** — Turns text into numeric vectors based on word frequency and relative importance.
  - **`cosine_similarity`** — Compares those vectors to produce a similarity score (0 to 1).
- **Supporting Libraries** (they don't detect anything themselves, they just feed data in or format results out):
  - **`difflib`** *(built into Python)* — A second, simpler similarity score based on character overlap.
  - **`re`** *(built into Python)* — Splits text into words/sentences and marks the matched parts for dual-category visual highlighting:
    - 🔴 **Plagiarism (External Source):** Highlighted in red with reference citation.
    - 🟡 **Copyright / Database Duplicate (Shared Post Content):** Highlighted in yellow with clamped tags and line count triggers.
  - **`sqlalchemy` + `pandas`** — Pull your existing posts out of your database so there's something to check against.

---

## 🌟 Key Application Features

### 📸 Semantic Image-to-Blog AI Engine
- **Perceptual Scene Analysis:** Analyzes vegetation density, neon luminescences, blue/green ratios, and vertical flow vectors to categorize images.
- **Dominant Palette & Lighting:** K-Means clustering identifies dominant colors; calculates contrast and warm/cool balance.
- **Texture, Composition & EXIF:** Evaluates Rule of Thirds focal points, edge density, and camera metadata.
- **Live Re-Generation:** Single-click **"Regenerate AI Content"** button on both the Create and Edit post pages to generate clean, unique phrasing.

### 🛡️ Dual-Category Copyright & Plagiarism Shield
- **Dual Visual Highlighting:** Real-time span highlights distinguishing external plagiarism (Red) from internal database duplication (Yellow).
- **Expandable Highlights:** Long highlight spans exceeding 3 lines feature a clean, collapsible **"More / Less"** toggle button.
- **Dashboard Feed Annotations:** Public discovery feed and author dashboard automatically scan and annotate post cards.

### ✍️ Blog & Content Management
- Full CRUD functionality: Create, preview, edit, and publish blog articles.
- **Visibility Settings:** Control post exposure with `Public`, `Login Only`, or `Private` permissions.
- **Media Upload Pipeline:** Secure upload handling with UUID renaming, MIME validation, and responsive display.

### 🔐 Security & User Management
- Session-based authentication using `Flask-Login` and `bcrypt` password hashing.
- CSRF protection enabled across all forms via `Flask-WTF`.
- Parameterized database operations through SQLAlchemy ORM to prevent SQL injection.
- Role-based commenting system with fine-grained access control.

---

## 🏗️ Architecture & Directory Structure

```text
ai-blog-studio/
├── app/
│   ├── models/                     # SQLAlchemy database models
│   │   ├── blog.py                 # BlogPost model
│   │   ├── comment.py              # Comment model
│   │   ├── login_history.py        # Authentication log model
│   │   └── user.py                 # User account model
│   ├── routes/                     # Flask Blueprints
│   │   ├── auth.py                 # Authentication routes (login, register, logout)
│   │   ├── blog.py                 # Blog CRUD, AI generation, re-generation, comments
│   │   └── main.py                 # Home feed, dashboard, profile
│   ├── services/
│   │   └── ai_service.py           # Glue layer connecting Flask to image_to_blog engine
│   ├── static/
│   │   ├── style.css               # Application styles and highlight badges
│   │   └── uploads/blog/           # Uploaded blog images
│   ├── templates/                  # Jinja2 HTML templates
│   │   ├── auth/                   # Login & Register views
│   │   ├── blog/                   # Blog creation, edit, and view templates
│   │   ├── dashboard.html          # Author management dashboard
│   │   └── home.html               # Public feed
│   ├── extensions.py               # Database and LoginManager instances
│   ├── forms.py                    # WTForms schemas
│   └── __init__.py                 # Flask application factory
│
├── db_copyright_checker.py         # TF-IDF & Cosine Similarity Copyright/Plagiarism Engine
├── reference_docs/                 # Local reference archives for plagiarism scanning
│   ├── internal_copyright_archive.txt
│   └── sample_article.txt
│
├── image_to_blog/                  # Standalone Computer Vision & Text Generation Engine
│   ├── __init__.py                 # Public module exports
│   ├── api.py                      # Public entrypoint: generate_blog_text()
│   ├── config.py                   # Color names, thresholds, grammar rules
│   ├── ingestion.py                # Image validator, normalizer & EXIF loader
│   ├── tracery_generator.py        # Combinatorial grammar narrative generator
│   ├── phrasing.py                 # Feature-to-phrase mapping
│   ├── features/                   # Vision feature extractors
│   │   ├── color.py                # K-Means dominant color clustering
│   │   ├── composition.py          # Rule of Thirds & focal point detector
│   │   ├── light.py                # Brightness, contrast & color temperature
│   │   ├── metadata.py             # EXIF parser
│   │   ├── scene_analyzer.py       # Semantic scene classifier
│   │   ├── text_ocr.py             # Tesseract OCR extraction
│   │   └── texture.py              # Laplacian sharpness & Canny edge density
│   ├── templates/                  # Jinja2 text templates
│   └── generator.py                # Pipeline orchestrator
│
├── migrations/                     # Alembic database migration scripts
├── tests/                          # Automated unit and integration test suite
│   ├── test_blog_edit.py           # Edit and re-generation route test cases
│   ├── test_copyright_checker.py   # TF-IDF, shingling, and highlight test cases
│   └── test_image_to_blog.py       # Computer vision pipeline test cases
├── config.py                       # Application configuration
├── requirements.txt                # Python dependencies
├── run.py                          # Application entry point
└── README.md                       # Project documentation
```

---

## ⚙️ Prerequisites

- **Python:** 3.10+ (tested on Python 3.12 & 3.14)
- **PostgreSQL:** 14+ (or SQLite for development)
- **Tesseract OCR:** System binary required for image text detection
  - **Ubuntu/Debian:** `sudo apt update && sudo apt install -y tesseract-ocr`
  - **macOS (Homebrew):** `brew install tesseract`
  - **Windows:** Download installer from [UB-Mannheim Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)

---

## 🚀 Quickstart & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/kushalgirdhar/ai-blog-studio.git
cd ai-blog-studio
```

### 2. Create and Activate a Virtual Environment
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
Create a `.env` file in the project root:
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

### 6. Run the Application
```bash
python run.py
```
Open your browser and navigate to `http://127.0.0.1:5000`.

---

## 🧪 Running Automated Tests

Run the complete test suite covering the computer vision pipeline, copyright detection, and blog editing workflows:

```bash
python -m unittest discover -s tests -v
```

---

## 🌐 Production Deployment

### Gunicorn WSGI Server
Run the production server with multiple worker processes:
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

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).