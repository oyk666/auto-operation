import { useState } from "react";
import { Plus, Trash2 } from "lucide-react";
import { createClient } from "@supabase/supabase-js";

const supabase = createClient(
  import.meta.env.VITE_SUPABASE_URL,
  import.meta.env.VITE_SUPABASE_ANON_KEY
);

export default function OperationsList({
  operations,
  selectedId,
  onSelect,
  onDelete,
  onRefresh,
}: {
  operations: any[];
  selectedId?: string;
  onSelect: (op: any) => void;
  onDelete: (id: string) => void;
  onRefresh: () => void;
}) {
  const [creatingNew, setCreatingNew] = useState(false);
  const [newName, setNewName] = useState("");

  const handleCreateNew = async () => {
    if (!newName.trim()) return;

    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) return;

      const { data, error } = await supabase
        .from("automation_operations")
        .insert({
          user_id: user.id,
          name: newName,
          description: "",
        })
        .select()
        .single();

      if (error) throw error;

      onSelect(data);
      onRefresh();
      setNewName("");
      setCreatingNew(false);
    } catch (error) {
      console.error("Failed to create operation:", error);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-slate-200 bg-gradient-to-r from-slate-50 to-blue-50">
        <h2 className="font-bold text-slate-900 mb-3">Your Operations</h2>
        <button
          onClick={() => setCreatingNew(true)}
          className="w-full flex items-center justify-center gap-2 py-2 px-3 rounded-lg bg-blue-600 text-white hover:bg-blue-700 transition-colors font-medium text-sm"
        >
          <Plus size={16} />
          New Operation
        </button>
      </div>

      {/* Create New Form */}
      {creatingNew && (
        <div className="p-4 border-b border-slate-200 bg-blue-50 space-y-2">
          <input
            type="text"
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            placeholder="Operation name..."
            autoFocus
            className="w-full px-3 py-2 rounded-lg border border-blue-200 focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-slate-900"
            onKeyDown={(e) => {
              if (e.key === "Enter") handleCreateNew();
              if (e.key === "Escape") setCreatingNew(false);
            }}
          />
          <div className="flex gap-2">
            <button
              onClick={handleCreateNew}
              className="flex-1 py-2 px-3 rounded-lg bg-blue-600 text-white hover:bg-blue-700 font-medium text-sm"
            >
              Create
            </button>
            <button
              onClick={() => setCreatingNew(false)}
              className="flex-1 py-2 px-3 rounded-lg bg-slate-200 text-slate-900 hover:bg-slate-300 font-medium text-sm"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Operations List */}
      <div className="divide-y divide-slate-200 max-h-96 overflow-y-auto">
        {operations.length === 0 ? (
          <div className="p-8 text-center">
            <p className="text-slate-500 text-sm">No operations yet</p>
          </div>
        ) : (
          operations.map((op) => (
            <div
              key={op.id}
              onClick={() => onSelect(op)}
              className={`p-3 cursor-pointer transition-colors ${
                selectedId === op.id
                  ? "bg-blue-50 border-l-4 border-l-blue-600"
                  : "hover:bg-slate-50"
              }`}
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-slate-900 text-sm truncate">
                    {op.name}
                  </h3>
                  <p className="text-xs text-slate-500 mt-1 truncate">
                    {op.description || "No description"}
                  </p>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onDelete(op.id);
                  }}
                  className="text-slate-400 hover:text-red-600 transition-colors p-1"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
