"""
Extractive Event Title, Category, and Summary generator.
Selects representative central headlines and synthesizes concise, fact-grounded extractive summaries.
"""
from typing import List, Dict, Any, Optional
import re
from collections import Counter
from backend.app.ml.preprocessor import clean_text, ENGLISH_STOPWORDS


class EventTitleSummaryGenerator:
    """
    Deterministically derives event titles, extractive descriptions, and categories
    from actual member articles without generative hallucination.
    """

    CATEGORIES = {
        "Natural Disasters": ["earthquake", "tsunami", "flood", "hurricane", "typhoon", "wildfire", "volcano", "storm", "tremor"],
        "Science": ["telescope", "galaxy", "nasa", "astronomy", "space", "quantum", "discovery", "species", "biology", "fossil"],
        "Economy": ["ecb", "inflation", "interest rate", "bank", "central bank", "stocks", "bonds", "gdp", "recession", "markets"],
        "Environment": ["climate", "summit", "renewable", "carbon", "emissions", "pollution", "solar", "cop", "warming"],
        "Politics": ["election", "parliament", "congress", "senate", "minister", "president", "treaty", "diplomacy", "vote"],
        "Culture": ["museum", "exhibition", "art", "film", "renaissance", "festival", "theatre", "music"],
        "Public Safety": ["accident", "fire", "crash", "investigation", "police", "rescue", "safety"]
    }

    def select_representative_title(self, headlines: List[str], similarity_submatrix: Optional[Any] = None) -> str:
        """
        Select the headline that best represents the entire cluster.
        If similarity matrix is provided, chooses the central medoid (highest sum of similarities).
        Otherwise chooses the headline with highest frequency of dominant terms.
        """
        if not headlines:
            return "Untitled Event"
        if len(headlines) == 1:
            return headlines[0]

        if similarity_submatrix is not None and len(similarity_submatrix) == len(headlines):
            # Medoid selection: index with maximum row sum of similarities
            row_sums = [sum(row) for row in similarity_submatrix]
            best_idx = int(max(range(len(row_sums)), key=lambda i: row_sums[i]))
            return headlines[best_idx]

        # Term frequency fallback
        all_words = []
        for h in headlines:
            words = [w.lower() for w in re.findall(r"\b[a-zA-Z]{3,}\b", h) if w.lower() not in ENGLISH_STOPWORDS]
            all_words.extend(words)
        
        counts = Counter(all_words)
        # Score each headline by sum of keyword frequencies
        scores = []
        for h in headlines:
            words = [w.lower() for w in re.findall(r"\b[a-zA-Z]{3,}\b", h) if w.lower() not in ENGLISH_STOPWORDS]
            s = sum(counts[w] for w in words)
            scores.append(s)

        best_idx = int(max(range(len(scores)), key=lambda i: scores[i]))
        return headlines[best_idx]

    def infer_category(self, texts: List[str]) -> str:
        """
        Rule-based topic category classification based on matched domain keywords.
        Returns the category with highest term frequency match, or 'Unclassified'.
        """
        combined_text = " ".join(texts).lower()
        category_scores = {}

        for cat, keywords in self.CATEGORIES.items():
            score = sum(combined_text.count(kw) for kw in keywords)
            if score > 0:
                category_scores[cat] = score

        if not category_scores:
            return "Unclassified"

        best_cat = max(category_scores, key=category_scores.get)
        return best_cat

    def generate_extractive_summary(self, articles: List[Dict[str, Any]], max_sentences: int = 3) -> str:
        """
        Extract the first lead sentence from each unique source article to build
        a factual, source-attributed multi-article summary.
        """
        if not articles:
            return "No content available."

        sentences = []
        for art in articles:
            body = clean_text(art.get("body", ""))
            if not body:
                continue
            # Extract first sentence
            first_sentence_match = re.split(r"(?<=[.!?])\s+", body)
            if first_sentence_match and first_sentence_match[0]:
                lead_sent = first_sentence_match[0].strip()
                if len(lead_sent) > 20 and lead_sent not in sentences:
                    source = art.get("source_name", "Source")
                    sentences.append(f"{lead_sent} ({source})")
            if len(sentences) >= max_sentences:
                break

        if not sentences:
            return clean_text(articles[0].get("headline", ""))

        return " ".join(sentences)
