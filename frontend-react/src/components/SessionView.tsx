import { useState, useEffect } from 'react';
import { Trash2, AlertCircle, Loader2 } from 'lucide-react';
import { fetchAgentState, deleteSession } from '../lib/api.ts';
import type { APIKeys } from '../lib/api.ts';
import { AgentState } from '../types';
import { TaskCard } from './TaskCard';
import { FinalReport } from './FinalReport';
import { ExecutionControls } from './ExecutionControls';
import { formatSessionId } from '../utils/format';

interface SessionViewProps {
  sessionId: string;
  apiKeys: APIKeys;
  onSessionDeleted: () => void;
  onRefresh?: () => void;
}

export function SessionView({ sessionId, apiKeys, onSessionDeleted, onRefresh: _onRefresh }: SessionViewProps) {
  const [state, setState] = useState<AgentState | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deleting, setDeleting] = useState(false);

  const loadState = async () => {
    try {
      setError(null);
      const data = await fetchAgentState(sessionId);
      if (!data) {
        setError('Session not found. It may have been deleted.');
        return;
      }
      setState(data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load session.';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadState();
  }, [sessionId]);

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this session? This action cannot be undone.')) {
      return;
    }

    setDeleting(true);
    try {
      await deleteSession(sessionId);
      onSessionDeleted();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to delete session.';
      setError(errorMessage);
    } finally {
      setDeleting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center space-y-4">
          <Loader2 className="w-8 h-8 animate-spin mx-auto text-gray-400" />
          <p className="text-gray-600 font-inter">Loading session...</p>
        </div>
      </div>
    );
  }

  if (error || !state) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="flex items-start gap-3 p-4 bg-red-50 border border-red-300 rounded-lg">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="font-manrope font-600 text-red-700">Error</h3>
            <p className="text-sm text-red-700 font-inter mt-1">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  const statusBadge = !state.is_active ? 'DONE' : `Step ${state.current_step}/${state.tasks.length}`;

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 space-y-8">
      {/* Goal Card */}
      <div className="p-6 bg-libra-light-gray border border-libra-border rounded-lg">
        <h2 className="text-sm font-manrope font-600 text-gray-600 uppercase tracking-wide mb-2">
          Research Goal
        </h2>
        <p className="text-lg font-inter text-libra-black leading-relaxed">{state.goal}</p>
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-3 gap-4">
        <div className="px-6 py-4 bg-white border border-libra-border rounded-lg">
          <p className="text-xs font-manrope font-600 text-gray-600 uppercase tracking-wide">Session ID</p>
          <p className="text-xl font-manrope font-700 text-libra-black mt-2">{formatSessionId(state.session_id)}</p>
        </div>
        <div className="px-6 py-4 bg-white border border-libra-border rounded-lg">
          <p className="text-xs font-manrope font-600 text-gray-600 uppercase tracking-wide">Progress</p>
          <p className="text-xl font-manrope font-700 text-libra-black mt-2">
            {state.current_step} / {state.tasks.length}
          </p>
        </div>
        <div className="px-6 py-4 bg-white border border-libra-border rounded-lg">
          <p className="text-xs font-manrope font-600 text-gray-600 uppercase tracking-wide">Status</p>
          <p
            className={`text-xl font-manrope font-700 mt-2 ${
              state.is_active ? 'text-blue-600' : 'text-green-600'
            }`}
          >
            {statusBadge}
          </p>
        </div>
      </div>

      {/* Tasks Section */}
      <div className="space-y-4">
        <h2 className="text-2xl font-manrope font-700 text-libra-black">Research Plan</h2>
        <div className="space-y-3">
          {state.tasks.map((task, idx) => (
            <TaskCard key={task.id} task={task} taskNumber={idx + 1} />
          ))}
        </div>
      </div>

      {/* Context Notes */}
      {state.context_notes.length > 0 && (
        <div className="space-y-4">
          <h2 className="text-xl font-manrope font-700 text-libra-black">Accumulated Research Context</h2>
          <div className="p-4 bg-libra-light-gray border border-libra-border rounded-lg space-y-2">
            {state.context_notes.map((note, idx) => (
              <p key={idx} className="text-sm text-gray-700 font-inter">
                • {note}
              </p>
            ))}
          </div>
        </div>
      )}

      {/* Final Report */}
      {state.final_report_path && (
        <div className="space-y-4">
          <h2 className="text-xl font-manrope font-700 text-libra-black">📄 Final Report</h2>
          <FinalReport sessionId={state.session_id} reportPath={state.final_report_path} />
        </div>
      )}

      {/* Execution Controls */}
      {state.is_active && (
        <div className="space-y-4">
          <h2 className="text-xl font-manrope font-700 text-libra-black">Execution Controls</h2>
          <ExecutionControls
            sessionId={state.session_id}
            apiKeys={apiKeys}
            isActive={state.is_active}
            onExecutionComplete={loadState}
          />
        </div>
      )}

      {/* Delete Button */}
      <div className="border-t border-libra-border pt-8">
        <button
          onClick={handleDelete}
          disabled={deleting}
          className="flex items-center justify-center gap-2 px-6 py-3 bg-red-50 border border-red-300 text-red-700 rounded-lg font-manrope font-600 text-sm hover:bg-red-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {deleting ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Deleting...
            </>
          ) : (
            <>
              <Trash2 className="w-4 h-4" />
              Delete This Session
            </>
          )}
        </button>
      </div>
    </div>
  );
}
