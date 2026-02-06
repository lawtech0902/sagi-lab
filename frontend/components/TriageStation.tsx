import React, { useState } from 'react';
import { Play, Eraser, Database, Loader2, Cpu } from 'lucide-react';
import { analyzeAlert } from '../services/api';

import { SAMPLE_ALERT_JSON } from '../types';

export const TriageStation: React.FC = () => {
  const [inputJson, setInputJson] = useState('');
  const [output, setOutput] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleExecute = async () => {
    if (!inputJson.trim()) return;

    setLoading(true);
    setOutput(null); // Clear previous
    try {
      const result = await analyzeAlert(inputJson);
      setOutput(result);
    } catch (e) {
      setOutput("Error processing request.");
    } finally {
      setLoading(false);
    }
  };

  const loadSample = () => setInputJson(SAMPLE_ALERT_JSON);
  const clear = () => {
    setInputJson('');
    setOutput(null);
  };

  // Helper to render markdown-like output roughly without a heavy library
  const renderOutput = (text: string) => {
    return text.split('\n').map((line, i) => {
      if (line.startsWith('### ')) return <h3 key={i} className="text-lg font-bold text-cyan-400 mt-4 mb-2">{line.replace('### ', '')}</h3>;
      if (line.startsWith('**')) return <p key={i} className="font-bold text-slate-200 mt-2 mb-1">{line.replace(/\*\*/g, '')}</p>;
      if (line.startsWith('- ')) return <li key={i} className="ml-4 text-slate-300 list-disc marker:text-cyan-600">{line.replace('- ', '')}</li>;
      return <p key={i} className="text-slate-400 leading-relaxed min-h-[1em]">{line}</p>;
    });
  };

  return (
    <div className="h-full flex flex-col gap-6 animate-in fade-in slide-in-from-bottom-4 duration-500">

      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-semibold text-slate-100 flex items-center gap-3">
          <span className="p-2 bg-cyan-500/10 rounded-lg border border-cyan-500/20">
            <Cpu className="text-cyan-400" size={24} />
          </span>
          AI Triage Station
        </h2>
        <div className="flex gap-2">
          <span className="text-xs font-mono text-cyan-600/80 bg-cyan-950/30 px-3 py-1 rounded border border-cyan-900/50">MODEL: GEMINI-2.5-FLASH</span>
        </div>
      </div>

      <div className="flex-1 grid grid-cols-1 lg:grid-cols-2 gap-6 h-full min-h-[500px]">

        {/* Left: Input */}
        <div className="flex flex-col bg-slate-900/80 backdrop-blur border border-slate-800 rounded-xl overflow-hidden shadow-lg">
          <div className="p-4 border-b border-slate-800 bg-slate-950/50 flex justify-between items-center">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-cyan-500 animate-pulse"></div>
              <span className="text-xs font-bold text-slate-400 tracking-wider">INPUT STREAM</span>
            </div>
            <button
              onClick={loadSample}
              className="text-xs text-cyan-400 hover:text-cyan-300 flex items-center gap-1 px-2 py-1 hover:bg-cyan-950/30 rounded transition-all"
            >
              <Database size={12} /> Load Sample
            </button>
          </div>
          <div className="flex-1 relative">
            <textarea
              value={inputJson}
              onChange={(e) => setInputJson(e.target.value)}
              placeholder='Paste alert JSON here...'
              className="w-full h-full bg-slate-900 text-slate-300 font-mono text-sm p-4 outline-none resize-none focus:bg-slate-800/50 transition-colors"
              spellCheck={false}
            />
          </div>
          <div className="p-4 border-t border-slate-800 bg-slate-950/30 flex gap-3">
            <button
              onClick={handleExecute}
              disabled={loading || !inputJson}
              className="flex-1 bg-cyan-600 hover:bg-cyan-500 disabled:bg-slate-800 disabled:text-slate-500 text-white font-medium py-2.5 rounded-lg flex items-center justify-center gap-2 transition-all shadow-[0_0_15px_rgba(6,182,212,0.2)] disabled:shadow-none"
            >
              {loading ? <Loader2 className="animate-spin" size={18} /> : <Play size={18} fill="currentColor" />}
              Execute Analysis
            </button>
            <button
              onClick={clear}
              className="px-4 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg flex items-center justify-center transition-colors border border-slate-700"
            >
              <Eraser size={18} />
            </button>
          </div>
        </div>

        {/* Right: Output */}
        <div className="flex flex-col bg-slate-900/80 backdrop-blur border border-slate-800 rounded-xl overflow-hidden shadow-lg relative">
          <div className="p-4 border-b border-slate-800 bg-slate-950/50 flex justify-between items-center">
            <div className="flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full transition-colors ${loading ? 'bg-yellow-500 animate-ping' : output ? 'bg-green-500' : 'bg-slate-600'}`}></span>
              <span className="text-xs font-bold text-slate-400 tracking-wider">ANALYSIS OUTPUT</span>
            </div>
          </div>

          <div className="flex-1 p-6 overflow-y-auto bg-slate-900/50">
            {loading ? (
              <div className="h-full flex flex-col items-center justify-center text-slate-500 gap-4">
                <div className="relative">
                  <div className="w-16 h-16 border-4 border-cyan-500/20 border-t-cyan-500 rounded-full animate-spin"></div>
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="w-2 h-2 bg-cyan-400 rounded-full"></div>
                  </div>
                </div>
                <p className="font-mono text-sm animate-pulse">Processing Neural Vectors...</p>
              </div>
            ) : output ? (
              <div className="prose prose-invert max-w-none prose-p:text-sm prose-h3:text-cyan-400 prose-strong:text-slate-200">
                {renderOutput(output)}
              </div>
            ) : (
              <div className="h-full flex flex-col items-center justify-center opacity-30">
                <Cpu size={64} className="text-slate-600 mb-4" />
                <p className="text-slate-400 font-mono text-sm">AWAITING INPUT_STREAM</p>
              </div>
            )}
          </div>
        </div>

      </div>
    </div>
  );
};