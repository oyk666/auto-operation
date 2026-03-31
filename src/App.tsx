import { useEffect, useState } from "react";
import { createClient } from "@supabase/supabase-js";
import AuthPanel from "./components/AuthPanel";
import OperationsList from "./components/OperationsList";
import OperationEditor from "./components/OperationEditor";
import ExecutionMonitor from "./components/ExecutionMonitor";

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

const supabase = createClient(supabaseUrl, supabaseKey);

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<any>(null);
  const [selectedOperation, setSelectedOperation] = useState<any>(null);
  const [operations, setOperations] = useState<any[]>([]);
  const [showExecutionMonitor, setShowExecutionMonitor] = useState(false);

  useEffect(() => {
    checkAuth();
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (event, session) => {
        if (session?.user) {
          setIsAuthenticated(true);
          setUser(session.user);
          loadOperations();
        } else {
          setIsAuthenticated(false);
          setUser(null);
          setOperations([]);
        }
      }
    );
    return () => subscription.unsubscribe();
  }, []);

  const checkAuth = async () => {
    const { data: { session } } = await supabase.auth.getSession();
    if (session?.user) {
      setIsAuthenticated(true);
      setUser(session.user);
      loadOperations();
    }
  };

  const loadOperations = async () => {
    try {
      const { data, error } = await supabase
        .from("automation_operations")
        .select("*")
        .order("updated_at", { ascending: false });

      if (error) throw error;
      setOperations(data || []);
    } catch (error) {
      console.error("Failed to load operations:", error);
    }
  };

  const handleOperationSaved = () => {
    loadOperations();
    setSelectedOperation(null);
  };

  const handleDeleteOperation = async (id: string) => {
    if (confirm("Are you sure you want to delete this operation?")) {
      try {
        const { error } = await supabase
          .from("automation_operations")
          .delete()
          .eq("id", id);

        if (error) throw error;
        loadOperations();
        if (selectedOperation?.id === id) {
          setSelectedOperation(null);
        }
      } catch (error) {
        console.error("Failed to delete operation:", error);
      }
    }
  };

  if (!isAuthenticated) {
    return <AuthPanel onSuccess={() => checkAuth()} />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-slate-900">
                Automation Tool
              </h1>
              <p className="text-slate-600 text-sm mt-1">
                Batch automation for repetitive software operations
              </p>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-sm">
                <p className="text-slate-600">Signed in as</p>
                <p className="font-semibold text-slate-900">{user?.email}</p>
              </div>
              <button
                onClick={() => {
                  supabase.auth.signOut();
                  setIsAuthenticated(false);
                }}
                className="px-4 py-2 rounded-lg bg-red-50 text-red-700 hover:bg-red-100 transition-colors font-medium"
              >
                Sign Out
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Sidebar - Operations List */}
          <div className="lg:col-span-1">
            <OperationsList
              operations={operations}
              selectedId={selectedOperation?.id}
              onSelect={setSelectedOperation}
              onDelete={handleDeleteOperation}
              onRefresh={loadOperations}
            />
          </div>

          {/* Main Content Area */}
          <div className="lg:col-span-2">
            {showExecutionMonitor && selectedOperation ? (
              <ExecutionMonitor
                operation={selectedOperation}
                onClose={() => setShowExecutionMonitor(false)}
              />
            ) : selectedOperation ? (
              <OperationEditor
                operation={selectedOperation}
                onSaved={handleOperationSaved}
                onExecute={() => setShowExecutionMonitor(true)}
              />
            ) : (
              <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-12 text-center">
                <div className="max-w-sm mx-auto">
                  <svg
                    className="w-16 h-16 mx-auto mb-4 text-slate-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={1.5}
                      d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                    />
                  </svg>
                  <h3 className="text-lg font-semibold text-slate-900 mb-2">
                    No Operation Selected
                  </h3>
                  <p className="text-slate-600 mb-6">
                    Select an operation from the list or create a new one to get started.
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
