import { useCallback, useEffect, useState } from 'react';
import { Plus, RefreshCw, Trash2, X } from 'lucide-react';
import { fetchSessions, deleteSession } from '../lib/api';
import type { APIKeys } from '../types';
import { Session } from '../types';
import { truncateText, formatDate } from '../utils/format';

interface SidebarProps {
  currentSessionId: string | null;
  onSessionSelect: (sessionId: string | null) => void;
  apiKeys: APIKeys;
  onApiKeysChange: (keys: APIKeys) => void;
  onCloseMobile?: () => void;
}

export function Sidebar({
  currentSessionId,
  onSessionSelect,
  apiKeys,
  onApiKeysChange,
  onCloseMobile,
}: SidebarProps) {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const loadSessions = useCallback(async () => {
    const data = await fetchSessions();
    setSessions(data.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()));
  }, []);

  useEffect(() => {
    loadSessions();
    const interval = setInterval(loadSessions, 10000);
    return () => clearInterval(interval);
  }, [loadSessions]);

  const getStatusBadge = (session: Session): string => {
    if (!session.is_active) {
      return 'DONE';
    }
    return `Step ${session.current_step}`;
  };

  const handleDeleteSession = async (e: React.MouseEvent, sessionId: string) => {
    e.stopPropagation();
    if (!window.confirm('Delete this session? This cannot be undone.')) return;
    setDeletingId(sessionId);
    try {
      await deleteSession(sessionId);
      if (currentSessionId === sessionId) {
        onSessionSelect(null);
      }
      await loadSessions();
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <div className="w-60 bg-white border-r border-libra-border flex flex-col h-full">
      {/* Header */}
      <div className="px-4 py-6 border-b border-libra-border flex items-start justify-between gap-2">
        <div>
          <h1 className="text-2xl font-manrope font-700 text-libra-black">⚖️ LexAgent</h1>
          <p className="text-xs text-gray-600 mt-1">Legal Research AI Agent</p>
        </div>
        {onCloseMobile && (
          <button
            onClick={onCloseMobile}
            className="md:hidden flex-shrink-0 p-2 rounded-lg hover:bg-libra-light-gray transition-colors touch-manipulation min-h-[44px] min-w-[44px] flex items-center justify-center"
            aria-label="Close menu"
          >
            <X className="w-5 h-5" />
          </button>
        )}
      </div>

      {/* API Keys (optional) */}
      <details className="px-2 py-2 border-b border-libra-border">
        <summary className="flex items-center gap-2 text-xs font-manrope font-600 text-gray-600 cursor-pointer list-none">
          API keys (optional)
        </summary>
        <div className="mt-2 space-y-2">
          <input
            type="password"
            placeholder="OpenAI API Key"
            value={apiKeys.openai ?? ''}
            onChange={(e) => onApiKeysChange({ ...apiKeys, openai: e.target.value })}
            className="w-full px-2 py-1.5 text-xs border border-libra-border rounded focus:outline-none focus:ring-1 focus:ring-libra-black"
          />
          <input
            type="password"
            placeholder="Tavily API Key"
            value={apiKeys.tavily ?? ''}
            onChange={(e) => onApiKeysChange({ ...apiKeys, tavily: e.target.value })}
            className="w-full px-2 py-1.5 text-xs border border-libra-border rounded focus:outline-none focus:ring-1 focus:ring-libra-black"
          />
          <p className="text-[10px] text-gray-500">Leave blank to use server defaults.</p>
        </div>
      </details>

      {/* New Session Button */}
      <button
        onClick={() => onSessionSelect(null)}
        className="m-4 w-[calc(100%-2rem)] min-h-[44px] flex items-center justify-center gap-2 px-4 py-2 border border-libra-border rounded-lg bg-white hover:bg-libra-light-gray transition-colors font-inter font-600 text-sm text-libra-black touch-manipulation"
      >
        <Plus className="w-4 h-4" />
        New Session
      </button>

      {/* Sessions List */}
      <div className="flex-1 overflow-y-auto px-2">
        {sessions.length > 0 && (
          <div className="mb-2">
            <h2 className="px-2 py-2 text-xs font-manrope font-600 text-gray-600 uppercase tracking-wide">
              Manage Sessions
            </h2>
            <div className="space-y-1">
              {sessions.map((session) => {
                const isActive = session.session_id === currentSessionId;
                const status = getStatusBadge(session);

                return (
                  <div
                    key={session.session_id}
                    className={`flex items-center gap-1 w-full px-3 py-2 rounded-lg transition-colors group ${
                      isActive ? 'bg-libra-black text-white' : 'bg-white text-libra-black hover:bg-libra-light-gray'
                    }`}
                  >
                    <button
                      onClick={() => onSessionSelect(session.session_id)}
                      className="flex-1 min-w-0 text-left"
                    >
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex-1 min-w-0">
                          <p className={`text-xs font-inter font-500 ${isActive ? 'text-white' : 'text-libra-dark-gray'}`}>
                            {truncateText(session.goal, 30)}
                          </p>
                          <p className={`text-xs mt-1 ${isActive ? 'text-gray-300' : 'text-gray-500'}`}>
                            {formatDate(session.created_at)}
                          </p>
                        </div>
                        <span
                          className={`flex-shrink-0 text-xs px-2 py-1 rounded whitespace-nowrap ${
                            isActive ? 'bg-white text-libra-black' : 'bg-libra-light-gray text-libra-dark-gray'
                          } font-inter font-600`}
                        >
                          {status}
                        </span>
                      </div>
                    </button>
                    <button
                      onClick={(e) => handleDeleteSession(e, session.session_id)}
                      disabled={deletingId === session.session_id}
                      title="Delete session"
                      aria-label="Delete session"
                      className={`flex-shrink-0 p-1.5 rounded hover:bg-red-100 transition-colors disabled:opacity-50 ${
                        isActive ? 'text-white hover:bg-white/20' : 'text-gray-500 hover:text-red-600'
                      }`}
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="mt-auto border-t border-libra-border px-4 py-3">
        <div className="flex gap-2">
        <button
          onClick={() => loadSessions()}
          className="flex-1 flex items-center justify-center gap-2 px-3 py-2 border border-libra-border rounded-lg hover:bg-libra-light-gray transition-colors text-sm font-inter text-gray-700"
          title="Refresh sessions"
        >
          <RefreshCw className="w-4 h-4" />
          <span className="hidden sm:inline">Refresh</span>
        </button>
        </div>
      </div>
    </div>
  );
}
