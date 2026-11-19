import React, { useEffect, useState } from 'react';
import { Settings, Save, CheckCircle2, AlertTriangle, Key, Layers, Sliders } from 'lucide-react';
import { api } from '../api/client';
import { SystemSettings } from '../types';

export const SettingsPage: React.FC = () => {
  const [settingsData, setSettingsData] = useState<SystemSettings>({
    default_embedding_model: 'sentence-transformers/all-MiniLM-L6-v2',
    alpha_semantic: 0.55,
    beta_temporal: 0.25,
    gamma_entity: 0.20,
    similarity_threshold: 0.60,
    temporal_decay_hours: 72.0,
    has_newsapi_key: false
  });

  const [newsApiKey, setNewsApiKey] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    const fetchSettings = async () => {
      setIsLoading(true);
      try {
        const res = await api.getSettings();
        setSettingsData(res.settings);
      } catch (err) {
        console.error('Failed to load settings:', err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchSettings();
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    setSaveSuccess(false);
    setErrorMessage(null);

    const sum = settingsData.alpha_semantic + settingsData.beta_temporal + settingsData.gamma_entity;
    if (Math.abs(sum - 1.0) > 0.005) {
      setErrorMessage(`Weights must sum to 1.0 (current sum: ${sum.toFixed(3)}).`);
      setIsSaving(false);
      return;
    }

    try {
      await api.updateSettings({
        ...settingsData,
        newsapi_key: newsApiKey.trim() || undefined
      } as any);
      setSaveSuccess(true);
      setNewsApiKey('');
      const updated = await api.getSettings();
      setSettingsData(updated.settings);
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to update settings.');
    } finally {
      setIsSaving(false);
    }
  };

  const weightsSum = settingsData.alpha_semantic + settingsData.beta_temporal + settingsData.gamma_entity;
  const isWeightsValid = Math.abs(weightsSum - 1.0) < 0.005;

  return (
    <div className="space-y-6 max-w-4xl">
      <div className="bg-[#0f172a] border border-slate-800 rounded-xl p-6 space-y-5">
        <div>
          <h3 className="text-base font-semibold text-slate-100 flex items-center gap-2">
            <Settings className="w-5 h-5 text-blue-400" />
            <span>System & Model Configuration</span>
          </h3>
          <p className="text-xs text-slate-400">
            Configure default neural embedding models, clustering distance thresholds, and hybrid similarity weights.
          </p>
        </div>

        {saveSuccess && (
          <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-lg text-xs text-emerald-400 flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 shrink-0" />
            <span>Settings saved successfully and updated in persistent database!</span>
          </div>
        )}

        {errorMessage && (
          <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-xs text-red-400 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 shrink-0" />
            <span>{errorMessage}</span>
          </div>
        )}

        <form onSubmit={handleSave} className="space-y-6 text-xs">
          {/* Section 1: Embedding Model */}
          <div className="space-y-3">
            <h4 className="text-xs font-semibold text-slate-200 uppercase tracking-wider flex items-center gap-1.5">
              <Layers className="w-4 h-4 text-blue-400" />
              <span>Semantic Embedding Architecture</span>
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-slate-400 mb-1">Sentence Transformer Model Identifier</label>
                <input
                  type="text"
                  value={settingsData.default_embedding_model}
                  onChange={(e) => setSettingsData({ ...settingsData, default_embedding_model: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded-lg text-slate-100 font-mono text-xs focus:outline-none focus:border-blue-500"
                />
                <p className="text-[11px] text-slate-500 mt-1">
                  Default: sentence-transformers/all-MiniLM-L6-v2 (384-dimensional normalized embeddings)
                </p>
              </div>

              <div>
                <label className="block text-slate-400 mb-1">Default Similarity Threshold</label>
                <input
                  type="number"
                  step="0.01"
                  min="0.30"
                  max="0.95"
                  value={settingsData.similarity_threshold}
                  onChange={(e) => setSettingsData({ ...settingsData, similarity_threshold: parseFloat(e.target.value) || 0.60 })}
                  className="w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded-lg text-slate-100 text-xs focus:outline-none focus:border-blue-500"
                />
                <p className="text-[11px] text-slate-500 mt-1">
                  Minimum combined score required to merge two articles into the same event
                </p>
              </div>
            </div>
          </div>

          {/* Section 2: Hybrid Weights */}
          <div className="space-y-3 pt-3 border-t border-slate-800">
            <div className="flex items-center justify-between">
              <h4 className="text-xs font-semibold text-slate-200 uppercase tracking-wider flex items-center gap-1.5">
                <Sliders className="w-4 h-4 text-emerald-400" />
                <span>Default Hybrid Component Weights</span>
              </h4>
              <span className={`text-[11px] font-mono px-2 py-0.5 rounded border ${
                isWeightsValid
                  ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400'
                  : 'bg-red-500/10 border-red-500/20 text-red-400'
              }`}>
                Sum: {weightsSum.toFixed(2)} (Must equal 1.0)
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div>
                <label className="flex justify-between text-slate-400 mb-1">
                  <span>Semantic Weight (α)</span>
                  <span className="font-mono text-blue-400 font-bold">{settingsData.alpha_semantic.toFixed(2)}</span>
                </label>
                <input
                  type="range"
                  min="0.0"
                  max="1.0"
                  step="0.05"
                  value={settingsData.alpha_semantic}
                  onChange={(e) => setSettingsData({ ...settingsData, alpha_semantic: parseFloat(e.target.value) })}
                  className="w-full accent-blue-500"
                />
              </div>

              <div>
                <label className="flex justify-between text-slate-400 mb-1">
                  <span>Temporal Decay (β)</span>
                  <span className="font-mono text-emerald-400 font-bold">{settingsData.beta_temporal.toFixed(2)}</span>
                </label>
                <input
                  type="range"
                  min="0.0"
                  max="1.0"
                  step="0.05"
                  value={settingsData.beta_temporal}
                  onChange={(e) => setSettingsData({ ...settingsData, beta_temporal: parseFloat(e.target.value) })}
                  className="w-full accent-emerald-500"
                />
              </div>

              <div>
                <label className="flex justify-between text-slate-400 mb-1">
                  <span>Entity Overlap (γ)</span>
                  <span className="font-mono text-amber-400 font-bold">{settingsData.gamma_entity.toFixed(2)}</span>
                </label>
                <input
                  type="range"
                  min="0.0"
                  max="1.0"
                  step="0.05"
                  value={settingsData.gamma_entity}
                  onChange={(e) => setSettingsData({ ...settingsData, gamma_entity: parseFloat(e.target.value) })}
                  className="w-full accent-amber-500"
                />
              </div>
            </div>

            <div className="pt-2">
              <label className="block text-slate-400 mb-1">Temporal Half-Decay Window (τ in hours)</label>
              <input
                type="number"
                min="6"
                max="360"
                step="6"
                value={settingsData.temporal_decay_hours}
                onChange={(e) => setSettingsData({ ...settingsData, temporal_decay_hours: parseFloat(e.target.value) || 72.0 })}
                className="w-full sm:w-1/2 px-3 py-2 bg-slate-900 border border-slate-800 rounded-lg text-slate-100 text-xs focus:outline-none focus:border-blue-500"
              />
              <p className="text-[11px] text-slate-500 mt-1">
                Exponential formula: S_temporal = exp(-Δt / τ). Articles separated by τ hours receive a decay score of 1/e ≈ 0.368.
              </p>
            </div>
          </div>

          {/* Section 3: Live API Secret Key */}
          <div className="space-y-3 pt-3 border-t border-slate-800">
            <h4 className="text-xs font-semibold text-slate-200 uppercase tracking-wider flex items-center gap-1.5">
              <Key className="w-4 h-4 text-purple-400" />
              <span>Live NewsAPI Credentials (Optional)</span>
            </h4>
            <div>
              <label className="block text-slate-400 mb-1">
                NewsAPI Secret Key {settingsData.has_newsapi_key && <span className="text-emerald-400 font-normal">(Configured)</span>}
              </label>
              <input
                type="password"
                value={newsApiKey}
                onChange={(e) => setNewsApiKey(e.target.value)}
                placeholder={settingsData.has_newsapi_key ? '••••••••••••••••••••••••' : 'Enter NewsAPI key...'}
                className="w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded-lg text-slate-100 font-mono text-xs focus:outline-none focus:border-blue-500"
              />
              <p className="text-[11px] text-slate-500 mt-1">
                Stored securely on backend. Never committed to version control or transmitted to frontend.
              </p>
            </div>
          </div>

          <div className="flex justify-end pt-4 border-t border-slate-800">
            <button
              type="submit"
              disabled={isSaving || !isWeightsValid}
              className="flex items-center space-x-2 px-6 py-2.5 bg-blue-600 hover:bg-blue-500 text-white font-semibold rounded-lg shadow-sm transition disabled:opacity-50 cursor-pointer"
            >
              <Save className="w-4 h-4" />
              <span>{isSaving ? 'Saving Changes...' : 'Save Configuration'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
