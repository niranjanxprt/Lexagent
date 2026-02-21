import { useState, useEffect, useCallback } from 'react';
import { Trash2, Loader2, ChevronDown, ChevronUp, Copy, Check } from 'lucide-react';
import { fetchAgentState, deleteSession } from '../lib/api';
import type { APIKeys } from '../types';
import { AgentState } from '../types';
import { TaskCard } from './TaskCard';
import { FinalReport } from './FinalReport';
import { ExecutionControls } from './ExecutionControls';
import { ErrorMessage } from './ErrorMessage';
import { formatSessionId } from '../utils/format';

function ContextNotesSection({ notes }: { notes: string[] }) {
  const [isOpen, setIsOpen] = useState(false);
  const [copied, setCopied] = useState(false);

  const markdown = notes.map((n) => `- ${n}`).join('\n');

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(markdown);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // fallback for older browsers
      const ta = document.createElement('textarea');
      ta.value = markdown;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand('copy');
      document.body.removeChild(ta);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="border border-libra-border rounded-lg overflow-hidden">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-4 py-3 bg-libra-light-gray hover:bg-gray-200 transition-colors flex items-center justify-between"
      >
        <h2 className="text-xl font-manrope font-700 text-libra-black">Accumulated Research Context</h2>
        {isOpen ? (
          <ChevronUp className="w-5 h-5 text-gray-700" />
        ) : (
          <ChevronDown className="w-5 h-5 text-gray-700" />
        )}
      </button>
      {isOpen && (
        <div className="p-4 bg-white border-t border-libra-border space-y-4">
          <div className="flex justify-end">
            <button
              onClick={handleCopy}
              className="flex items-center gap-2 px-4 py-2 bg-libra-black text-white rounded-lg font-manrope font-600 text-sm hover:bg-libra-dark-gray transition-colors"
            >
              {copied ? (
                <>
                  <Check className="w-4 h-4" />
                  Copied!
                </>
              ) : (
                <>
                  <Copy className="w-4 h-4" />
                  Copy Markdown
                </>
              )}
            </button>
          </div>
          <div className="space-y-2">
            {notes.map((note, idx) => (
              <p key={idx} className="text-sm text-gray-700 font-inter">
                • {note}
              </p>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

interface SessionViewProps {
  sessionId: string;
  apiKeys: APIKeys;
  onSessionDeleted: () => void;
}

export function SessionView({ sessionId, apiKeys, onSessionDeleted }: SessionViewProps) {
  const [state, setState] = useState<AgentState | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deleting, setDeleting] = useState(false);

  const loadState = useCallback(async () => {
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
  }, [sessionId]);

  useEffect(() => {
    loadState();
  }, [loadState]);

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
        <ErrorMessage message={error ?? 'Session not found.'} />
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

      {/* Context Notes - Collapsible, collapsed by default */}
      {state.context_notes.length > 0 && (
        <ContextNotesSection notes={state.context_notes} />
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
