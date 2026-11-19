"""
Text preprocessing and normalization pipeline for news articles.
Handles tokenization, cleaning, HTML unescaping, punctuation normalization, and stable content hashing.
"""
import re
import html
import string
import hashlib
from typing import List, Set

ENGLISH_STOPWORDS: Set[str] = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", 
    "aren't", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", 
    "but", "by", "can", "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", 
    "doesn't", "doing", "don't", "down", "during", "each", "few", "for", "from", "further", "had", 
    "hadn't", "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", 
    "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", 
    "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", 
    "let's", "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", 
    "on", "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own", 
    "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", 
    "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", 
    "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", 
    "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we", 
    "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when", "when's", 
    "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with", "won't", 
    "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours", 
    "yourself", "yourselves"
}


def clean_text(text: str) -> str:
    """
    Standardize text: unescapes HTML entities, strips tags, attaches trailing punctuation,
    and normalizes whitespace.
    """
    if not text:
        return ""
    # Unescape HTML entities (&nbsp;, &amp;, etc.)
    text = html.unescape(text)
    # Strip HTML tags
    text = re.sub(r"<[^>]+>", " ", text)
    # Attach floating punctuation attached to whitespace (e.g. "word !" -> "word!")
    text = re.sub(r"\s+([.,!?;:])", r"\1", text)
    # Normalize unicode whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenize(text: str, remove_stopwords: bool = True) -> List[str]:
    """
    Tokenize text into lowercased alphanumeric words, optionally removing stopwords.
    """
    cleaned = clean_text(text).lower()
    raw_tokens = re.findall(r"\b[a-z0-9\-]+\b", cleaned)
    tokens = []
    for tok in raw_tokens:
        tok = tok.strip("-")
        if not tok or len(tok) < 2:
            continue
        if remove_stopwords and tok in ENGLISH_STOPWORDS:
            continue
        tokens.append(tok)
    return tokens


def compute_content_hash(headline: str, body: str) -> str:
    """
    Compute a deterministic SHA-256 hash of normalized headline and body content
    to detect exact and near-exact duplicate articles.
    """
    norm_h = clean_text(headline).lower()
    norm_b = clean_text(body).lower()
    payload = f"{norm_h}|{norm_b}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()
