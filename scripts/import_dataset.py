"""
CLI script to import a dataset CSV or JSON file into the database.
Usage:
    python scripts/import_dataset.py --file data/fixtures/test_news_events.json
"""
import sys
import os
import argparse
import json
from datetime import datetime, timezone

# Ensure project root in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.db.session import init_db, SessionLocal
from backend.app.services.article_service import ArticleService
from backend.app.ingestion.file_provider import FileDatasetProvider


def main():
    parser = argparse.ArgumentParser(description="Import news dataset into persistent database.")
    parser.add_argument("--file", "-f", required=True, help="Path to CSV or JSON dataset file.")
    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"Error: File '{args.file}' not found.")
        sys.exit(1)

    init_db()
    db = SessionLocal()

    with open(args.file, "rb") as f:
        content = f.read()

    provider = FileDatasetProvider()
    try:
        report = provider.parse_and_validate(content, os.path.basename(args.file))
        print(f"Validation successful: {report['valid_rows']} valid rows, {report['duplicate_rows']} duplicates.")
        
        service = ArticleService(db)
        result = service.import_articles_batch(report["valid_articles"])
        print(f"Import complete: {result['inserted']} articles inserted, {result['skipped']} duplicates skipped.")
    except Exception as e:
        print(f"Import failed: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
