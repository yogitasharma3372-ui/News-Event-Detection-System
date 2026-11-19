"""
Dataset File Ingestion and Validation Provider.
Parses, validates, and deduplicates imported CSV and JSON files.
"""
from datetime import datetime, timezone
import json
import io
import csv
from typing import List, Dict, Any, Tuple, Optional
from backend.app.ml.preprocessor import clean_text, compute_content_hash


class FileDatasetProvider:
    """
    Parses and rigorously validates CSV and JSON datasets containing news records.
    """

    SUPPORTED_EXTENSIONS = [".csv", ".json"]
    MAX_FILE_BYTES = 25 * 1024 * 1024 # 25 MB safety limit

    def parse_and_validate(
        self,
        file_content: bytes,
        filename: str,
        column_mapping: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Validate file structure, detect duplicates, and extract normalized records.
        """
        if len(file_content) > self.MAX_FILE_BYTES:
            raise ValueError(f"File exceeds maximum allowed size of {self.MAX_FILE_BYTES // (1024*1024)} MB.")

        is_json = filename.lower().endswith(".json")
        is_csv = filename.lower().endswith(".csv")

        if not (is_json or is_csv):
            raise ValueError("Unsupported file format. Please upload a .csv or .json file.")

        raw_rows: List[Dict[str, Any]] = []

        if is_json:
            try:
                data = json.loads(file_content.decode("utf-8"))
                if isinstance(data, list):
                    raw_rows = data
                elif isinstance(data, dict) and "articles" in data:
                    raw_rows = data["articles"]
                else:
                    raise ValueError("JSON file must be an array of objects or contain an 'articles' key.")
            except Exception as e:
                raise ValueError(f"Invalid JSON format: {e}")
        else:
            try:
                text_stream = io.StringIO(file_content.decode("utf-8-sig"))
                reader = csv.DictReader(text_stream)
                raw_rows = [row for row in reader]
            except Exception as e:
                raise ValueError(f"Invalid CSV format: {e}")

        # Column mapping defaults
        mapping = {
            "headline": "headline",
            "body": "body",
            "source_name": "source_name",
            "source_url": "source_url",
            "published_at": "published_at",
            "external_id": "external_id",
            "ground_truth_event_id": "ground_truth_event_id",
            "category": "category"
        }
        if column_mapping:
            mapping.update(column_mapping)

        valid_articles: List[Dict[str, Any]] = []
        errors: List[str] = []
        seen_hashes = set()
        duplicate_count = 0

        for row_idx, row in enumerate(raw_rows):
            line_num = row_idx + 1

            headline = clean_text(str(row.get(mapping["headline"], "") or ""))
            body = clean_text(str(row.get(mapping["body"], "") or ""))

            if not headline:
                errors.append(f"Row {line_num}: Missing required 'headline'.")
                continue

            if not body:
                body = headline # Fallback to headline if body empty

            source = clean_text(str(row.get(mapping["source_name"], "") or "Unknown Source"))
            url = row.get(mapping["source_url"])
            if url:
                url = str(url).strip()

            # Parse timestamp
            raw_time = row.get(mapping["published_at"])
            pub_date = None
            if raw_time:
                try:
                    time_str = str(raw_time).strip().replace("Z", "+00:00")
                    pub_date = datetime.fromisoformat(time_str)
                except Exception:
                    # Try common format
                    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d/%m/%Y"):
                        try:
                            pub_date = datetime.strptime(str(raw_time).strip(), fmt)
                            break
                        except Exception:
                            pass

            if pub_date is None:
                errors.append(f"Row {line_num}: Invalid or missing published_at timestamp ('{raw_time}').")
                continue

            # Ensure UTC timezone
            if pub_date.tzinfo is None:
                pub_date = pub_date.replace(tzinfo=timezone.utc)
            else:
                pub_date = pub_date.astimezone(timezone.utc)

            content_hash = compute_content_hash(headline, body)
            if content_hash in seen_hashes:
                duplicate_count += 1
                continue
            seen_hashes.add(content_hash)

            gt_id = row.get(mapping["ground_truth_event_id"])
            if gt_id:
                gt_id = str(gt_id).strip() or None

            cat = row.get(mapping["category"])
            if cat:
                cat = str(cat).strip() or None

            ext_id = row.get(mapping["external_id"]) or row.get("id")
            if ext_id:
                ext_id = str(ext_id).strip()

            valid_articles.append({
                "headline": headline,
                "body": body,
                "source_name": source,
                "source_url": url,
                "published_at": pub_date,
                "external_id": ext_id,
                "content_hash": content_hash,
                "ground_truth_event_id": gt_id,
                "category": cat,
                "language": "en"
            })

        preview_records = []
        for art in valid_articles[:5]:
            p = art.copy()
            p["published_at"] = p["published_at"].isoformat()
            preview_records.append(p)

        return {
            "total_rows": len(raw_rows),
            "valid_rows": len(valid_articles),
            "invalid_rows": len(errors),
            "duplicate_rows": duplicate_count,
            "errors": errors[:20],
            "valid_articles": valid_articles,
            "preview": preview_records
        }
