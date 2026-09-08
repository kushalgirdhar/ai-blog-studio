"""
Database & Local Reference Copyright / Duplication Checker.

Checks newly generated blog text against:
  1. Your ALREADY-POSTED blog content — pulled directly from your database
     via SQLAlchemy / BlogPost model or direct DB connection string.
  2. Any extra local reference documents (.txt / .md) in reference_docs/ folder.
  3. In-memory corpus dictionaries.

Zero external API keys, 100% offline local computation (TF-IDF cosine similarity + n-gram shingles).
"""

import os
import re
import difflib
import logging
from typing import Dict, List, Set, Tuple, Optional, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

DEFAULT_CORPUS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reference_docs")
DEFAULT_DB_QUERY = "SELECT id, title, short_description, description FROM blog_posts"


# ===========================================================================
# 1. Corpus Loading (Database + Reference Docs)
# ===========================================================================

def load_posts_from_db(
    connection_string: Optional[str] = None,
    query: str = DEFAULT_DB_QUERY,
) -> Dict[str, str]:
    """
    Returns {label: combined_text} for every post in the database.
    Falls back gracefully if database is unreachable.
    """
    db_uri = connection_string or os.getenv("DATABASE_URL")
    if not db_uri:
        return {}

    try:
        from sqlalchemy import create_engine, text

        engine = create_engine(db_uri)
        posts = {}
        with engine.connect() as conn:
            result = conn.execute(text(query))
            for row in result.mappings():
                pid = row.get("id", "?")
                title = str(row.get("title", "") or "")
                short_desc = str(row.get("short_description", "") or "")
                desc = str(row.get("description", "") or row.get("full_description", "") or "")
                label = f"db_post_{pid}_{title[:30]}"
                combined = f"{title}\n{short_desc}\n{desc}".strip()
                if combined:
                    posts[label] = combined
        return posts
    except Exception as e:
        logger.warning(f"Could not load posts via direct DB connection: {e}")
        return {}


def load_local_reference_folder(folder_path: Optional[str] = None) -> Dict[str, str]:
    """Reads all .txt and .md files in the reference directory -> {filename: text}"""
    folder = folder_path or DEFAULT_CORPUS_DIR
    if not os.path.isdir(folder):
        return {}
    corpus = {}
    for fname in os.listdir(folder):
        if fname.endswith((".txt", ".md")):
            fpath = os.path.join(folder, fname)
            try:
                with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read().strip()
                    if content:
                        corpus[fname] = content
            except Exception:
                continue
    return corpus


# ===========================================================================
# 2. Similarity & NLP Utilities
# ===========================================================================

def difflib_ratio(text_a: str, text_b: str) -> float:
    """Calculates sequence matcher ratio between two strings (0.0 to 1.0)."""
    if not text_a or not text_b:
        return 0.0
    return difflib.SequenceMatcher(None, text_a, text_b).ratio()


def tfidf_cosine_scores(generated_text: str, corpus: Dict[str, str]) -> Dict[str, float]:
    """TF-IDF vectorizes generated_text + reference corpus and calculates cosine similarity."""
    if not corpus or not generated_text.strip():
        return {}
    labels = list(corpus.keys())
    documents = [generated_text] + [corpus[l] for l in labels]

    try:
        vectorizer = TfidfVectorizer(stop_words="english")
        tfidf_matrix = vectorizer.fit_transform(documents)
        scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])[0]
        return {labels[i]: float(scores[i]) for i in range(len(labels))}
    except Exception:
        return {l: difflib_ratio(generated_text, corpus[l]) for l in labels}


def tokenize(text: str) -> List[str]:
    """Lowercase word tokens, stripped of punctuation."""
    return re.findall(r"\b\w+\b", text.lower())


def get_shingles(tokens: List[str], n: int = 3) -> Set[str]:
    """Set of n-word phrase shingles. Auto-shrinks for shorter token lists."""
    if len(tokens) == 0:
        return set()
    effective_n = min(n, len(tokens))
    if effective_n < 2:
        return set()
    return {" ".join(tokens[i:i + effective_n]) for i in range(len(tokens) - effective_n + 1)}


