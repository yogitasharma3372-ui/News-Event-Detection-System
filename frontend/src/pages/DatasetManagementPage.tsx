import React, { useState } from 'react';
import {
  FolderInput,
  Upload,
  CheckCircle2,
  AlertTriangle,
  FileText,
  Sparkles,
  ArrowRight,
  Database
} from 'lucide-react';
import { api } from '../api/client';

export const DatasetManagementPage: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [validationReport, setValidationReport] = useState<any | null>(null);
  const [isValidating, setIsValidating] = useState(false);
  const [isImporting, setIsImporting] = useState(false);
  const [importResult, setImportResult] = useState<any | null>(null);

  const [isImportingFixture, setIsImportingFixture] = useState(false);
  const [fixtureMessage, setFixtureMessage] = useState<string | null>(null);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setSelectedFile(file);
    setValidationReport(null);
    setImportResult(null);

    // Run dry-run validation
    setIsValidating(true);
    try {
      const report = await api.validateUpload(file);
      setValidationReport(report);
    } catch (err: any) {
      alert(`Validation error: ${err.message}`);
    } finally {
      setIsValidating(false);
    }
  };

  const handleConfirmImport = async () => {
    if (!selectedFile) return;
    setIsImporting(true);
    try {
      const res = await api.importFile(selectedFile);
      setImportResult(res);
      setSelectedFile(null);
      setValidationReport(null);
    } catch (err: any) {
      alert(`Import error: ${err.message}`);
    } finally {
      setIsImporting(false);
    }
  };

  const handleImportFixture = async () => {
    setIsImportingFixture(true);
    setFixtureMessage(null);
    try {
      const res = await api.importFixture();
      await api.detectEvents({});
      setFixtureMessage(`Successfully imported ${res.inserted} fixture articles (${res.skipped_duplicates} duplicates skipped) and clustered into events!`);
    } catch (err: any) {
      alert(`Fixture error: ${err.message}`);
    } finally {
      setIsImportingFixture(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Quick Benchmark Importer */}
      <div className="bg-[#0f172a] border border-slate-800 rounded-xl p-6 space-y-4">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="space-y-1">
            <h3 className="text-base font-semibold text-slate-100 flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-blue-400" />
              <span>Standard Verified Research Benchmark Fixture</span>
            </h3>
            <p className="text-xs text-slate-400 max-w-xl">
              Quickly load the standard test fixture containing 14 verified articles across 4 ground-truth event clusters (Japan Sendai Earthquake, JWST Galaxy Cluster, ECB Rate Hike, Dubai Climate Summit) plus 2 unassigned noise articles.
            </p>
          </div>

          <button
            onClick={handleImportFixture}
            disabled={isImportingFixture}
            className="flex items-center space-x-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold rounded-lg shadow-sm transition disabled:opacity-50 shrink-0 cursor-pointer"
          >
            <Database className="w-4 h-4" />
            <span>{isImportingFixture ? 'Importing Fixture...' : 'Load Standard Benchmark'}</span>
          </button>
        </div>

        {fixtureMessage && (
          <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-lg text-xs text-emerald-400 flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 shrink-0" />
            <span>{fixtureMessage}</span>
          </div>
        )}
      </div>

      {/* Custom Dataset Upload Box */}
      <div className="bg-[#0f172a] border border-slate-800 rounded-xl p-6 space-y-5">
        <div>
          <h3 className="text-base font-semibold text-slate-100 flex items-center gap-2">
            <FolderInput className="w-5 h-5 text-blue-400" />
            <span>Import Custom News Dataset (CSV / JSON)</span>
          </h3>
          <p className="text-xs text-slate-400">
            Upload custom article collections with pre-validation, timestamp normalization, and duplicate detection.
          </p>
        </div>

        {/* Dropzone */}
        <label className="border-2 border-dashed border-slate-700 hover:border-blue-500/50 rounded-xl p-8 flex flex-col items-center justify-center space-y-3 cursor-pointer bg-slate-900/40 transition">
          <div className="w-12 h-12 rounded-full bg-blue-500/10 flex items-center justify-center text-blue-400">
            <Upload className="w-6 h-6" />
          </div>
          <div className="text-center space-y-1">
            <p className="text-xs font-semibold text-slate-200">
              Click to select or drag and drop a news dataset file
            </p>
            <p className="text-[11px] text-slate-500">Supports .csv or .json files up to 25 MB</p>
          </div>
          <input
            type="file"
            accept=".csv,.json"
            onChange={handleFileChange}
            className="hidden"
          />
        </label>

        {/* Validation In Progress */}
        {isValidating && (
          <div className="p-4 bg-slate-900 rounded-lg text-center text-xs text-slate-400 flex items-center justify-center space-x-2">
            <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
            <span>Validating file structure, schema, and timestamps...</span>
          </div>
        )}

        {/* Pre-Import Validation Report */}
        {validationReport && (
          <div className="p-5 bg-slate-900 border border-slate-800 rounded-xl space-y-4 text-xs">
            <div className="flex items-center justify-between">
              <h4 className="font-semibold text-slate-200 flex items-center gap-2">
                <FileText className="w-4 h-4 text-blue-400" />
                <span>Pre-Import Validation Report: {validationReport.filename}</span>
              </h4>
              <span className="text-slate-400">
                {validationReport.valid_rows} valid / {validationReport.total_rows} total rows
              </span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
              <div className="p-3 bg-[#0f172a] rounded-lg border border-slate-800">
                <span className="text-[10px] text-slate-500 uppercase block font-semibold">Total Rows</span>
                <span className="text-lg font-bold text-slate-200">{validationReport.total_rows}</span>
              </div>
              <div className="p-3 bg-[#0f172a] rounded-lg border border-slate-800">
                <span className="text-[10px] text-slate-500 uppercase block font-semibold">Valid Rows</span>
                <span className="text-lg font-bold text-emerald-400">{validationReport.valid_rows}</span>
              </div>
              <div className="p-3 bg-[#0f172a] rounded-lg border border-slate-800">
                <span className="text-[10px] text-slate-500 uppercase block font-semibold">Duplicates</span>
                <span className="text-lg font-bold text-amber-400">{validationReport.duplicate_rows}</span>
              </div>
              <div className="p-3 bg-[#0f172a] rounded-lg border border-slate-800">
                <span className="text-[10px] text-slate-500 uppercase block font-semibold">Invalid / Errors</span>
                <span className="text-lg font-bold text-red-400">{validationReport.invalid_rows}</span>
              </div>
            </div>

            {/* Validation Errors list if any */}
            {validationReport.errors && validationReport.errors.length > 0 && (
              <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg space-y-1">
                <p className="font-semibold text-red-400 text-xs">Validation Issues Detected:</p>
                <ul className="list-disc list-inside text-[11px] text-red-300 space-y-0.5">
                  {validationReport.errors.map((err: string, i: number) => (
                    <li key={i}>{err}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Preview of first 2 rows */}
            {validationReport.preview && validationReport.preview.length > 0 && (
              <div className="space-y-2">
                <p className="font-semibold text-slate-300 text-[11px]">Preview Sample Records:</p>
                <div className="space-y-1.5 font-mono text-[11px]">
                  {validationReport.preview.slice(0, 2).map((item: any, i: number) => (
                    <div key={i} className="p-2.5 bg-[#0f172a] rounded border border-slate-800 text-slate-300">
                      <div className="text-blue-400 font-bold">{item.headline}</div>
                      <div className="text-slate-500 text-[10px]">{item.source_name} • {item.published_at}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Explicit Confirm Button */}
            <div className="flex justify-end pt-2">
              <button
                onClick={handleConfirmImport}
                disabled={isImporting || validationReport.valid_rows === 0}
                className="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold rounded-lg shadow-sm transition disabled:opacity-50 flex items-center space-x-1.5 cursor-pointer"
              >
                <CheckCircle2 className="w-4 h-4" />
                <span>
                  {isImporting ? 'Writing to SQLite Database...' : `Confirm & Commit ${validationReport.valid_rows} Articles`}
                </span>
              </button>
            </div>
          </div>
        )}

        {/* Import Success Notification */}
        {importResult && (
          <div className="p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-xl space-y-2 text-xs text-emerald-400">
            <div className="flex items-center gap-2 font-semibold">
              <CheckCircle2 className="w-5 h-5 shrink-0" />
              <span>Dataset Import Completed Successfully!</span>
            </div>
            <p className="text-slate-300">
              Successfully inserted <strong>{importResult.inserted}</strong> new articles into persistent storage.
              {importResult.skipped_duplicates > 0 && ` (${importResult.skipped_duplicates} duplicate records skipped)`}
            </p>
          </div>
        )}
      </div>
    </div>
  );
};
