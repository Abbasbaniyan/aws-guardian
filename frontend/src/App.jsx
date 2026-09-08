import React, { useState, useEffect } from 'react';
import { 
  ShieldCheck, 
  AlertTriangle, 
  CheckCircle, 
  Server, 
  Clock, 
  DollarSign, 
  RotateCcw,
  Zap
} from 'lucide-react';
import { fetchInstances, fetchDailyBrief, fetchAuditLogs, stopInstance } from './services/api';

export default function App() {
  const [instancesData, setInstancesData] = useState(null);
  const [brief, setBrief] = useState(null);
  const [auditLogs, setAuditLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [actionMessage, setActionMessage] = useState(null);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const [inst, brf, logs] = await Promise.all([
        fetchInstances(),
        fetchDailyBrief(),
        fetchAuditLogs(),
      ]);
      setInstancesData(inst);
      setBrief(brf);
      setAuditLogs(logs);
    } catch (err) {
      console.error("Error loading dashboard data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  const handleStop = async (instanceId) => {
    if (!window.confirm(`Confirm: Stop instance ${instanceId}?`)) return;
    try {
      setActionLoading(true);
      const res = await stopInstance(instanceId);
      setActionMessage({ type: 'success', text: res.message });
      await loadDashboardData();
    } catch (err) {
      const errDetail = err.response?.data?.detail || "Action failed";
      setActionMessage({ type: 'error', text: errDetail });
    } finally {
      setActionLoading(false);
      setTimeout(() => setActionMessage(null), 5000);
    }
  };

  if (loading && !instancesData) {
    return (
      <div className="flex h-screen items-center justify-center bg-slate-950 text-slate-400">
        <div className="flex items-center space-x-3">
          <ShieldCheck className="h-7 w-7 animate-pulse text-teal-400" />
          <span className="text-lg font-medium">AWS Guardian is synchronizing...</span>
        </div>
      </div>
    );
  }

  const alertItem = brief?.alerts?.[0];

  return (
    <div className="min-h-screen bg-slate-950 p-6 text-slate-100 flex flex-col items-center">
      {/* Top Banner */}
      <div className="w-full max-w-5xl flex justify-between items-center mb-6">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 bg-teal-500/10 border border-teal-500/30 rounded-xl">
            <ShieldCheck className="h-8 w-8 text-teal-400" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
              AWS Guardian
              <span className="text-xs px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 font-mono">
                {instancesData?.data_source}
              </span>
            </h1>
            <p className="text-xs text-slate-400">You run your servers. We watch them.</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs text-emerald-400">
            <CheckCircle className="h-4 w-4" />
            <span>Rules Engine: Active</span>
          </div>
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs text-teal-400">
            <Zap className="h-4 w-4" />
            <span>AI Layer: Connected</span>
          </div>
          <button 
            onClick={loadDashboardData}
            className="p-2 rounded-lg bg-slate-900 border border-slate-800 hover:bg-slate-800 text-slate-300 transition"
            title="Refresh Watchdog"
          >
            <RotateCcw className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Action Notification Toast */}
      {actionMessage && (
        <div className={`w-full max-w-5xl mb-4 p-3.5 rounded-xl border text-sm flex items-center justify-between ${
          actionMessage.type === 'error' 
            ? 'bg-rose-500/10 border-rose-500/30 text-rose-300' 
            : 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
        }`}>
          <span>{actionMessage.text}</span>
          <button onClick={() => setActionMessage(null)} className="text-xs font-semibold uppercase">Dismiss</button>
        </div>
      )}

      {/* Main Grid Layout */}
      <div className="w-full max-w-5xl grid grid-cols-1 md:grid-cols-3 gap-6">
        
        {/* Left Card: Status Overview */}
        <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-5 backdrop-blur flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <span className="text-xs uppercase tracking-wider font-semibold text-slate-400">Fleet Inventory</span>
              <Server className="h-4 w-4 text-slate-500" />
            </div>

            <div className="flex items-baseline gap-2 mb-6">
              <span className="text-4xl font-extrabold text-white">{instancesData?.total_count || 0}</span>
              <span className="text-sm text-slate-400">Instances</span>
            </div>

            <div className="space-y-3">
              <div className="flex justify-between items-center text-sm p-2.5 rounded-lg bg-slate-950/40 border border-slate-800/40">
                <span className="flex items-center gap-2">
                  <span className="h-2.5 w-2.5 rounded-full bg-emerald-500"></span>
                  <span>Normal Workloads</span>
                </span>
                <span className="font-semibold">{brief?.normal_count || 0}</span>
              </div>

              <div className="flex justify-between items-center text-sm p-2.5 rounded-lg bg-slate-950/40 border border-slate-800/40">
                <span className="flex items-center gap-2">
                  <span className="h-2.5 w-2.5 rounded-full bg-amber-500"></span>
                  <span>Attention Required</span>
                </span>
                <span className="font-semibold">{brief?.attention_count || 0}</span>
              </div>

              <div className="flex justify-between items-center text-sm p-2.5 rounded-lg bg-slate-950/40 border border-slate-800/40">
                <span className="flex items-center gap-2">
                  <span className="h-2.5 w-2.5 rounded-full bg-rose-500"></span>
                  <span>Unusual / Runaway</span>
                </span>
                <span className="font-semibold">{brief?.critical_count || 0}</span>
              </div>
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-slate-800/60 text-xs text-slate-400 flex items-center justify-between">
            <span>Production Protected</span>
            <span className="text-teal-400 font-medium">{instancesData?.protected_count || 0} nodes</span>
          </div>
        </div>

        {/* Center & Right Card: Active AI Heads-Up Alert */}
        <div className="md:col-span-2 bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 backdrop-blur flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-2 text-amber-400">
                <AlertTriangle className="h-5 w-5" />
                <span className="text-xs uppercase tracking-wider font-bold">AI Heads-Up</span>
              </div>
              {alertItem && (
                <span className="text-xs px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 font-mono">
                  {alertItem.severity.toUpperCase()}
                </span>
              )}
            </div>

            {alertItem ? (
              <div className="space-y-4">
                <div>
                  <h3 className="text-lg font-bold text-white mb-1">{alertItem.headline}</h3>
                  <p className="text-xs text-slate-400 font-mono">{alertItem.instance_name} ({alertItem.instance_id})</p>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 p-3 rounded-xl bg-slate-950/50 border border-slate-800/60 text-xs">
                  <div>
                    <span className="text-slate-400 block mb-0.5">Running for</span>
                    <span className="font-semibold text-white flex items-center gap-1">
                      <Clock className="h-3 w-3 text-slate-400" />
                      {alertItem.runtime_formatted}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400 block mb-0.5">Typical Baseline</span>
                    <span className="font-semibold text-slate-300">{alertItem.normal_runtime_formatted}</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block mb-0.5">Waste Awareness</span>
                    <span className="font-semibold text-amber-400 flex items-center">
                      <DollarSign className="h-3 w-3" />
                      ~${alertItem.estimated_waste_cost_usd}
                    </span>
                  </div>
                </div>

                <p className="text-xs leading-relaxed text-slate-300 bg-slate-800/40 p-3 rounded-xl border border-slate-800/50">
                  {alertItem.explanation}
                </p>
              </div>
            ) : (
              <div className="py-12 text-center text-slate-400">
                <CheckCircle className="h-10 w-10 text-emerald-400 mx-auto mb-2 opacity-80" />
                <p className="text-sm font-medium text-white">All instances operating within normal limits.</p>
                <p className="text-xs text-slate-500 mt-1">No forgotten or idle workloads detected.</p>
              </div>
            )}
          </div>

          {/* Action Row */}
          {alertItem && (
            <div className="mt-6 pt-4 border-t border-slate-800/60 flex items-center justify-between">
              <span className="text-xs text-slate-400">
                {alertItem.can_execute_auto_stop ? "Eligible for action" : "Protected from automation"}
              </span>
              <div className="flex gap-2">
                {alertItem.can_execute_auto_stop && (
                  <button
                    disabled={actionLoading}
                    onClick={() => handleStop(alertItem.instance_id)}
                    className="px-4 py-2 text-xs font-semibold rounded-lg bg-rose-600 hover:bg-rose-500 text-white transition disabled:opacity-50"
                  >
                    {actionLoading ? "Executing..." : "Stop Instance"}
                  </button>
                )}
                <button
                  onClick={loadDashboardData}
                  className="px-4 py-2 text-xs font-semibold rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 transition"
                >
                  Keep Running
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Bottom Audit Feed Card */}
        <div className="md:col-span-3 bg-slate-900/40 border border-slate-800/80 rounded-2xl p-5">
          <span className="text-xs uppercase tracking-wider font-semibold text-slate-400 block mb-3">Audit Trail</span>
          <div className="divide-y divide-slate-800/60">
            {auditLogs.length > 0 ? (
              auditLogs.slice(0, 4).map((log) => (
                <div key={log.id} className="py-2 flex items-center justify-between text-xs">
                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
                      log.status === 'SUCCESS' 
                        ? 'bg-emerald-500/20 text-emerald-300' 
                        : 'bg-rose-500/20 text-rose-300'
                    }`}>
                      {log.status}
                    </span>
                    <span className="font-mono text-slate-300">{log.instance_name}</span>
                    <span className="text-slate-500 text-[11px]">— {log.reason}</span>
                  </div>
                  <span className="text-slate-500 font-mono text-[10px]">{new Date(log.timestamp).toLocaleTimeString()}</span>
                </div>
              ))
            ) : (
              <p className="text-xs text-slate-500 py-2">No security audit records logged yet.</p>
            )}
          </div>
        </div>

      </div>
    </div>
  );
}