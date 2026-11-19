# Dataset Guide and Ingestion Format

## 1. Supported Formats

The system supports importing offline news article datasets via either **JSON** or **CSV** formats through the `Dataset Management` UI page or the `POST /api/articles/import` endpoint.

---

## 2. Schema Specification

Each record in a dataset should contain the following fields:

| Field | Type | Required | Description |
|---|---|---|---|
| `headline` | String | Yes | Article headline / title (min 3 characters). |
| `body` | String | Yes | Full article text content. |
| `source_name` | String | Yes | Name of publisher or agency (e.g. "Reuters", "BBC News"). |
| `published_at` | ISO-8601 String | Yes | UTC timestamp (e.g. `2024-03-11T08:15:00Z`). |
| `source_url` | String / URL | No | Web URL of original article publication. |
| `external_id` | String | No | Unique identifier in originating feed or source archive. |
| `ground_truth_event_id` | String | No | Ground-truth event cluster ID for evaluation (e.g. `event-sendai-quake-2024`). Set to `null` or omit for noise articles. |
| `category` | String | No | Optional topic category (e.g. "Natural Disasters", "Science", "Economy"). |

---

## 3. JSON Structure Example

```json
[
  {
    "headline": "Magnitude 7.2 earthquake strikes off coast of Sendai, triggering tsunami advisory",
    "body": "A powerful 7.2-magnitude earthquake struck off the northeastern coast of Japan near Sendai on Monday morning...",
    "source_name": "Reuters",
    "source_url": "https://www.reuters.com/world/asia-pacific/earthquake-japan-sendai-2024",
    "published_at": "2024-03-11T08:15:00Z",
    "ground_truth_event_id": "event-sendai-quake-2024",
    "category": "Natural Disasters"
  }
]
```

---

## 4. Built-in Benchmark Fixture

A pre-packaged verified research benchmark fixture is available at:
- `data/fixtures/test_news_events.json`
- `data/fixtures/test_news_events.csv`

It contains 14 articles across 4 ground-truth real-world events and 2 noise singletons:
1. **Sendai Japan Offshore Earthquake (March 11–12, 2024)**: 4 articles from Reuters, AP, BBC, Japan Times.
2. **James Webb Space Telescope Ancient Galaxy Cluster (March 14–15, 2024)**: 3 articles from NASA Science, Nature Astronomy, ScienceDaily.
3. **European Central Bank Interest Rate Decision (March 18–19, 2024)**: 3 articles from Financial Times, Bloomberg, Reuters.
4. **Dubai Global Climate Summit Renewable Accord (March 23, 2024)**: 2 articles from The Guardian, The New York Times.
5. **Noise / Singletons**: 2 articles (Murano Glass Exhibition, Bioluminescent Lanternfish in Kermadec Trench).
