import { useState, useEffect } from "react";
import { createClient } from "@supabase/supabase-js";
import { ArrowLeft } from "lucide-react";

const supabase = createClient(
  import.meta.env.VITE_SUPABASE_URL,
  import.meta.env.VITE_SUPABASE_ANON_KEY
);

export default function ExecutionMonitor({
  operation,
  onClose,
}: {
  operation: any;
  onClose: () => void;
}) {
  const [batchItems, setBatchItems] = useState("");
  const [logs, setLogs] = useState<any[]>([]);
  const [executing, setExecuting] = useState(false);
  const [stats, setStats] = useState({ success: 0, error: 0, total: 0 });

  useEffect(() => {
    loadLogs();
    const interval = setInterval(loadLogs, 2000);
    return () => clearInterval(interval);
  }, [operation.id]);

  const loadLogs = async () => {
    try {
      const { data, error } = await supabase
        .from("execution_logs")
        .select("*")
        .eq("operation_id", operation.id)
        .order("started_at", { ascending: false })
        .limit(50);

      if (error) throw error;
      setLogs(data || []);

      const success = data?.filter((l) => l.status === "success").length || 0;
      const error_count =
        data?.filter((l) => l.status === "error").length || 0;
      setStats({
        success,
        error: error_count,
        total: data?.length || 0,
      });
    } catch (error) {
      console.error("Failed to load logs:", error);
    }
  };

  const handleExecute = async () => {
    const items = batchItems
      .split("\n")
      .map((i) => i.trim())
      .filter((i) => i);

    if (items.length === 0) {
      alert("Please enter at least one item");
      return;
    }

    setExecuting(true);

    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) return;

      for (const item of items) {
        await supabase.from("execution_logs").insert({
          operation_id: operation.id,
          user_id: user.id,
          batch_item: item,
          status: "pending",
        });
      }

      setBatchItems("");
      await loadLogs();
    } catch (error) {
      console.error("Failed to create execution logs:", error);
    } finally {
      setExecuting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <button
          onClick={onClose}
          className="p-2 hover:bg-slate-100 rounded-lg transition-colors"
        >
          <ArrowLeft size={20} className="text-slate-600" />
        </button>
        <div>
          <h2 className="text-2xl font-bold text-slate-900">
            {operation.name}
          </h2>
          <p className="text-slate-600 text-sm">Batch Execution Monitor</p>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-4">
          <p className="text-slate-600 text-sm">Total</p>
          <p className="text-3xl font-bold text-slate-900">{stats.total}</p>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-4">
          <p className="text-slate-600 text-sm">Success</p>
          <p className="text-3xl font-bold text-green-600">{stats.success}</p>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-4">
          <p className="text-slate-600 text-sm">Errors</p>
          <p className="text-3xl font-bold text-red-600">{stats.error}</p>
        </div>
      </div>

      {/* Input */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
        <label className="block text-sm font-medium text-slate-700 mb-3">
          Items to Process (one per line)
        </label>
        <textarea
          value={batchItems}
          onChange={(e) => setBatchItems(e.target.value)}
          placeholder="apple&#10;banana&#10;orange&#10;..."
          className="w-full px-4 py-3 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-slate-900 resize-none h-28 font-mono text-sm"
        />
        <button
          onClick={handleExecute}
          disabled={executing || !batchItems.trim()}
          className="mt-4 w-full py-2 px-4 rounded-lg font-semibold text-white bg-green-600 hover:bg-green-700 disabled:bg-green-400 transition-colors"
        >
          {executing ? "Starting..." : "Start Execution"}
        </button>
      </div>

      {/* Logs */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        <div className="p-4 border-b border-slate-200 bg-gradient-to-r from-slate-50 to-blue-50">
          <h3 className="font-bold text-slate-900">Execution Logs</h3>
        </div>

        <div className="divide-y divide-slate-200 max-h-96 overflow-y-auto">
          {logs.length === 0 ? (
            <div className="p-8 text-center">
              <p className="text-slate-500 text-sm">No executions yet</p>
            </div>
          ) : (
            logs.map((log) => (
              <div
                key={log.id}
                className={`p-4 ${
                  log.status === "success"
                    ? "bg-green-50"
                    : log.status === "error"
                      ? "bg-red-50"
                      : "bg-slate-50"
                }`}
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-mono text-sm font-semibold text-slate-900">
                        {log.batch_item}
                      </span>
                      <span
                        className={`text-xs px-2 py-1 rounded-full font-semibold ${
                          log.status === "success"
                            ? "bg-green-100 text-green-700"
                            : log.status === "error"
                              ? "bg-red-100 text-red-700"
                              : "bg-slate-100 text-slate-700"
                        }`}
                      >
                        {log.status}
                      </span>
                    </div>
                    {log.error_message && (
                      <p className="text-xs text-red-600 mt-1">
                        {log.error_message}
                      </p>
                    )}
                    <p className="text-xs text-slate-500 mt-1">
                      {new Date(log.started_at).toLocaleString()}
                    </p>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