def find_overlapping_phrases(generated_text: str, reference_text: str, n: int = 3) -> Set[str]:
    """Finds exact overlapping n-gram word sequences between generated and reference text."""
    gen_tokens = tokenize(generated_text)
    ref_tokens = tokenize(reference_text)
    if not gen_tokens or not ref_tokens:
        return set()
    return get_shingles(gen_tokens, n) & get_shingles(ref_tokens, n)


def highlight_matches(generated_text: str, overlapping_phrases: Set[str], mode: str = "html") -> str:
    """
    Highlights matching phrases in text using non-destructive merged character spans.
    Prevents nested/broken tags.
    """
    if not overlapping_phrases or not generated_text:
        return generated_text

    spans: List[Tuple[int, int]] = []
    for phrase in overlapping_phrases:
        if not phrase.strip():
            continue
        for m in re.finditer(rf"\b{re.escape(phrase)}\b", generated_text, re.IGNORECASE):
            spans.append((m.start(), m.end()))

    if not spans:
        return generated_text

    # Sort & merge overlapping or contiguous spans
    spans.sort(key=lambda s: (s[0], -s[1]))
    merged: List[Tuple[int, int]] = []
    cur_start, cur_end = spans[0]

    for s, e in spans[1:]:
        if s <= cur_end:
            cur_end = max(cur_end, e)
        else:
            merged.append((cur_start, cur_end))
            cur_start, cur_end = s, e
    merged.append((cur_start, cur_end))

    # Single-pass build
    mark_open = (
        '<mark class="copyright-highlight" style="background:#fef08a; color:#854d0e; padding:2px 4px; border-radius:4px; font-weight:600;">'
        if mode == "html"
        else "**"
    )
    mark_close = "</mark>" if mode == "html" else "**"

    result = []
    cursor = 0
    for start, end in merged:
        result.append(generated_text[cursor:start])
        result.append(f"{mark_open}{generated_text[start:end]}{mark_close}")
        cursor = end
    result.append(generated_text[cursor:])

    return "".join(result)


# ===========================================================================
# 3. Main Checker Functions
# ===========================================================================

def check_generated_text(
    generated_text: str,
    db_connection_string: Optional[str] = None,
    db_query: str = DEFAULT_DB_QUERY,
    local_folder: Optional[str] = None,
    extra_corpus: Optional[Dict[str, str]] = None,
    shingle_size: int = 3,
    similarity_warn_threshold: float = 0.35,
) -> Dict[str, Any]:
    """
    Performs full copyright and duplication check against database posts,
    local reference files, and extra dictionary items.
    """
    corpus: Dict[str, str] = {}

    # 1. Database posts
    if db_connection_string or os.getenv("DATABASE_URL"):
        corpus.update(load_posts_from_db(db_connection_string, db_query))

    # 2. Local reference docs folder
    corpus.update(load_local_reference_folder(local_folder))

    # 3. Extra in-memory corpus
    if extra_corpus:
        corpus.update(extra_corpus)

    if not corpus or not generated_text.strip():
        return {
            "is_flagged": False,
            "max_similarity": 0.0,
            "overall_scores": {},
            "flagged_documents": {},
            "matched_phrases": [],
            "highlighted_text": generated_text,
            "highlighted_markdown": generated_text,
            "summary_message": "100% Unique. No reference documents found to compare against.",
        }

    overall_scores: Dict[str, Dict[str, float]] = {}
    for label, ref_text in corpus.items():
        diff_score = difflib_ratio(generated_text, ref_text)
        overall_scores[label] = {"difflib_ratio": round(diff_score, 3)}

    tfidf_scores = tfidf_cosine_scores(generated_text, corpus)
    max_sim = 0.0
    for label, score in tfidf_scores.items():
        overall_scores[label]["tfidf_cosine"] = round(float(score), 3)
        if score > max_sim:
            max_sim = float(score)

    flagged_docs: Dict[str, Any] = {}
    all_overlaps: Set[str] = set()

    for label, ref_text in corpus.items():
        overlaps = find_overlapping_phrases(generated_text, ref_text, n=shingle_size)
        score = overall_scores.get(label, {}).get("tfidf_cosine", 0.0)
        if overlaps or score >= similarity_warn_threshold:
            flagged_docs[label] = {
                "tfidf_cosine": round(score, 3),
                "matched_phrases": sorted(list(overlaps)),
            }
            all_overlaps |= overlaps

    is_flagged = len(all_overlaps) > 0 or max_sim >= similarity_warn_threshold

    if is_flagged:
        summary_msg = f"Duplication Flagged: {len(all_overlaps)} matched phrase(s) detected (Max similarity: {round(max_sim * 100, 1)}%)."
    else:
        summary_msg = f"100% Unique: No significant duplication detected (Max similarity: {round(max_sim * 100, 1)}%)."

    return {
        "is_flagged": is_flagged,
        "max_similarity": round(max_sim, 3),
        "overall_scores": overall_scores,
        "flagged_documents": flagged_docs,
        "matched_phrases": sorted(list(all_overlaps)),
        "highlighted_text": highlight_matches(generated_text, all_overlaps, mode="html"),
        "highlighted_markdown": highlight_matches(generated_text, all_overlaps, mode="markdown"),
        "summary_message": summary_msg,
    }


