export interface Article {
  id: string;
  external_id?: string | null;
  headline: string;
  body: string;
  source_name: string;
  source_url?: string | null;
  published_at: string;
  ingested_at: string;
  language: string;
  content_hash: string;
  assigned_event_id?: string | null;
  ground_truth_event_id?: string | null;
  category?: string | null;
  entities_json?: string | null;
  processing_status: string;
  processing_error?: string | null;
  created_at: string;
  updated_at: string;
}

export interface ArticleListResponse {
  items: Article[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface Event {
  id: string;
  title: string;
  description?: string | null;
  first_observed_at: string;
  last_observed_at: string;
  category: string;
  status: string;
  article_count: number;
  average_confidence: number;
  model_version: string;
  assignment_method: string;
  key_entities_json?: string | null;
  created_at: string;
  updated_at: string;
}

export interface EventDetail extends Event {
  articles: Article[];
}

export interface TimelineItem {
  article_id: string;
  headline: string;
  source_name: string;
  source_url?: string | null;
  published_at: string;
  summary_excerpt: string;
  combined_score: number;
  is_first_observed: boolean;
}

export interface SystemMetadata {
  total_articles: number;
  assigned_articles: number;
  unassigned_articles: number;
  total_events: number;
  total_sources: number;
  sources: string[];
  total_experiments: number;
  latest_ingestion_timestamp?: string | null;
  event_categories_distribution: Record<string, number>;
  default_model: string;
  hybrid_weights: {
    alpha_semantic: number;
    beta_temporal: number;
    gamma_entity: number;
  };
}

export interface EvaluationMetrics {
  bcubed_precision: number;
  bcubed_recall: number;
  bcubed_f1: number;
  adjusted_rand_index: number;
  normalized_mutual_info: number;
  pairwise_precision?: number | null;
  pairwise_recall?: number | null;
  pairwise_f1?: number | null;
  evaluated_articles_count: number;
  reference_clusters_count: number;
  detected_clusters_count: number;
  runtime_seconds: number;
}

export interface Experiment {
  id: string;
  name: string;
  dataset_name: string;
  algorithm: string;
  parameters: Record<string, any>;
  metrics?: EvaluationMetrics | null;
  status: string;
  runtime_seconds?: number | null;
  evaluated_articles_count: number;
  reference_clusters_count: number;
  detected_clusters_count: number;
  error_message?: string | null;
  start_time: string;
  end_time?: string | null;
}

export interface IngestionJob {
  id: string;
  provider: string;
  query?: string | null;
  status: string;
  articles_fetched: number;
  articles_inserted: number;
  duplicates_skipped: number;
  failures: number;
  error_summary?: string | null;
  start_time: string;
  end_time?: string | null;
}

export interface SystemSettings {
  default_embedding_model: string;
  alpha_semantic: number;
  beta_temporal: number;
  gamma_entity: number;
  similarity_threshold: number;
  temporal_decay_hours: number;
  has_newsapi_key: boolean;
}
