import React, { useEffect, useState } from 'react';
import {
  FlaskConical,
  Play,
  Download,
  CheckCircle2,
  AlertCircle,
  HelpCircle,
  Sliders,
  Layers,
  Clock,
  Sparkles
} from 'lucide-react';
import { api } from '../api/client';
import { Experiment } from '../types';

export const ResearchLabPage: React.FC = () => {
  const [experiments, setExperiments] = useState<Experiment[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Form
  const [expName, setExpName] = useState('');
  const [algorithm, setAlgorithm] = useState<'tfidf' | 'semantic' | 'hybrid'>('hybrid');
  const [alpha, setAlpha] = useState(0.55);
  const [beta, setBeta] = useState(0.25);
  const [gamma, setGamma] = useState(0.20);
  const [similarityThreshold, setSimilarityThreshold] = useState(0.60);
  const [decayHours, setDecayHours] = useState(72.0);
  const [embeddingModel, setEmbeddingModel] = useState('sentence-transformers/all-MiniLM-L6-v2');

  const [isRunning, setIsRunning] = useState(false);
  const [selectedExp, setSelectedExp] = useState<Experiment | null>(null);

  const fetchExperiments = async () => {
    setIsLoading(true);
    try {
      const data = await api.getExperiments();
      setExperiments(data);
      if (data.length > 0 && !selectedExp) {
        setSelectedExp(data[0]);
      }
    } catch (err) {
      console.error('Failed to load experiments:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchExperiments();
  }, []);

  const handleRunExperiment = async (e: React.FormEvent) => {
    e.preventDefault();
    const name = expName.trim() || `${algorithm.toUpperCase()} Research Run #${experiments.length + 1}`;
    setIsRunning(true);
    try {
      const newExp = await api.runExperiment({
        name,
        algorithm,
        alpha_semantic: algorithm === 'hybrid' ? alpha : algorithm === 'semantic' ? 1.0 : 0.0,
        beta_temporal: algorithm === 'hybrid' ? beta : 0.0,
        gamma_entity: algorithm === 'hybrid' ? gamma : 0.0,
        similarity_threshold: similarityThreshold,
        temporal_decay_hours: decayHours,
        embedding_model: embeddingModel
      });
      setExpName('');
      await fetchExperiments();
      setSelectedExp(newExp);
    } catch (err: any) {
      alert(`Experiment run error: ${err.message}`);
    } finally {
      setIsRunning(false);
    }
  };

  const handleDownloadJSON = (exp: Experiment) => {
    const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(exp, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute('href', dataStr);
    downloadAnchor.setAttribute('download', `${exp.id}_results.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  const weightsSum = alpha + beta + gamma;
  const isWeightsValid = Math.abs(weightsSum - 1.0) < 0.005;

  return (
    <div className="space-y-6">
      {/* Experiment Configurator Card */}
      <div className="bg-[#0f172a] border border-slate-800 rounded-xl p-6 space-y-5">
        <div>
          <h3 className="text-base font-semibold text-slate-100 flex items-center gap-2">
            <FlaskConical className="w-5 h-5 text-blue-400" />
            <span>Research Experiment Runner</span>
          </h3>
          <p className="text-xs text-slate-400">
            Compare TF-IDF, Semantic Dense Embeddings, and the Proposed Hybrid Model on ground-truth benchmark articles.
          </p>
        </div>

        <form onSubmit={handleRunExperiment} className="space-y-4 text-xs">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-slate-300 font-medium mb-1">Experiment Name</label>
              <input
                type="text"
                value={expName}
                onChange={(e) => setExpName(e.target.value)}
                placeholder="e.g. Hybrid α=0.55 β=0.25 γ=0.20 Benchmark Run"
                className="w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded-lg text-slate-100 placeholder-slate-600 focus:outline-none focus:border-blue-500"
              />
            </div>

            <div>
              <label className="block text-slate-300 font-medium mb-1">Methodology Pipeline</label>
              <select
                value={algorithm}
                onChange={(e) => setAlgorithm(e.target.value as any)}
                className="w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded-lg text-slate-200 focus:outline-none focus:border-blue-500 font-medium"
              >
                <option value="hybrid">Experiment 3: Proposed Hybrid (Semantic + Time + NER)</option>
                <option value="semantic">Experiment 2: Semantic Dense Embedding Baseline</option>
                <option value="tfidf">Experiment 1: TF-IDF Cosine Similarity Baseline</option>
              </select>
            </div>
          </div>

          {/* Hybrid Weights if Hybrid Pipeline Selected */}
          {algorithm === 'hybrid' && (
            <div className="p-4 bg-slate-900/80 border border-slate-800 rounded-xl space-y-3">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-slate-200">
                  Hybrid Component Weights (α + β + γ = 1.0)
                </span>
                <span className={`text-[11px] font-mono px-2 py-0.5 rounded border ${
                  isWeightsValid
                    ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400'
                    : 'bg-red-500/10 border-red-500/20 text-red-400'
                }`}>
                  Sum: {weightsSum.toFixed(2)} {isWeightsValid ? '(Valid)' : '(Must equal 1.0)'}
                </span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
                <div>
                  <div className="flex justify-between text-slate-400 mb-1">
                    <span>Semantic (α)</span>
                    <span className="font-mono text-blue-400 font-bold">{alpha.toFixed(2)}</span>
                  </div>
                  <input
                    type="range"
                    min="0.0"
                    max="1.0"
                    step="0.05"
                    value={alpha}
                    onChange={(e) => setAlpha(parseFloat(e.target.value))}
                    className="w-full accent-blue-500"
                  />
                </div>

                <div>
                  <div className="flex justify-between text-slate-400 mb-1">
                    <span>Temporal Decay (β)</span>
                    <span className="font-mono text-emerald-400 font-bold">{beta.toFixed(2)}</span>
                  </div>
                  <input
                    type="range"
                    min="0.0"
                    max="1.0"
                    step="0.05"
                    value={beta}
                    onChange={(e) => setBeta(parseFloat(e.target.value))}
                    className="w-full accent-emerald-500"
                  />
                </div>

                <div>
                  <div className="flex justify-between text-slate-400 mb-1">
                    <span>Entity Overlap (γ)</span>
                    <span className="font-mono text-amber-400 font-bold">{gamma.toFixed(2)}</span>
                  </div>
                  <input
                    type="range"
                    min="0.0"
                    max="1.0"
                    step="0.05"
                    value={gamma}
                    onChange={(e) => setGamma(parseFloat(e.target.value))}
                    className="w-full accent-amber-500"
                  />
                </div>
              </div>
            </div>
          )}

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="flex justify-between text-slate-300 font-medium mb-1">
                <span>Clustering Similarity Threshold</span>
                <span className="font-mono text-slate-200">{similarityThreshold.toFixed(2)}</span>
              </label>
              <input
                type="range"
                min="0.30"
                max="0.90"
                step="0.02"
                value={similarityThreshold}
                onChange={(e) => setSimilarityThreshold(parseFloat(e.target.value))}
                className="w-full accent-slate-400"
              />
            </div>

            <div>
              <label className="flex justify-between text-slate-300 font-medium mb-1">
                <span>Temporal Half-Decay Window (hours)</span>
                <span className="font-mono text-slate-200">{decayHours} hours</span>
              </label>
              <input
                type="range"
                min="12"
                max="168"
                step="12"
                value={decayHours}
                onChange={(e) => setDecayHours(parseFloat(e.target.value))}
                className="w-full accent-slate-400"
              />
            </div>
          </div>

          <div className="flex justify-end pt-2">
            <button
              type="submit"
              disabled={isRunning || (algorithm === 'hybrid' && !isWeightsValid)}
              className="flex items-center space-x-2 px-6 py-2.5 bg-blue-600 hover:bg-blue-500 text-white font-semibold rounded-lg shadow-sm transition disabled:opacity-50 cursor-pointer"
            >
              <Play className="w-4 h-4" />
              <span>{isRunning ? 'Evaluating Model...' : 'Execute Research Pipeline'}</span>
            </button>
          </div>
        </form>
      </div>

      {/* Selected Experiment Inspector & Result Details */}
      {selectedExp && selectedExp.metrics && (
        <div className="bg-[#0f172a] border border-slate-800 rounded-xl p-6 space-y-4">
          <div className="flex items-center justify-between flex-wrap gap-2">
            <div>
              <span className="text-xs font-mono text-blue-400 uppercase font-semibold">
                {selectedExp.algorithm} Run
              </span>
              <h3 className="text-lg font-bold text-slate-100">{selectedExp.name}</h3>
              <p className="text-xs text-slate-400">
                Evaluated on {selectedExp.evaluated_articles_count} benchmark articles across {selectedExp.reference_clusters_count} ground-truth reference clusters.
              </p>
            </div>
            <button
              onClick={() => handleDownloadJSON(selectedExp)}
              className="flex items-center space-x-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium rounded-lg border border-slate-700 transition cursor-pointer"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Export Result JSON</span>
            </button>
          </div>

          {/* Research Metric Tiles */}
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 pt-2 text-center">
            <div className="p-3 bg-slate-900 rounded-lg border border-slate-800 space-y-1">
              <span className="text-[10px] text-slate-500 uppercase tracking-wider block font-semibold">B-cubed F1</span>
              <span className="text-xl font-bold text-emerald-400 font-mono">
                {(selectedExp.metrics.bcubed_f1 * 100).toFixed(1)}%
              </span>
            </div>
            <div className="p-3 bg-slate-900 rounded-lg border border-slate-800 space-y-1">
              <span className="text-[10px] text-slate-500 uppercase tracking-wider block font-semibold">B-cubed Precision</span>
              <span className="text-xl font-bold text-blue-400 font-mono">
                {(selectedExp.metrics.bcubed_precision * 100).toFixed(1)}%
              </span>
            </div>
            <div className="p-3 bg-slate-900 rounded-lg border border-slate-800 space-y-1">
              <span className="text-[10px] text-slate-500 uppercase tracking-wider block font-semibold">B-cubed Recall</span>
              <span className="text-xl font-bold text-blue-400 font-mono">
                {(selectedExp.metrics.bcubed_recall * 100).toFixed(1)}%
              </span>
            </div>
            <div className="p-3 bg-slate-900 rounded-lg border border-slate-800 space-y-1">
              <span className="text-[10px] text-slate-500 uppercase tracking-wider block font-semibold">Adjusted Rand (ARI)</span>
              <span className="text-xl font-bold text-amber-400 font-mono">
                {selectedExp.metrics.adjusted_rand_index.toFixed(3)}
              </span>
            </div>
            <div className="p-3 bg-slate-900 rounded-lg border border-slate-800 space-y-1">
              <span className="text-[10px] text-slate-500 uppercase tracking-wider block font-semibold">Norm. Mutual Info</span>
              <span className="text-xl font-bold text-purple-400 font-mono">
                {selectedExp.metrics.normalized_mutual_info.toFixed(3)}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Experiment Runs Table */}
      <div className="bg-[#0f172a] border border-slate-800 rounded-xl p-5 space-y-4">
        <h3 className="text-sm font-semibold text-slate-100">Historical Experiment Executions</h3>
        {experiments.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-900/60 text-slate-500 border-b border-slate-800 uppercase tracking-wider text-[10px]">
                <tr>
                  <th className="py-2.5 px-3">Run Name</th>
                  <th className="py-2.5 px-3">Method</th>
                  <th className="py-2.5 px-3">Status</th>
                  <th className="py-2.5 px-3 text-right">B-cubed F1</th>
                  <th className="py-2.5 px-3 text-right">ARI</th>
                  <th className="py-2.5 px-3 text-right">NMI</th>
                  <th className="py-2.5 px-3 text-right">Runtime</th>
                  <th className="py-2.5 px-3 text-center">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                {experiments.map((exp) => (
                  <tr
                    key={exp.id}
                    onClick={() => setSelectedExp(exp)}
                    className={`hover:bg-slate-800/40 transition cursor-pointer ${
                      selectedExp?.id === exp.id ? 'bg-blue-600/10' : ''
                    }`}
                  >
                    <td className="py-3 px-3 font-sans font-medium text-slate-200">{exp.name}</td>
                    <td className="py-3 px-3 uppercase text-slate-400">{exp.algorithm}</td>
                    <td className="py-3 px-3 font-sans">
                      <span className={`px-2 py-0.5 rounded text-[11px] font-medium border ${
                        exp.status === 'completed'
                          ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400'
                          : 'bg-red-500/10 border-red-500/20 text-red-400'
                      }`}>
                        {exp.status}
                      </span>
                    </td>
                    <td className="py-3 px-3 text-right font-bold text-emerald-400">
                      {exp.metrics?.bcubed_f1 ? `${(exp.metrics.bcubed_f1 * 100).toFixed(1)}%` : '—'}
                    </td>
                    <td className="py-3 px-3 text-right text-amber-400">
                      {exp.metrics?.adjusted_rand_index ? exp.metrics.adjusted_rand_index.toFixed(3) : '—'}
                    </td>
                    <td className="py-3 px-3 text-right text-purple-400">
                      {exp.metrics?.normalized_mutual_info ? exp.metrics.normalized_mutual_info.toFixed(3) : '—'}
                    </td>
                    <td className="py-3 px-3 text-right text-slate-400">
                      {exp.runtime_seconds ? `${exp.runtime_seconds.toFixed(2)}s` : '—'}
                    </td>
                    <td className="py-3 px-3 text-center font-sans">
                      <button
                        onClick={(e) => { e.stopPropagation(); handleDownloadJSON(exp); }}
                        className="text-xs text-blue-400 hover:text-blue-300 font-medium"
                      >
                        JSON
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="py-10 text-center text-xs text-slate-500">
            No experiments run yet. Configure parameters above and click "Execute Research Pipeline".
          </div>
        )}
      </div>
    </div>
  );
};
