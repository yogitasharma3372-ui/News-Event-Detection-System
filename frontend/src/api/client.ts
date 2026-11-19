import {
  Article,
  ArticleListResponse,
  Event,
  EventDetail,
  TimelineItem,
  SystemMetadata,
  Experiment,
  IngestionJob,
  SystemSettings
} from '../types';

const BASE_URL = '/api';

async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${BASE_URL}${endpoint}`;
  const response = await fetch(url, options);
  
  if (!response.ok) {
    let errorMsg = `HTTP Error ${response.status}: ${response.statusText}`;
    try {
      const errorData = await response.json();
      if (errorData.detail) {
        errorMsg = typeof errorData.detail === 'string' ? errorData.detail : JSON.stringify(errorData.detail);
      }
    } catch {
      // ignore
    }
    throw new Error(errorMsg);
  }
  return response.json();
}

export const api = {
  // Metadata & Health
  getMetadata: () => request<SystemMetadata>('/metadata'),
  getSources: () => request<{ sources: { name: string; article_count: number }[] }>('/sources'),

  // Articles
  getArticles: (params: Record<string, any> = {}) => {
    const q = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== '') {
        q.append(k, String(v));
      }
    });
    return request<ArticleListResponse>(`/articles?${q.toString()}`);
  },
  getArticle: (id: string) => request<Article>(`/articles/${id}`),
  importFixture: () => request<{ status: string; inserted: number; skipped_duplicates: number }>('/articles/import-fixture', {
    method: 'POST'
  }),
  validateUpload: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return request<any>('/articles/validate-upload', {
      method: 'POST',
      body: formData
    });
  },
  importFile: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return request<any>('/articles/import', {
      method: 'POST',
      body: formData
    });
  },

  // Events
  getEvents: (params: Record<string, any> = {}) => {
    const q = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== '') {
        q.append(k, String(v));
      }
    });
    return request<{ items: Event[]; total: number; page: number; pages: number }>(`/events?${q.toString()}`);
  },
  getEvent: (id: string) => request<EventDetail>(`/events/${id}`),
  getEventTimeline: (id: string) => request<TimelineItem[]>(`/events/${id}/timeline`),
  detectEvents: (params: {
    alpha?: number;
    beta?: number;
    gamma?: number;
    similarity_threshold?: number;
    decay_hours?: number;
  }) => {
    const q = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined) q.append(k, String(v));
    });
    return request<any>(`/events/detect?${q.toString()}`, {
      method: 'POST'
    });
  },
  reviewAssignment: (data: {
    article_id: string;
    target_event_id?: string | null;
    create_new_event?: boolean;
    new_event_title?: string;
    notes?: string;
  }) => request<any>('/events/assignments/review', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  }),

  // Experiments & Evaluation
  getExperiments: () => request<Experiment[]>('/experiments'),
  runExperiment: (data: {
    name: string;
    dataset_name?: string;
    algorithm: string;
    alpha_semantic?: number;
    beta_temporal?: number;
    gamma_entity?: number;
    similarity_threshold?: number;
    temporal_decay_hours?: number;
    embedding_model?: string;
  }) => request<Experiment>('/experiments', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  }),
  runAblation: (threshold = 0.60, decay = 72.0) => request<{ ablation_results: any[] }>(
    `/evaluation/ablation?similarity_threshold=${threshold}&decay_hours=${decay}`,
    { method: 'POST' }
  ),

  // Ingestion
  getIngestionJobs: () => request<IngestionJob[]>('/ingestion/jobs'),
  triggerIngestion: (data: {
    provider: string;
    query?: string;
    feed_url?: string;
    max_articles?: number;
  }) => request<IngestionJob>('/ingestion/jobs', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  }),

  // Settings
  getSettings: () => request<{ settings: SystemSettings; weights_valid: boolean; description: string }>('/settings'),
  updateSettings: (data: Partial<SystemSettings>) => request<any>('/settings', {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  })
};
