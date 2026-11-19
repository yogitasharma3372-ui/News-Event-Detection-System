import React, { useEffect, useState } from 'react';
import {
  BarChart3,
  Play,
  Download,
  CheckCircle2,
  HelpCircle,
  TrendingUp,
  Layers,
  Clock,
  Sparkles
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid
} from 'recharts';
import { api } from '../api/client';

export const EvaluationPage: React.FC = () => {
  const [ablationResults, setAblationResults] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [similarityThreshold, setSimilarityThreshold] = useState(0.60);
  const [decayHours, setDecayHours] = useState(72.0);

  const runAblationStudy = async () => {
    setIsLoading(true);
    try {
      const res = await api.runAblation(similarityThreshold, decayHours);
      setAblationResults(res.ablation_results);
    } catch (err: any) {
      alert(`Ablation run error: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    runAblationStudy();
  }, []);

  // Format comparative chart data
  const chartData = ablationResults.map((item) => ({
    name: item.configuration_name,
    'B-cubed F1 (%)': Number((item.metrics.bcubed_f1 * 100).toFixed(1)),
    'ARI': Number(item.metrics.adjusted_rand_index.toFixed(3)),
    'NMI': Number(item.metrics.normalized_mutual_info.toFixed(3)),
    'Runtime (s)': Number(item.runtime_seconds.toFixed(2))
  }));

  return (
    <div className="space-y-6">
      {/* Top Explanation & Control Banner */}
      <div className="bg-[#0f172a] border border-slate-800 rounded-xl p-6 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h3 className="text-base font-semibold text-slate-100 flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-blue-400" />
              <span>Ablation Benchmark & Comparative Evaluation</span>
            </h3>
            <p className="text-xs text-slate-400 max-w-2xl mt-1">
              Investigates the core research question: <em>Does combining semantic similarity with temporal decay and entity overlap improve news event clustering compared to baselines?</em>
            </p>
          </div>

          <button
            onClick={runAblationStudy}
            disabled={isLoading}
            className="flex items-center space-x-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold rounded-lg shadow-sm transition disabled:opacity-50 shrink-0 cursor-pointer"
          >
            <Play className="w-3.5 h-3.5" />
            <span>{isLoading ? 'Running Ablations...' : 'Re-Run Ablation Benchmark'}</span>
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2 border-t border-slate-800/80 text-xs">
          <div>
            <label className="flex justify-between text-slate-300 mb-1">
              <span>Similarity Threshold (Cluster Merge Distance)</span>
              <span className="font-mono text-slate-200">{similarityThreshold.toFixed(2)}</span>
            </label>
            <input
              type="range"
              min="0.30"
              max="0.85"
              step="0.05"
              value={similarityThreshold}
              onChange={(e) => setSimilarityThreshold(parseFloat(e.target.value))}
              className="w-full accent-slate-400"
            />
          </div>

          <div>
            <label className="flex justify-between text-slate-300 mb-1">
              <span>Temporal Half-Decay Window</span>
              <span className="font-mono text-slate-200">{decayHours}h</span>
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
      </div>

      {/* Comparative Visual Bar Chart */}
      <div className="bg-[#0f172a] border border-slate-800 rounded-xl p-5 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-semibold text-slate-100">B-cubed F1 and Clustering Metrics Comparison</h3>
            <p className="text-xs text-slate-500">Evaluated simultaneously on identical benchmark articles</p>
          </div>
          <span className="text-xs text-slate-400 font-mono">
            {ablationResults[0]?.metrics?.evaluated_articles_count || 14} articles evaluated
          </span>
        </div>

        {chartData.length > 0 ? (
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 10, right: 20, left: 0, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="name" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} domain={[0, 100]} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                />
                <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
                <Bar dataKey="B-cubed F1 (%)" fill="#10b981" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <div className="h-72 flex items-center justify-center text-xs text-slate-500">
            {isLoading ? 'Computing ablation runs...' : 'No benchmark data available.'}
          </div>
        )}
      </div>

      {/* Detailed Ablation Comparison Table */}
      <div className="bg-[#0f172a] border border-slate-800 rounded-xl p-5 space-y-4">
        <h3 className="text-sm font-semibold text-slate-100">Quantitative Results Table</h3>
        
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-900/60 text-slate-500 border-b border-slate-800 uppercase tracking-wider text-[10px]">
              <tr>
                <th className="py-2.5 px-3">Model Variant</th>
                <th className="py-2.5 px-3">Weights (α, β, γ)</th>
                <th className="py-2.5 px-3 text-right">B-cubed F1</th>
                <th className="py-2.5 px-3 text-right">Precision</th>
                <th className="py-2.5 px-3 text-right">Recall</th>
                <th className="py-2.5 px-3 text-right">Adj. Rand (ARI)</th>
                <th className="py-2.5 px-3 text-right">Norm. MI (NMI)</th>
                <th className="py-2.5 px-3 text-right">Runtime</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {ablationResults.map((item, idx) => (
                <tr key={idx} className="hover:bg-slate-800/30 transition">
                  <td className="py-3 px-3 font-sans font-semibold text-slate-200">
                    {item.configuration_name}
                    <span className="block text-[11px] font-normal text-slate-500">{item.description}</span>
                  </td>
                  <td className="py-3 px-3 text-slate-400">
                    ({item.parameters.alpha.toFixed(2)}, {item.parameters.beta.toFixed(2)}, {item.parameters.gamma.toFixed(2)})
                  </td>
                  <td className="py-3 px-3 text-right font-bold text-emerald-400 text-sm">
                    {(item.metrics.bcubed_f1 * 100).toFixed(1)}%
                  </td>
                  <td className="py-3 px-3 text-right text-blue-400">
                    {(item.metrics.bcubed_precision * 100).toFixed(1)}%
                  </td>
                  <td className="py-3 px-3 text-right text-blue-400">
                    {(item.metrics.bcubed_recall * 100).toFixed(1)}%
                  </td>
                  <td className="py-3 px-3 text-right text-amber-400">
                    {item.metrics.adjusted_rand_index.toFixed(3)}
                  </td>
                  <td className="py-3 px-3 text-right text-purple-400">
                    {item.metrics.normalized_mutual_info.toFixed(3)}
                  </td>
                  <td className="py-3 px-3 text-right text-slate-400">
                    {item.runtime_seconds.toFixed(2)}s
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Methodology Documentation Note */}
      <div className="bg-[#0f172a] border border-slate-800 rounded-xl p-5 space-y-2 text-xs text-slate-400 leading-relaxed">
        <h4 className="font-semibold text-slate-200 flex items-center gap-1.5">
          <HelpCircle className="w-4 h-4 text-blue-400" />
          <span>Evaluation Protocol & Ground Truth Standards</span>
        </h4>
        <p>
          Evaluation is computed using strict B-cubed item-level precision and recall. Unlike simple cluster purity metrics, B-cubed penalizes both incorrect cluster mergers (which drops precision) and excessive cluster splitting (which drops recall).
        </p>
        <p>
          Articles with no reference cluster label are treated as distinct singletons, ensuring noise stories are never erroneously rewarded for matching other noise stories.
        </p>
      </div>
    </div>
  );
};
