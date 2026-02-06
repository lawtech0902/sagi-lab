import React, { useState, useEffect, useCallback } from 'react';
import { SecurityAlert, AlertLevel } from '../types';
import { fetchAlerts, fetchAlertStats, AlertStats } from '../services/api';
import { Search, ChevronLeft, ChevronRight, ShieldAlert, Activity, Loader2 } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

interface AlertListProps {
  onNavigate: () => void;
}

const LevelBadge = ({ level }: { level: AlertLevel | string }) => {
  const colors: Record<string, string> = {
    Critical: 'bg-red-500/20 text-red-400 border-red-500/50',
    High: 'bg-orange-500/20 text-orange-400 border-orange-500/50',
    Medium: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/50',
    Low: 'bg-blue-500/20 text-blue-400 border-blue-500/50',
    Info: 'bg-slate-500/20 text-slate-400 border-slate-500/50',
  };

  // Default to Info if unknown level
  const style = colors[level] || colors['Info'];

  return (
    <span className={`px-2 py-0.5 text-xs font-mono font-medium border rounded ${style}`}>
      {level.toUpperCase()}
    </span>
  );
};

export const AlertList: React.FC<AlertListProps> = ({ onNavigate }) => {

  const [alerts, setAlerts] = useState<SecurityAlert[]>([]);
  const [stats, setStats] = useState<AlertStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadingStats, setLoadingStats] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Pagination & Filtering state
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);
  const [filters, setFilters] = useState({
    level: 'All Levels',
    verdict: 'All Verdicts',
    attackerIp: '',
  });

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const data = await fetchAlerts(page, 20, 'upload_time', 'desc', filters);
      setAlerts(data.items);
      setTotalPages(data.total_pages);
      setTotalItems(data.total);
      setError(null);
    } catch (err) {
      console.error(err);
      setError("Failed to load alerts");
    } finally {
      setLoading(false);
    }
  }, [page, filters]);

  const loadStats = useCallback(async () => {
    setLoadingStats(true);
    try {
      const data = await fetchAlertStats();
      setStats(data);
    } catch (err) {
      console.error(err);
      // Don't set main error for stats failure, just log it
    } finally {
      setLoadingStats(false);
    }
  }, []);

  useEffect(() => {
    loadStats();
  }, [loadStats]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleFilterChange = (key: string, value: string) => {
    setFilters(prev => ({ ...prev, [key]: value }));
    setPage(1); // Reset to first page on filter change
  };

  const handleApplyFilters = () => {
    loadData();
  };

  return (
    <div className="flex flex-col h-full space-y-6 animate-in fade-in duration-500">

      {/* Top Stats Section */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="col-span-3 bg-slate-900/50 backdrop-blur-md border border-slate-800 rounded-xl p-5 shadow-lg relative overflow-hidden group min-h-[12rem]">
          <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
            <Activity size={100} className="text-cyan-500" />
          </div>

          {loadingStats ? (
            <div className="flex h-full items-center justify-center">
              <Loader2 className="animate-spin text-cyan-500" size={32} />
            </div>
          ) : (
            <>
              <h3 className="text-lg font-medium text-slate-100 mb-4 flex items-center gap-2">
                <Activity size={18} className="text-cyan-400" /> Alert Volume (24h)
              </h3>
              <div className="h-40 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={stats?.by_level || []} layout="vertical" margin={{ left: 0, right: 20 }}>
                    <XAxis type="number" hide />
                    <YAxis dataKey="name" type="category" width={80} tick={{ fill: '#94a3b8', fontSize: 12 }} axisLine={false} tickLine={false} />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#f1f5f9' }}
                      cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                    />
                    <Bar dataKey="count" radius={[0, 4, 4, 0]} barSize={20}>
                      {stats?.by_level.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </>
          )}
        </div>

        <div className="bg-gradient-to-br from-slate-900 to-slate-950 border border-slate-800 rounded-xl p-6 flex flex-col justify-center items-center shadow-lg min-h-[12rem]">
          <div className="relative">
            <div className="absolute inset-0 bg-cyan-500 blur-xl opacity-20 rounded-full"></div>
            <ShieldAlert size={48} className="text-cyan-400 relative z-10 mb-2" />
          </div>
          {loadingStats ? (
            <Loader2 className="animate-spin text-cyan-500 mt-2" size={24} />
          ) : (
            <>
              <div className="text-4xl font-bold text-white mt-2">{stats?.total_critical || 0}</div>
              <div className="text-sm text-slate-400 uppercase tracking-wider font-medium mt-1">Critical Alerts</div>
            </>
          )}
        </div>
      </div>

      {/* Filters */}
      <div className="bg-slate-900/80 backdrop-blur border border-slate-800 p-4 rounded-xl shadow-sm flex flex-wrap gap-4 items-end">
        <div className="flex-1 min-w-[200px]">
          <label className="text-xs text-slate-400 font-semibold mb-1.5 block uppercase tracking-wide">Alert Level</label>
          <select
            value={filters.level}
            onChange={(e) => handleFilterChange('level', e.target.value)}
            className="w-full bg-slate-950 border border-slate-700 text-slate-300 text-sm rounded-lg p-2.5 focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500 outline-none transition-all"
          >
            <option>All Levels</option>
            <option>Critical</option>
            <option>High</option>
            <option>Medium</option>
            <option>Low</option>
          </select>
        </div>
        <div className="flex-1 min-w-[200px]">
          <label className="text-xs text-slate-400 font-semibold mb-1.5 block uppercase tracking-wide">AI Conclusion</label>
          <select
            value={filters.verdict}
            onChange={(e) => handleFilterChange('verdict', e.target.value)}
            className="w-full bg-slate-950 border border-slate-700 text-slate-300 text-sm rounded-lg p-2.5 focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500 outline-none transition-all"
          >
            <option>All Verdicts</option>
            <option>Malicious</option>
            <option>Suspicious</option>
            <option>Benign</option>
          </select>
        </div>
        <div className="flex-1 min-w-[200px]">
          <label className="text-xs text-slate-400 font-semibold mb-1.5 block uppercase tracking-wide">Attacker IP</label>
          <div className="relative">
            <input
              type="text"
              placeholder="e.g., 192.168.1.1"
              value={filters.attackerIp}
              onChange={(e) => handleFilterChange('attackerIp', e.target.value)}
              className="w-full bg-slate-950 border border-slate-700 text-slate-300 text-sm rounded-lg p-2.5 pl-9 focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500 outline-none font-mono transition-all"
            />
            <Search className="absolute left-3 top-2.5 text-slate-500" size={16} />
          </div>
        </div>
        <div className="flex-none">
          <button
            onClick={handleApplyFilters}
            className="bg-cyan-600 hover:bg-cyan-500 text-white font-medium py-2.5 px-6 rounded-lg transition-colors shadow-[0_0_15px_rgba(6,182,212,0.3)]"
          >
            Apply Filters
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="flex-1 bg-slate-900/80 backdrop-blur border border-slate-800 rounded-xl shadow-lg overflow-hidden flex flex-col">
        <div className="overflow-x-auto flex-1 h-[500px]">
          {loading ? (
            <div className="flex h-full items-center justify-center">
              <Loader2 className="animate-spin text-cyan-500" size={48} />
            </div>
          ) : error ? (
            <div className="flex h-full items-center justify-center text-red-400">
              {error}
            </div>
          ) : (
            <table className="w-full text-left border-collapse min-w-[1400px]">
              <thead>
                <tr className="bg-slate-950/50 border-b border-slate-800 text-xs text-slate-400 uppercase tracking-wider font-semibold">
                  <th className="p-4 whitespace-nowrap">AI Conclusion</th>
                  <th className="p-4 whitespace-nowrap">Alert Name</th>
                  <th className="p-4 whitespace-nowrap">Level</th>
                  <th className="p-4 whitespace-nowrap">Tactic</th>
                  <th className="p-4 whitespace-nowrap">Technique</th>
                  <th className="p-4 whitespace-nowrap">Attacker IP</th>
                  <th className="p-4 whitespace-nowrap">Victim IP</th>
                  <th className="p-4 whitespace-nowrap">Host IP</th>
                  <th className="p-4 whitespace-nowrap">First Alert Time</th>
                  <th className="p-4 whitespace-nowrap">Last Alert Time</th>
                  <th className="p-4 whitespace-nowrap">Upload Time</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800 text-sm text-slate-300">
                {alerts.map((alert) => (
                  <tr key={alert.id} className="hover:bg-slate-800/50 transition-colors group cursor-pointer" onClick={onNavigate}>
                    <td className="p-4 whitespace-nowrap">
                      <span className={`inline-flex items-center gap-1.5 px-2 py-1 rounded text-xs font-semibold ${alert.verdict === 'Malicious' ? 'text-red-400 bg-red-950/30' :
                        alert.verdict === 'Suspicious' ? 'text-yellow-400 bg-yellow-950/30' : 'text-slate-400'
                        }`}>
                        <div className={`w-1.5 h-1.5 rounded-full ${alert.verdict === 'Malicious' ? 'bg-red-500' : alert.verdict === 'Suspicious' ? 'bg-yellow-500' : 'bg-slate-500'}`}></div>
                        {alert.verdict?.toUpperCase() || 'UNKNOWN'}
                      </span>
                    </td>
                    <td className="p-4 font-medium text-white group-hover:text-cyan-400 transition-colors max-w-[200px] truncate" title={alert.name}>{alert.name}</td>
                    <td className="p-4 whitespace-nowrap"><LevelBadge level={alert.level} /></td>
                    <td className="p-4 text-slate-400 whitespace-nowrap">{alert.tactic}</td>
                    <td className="p-4 text-slate-400 font-mono text-xs whitespace-nowrap">{alert.technique}</td>
                    <td className="p-4 font-mono text-cyan-500/80 whitespace-nowrap">{alert.sourceIp}</td>
                    <td className="p-4 font-mono text-slate-400 whitespace-nowrap">{alert.destIp}</td>
                    <td className="p-4 font-mono text-slate-400 whitespace-nowrap">{alert.hostIp}</td>
                    <td className="p-4 text-slate-500 text-xs tabular-nums whitespace-nowrap">{new Date(alert.firstAlertTime).toLocaleString()}</td>
                    <td className="p-4 text-slate-500 text-xs tabular-nums whitespace-nowrap">{new Date(alert.lastAlertTime).toLocaleString()}</td>
                    <td className="p-4 text-slate-500 text-xs tabular-nums whitespace-nowrap">{new Date(alert.uploadTime).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {/* Pagination */}
        <div className="p-4 border-t border-slate-800 flex justify-between items-center bg-slate-950/30">
          <span className="text-xs text-slate-500">
            Showing <span className="text-slate-300 font-medium">{(page - 1) * 20 + 1}</span> to <span className="text-slate-300 font-medium">{Math.min(page * 20, totalItems)}</span> of <span className="text-slate-300 font-medium">{totalItems}</span> results
          </span>
          <div className="flex gap-2">
            <button
              disabled={page === 1}
              onClick={() => setPage(p => Math.max(1, p - 1))}
              className="p-1.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-400 transition-colors disabled:opacity-50"
            >
              <ChevronLeft size={16} />
            </button>
            <div className="px-3 py-1 rounded bg-cyan-600/20 text-cyan-400 border border-cyan-500/30 text-xs font-medium">
              {page} / {totalPages}
            </div>
            <button
              disabled={page === totalPages}
              onClick={() => setPage(p => Math.min(totalPages, p + 1))}
              className="p-1.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-400 transition-colors disabled:opacity-50"
            >
              <ChevronRight size={16} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};