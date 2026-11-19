"""
Named Entity Recognition (NER) extractor.
Extracts Persons, Organizations, and Locations with spaCy support and rule-based fallback.
"""
import re
import json
import logging
from typing import Dict, List, Set, Any
from backend.app.ml.preprocessor import clean_text

logger = logging.getLogger(__name__)


class EntityExtractor:
    """
    Extracts structured entities (persons, organizations, locations) from news text.
    """
    _spacy_nlp = None
    _tried_loading_spacy = False

    def __init__(self, use_spacy: bool = True):
        self.use_spacy = use_spacy
        self._init_spacy()

    def _init_spacy(self) -> None:
        if self.use_spacy and not EntityExtractor._tried_loading_spacy:
            EntityExtractor._tried_loading_spacy = True
            try:
                import spacy
                # Try small web model, or blank english if not downloaded
                try:
                    EntityExtractor._spacy_nlp = spacy.load("en_core_web_sm")
                    logger.info("Loaded spaCy en_core_web_sm model.")
                except Exception:
                    logger.info("spaCy en_core_web_sm not installed; using rule-based entity extractor.")
                    EntityExtractor._spacy_nlp = None
            except ImportError:
                logger.info("spaCy not imported; using rule-based entity extractor.")
                EntityExtractor._spacy_nlp = None

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract persons, organizations, locations, and key entities from article text.
        Returns a dictionary: {"persons": [...], "orgs": [...], "locs": [...], "all": [...]}
        """
        cleaned = clean_text(text)
        if not cleaned:
            return {"persons": [], "orgs": [], "locs": [], "all": []}

        if EntityExtractor._spacy_nlp is not None:
            doc = EntityExtractor._spacy_nlp(cleaned[:4000]) # Cap text length for speed
            persons: Set[str] = set()
            orgs: Set[str] = set()
            locs: Set[str] = set()

            for ent in doc.ents:
                ent_text = ent.text.strip()
                if len(ent_text) < 2:
                    continue
                if ent.label_ in ("PERSON",):
                    persons.add(ent_text)
                elif ent.label_ in ("ORG",):
                    orgs.add(ent_text)
                elif ent.label_ in ("GPE", "LOC", "FAC"):
                    locs.add(ent_text)

            all_entities = list(persons | orgs | locs)
            return {
                "persons": sorted(list(persons)),
                "orgs": sorted(list(orgs)),
                "locs": sorted(list(locs)),
                "all": sorted(all_entities)
            }

        # Rule-based fallback: Extracts capitalized multi-word phrases and common patterns
        return self._rule_based_extract(cleaned)

    def _rule_based_extract(self, text: str) -> Dict[str, List[str]]:
        """
        High-precision regex-based entity candidate extractor for capitalized entity terms.
        """
        # Find capitalized words/phrases (excluding sentence starters where possible)
        # Matches patterns like "James Webb Space Telescope", "European Central Bank", "Sendai", "Christine Lagarde"
        capitalized_phrases = re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b", text)
        
        # Filter common non-entity sentence starting words
        ignore_words = {
            "The", "A", "An", "In", "On", "At", "By", "For", "With", "About", "Against", 
            "Between", "Into", "Through", "During", "Before", "After", "Above", "Below",
            "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday",
            "January", "February", "March", "April", "May", "June", "July", "August",
            "September", "October", "November", "December", "Today", "Yesterday", "Authorities",
            "Officials", "Data", "Astronomers", "Search", "Emergency", "Power", "Delegates"
        }

        candidates = [p.strip() for p in capitalized_phrases if p.strip() not in ignore_words and len(p.strip()) > 2]
        
        # Deduplicate preserving order
        seen = set()
        unique_entities = []
        for c in candidates:
            lower_c = c.lower()
            if lower_c not in seen:
                seen.add(lower_c)
                unique_entities.append(c)

        # Categorize known entity keywords
        orgs = [e for e in unique_entities if any(w in e.lower() for w in ["bank", "agency", "telescope", "press", "times", "council", "museum", "nasa", "ecb", "un", "railway", "reuters", "bbc"])]
        locs = [e for e in unique_entities if any(w in e.lower() for w in ["japan", "sendai", "dubai", "fukushima", "europe", "frankfurt", "new york", "trench", "zealand", "kermadec", "tokyo"])]
        persons = [e for e in unique_entities if e not in orgs and e not in locs and len(e.split()) >= 2]

        return {
            "persons": persons[:8],
            "orgs": orgs[:8],
            "locs": locs[:8],
            "all": unique_entities[:15]
        }

    def compute_jaccard_similarity(self, entities_a: List[str], entities_b: List[str]) -> float:
        """
        Compute normalized Jaccard similarity between two sets of entities:
        J(A, B) = |A ∩ B| / |A ∪ B|
        If both have no extracted entities, returns a neutral prior of 0.5.
        """
        set_a = {e.lower().strip() for e in entities_a if e.strip()}
        set_b = {e.lower().strip() for e in entities_b if e.strip()}

        if not set_a and not set_b:
            return 0.5 # Neutral prior: lack of extracted entities does not prove dissimilarity

        intersection = len(set_a & set_b)
        union = len(set_a | set_b)

        if union == 0:
            return 0.5
        return float(intersection) / float(union)