def check_blog_draft_copyright(
    title: str,
    short_description: str,
    description: str,
    db_connection_string: Optional[str] = None,
    corpus_folder: Optional[str] = None,
    extra_corpus: Optional[Dict[str, str]] = None,
    shingle_size: int = 3,
) -> Dict[str, Any]:
    """
    Checks full blog draft (title, short description, description) and returns highlighted fields.
    """
    combined_text = f"{title}\n{short_description}\n{description}"
    report = check_generated_text(
        combined_text,
        db_connection_string=db_connection_string,
        local_folder=corpus_folder,
        extra_corpus=extra_corpus,
        shingle_size=shingle_size,
    )

    all_overlaps = set(report.get("matched_phrases", []))

    highlighted_title = highlight_matches(title, all_overlaps, mode="html")
    highlighted_short = highlight_matches(short_description, all_overlaps, mode="html")
    highlighted_desc = highlight_matches(description, all_overlaps, mode="html")

    report["highlighted_fields"] = {
        "title": highlighted_title,
        "short_description": highlighted_short,
        "description": highlighted_desc,
    }

    return report


def annotate_posts_with_copyright_info(
    posts: List[Any],
    corpus_folder: Optional[str] = None,
    shingle_size: int = 3,
    similarity_warn_threshold: float = 0.35,
) -> List[Any]:
    """
    Annotates a list of BlogPost objects with live copyright info:
      - post.is_flagged
      - post.max_similarity
      - post.matched_phrases
      - post.highlighted_title
      - post.highlighted_short_description
      - post.highlighted_description
    """
    if not posts:
        return posts

    folder = corpus_folder or DEFAULT_CORPUS_DIR
    ref_corpus = load_local_reference_folder(folder) if os.path.exists(folder) else {}

    post_corpus: Dict[str, str] = {}
    for p in posts:
        pid = getattr(p, "id", None)
        title = getattr(p, "title", "") or ""
        short_desc = getattr(p, "short_description", "") or ""
        desc = getattr(p, "description", "") or ""
        key = f"post_{pid}" if pid is not None else f"post_{id(p)}"
        post_corpus[key] = f"{title}\n{short_desc}\n{desc}"

    for p in posts:
        pid = getattr(p, "id", None)
        cur_key = f"post_{pid}" if pid is not None else f"post_{id(p)}"
        title = getattr(p, "title", "") or ""
        short_desc = getattr(p, "short_description", "") or ""
        desc = getattr(p, "description", "") or ""

        target_corpus = dict(ref_corpus)
        for k, v in post_corpus.items():
            if k != cur_key:
                target_corpus[k] = v

        report = check_blog_draft_copyright(
            title=title,
            short_description=short_desc,
            description=desc,
            extra_corpus=target_corpus,
            shingle_size=shingle_size,
            corpus_folder=folder,
        )

        p.is_flagged = report.get("is_flagged", False)
        p.max_similarity = report.get("max_similarity", 0.0)
        p.matched_phrases = report.get("matched_phrases", [])
        highlighted_fields = report.get("highlighted_fields", {})
        p.highlighted_title = highlighted_fields.get("title", title)
        p.highlighted_short_description = highlighted_fields.get("short_description", short_desc)
        p.highlighted_description = highlighted_fields.get("description", desc)

    return posts
