# Implementation Guide: Plagiarism & Copyright Checker

How to wire `db_copyright_checker.py` into your blog project so every
AI-generated post gets checked against your existing posts before publishing.

---

## 1. What this checks (and what it doesn't)

| Layer | Library | Catches |
|---|---|---|
| Exact/near-exact phrase copying | `re` (n-gram "shingles") | Word-for-word or near-identical chunks (3-5 word phrases) |
| Whole-document similarity | `difflib` + scikit-learn TF-IDF/cosine | Overall how alike two full texts are |
| Sentence-level plagiarism | scikit-learn TF-IDF/cosine | Copied or lightly-reworded sentences, even without exact phrase matches |

**Hard limitation:** none of this can catch a *fully reworded* sentence
that shares almost no vocabulary with the original (e.g. "hand" → "palm",
"dark background" → "dim backdrop"). That requires a semantic/embedding
model, which is outside your no-AI-model constraint. Document this
limitation wherever the feature is surfaced to end users.

---

## 2. Install dependencies

```bash
pip install sqlalchemy pandas psycopg2-binary scikit-learn --break-system-packages
```
Use `pymysql` instead of `psycopg2-binary` if your database is MySQL, not Postgres.

---

## 3. Configure it for your real database

Open `db_copyright_checker.py` and edit the three config values at the top:

```python
DB_CONNECTION_STRING = "postgresql+psycopg2://USER:PASSWORD@HOST:5432/DBNAME"

BLOG_POSTS_QUERY = """
    SELECT id, title, short_description, full_description
    FROM blog_posts
"""

LOCAL_REFERENCE_FOLDER = None  # or a path, if you also want to check local .txt files
```

- Replace `blog_posts` and the column names with your actual table/schema.
- Keep the query cheap — it currently pulls *all* posts on every check. If your
  table grows large, add a `WHERE status = 'published'` filter, or cache the
  corpus (see Section 6).
- Never commit the real password into source control — load it from an
  environment variable instead:
  ```python
  import os
  DB_CONNECTION_STRING = os.environ["BLOG_DB_URL"]
  ```

---

## 4. Where to call it in your pipeline

Your existing flow is:

```
image → feature extraction (OpenCV/Pillow/Tesseract)
      → text generation (Tracery)
      → [NEW STEP GOES HERE]
      → save post to database
```

Call the checker **after text generation, before saving**:

```python
from db_copyright_checker import check_generated_text

generated = generate_blog_text(image_features)   # your Tracery pipeline

report = check_generated_text(
    generated["long_description"],
    DB_CONNECTION_STRING,
    BLOG_POSTS_QUERY,
    shingle_size=3,             # tuned lower to catch light rewording too
    similarity_warn_threshold=0.3,
    plagiarism_threshold=0.6,
)

# also worth checking title + short_description the same way
title_report = check_generated_text(generated["title"], DB_CONNECTION_STRING, BLOG_POSTS_QUERY)
```

---

## 5. Deciding what to do with the result

`report` gives you three things to act on:

```python
report["flagged_documents"]      # dict: which existing posts overlap, and by how much
report["plagiarized_sentences"]  # list: sentences that matched an existing sentence closely
report["highlighted_text"]       # string: your text with matches marked
                                  #   ** exact-phrase match **
                                  #   ~~ paraphrased-sentence match ~~
```

A simple policy to start with:

```python
def decide_action(report, block_threshold=0.5):
    max_score = max(
        (d["tfidf_cosine"] for d in report["flagged_documents"].values()),
        default=0.0
    )
    if max_score >= block_threshold:
        return "block"      # too similar — don't auto-publish, send for human review
    elif report["flagged_documents"]:
        return "warn"       # some overlap — publish but flag in the admin UI
    else:
        return "clear"      # no meaningful overlap
```

In your admin dashboard (the one in your screenshot), you could render
`report["highlighted_text"]` directly instead of the plain description, so
whoever reviews a "Private" draft before publishing sees the flagged words
highlighted in place.

---

## 6. Performance note for production

Right now, every call re-reads your entire posts table and rebuilds the
TF-IDF vectors from scratch. Fine for testing; not efficient if you have
hundreds/thousands of posts and check frequently. Two options once this is
live:

- **Cache the corpus** — load `load_posts_from_db()` once (e.g. on app
  startup, or on a schedule), reuse it across checks, and only refresh it
  after a new post is actually published.
- **Only compare against recent/similar posts** — e.g. filter `BLOG_POSTS_QUERY`
  to the same category/tag as the new post, instead of your entire archive.

---

## 7. Testing checklist before going live

- [ ] Run against a post you know is a near-duplicate of an existing one — confirm it gets flagged and highlighted
- [ ] Run against a completely original piece of text — confirm nothing gets flagged (no false positives)
- [ ] Run against a very short title (a few words) — confirm no crash (this was a bug in an earlier version, now fixed)
- [ ] Confirm your DB credentials are pulled from environment variables, not hardcoded, before this goes anywhere near production
- [ ] Decide and document your actual `block_threshold` / `plagiarism_threshold` values based on a batch of real posts, not the demo defaults
