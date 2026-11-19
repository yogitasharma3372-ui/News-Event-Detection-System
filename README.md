# News Event Detection and Tracking System — Time-Aware Semantic News Intelligence

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.15+-ee4c2c.svg)](https://pytorch.org/)
[![Sentence--Transformers](https://img.shields.io/badge/Sentence--Transformers-all--MiniLM--L6--v2-orange.svg)](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
[![React 19](https://img.shields.io/badge/React-19.3-61dafb.svg)](https://react.dev/)
[![Tests](https://img.shields.io/badge/Tests-24%20Passing-emerald.svg)](backend/tests/)

An end-to-end Machine Learning research platform and interactive intelligence dashboard designed to automatically discover, cluster, track, and evaluate real-world news stories across temporal intervals and journalistic sources.

---

## 1. Project Overview & Problem Statement

In the modern digital information ecosystem, thousands of news stories are published every minute across hundreds of agencies, blogs, and syndication feeds. News readers, financial analysts, and intelligence teams face two fundamental challenges:

1. **Information Fragmentation & Duplication**: The same real-world event (e.g., a natural disaster, macroeconomic policy announcement, or diplomatic accord) is reported by multiple independent publishers using disparate vocabulary, varied journalistic framing, and differing levels of detail.
2. **Entity & Topical Ambiguity**: Distinct, independent events often share identical named entities, organizations, or geopolitical locations (e.g., two unrelated bilateral summits occurring months apart in the same city, or separate legal proceedings involving the same multinational corporation).

Conventional keyword matching and pure bag-of-words models (e.g., TF-IDF) fail to capture semantic paraphrasing and conflate unrelated articles that merely mention the same recurring public figures or locations. Conversely, standard semantic embeddings ignore publication timestamps and can erroneously cluster recurring events that occurred months or years apart.

**Time-Aware Semantic News Intelligence** solves this dilemma by fusing dense semantic sentence embeddings, exponential temporal decay, and named-entity Jaccard overlap into a unified convex similarity metric for precision event clustering.

---

## 2. Research Questions & Objectives

### Primary Research Question
> **Does combining dense semantic embeddings with temporal proximity decay and named-entity overlap improve news event clustering compared to conventional TF-IDF and semantic-embedding baselines?**

### Secondary Research Questions
1. **Temporal Disambiguation**: Does incorporating exponential temporal decay $S_{\text{temporal}} = \exp(-\Delta t / \tau)$ systematically prevent false merges of temporally distant stories that share topical vocabulary?
2. **Entity Grounding**: Does Jaccard overlap of extracted named entities (persons, organizations, geopolitical locations) improve cluster purity on heterogeneous news corpora?
3. **Incremental Assignment**: How effectively can an online system incrementally assign incoming streaming articles to active event timelines without re-clustering the historical archive from scratch?
4. **Modality Contribution**: Which individual component contributes most significantly to clustering quality across standard B-cubed, ARI, and NMI metrics?

### Main Project Objectives
- Build an end-to-end reproducible machine learning pipeline for automated news event discovery.
- Implement and benchmark three competing approaches: TF-IDF baseline, dense Sentence Transformer semantic baseline, and the proposed hybrid multi-modal fusion model.
- Provide a persistent relational database backing historical article tracking, deduplication, event evolution, and manual human verification.
- Offer an interactive, research-grade React dashboard featuring 8 functional pages for data exploration, real-time live ingestion, parameter sensitivity tuning, and ablation visualization.

---

## 3. Key System Features

- **Automated Text Normalization & SHA-256 Deduplication**: Unescapes HTML entities, normalizes whitespace and punctuation, strips boilerplate, and computes deterministic content hashes to eliminate exact and near-verbatim duplicate articles.
- **Dense Embedding Pipeline with Disk Caching**: Real on-device neural inference using `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions) with persistent `.npy` file caching for high-throughput batch operations.
- **Named Entity Recognition (NER)**: Extracts Persons (`PER`), Organizations (`ORG`), and Geopolitical Entities (`LOC`/`GPE`) with fallback regex rule-based extraction when NLP models are offline.
- **Exponential Temporal Decay**: Calibrated temporal scoring window ($\tau = 72\text{ hours}$) that models natural news story life cycles while allowing cross-day event tracking.
- **Distance-Thresholded Agglomerative Clustering**: Average linkage hierarchical clustering operating over the unified hybrid distance matrix $D(A, B) = 1.0 - S_{\text{combined}}(A, B)$, with explicit singleton noise separation ($C_i = -1$).
- **Extractive Event Summarization**: Automatically synthesizes event titles by selecting the centroid medoid article headline and extracts representative lead sentences with source agency attribution.
- **Live News Ingestion Pipeline**: Ingests live RSS 2.0 / Atom feeds and connects to the NewsAPI REST endpoint with rate-limit guards and error resilience.
- **Comprehensive Evaluation Benchmark**: Computes B-cubed Precision, B-cubed Recall, B-cubed F1, Adjusted Rand Index (ARI), Normalized Mutual Information (NMI), and Pairwise F1 metrics with a dedicated 4-way ablation suite.
- **Manual Verification Audit Trail**: Allows human analysts to reassign articles or override event boundaries while protecting human-verified records from being overwritten by automated batch jobs.

---

## 4. System Architecture

```
news-event-detection/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application entrypoint & middleware
│   │   ├── core/config.py       # Pydantic Settings & environment variables
│   │   ├── db/                  # SQLite declarative base, engine, & sessionmaker
│   │   ├── models/              # SQLAlchemy 2.0 ORM models (Article, Event, Assignment, etc.)
│   │   ├── schemas/             # Pydantic validation schemas
│   │   ├── ml/                  # Machine Learning & NLP algorithms
│   │   │   ├── preprocessor.py  # Text normalization, tokenization, SHA-256 content hash
│   │   │   ├── tfidf_model.py   # Baseline 1: TF-IDF vectorizer & cosine similarity
│   │   │   ├── embedding_model.py # Baseline 2: SentenceTransformer (all-MiniLM-L6-v2) with cache
│   │   │   ├── ner_extractor.py # Named Entity Recognition (spaCy & rule-based parser)
│   │   │   ├── temporal_scoring.py # Exponential decay temporal proximity calculator
│   │   │   ├── hybrid_scorer.py # Proposed Hybrid Model (alpha, beta, gamma fusion)
│   │   │   ├── clusterer.py     # Agglomerative clustering & online incremental assigner
│   │   │   └── title_generator.py # Extractive title, category, & lead-sentence synthesis
│   │   ├── evaluation/          # B-cubed, ARI, NMI, and 4-way ablation benchmark engine
│   │   ├── ingestion/           # RSS/Atom, NewsAPI, and CSV/JSON upload adapters
│   │   └── services/            # Business logic orchestration
│   ├── tests/                   # 24 automated unit & integration tests
│   └── requirements.txt         # Pinned backend dependencies
├── frontend/
│   ├── src/
│   │   ├── api/client.ts        # Typed fetch client connecting to FastAPI backend
│   │   ├── components/          # Reusable UI widgets (Navbar, Sidebar, Cards, Timeline)
│   │   ├── pages/               # 8 Core Dashboard Pages
│   │   │   ├── OverviewPage.tsx         # Dashboard summary & category distributions
│   │   │   ├── NewsExplorerPage.tsx     # Article search, source & date filtering
│   │   │   ├── EventExplorerPage.tsx    # Event clusters & parameter tuning
│   │   │   ├── EventDetailPage.tsx      # Chronological timeline & article inspector
│   │   │   ├── LiveMonitorPage.tsx      # Live RSS & API ingestion monitor
│   │   │   ├── ResearchLabPage.tsx      # Interactive model comparison & parameter sliders
│   │   │   ├── EvaluationPage.tsx       # 4-way ablation comparative charts
│   │   │   ├── DatasetManagementPage.tsx # Pre-validation report & CSV/JSON import
│   │   │   └── SettingsPage.tsx         # Model parameters & API key configuration
│   │   ├── types/index.ts       # TypeScript domain interfaces
│   │   ├── App.tsx              # Root application layout & state
│   │   └── index.css            # Tailwind CSS styling
│   ├── package.json
│   └── vite.config.ts           # Vite development server with backend proxy
├── data/
│   └── fixtures/                # Pre-packaged 14-article verified research benchmark
├── docs/                        # Architecture, methodology, and evaluation guides
│   ├── architecture.md
│   ├── dataset_guide.md
│   ├── evaluation_protocol.md
│   ├── methodology.md
│   └── troubleshooting.md
├── scripts/                     # Standalone CLI tools for import, training, and evaluation
│   ├── evaluate_models.py
│   ├── import_dataset.py
│   ├── run_experiment.py
│   └── verify_endpoints.py
├── .env.example
├── .gitignore
├── pytest.ini
└── README.md
```

---

## 5. Technology Stack

| Layer | Technologies |
|---|---|
| **Backend Framework** | Python 3.12 / 3.11, FastAPI 0.115+, Pydantic v2, Uvicorn |
| **ORM & Database** | SQLAlchemy 2.0, SQLite (persistent, zero-configuration) |
| **Data Ingestion** | Feedparser (RSS 2.0 / Atom), HTTPX (async client), Pandas, NumPy |
| **Machine Learning & NLP** | `sentence-transformers` (`all-MiniLM-L6-v2`), `scikit-learn` 1.4+, `PyTorch` 2.15+ |
| **Frontend Framework** | React 19, TypeScript, Vite 8 |
| **Styling & Visualization** | Tailwind CSS v4, Recharts 3.11, Lucide React Icons |
| **Testing & Quality** | Pytest 8, In-memory SQLite fixtures, Static typing |

---

## 6. Machine Learning Methodology & Formulas

### 6.1 Baseline 1: TF-IDF Vectorizer
Extracts unigram and bigram token frequencies weighted by sublinear inverse document frequency:
$$\text{TF-IDF}(t, d, D) = (1 + \log \text{TF}(t, d)) \cdot \log\left(\frac{1 + |D|}{1 + \text{DF}(t, D)}\right)$$
Pairwise similarity is computed via cosine similarity between sparse vectors:
$$S_{\text{tfidf}}(A, B) = \frac{\mathbf{u}_{\text{tfidf}} \cdot \mathbf{v}_{\text{tfidf}}}{\|\mathbf{u}_{\text{tfidf}}\|_2 \|\mathbf{v}_{\text{tfidf}}\|_2}$$

### 6.2 Baseline 2: Dense Semantic Embeddings
Articles are embedded using the lightweight SentenceTransformer model `all-MiniLM-L6-v2` ($d = 384$). Raw cosine similarity is mapped to a strictly non-negative range $[0.0, 1.0]$:
$$S_{\text{semantic}}(A, B) = \text{clip}\left(\frac{\cos(\mathbf{e}_A, \mathbf{e}_B) + 1.0}{2.0}, 0.0, 1.0\right)$$

### 6.3 Exponential Temporal Decay ($S_{\text{temporal}}$)
Given publication timestamps $t_A, t_B \in \text{UTC}$:
$$\Delta t = \frac{|t_A - t_B|_{\text{seconds}}}{3600.0} \quad (\text{elapsed hours})$$
$$S_{\text{temporal}}(A, B) = \exp\left( -\frac{\Delta t}{\tau} \right)$$
- $\tau$: Half-decay time constant in hours (calibrated default: $\tau = 72.0\text{ hours}$).
- For articles missing a publication timestamp, a neutral uninformative prior of $S_{\text{temporal}} = 0.5$ is applied.

### 6.4 Named-Entity Jaccard Overlap ($S_{\text{entity}}$)
Given entity sets $E_A, E_B \subset \{\text{Persons, Organizations, Geopolitical Entities}\}$:
$$S_{\text{entity}}(A, B) = \begin{cases}
\frac{|E_A \cap E_B|}{|E_A \cup E_B|} & \text{if } |E_A \cup E_B| > 0 \\
0.5 & \text{otherwise (neutral prior)}
\end{cases}$$

### 6.5 Unified Hybrid Model Formulation
The overall pairwise similarity $S_{\text{combined}}$ is defined as a convex combination:
$$S_{\text{combined}}(A, B) = \alpha \cdot S_{\text{semantic}}(A, B) + \beta \cdot S_{\text{temporal}}(A, B) + \gamma \cdot S_{\text{entity}}(A, B)$$
Subject to the simplex constraints:
$$\alpha + \beta + \gamma = 1.0, \quad \alpha \ge 0, \beta \ge 0, \gamma \ge 0$$

**Default Calibrated Weights**:
- $\alpha = 0.55$ (Semantic weight)
- $\beta = 0.25$ (Temporal weight)
- $\gamma = 0.20$ (Entity weight)
- Clustering Distance Threshold $\theta_{\text{sim}} = 0.60 - 0.62$

---

## 7. Dataset Information & Source Attribution

The system includes a pre-packaged, verified research benchmark fixture located in `data/fixtures/`:
- `data/fixtures/test_news_events.json`
- `data/fixtures/test_news_events.csv`

### Benchmark Composition (14 Articles, 4 Ground-Truth Events, 2 Singletons)
1. **Sendai Japan Offshore Earthquake (March 11–12, 2024)**: 4 articles from Reuters, Associated Press, BBC World News, and The Japan Times.
2. **James Webb Space Telescope Ancient Galaxy Cluster (March 14–15, 2024)**: 3 articles from NASA Science, Nature Astronomy, and ScienceDaily.
3. **European Central Bank Interest Rate Decision (March 18–19, 2024)**: 3 articles from Financial Times, Bloomberg News, and Reuters Business.
4. **Dubai Global Climate Summit Renewable Accord (March 23, 2024)**: 2 articles from The Guardian and The New York Times.
5. **Noise / Singletons**: 2 articles (Venetian Murano Glass Craftsmanship Exhibition, Bioluminescent Lanternfish Discovery in Kermadec Trench).

Each record includes headline, full body text, publisher name, verified UTC timestamp, ground-truth event ID, and topical category.

---

## 8. Installation & Setup Guide (Windows PowerShell)

### Prerequisites
- Python 3.11 or Python 3.12
- Node.js 18+ and npm
- Git

### Step 1: Open PowerShell and Navigate to the Repository
```powershell
cd "c:\Users\Asus\OneDrive\Desktop\NLP project"
```

### Step 2: Set Up Python Virtual Environment
```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Step 3: Install Backend Dependencies
```powershell
pip install -r backend/requirements.txt
```

### Step 4: Install Frontend Dependencies
```powershell
cd frontend
npm install
cd ..
```

### Step 5: Configure Environment Variables
Create your local `.env` from the provided template:
```powershell
Copy-Item .env.example .env
```
*(The system works out-of-the-box with default settings; no third-party API key is required for local benchmarks and RSS feeds).*

---

## 9. Running the Application

### Start the FastAPI Backend Server
Open **Terminal 1**:
```powershell
.\.venv\Scripts\uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
- API Base URL: `http://127.0.0.1:8000`
- Swagger Interactive Docs: `http://127.0.0.1:8000/docs`
- Redoc API Reference: `http://127.0.0.1:8000/redoc`
- Health Check: `http://127.0.0.1:8000/api/health`

### Start the React Frontend Dashboard
Open **Terminal 2**:
```powershell
cd frontend
npm run dev
```
- Frontend Application URL: `http://localhost:5173`

---

## 10. API Endpoint Reference

| HTTP Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | System health, database connection, model cache status |
| `GET` | `/api/metadata` | Runtime configuration and supported model options |
| `GET` | `/api/articles` | Query paginated articles with search, source, and date filters |
| `POST` | `/api/articles` | Ingest and preprocess a single new article |
| `POST` | `/api/articles/import` | Batch import articles from JSON or CSV file |
| `GET` | `/api/events` | List all discovered event clusters with metrics |
| `GET` | `/api/events/{id}` | Detailed chronological event timeline and assigned articles |
| `POST` | `/api/events/recluster` | Trigger batch re-clustering with custom $\alpha, \beta, \gamma, \theta$ |
| `POST` | `/api/events/{id}/reassign` | Manual reassignment / human review override |
| `POST` | `/api/experiments/run` | Execute clustering experiment and record results |
| `GET` | `/api/experiments` | List historical clustering experiment runs |
| `GET` | `/api/evaluation/ablation` | Execute 4-way ablation benchmark and return metric comparisons |
| `POST` | `/api/ingestion/rss/fetch` | Trigger live RSS feed pull |
| `POST` | `/api/ingestion/newsapi/fetch` | Trigger live NewsAPI fetch (requires `NEWSAPI_KEY`) |
| `GET` | `/api/settings` | Retrieve active ML hyperparameters and configuration |
| `PUT` | `/api/settings` | Update runtime similarity weights and clustering thresholds |

---

## 11. Automated Testing & Verification

The project includes 24 automated Pytest tests verifying text preprocessing, tokenization, SHA-256 deduplication, ML baselines, hybrid scoring, agglomerative clustering, B-cubed evaluation, and API routes.

Run the complete test suite:
```powershell
.\.venv\Scripts\pytest -v
```
All 24 tests pass deterministically.

---

## 12. Command-Line Experiment Execution

### 1. Execute the 4-Way Model Ablation Study
```powershell
.\.venv\Scripts\python.exe scripts/evaluate_models.py
```
Output:
```
================================================================================
Model Variant             | B-cubed F1 | Precision  | Recall     | ARI      | NMI     
================================================================================
Semantic Only             |    100.0% |    100.0% |    100.0% |    1.000 |    1.000
Semantic + Time           |    100.0% |    100.0% |    100.0% |    1.000 |    1.000
Semantic + Entity         |     94.3% |    100.0% |     89.3% |    0.851 |    0.954
Proposed Full Hybrid      |    100.0% |    100.0% |    100.0% |    1.000 |    1.000
================================================================================
```

### 2. Run a Custom Parameter Sensitivity Experiment
```powershell
.\.venv\Scripts\python.exe scripts/run_experiment.py --algo hybrid --alpha 0.55 --beta 0.25 --gamma 0.20 --threshold 0.60
```

### 3. Import Research Dataset via CLI
```powershell
.\.venv\Scripts\python.exe scripts/import_dataset.py --file data/fixtures/test_news_events.json
```

---

## 13. Evaluation Metrics & Methodology

Clustering performance is assessed using rigorous, item-level metrics:
- **B-Cubed Precision & Recall**: Avoids cluster size bias by estimating per-item precision $P_i = \frac{|C(i) \cap L(i)|}{|C(i)|}$ and recall $R_i = \frac{|C(i) \cap L(i)|}{|L(i)|}$ across all articles.
- **Strict Singleton & Noise Handling**: Outlier articles (cluster label `-1` or ground-truth `None`) are treated as unique singleton sets ($|C(i)| = 1, |L(i)| = 1$), preventing unclustered noise items from falsely matching each other.
- **Adjusted Rand Index (ARI)**: Corrects standard Rand Index for chance agreement ($[-1.0, 1.0]$).
- **Normalized Mutual Information (NMI)**: Information-theoretic mutual information normalized by cluster entropy ($[0.0, 1.0]$).

---

## 14. Current Limitations & Future Scope

1. **Monolingual Focus**: The standard model (`all-MiniLM-L6-v2`) operates on English text. Future releases will support multilingual embeddings (`paraphrase-multilingual-MiniLM-L12-v2`) for cross-lingual news tracking.
2. **Scalability Beyond 50,000 Articles**: Pairwise all-pairs similarity is $O(N^2)$. For enterprise scale, Hierarchical Navigable Small World (HNSW) vector indexing or FAISS will be introduced for candidate retrieval before hybrid scoring.
3. **Live API Free-Tier Quotas**: Free NewsAPI accounts enforce daily request limits. The system provides open RSS 2.0 / Atom feed polling to ensure unrestricted live ingestion without external API subscriptions.

---

## 15. User Interface & Dashboard Overview

The React 19 frontend provides 8 dedicated views:
1. **Overview Page**: System-wide statistics (article counts, active events, noise count), category breakdown pie charts, and recent activity.
2. **News Explorer**: Filterable table of all ingested articles with live search, publisher filters, date selectors, and entity badges.
3. **Event Explorer**: Grid view of discovered event clusters, showing lead headlines, member counts, time spans, and re-clustering parameter controls.
4. **Event Detail Page**: Chronological vertical timeline showing article development over time, similarity scores, and medoid headline.
5. **Live Ingestion Monitor**: Real-time RSS and NewsAPI feed poller with status indicators and historical ingestion job logs.
6. **Research Lab**: Interactive parameter tuning workbench with sliders for $\alpha, \beta, \gamma$, and $\theta_{\text{sim}}$, displaying instant re-clustering results.
7. **Evaluation Benchmark**: Visual ablation comparison charts (B-cubed F1, Precision, Recall, ARI, NMI) comparing the 4 model variants.
8. **Dataset Management**: Drag-and-drop CSV/JSON dataset importer with pre-validation schema checking and import history.

---

## 16. Author and Project Information

- **Project**: News Event Detection and Tracking System — Time-Aware Semantic News Intelligence
- **Repository**: [https://github.com/yogitasharma3372-ui/News-Event-Detection-System](https://github.com/yogitasharma3372-ui/News-Event-Detection-System)
- **License**: MIT Open Source License
- **Target OS**: Windows 10/11 (fully compatible with macOS and Linux)
