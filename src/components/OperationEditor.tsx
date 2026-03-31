import { useState, useEffect } from "react";
import { createClient } from "@supabase/supabase-js";
import { Plus, Trash2, GripVertical, Play } from "lucide-react";
import CoordinatePicker from "./CoordinatePicker";

const supabase = createClient(
  import.meta.env.VITE_SUPABASE_URL,
  import.meta.env.VITE_SUPABASE_ANON_KEY
);

export default function OperationEditor({
  operation,
  onSaved,
  onExecute,
}: {
  operation: any;
  onSaved: () => void;
  onExecute: () => void;
}) {
  const [name, setName] = useState(operation.name);
  const [description, setDescription] = useState(operation.description || "");
  const [actions, setActions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [showPicker, setShowPicker] = useState(false);
  const [pickingActionId, setPickingActionId] = useState<string | null>(null);

  useEffect(() => {
    loadActions();
  }, [operation.id]);

  const loadActions = async () => {
    try {
      const { data, error } = await supabase
        .from("operation_actions")
        .select("*")
        .eq("operation_id", operation.id)
        .order("order");

      if (error) throw error;
      setActions(data || []);
    } catch (error) {
      console.error("Failed to load actions:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const { error } = await supabase
        .from("automation_operations")
        .update({
          name,
          description,
          updated_at: new Date().toISOString(),
        })
        .eq("id", operation.id);

      if (error) throw error;
      onSaved();
    } catch (error) {
      console.error("Failed to save operation:", error);
    } finally {
      setSaving(false);
    }
  };

  const handleAddAction = async (type: string) => {
    try {
      const order = Math.max(...actions.map((a) => a.order), -1) + 1;
      const { data, error } = await supabase
        .from("operation_actions")
        .insert({
          operation_id: operation.id,
          order,
          action_type: type,
          config: {},
        })
        .select()
        .single();

      if (error) throw error;
      setActions([...actions, data]);
    } catch (error) {
      console.error("Failed to add action:", error);
    }
  };

  const handleDeleteAction = async (id: string) => {
    try {
      const { error } = await supabase
        .from("operation_actions")
        .delete()
        .eq("id", id);

      if (error) throw error;
      setActions(actions.filter((a) => a.id !== id));
    } catch (error) {
      console.error("Failed to delete action:", error);
    }
  };

  const handleUpdateAction = async (id: string, config: any) => {
    try {
      const { error } = await supabase
        .from("operation_actions")
        .update({ config })
        .eq("id", id);

      if (error) throw error;
      setActions(
        actions.map((a) => (a.id === id ? { ...a, config } : a))
      );
    } catch (error) {
      console.error("Failed to update action:", error);
    }
  };

  const handleStartPicking = (actionId: string) => {
    setPickingActionId(actionId);
    setShowPicker(true);
  };

  const handleCoordinatesPicked = (x: number, y: number) => {
    if (pickingActionId) {
      const action = actions.find(a => a.id === pickingActionId);
      if (action) {
        const newConfig = { ...action.config, x, y };
        handleUpdateAction(pickingActionId, newConfig);
      }
      setPickingActionId(null);
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-8 text-center">
        <p className="text-slate-500">Loading...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <CoordinatePicker
        isOpen={showPicker}
        onClose={() => {
          setShowPicker(false);
          setPickingActionId(null);
        }}
        onPick={handleCoordinatesPicked}
      />
      {/* Operation Info */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Operation Name
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-4 py-2 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-slate-900"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Description
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full px-4 py-2 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-slate-900 resize-none h-20"
              placeholder="Describe what this operation does..."
            />
          </div>

          <div className="flex gap-3 pt-2">
            <button
              onClick={handleSave}
              disabled={saving}
              className="flex-1 py-2 px-4 rounded-lg font-semibold text-white bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 transition-colors"
            >
              {saving ? "Saving..." : "Save Changes"}
            </button>
            <button
              onClick={onExecute}
              className="flex-1 py-2 px-4 rounded-lg font-semibold text-white bg-green-600 hover:bg-green-700 transition-colors flex items-center justify-center gap-2"
            >
              <Play size={16} />
              Execute
            </button>
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        <div className="p-6 border-b border-slate-200 bg-gradient-to-r from-slate-50 to-blue-50">
          <h3 className="font-bold text-slate-900 mb-3">Actions</h3>
          <div className="grid grid-cols-2 gap-2">
            {["click", "type", "wait", "screenshot"].map((type) => (
              <button
                key={type}
                onClick={() => handleAddAction(type)}
                className="py-2 px-3 rounded-lg bg-blue-600 text-white hover:bg-blue-700 font-medium text-sm transition-colors"
              >
                + {type.charAt(0).toUpperCase() + type.slice(1)}
              </button>
            ))}
          </div>
        </div>

        <div className="divide-y divide-slate-200">
          {actions.length === 0 ? (
            <div className="p-8 text-center">
              <p className="text-slate-500 text-sm">No actions yet. Add one above.</p>
            </div>
          ) : (
            actions.map((action, idx) => (
              <ActionItem
                key={action.id}
                action={action}
                index={idx}
                onDelete={() => handleDeleteAction(action.id)}
                onUpdate={(config) => handleUpdateAction(action.id, config)}
                onStartPicking={handleStartPicking}
              />
            ))
          )}
        </div>
      </div>
    </div>
  );
}

function ActionItem({
  action,
  index,
  onDelete,
  onUpdate,
  onStartPicking,
}: {
  action: any;
  index: number;
  onDelete: () => void;
  onUpdate: (config: any) => void;
  onStartPicking?: (actionId: string) => void;
}) {
  const [editing, setEditing] = useState(false);

  return (
    <div className="p-4">
      <div className="flex items-start gap-3">
        <div className="flex items-center justify-center mt-1">
          <GripVertical size={16} className="text-slate-400" />
        </div>

        <div className="flex-1">
          <div className="flex items-center justify-between mb-2">
            <div>
              <h4 className="font-semibold text-slate-900">
                {index + 1}. {action.action_type.toUpperCase()}
              </h4>
              <p className="text-xs text-slate-500 mt-1">
                {getActionDescription(action)}
              </p>
            </div>
            <button
              onClick={() => setEditing(!editing)}
              className="text-xs px-2 py-1 rounded bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium"
            >
              {editing ? "Done" : "Edit"}
            </button>
          </div>

          {editing && (
            <div className="mt-3 pt-3 border-t border-slate-200">
              <ActionConfig
                action={action}
                onChange={onUpdate}
                onStartPicking={() => onStartPicking?.(action.id)}
              />
            </div>
          )}
        </div>

        <button
          onClick={onDelete}
          className="text-slate-400 hover:text-red-600 transition-colors p-1"
        >
          <Trash2 size={16} />
        </button>
      </div>
    </div>
  );
}

function ActionConfig({
  action,
  onChange,
  onStartPicking,
}: {
  action: any;
  onChange: (config: any) => void;
  onStartPicking?: () => void;
}) {
  const config = action.config || {};

  if (action.action_type === "click") {
    return (
      <div className="space-y-3 text-sm">
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-slate-600 mb-1">X</label>
            <input
              type="number"
              value={config.x || ""}
              onChange={(e) =>
                onChange({ ...config, x: parseInt(e.target.value) || 0 })
              }
              className="w-full px-2 py-1 rounded border border-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-slate-900"
            />
          </div>
          <div>
            <label className="block text-slate-600 mb-1">Y</label>
            <input
              type="number"
              value={config.y || ""}
              onChange={(e) =>
                onChange({ ...config, y: parseInt(e.target.value) || 0 })
              }
              className="w-full px-2 py-1 rounded border border-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-slate-900"
            />
          </div>
        </div>
        {onStartPicking && (
          <button
            onClick={onStartPicking}
            className="w-full py-2 px-3 rounded bg-blue-600 hover:bg-blue-700 text-white font-medium text-sm transition-colors flex items-center justify-center gap-2"
          >
            📍 Pick from Screen
          </button>
        )}
      </div>
    );
  }

  if (action.action_type === "type") {
    return (
      <div className="space-y-3 text-sm">
        <div>
          <label className="block text-slate-600 mb-1">
            Text (use {"{item}"} for batch items)
          </label>
          <textarea
            value={config.text || ""}
            onChange={(e) => onChange({ ...config, text: e.target.value })}
            className="w-full px-2 py-1 rounded border border-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-slate-900 resize-none h-16"
          />
        </div>
      </div>
    );
  }

  if (action.action_type === "wait") {
    return (
      <div className="space-y-3 text-sm">
        <div>
          <label className="block text-slate-600 mb-1">Duration (seconds)</label>
          <input
            type="number"
            value={config.duration || 1}
            onChange={(e) =>
              onChange({ ...config, duration: parseFloat(e.target.value) || 1 })
            }
            className="w-full px-2 py-1 rounded border border-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-slate-900"
            step="0.1"
          />
        </div>
      </div>
    );
  }

  if (action.action_type === "screenshot") {
    return (
      <div className="space-y-3 text-sm">
        <div>
          <label className="block text-slate-600 mb-1">Filename</label>
          <input
            type="text"
            value={config.filename || "screenshot.png"}
            onChange={(e) => onChange({ ...config, filename: e.target.value })}
            className="w-full px-2 py-1 rounded border border-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-slate-900"
          />
        </div>
      </div>
    );
  }

  return null;
}

function getActionDescription(action: any): string {
  const config = action.config || {};
  switch (action.action_type) {
    case "click":
      return `Click at (${config.x || "?"}, ${config.y || "?"})`;
    case "type":
      return `Type: "${(config.text || "").substring(0, 30)}..."`;
    case "wait":
      return `Wait ${config.duration || 1} seconds`;
    case "screenshot":
      return `Save to ${config.filename || "screenshot.png"}`;
    default:
      return "Unknown action";
  }
}
