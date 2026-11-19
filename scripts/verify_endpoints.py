import sys
import os
sys.path.insert(0, os.path.abspath("."))

import json
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

# 1. Health
r_health = client.get('/api/health')
print('=== /api/health ===')
print('Status:', r_health.status_code, r_health.json())

# 2. Articles
r_articles = client.get('/api/articles?page=1&page_size=3')
print('\n=== /api/articles ===')
print('Status:', r_articles.status_code, 'Total:', r_articles.json().get('total'))

# 3. Events
r_events = client.get('/api/events?page=1&page_size=2')
print('\n=== /api/events ===')
print('Status:', r_events.status_code, 'Total:', r_events.json().get('total'))

# 4. Evaluation / Ablation
r_eval = client.post('/api/evaluation/ablation?similarity_threshold=0.60&decay_hours=72.0')
print('\n=== /api/evaluation/ablation ===')
print('Status:', r_eval.status_code)
for res in r_eval.json().get('ablation_results', []):
    m = res['metrics']
    print(f"  {res['configuration_name']}: B-cubed F1={m['bcubed_f1']*100:.1f}%, ARI={m['adjusted_rand_index']:.3f}, NMI={m['normalized_mutual_info']:.3f}")
