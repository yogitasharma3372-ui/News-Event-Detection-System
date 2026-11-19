"""
Unit tests for data ingestion, CSV/JSON parser, and duplicate detection.
"""
import pytest
from backend.app.ingestion.file_provider import FileDatasetProvider

provider = FileDatasetProvider()


def test_parse_valid_csv():
    csv_bytes = (
        "headline,body,source_name,published_at\n"
        "\"Test Headline 1\",\"A full article body describing an event.\",\"Reuters\",\"2024-03-11T12:00:00Z\"\n"
        "\"Test Headline 2\",\"Another full article body content.\",\"BBC\",\"2024-03-11T14:00:00Z\"\n"
    ).encode("utf-8")

    report = provider.parse_and_validate(csv_bytes, "news.csv")
    assert report["valid_rows"] == 2
    assert report["invalid_rows"] == 0
    assert report["duplicate_rows"] == 0


def test_parse_detects_exact_duplicate_rows():
    csv_bytes = (
        "headline,body,source_name,published_at\n"
        "\"Duplicate Article\",\"Exact same body text here.\",\"Source A\",\"2024-03-11T12:00:00Z\"\n"
        "\"Duplicate Article\",\"Exact same body text here.\",\"Source B\",\"2024-03-11T13:00:00Z\"\n"
    ).encode("utf-8")

    report = provider.parse_and_validate(csv_bytes, "news_dupes.csv")
    assert report["valid_rows"] == 1
    assert report["duplicate_rows"] == 1


def test_parse_rejects_missing_headline():
    csv_bytes = (
        "headline,body,source_name,published_at\n"
        "\"\",\"Body content without headline.\",\"AP\",\"2024-03-11T12:00:00Z\"\n"
    ).encode("utf-8")

    report = provider.parse_and_validate(csv_bytes, "invalid.csv")
    assert report["valid_rows"] == 0
    assert report["invalid_rows"] == 1
    assert "Missing required 'headline'" in report["errors"][0]


def test_parse_rejects_malformed_timestamp():
    csv_bytes = (
        "headline,body,source_name,published_at\n"
        "\"Valid Headline\",\"Valid Body Content.\",\"AP\",\"not-a-valid-date\"\n"
    ).encode("utf-8")

    report = provider.parse_and_validate(csv_bytes, "invalid_time.csv")
    assert report["valid_rows"] == 0
    assert report["invalid_rows"] == 1
    assert "Invalid or missing published_at" in report["errors"][0]
