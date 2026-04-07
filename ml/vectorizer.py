"""
ml/vectorizer.py
TF-IDF vectorization of code chunks.

What it does:
  - Takes all chunks (list of dicts with "content")
  - Cleans and preprocesses the text
  - Fits a TF-IDF vectorizer on the chunk contents
  - Returns the fitted vectorizer + sparse matrix
  - Also vectorizes a query string using the same fitted vectorizer
"""

import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer


# ─── Text Preprocessor ───────────────────────────────────────────────────────

def preprocess(text: str) -> str:
    """
    Clean code text for TF-IDF:
      - Lowercase
      - Remove comments (#, //, /* */)
      - Split camelCase / snake_case into tokens
      - Remove special characters (keep letters + digits)
      - Collapse whitespace
    """
    # Remove single-line comments (# and //)
    text = re.sub(r'#.*', ' ', text)
    text = re.sub(r'//.*', ' ', text)

    # Remove multi-line comments (/* ... */)
    text = re.sub(r'/\*.*?\*/', ' ', text, flags=re.DOTALL)

    # Split snake_case → individual words
    text = text.replace('_', ' ')

    # Split camelCase → individual words  (e.g. getUserName → get User Name)
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)

    # Lowercase
    text = text.lower()

    # Remove anything that isn't a letter or digit
    text = re.sub(r'[^a-z0-9\s]', ' ', text)

    # Collapse whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    return text


# ─── Build Vectorizer ────────────────────────────────────────────────────────

def build_vectorizer(chunks: list[dict]):
    """
    Fit a TF-IDF vectorizer on the given chunks.

    Input:
        chunks = [{"chunk_id", "content", "file_path", ...}, ...]

    Returns:
        vectorizer  : fitted TfidfVectorizer
        tfidf_matrix: sparse matrix, shape (n_chunks, n_features)
        report      : dict with stats
    """
    if not chunks:
        return None, None, {"error": "No chunks provided"}

    # Preprocess each chunk's content
    corpus = [preprocess(c["content"]) for c in chunks]

    # Remove empty strings after preprocessing
    corpus = [text if text.strip() else "empty" for text in corpus]

    vectorizer = TfidfVectorizer(
        max_features=5000,      # top 5000 terms
        min_df=1,               # term must appear in at least 1 doc
        max_df=0.95,            # ignore terms in >95% of docs (too common)
        sublinear_tf=True,      # apply log normalization to TF
        ngram_range=(1, 2),     # unigrams + bigrams
    )

    tfidf_matrix = vectorizer.fit_transform(corpus)

    report = {
        "n_chunks"    : tfidf_matrix.shape[0],
        "n_features"  : tfidf_matrix.shape[1],
        "vocab_size"  : len(vectorizer.vocabulary_),
        "top_terms"   : _top_terms(vectorizer, n=10),
    }

    return vectorizer, tfidf_matrix, report


# ─── Vectorize a Query ───────────────────────────────────────────────────────

def vectorize_query(query: str, vectorizer):
    """
    Transform a user query into a TF-IDF vector using the fitted vectorizer.

    Returns:
        query_vector: sparse matrix, shape (1, n_features)
    """
    cleaned = preprocess(query)
    if not cleaned.strip():
        cleaned = query.lower()   # fallback: use raw query lowercased
    return vectorizer.transform([cleaned])


# ─── Helper ──────────────────────────────────────────────────────────────────

def _top_terms(vectorizer, n: int = 10) -> list[str]:
    """Return the top N terms by IDF score (most informative)."""
    feature_names = vectorizer.get_feature_names_out()
    idf_scores    = vectorizer.idf_
    # Higher IDF = more unique/informative term
    top_indices   = np.argsort(idf_scores)[::-1][:n]
    return [feature_names[i] for i in top_indices]