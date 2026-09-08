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


def highlight_matches(
    generated_text: str,
    overlapping_phrases: Set[str],
    mode: str = "html",
    highlight_type: str = "copyright",
) -> str:
    """
    Highlights matching phrases in text using non-destructive merged character spans.
    Supports highlight_type:
      - 'plagiarism': Red / Rose highlight (#fee2e2, #991b1b, border: #f87171)
      - 'copyright': Amber / Yellow highlight (#fef08a, #854d0e, border: #fde047)
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
    if mode == "html":
        if highlight_type == "plagiarism":
            mark_open = '<mark class="plagiarism-highlight" style="background:#fee2e2; color:#991b1b; padding:2px 4px; border-radius:4px; font-weight:600; border:1px solid #f87171;">'
        else:
            mark_open = '<mark class="copyright-highlight" style="background:#fef08a; color:#854d0e; padding:2px 4px; border-radius:4px; font-weight:600; border:1px solid #fde047;">'
        mark_close = "</mark>"
    else:
        mark_open = "**"
        mark_close = "**"

    result = []
    cursor = 0
    for start, end in merged:
        result.append(generated_text[cursor:start])
        result.append(f"{mark_open}{generated_text[start:end]}{mark_close}")
        cursor = end
    result.append(generated_text[cursor:])

    return "".join(result)


def highlight_matches_by_category(
    generated_text: str,
    plagiarism_phrases: Optional[Set[str]] = None,
    copyright_phrases: Optional[Set[str]] = None,
    mode: str = "html",
) -> str:
    """
    Highlights text with separate distinct colors:
      - Plagiarism (external reference docs): Red/Rose highlight (#fee2e2, #991b1b, border: #f87171)
      - Copyright / Duplication (internal DB posts): Amber/Yellow highlight (#fef08a, #854d0e, border: #fde047)
    """
    plag = set(plagiarism_phrases or [])
    copyr = set(copyright_phrases or []) - plag  # Plagiarism takes higher priority

    if not plag and not copyr:
        return generated_text

    typed_spans: List[Tuple[int, int, str]] = []

    for phrase in plag:
        if not phrase.strip():
            continue
        for m in re.finditer(rf"\b{re.escape(phrase)}\b", generated_text, re.IGNORECASE):
            typed_spans.append((m.start(), m.end(), "plagiarism"))

    for phrase in copyr:
        if not phrase.strip():
            continue
        for m in re.finditer(rf"\b{re.escape(phrase)}\b", generated_text, re.IGNORECASE):
            typed_spans.append((m.start(), m.end(), "copyright"))

    if not typed_spans:
        return generated_text

    # Sort spans: earlier start first; if same start, longer first; plagiarism priority
    typed_spans.sort(key=lambda s: (s[0], -s[1], 0 if s[2] == "plagiarism" else 1))

    merged: List[Tuple[int, int, str]] = []
    cur_start, cur_end, cur_type = typed_spans[0]

    for s, e, t in typed_spans[1:]:
        if s <= cur_end:
            cur_end = max(cur_end, e)
            if t == "plagiarism":
                cur_type = "plagiarism"
        else:
            merged.append((cur_start, cur_end, cur_type))
            cur_start, cur_end, cur_type = s, e, t
    merged.append((cur_start, cur_end, cur_type))

    result = []
    cursor = 0
    for start, end, t in merged:
        result.append(generated_text[cursor:start])
        if mode == "html":
            if t == "plagiarism":
                open_tag = '<mark class="plagiarism-highlight" style="background:#fee2e2; color:#991b1b; padding:2px 4px; border-radius:4px; font-weight:600; border:1px solid #f87171;">'
            else:
                open_tag = '<mark class="copyright-highlight" style="background:#fef08a; color:#854d0e; padding:2px 4px; border-radius:4px; font-weight:600; border:1px solid #fde047;">'
            close_tag = "</mark>"
        else:
            open_tag = "**"
            close_tag = "**"
        result.append(f"{open_tag}{generated_text[start:end]}{close_tag}")
        cursor = end
    result.append(generated_text[cursor:])

    return "".join(result)


# ===========================================================================
# 3. Main Checker Functions
# ===========================================================================

def is_db_post_key(key: str) -> bool:
    """Checks if a corpus document key belongs to an internal database blog post or copyright archive."""
    lower_k = key.lower()
    return (
        lower_k.startswith("db_post_")
        or lower_k.startswith("database_post_")
        or lower_k.startswith("post_")
        or "copyright" in lower_k
        or "internal" in lower_k
        or "archive" in lower_k
        or "company" in lower_k
        or "local_db" in lower_k
    )


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
            "has_plagiarism": False,
            "has_copyright": False,
            "max_similarity": 0.0,
            "overall_scores": {},
            "flagged_documents": {},
            "plagiarism_phrases": [],
            "copyright_phrases": [],
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
    plagiarism_overlaps: Set[str] = set()
    copyright_overlaps: Set[str] = set()

    for label, ref_text in corpus.items():
        overlaps = find_overlapping_phrases(generated_text, ref_text, n=shingle_size)
        score = overall_scores.get(label, {}).get("tfidf_cosine", 0.0)
        is_db = is_db_post_key(label)

        if overlaps or score >= similarity_warn_threshold:
            flagged_docs[label] = {
                "type": "copyright" if is_db else "plagiarism",
                "tfidf_cosine": round(score, 3),
                "matched_phrases": sorted(list(overlaps)),
            }
            if is_db:
                copyright_overlaps |= overlaps
            else:
                plagiarism_overlaps |= overlaps

    all_overlaps = plagiarism_overlaps | copyright_overlaps
    has_plagiarism = len(plagiarism_overlaps) > 0 or any(
        d.get("type") == "plagiarism" and d.get("tfidf_cosine", 0) >= similarity_warn_threshold
        for d in flagged_docs.values()
    )
    has_copyright = len(copyright_overlaps) > 0 or any(
        d.get("type") == "copyright" and d.get("tfidf_cosine", 0) >= similarity_warn_threshold
        for d in flagged_docs.values()
    )
    is_flagged = has_plagiarism or has_copyright

    if has_plagiarism and has_copyright:
        summary_msg = f"Plagiarism & Copyright Flagged: {len(plagiarism_overlaps)} reference phrase(s) and {len(copyright_overlaps)} database match(es) detected (Max similarity: {round(max_sim * 100, 1)}%)."
    elif has_plagiarism:
        summary_msg = f"Plagiarism Warning: {len(plagiarism_overlaps)} phrase(s) matched reference documents (Max similarity: {round(max_sim * 100, 1)}%)."
    elif has_copyright:
        summary_msg = f"Shared Content Flagged: {len(copyright_overlaps)} phrase(s) matched existing blog posts (Max similarity: {round(max_sim * 100, 1)}%)."
    else:
        summary_msg = f"100% Unique: No significant duplication detected (Max similarity: {round(max_sim * 100, 1)}%)."

    highlighted_html = highlight_matches_by_category(
        generated_text,
        plagiarism_phrases=plagiarism_overlaps,
        copyright_phrases=copyright_overlaps,
        mode="html",
    )
    highlighted_md = highlight_matches_by_category(
        generated_text,
        plagiarism_phrases=plagiarism_overlaps,
        copyright_phrases=copyright_overlaps,
        mode="markdown",
    )

    return {
        "is_flagged": is_flagged,
        "has_plagiarism": has_plagiarism,
        "has_copyright": has_copyright,
        "max_similarity": round(max_sim, 3),
        "overall_scores": overall_scores,
        "flagged_documents": flagged_docs,
        "plagiarism_phrases": sorted(list(plagiarism_overlaps)),
        "copyright_phrases": sorted(list(copyright_overlaps)),
        "matched_phrases": sorted(list(all_overlaps)),
        "highlighted_text": highlighted_html,
        "highlighted_markdown": highlighted_md,
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

    plag_phrases = set(report.get("plagiarism_phrases", []))
    copyr_phrases = set(report.get("copyright_phrases", []))

    highlighted_title = highlight_matches_by_category(title, plag_phrases, copyr_phrases, mode="html")
    highlighted_short = highlight_matches_by_category(short_description, plag_phrases, copyr_phrases, mode="html")
    highlighted_desc = highlight_matches_by_category(description, plag_phrases, copyr_phrases, mode="html")

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
    Annotates a list of BlogPost objects with live copyright & plagiarism info:
      - post.is_flagged
      - post.has_plagiarism
      - post.has_copyright
      - post.max_similarity
      - post.plagiarism_phrases
      - post.copyright_phrases
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
        key = f"db_post_{pid}" if pid is not None else f"db_post_{id(p)}"
        post_corpus[key] = f"{title}\n{short_desc}\n{desc}"

    for p in posts:
        pid = getattr(p, "id", None)
        cur_key = f"db_post_{pid}" if pid is not None else f"db_post_{id(p)}"
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
        p.has_plagiarism = report.get("has_plagiarism", False)
        p.has_copyright = report.get("has_copyright", False)
        p.max_similarity = report.get("max_similarity", 0.0)
        p.plagiarism_phrases = report.get("plagiarism_phrases", [])
        p.copyright_phrases = report.get("copyright_phrases", [])
        p.matched_phrases = report.get("matched_phrases", [])
        highlighted_fields = report.get("highlighted_fields", {})
        p.highlighted_title = highlighted_fields.get("title", title)
        p.highlighted_short_description = highlighted_fields.get("short_description", short_desc)
        p.highlighted_description = highlighted_fields.get("description", desc)

    return posts


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        target = sys.argv[1]
        if os.path.isfile(target):
            with open(target, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            print(f"[*] Checking file: {target}")
        else:
            content = " ".join(sys.argv[1:])
            print(f"[*] Checking input text...")

        report = check_generated_text(content, shingle_size=3)
        print("\n" + "=" * 60)
        status_label = "✅ 100% UNIQUE"
        if report["has_plagiarism"] and report["has_copyright"]:
            status_label = "🚨 PLAGIARISM & COPYRIGHT DUPLICATION DETECTED"
        elif report["has_plagiarism"]:
            status_label = "🔴 PLAGIARISM DETECTED (Reference docs match)"
        elif report["has_copyright"]:
            status_label = "🟡 SHARED CONTENT DETECTED (Database match)"

        print(f"Status: {status_label}")
        print(f"Max Cosine Similarity: {round(report['max_similarity'] * 100, 1)}%")
        print(f"Summary: {report['summary_message']}")
        print("=" * 60)

        if report["is_flagged"]:
            if report.get("plagiarism_phrases"):
                print(f"\n🔴 Plagiarism Matches (Red Highlight) ({len(report['plagiarism_phrases'])}):")
                for phrase in report["plagiarism_phrases"]:
                    print(f"  - \"{phrase}\"")

            if report.get("copyright_phrases"):
                print(f"\n🟡 Internal Duplicate Matches (Yellow Highlight) ({len(report['copyright_phrases'])}):")
                for phrase in report["copyright_phrases"]:
                    print(f"  - \"{phrase}\"")

            print("\n[!] Highlighted HTML Preview:")
            print("-" * 60)
            print(report["highlighted_text"])
            print("-" * 60)
        else:
            print("\nNo overlapping phrases or duplicate content detected.")
    else:
        print("Usage: python db_copyright_checker.py <file_path_or_text>")

