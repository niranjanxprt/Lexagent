import { useState, useEffect } from 'react';
import { Menu } from 'lucide-react';
import { Sidebar } from './components/Sidebar';
import { NewSession } from './components/NewSession';
import { SessionView } from './components/SessionView';
import type { APIKeys } from './types';
import { useLocalStorage } from './hooks/useLocalStorage';
import './App.css';

const LAST_SESSION_KEY = 'lastSessionId';

function migrateLastSessionId(): void {
  const raw = localStorage.getItem(LAST_SESSION_KEY);
  if (raw == null || raw === '') return;
  const trimmed = raw.trim();
  if (trimmed.startsWith('"') || trimmed.startsWith('[') || trimmed.startsWith('{')) return;
  try {
    JSON.parse(raw);
    return;
  } catch {
    /* not valid JSON — was stored as raw string */
  }
  localStorage.setItem(LAST_SESSION_KEY, JSON.stringify(raw));
}
migrateLastSessionId();

export function App() {
  const [apiKeys, setApiKeys] = useState<APIKeys>({});
  const [currentSessionId, setCurrentSessionId] = useLocalStorage<string | null>(LAST_SESSION_KEY, null);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const handleSessionCreated = (sessionId: string) => {
    setCurrentSessionId(sessionId);
  };

  const handleSessionDeleted = () => {
    setCurrentSessionId(null);
  };

  const handleSessionSelect = (sessionId: string | null) => {
    setCurrentSessionId(sessionId);
    setSidebarOpen(false);
  };

  useEffect(() => {
    if (sidebarOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => { document.body.style.overflow = ''; };
  }, [sidebarOpen]);

  return (
    <div className="flex h-screen bg-white overflow-hidden">
      {/* Mobile menu button */}
      <button
        onClick={() => setSidebarOpen(true)}
        className="md:hidden fixed top-4 left-4 z-30 p-2.5 rounded-lg bg-white border border-libra-border shadow-sm hover:bg-libra-light-gray transition-colors touch-manipulation"
        aria-label="Open menu"
      >
        <Menu className="w-6 h-6 text-libra-black" />
      </button>

      {/* Sidebar overlay (mobile) */}
      {sidebarOpen && (
        <div
          className="md:hidden fixed inset-0 bg-black/30 z-40"
          onClick={() => setSidebarOpen(false)}
          aria-hidden="true"
        />
      )}

      {/* Sidebar */}
      <aside
        className={`
          w-60 bg-white border-r border-libra-border flex flex-col h-full
          fixed md:relative inset-y-0 left-0 z-50
          transform transition-transform duration-200 ease-out
          md:transform-none
          ${sidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
        `}
      >
        <Sidebar
          currentSessionId={currentSessionId}
          onSessionSelect={handleSessionSelect}
          apiKeys={apiKeys}
          onApiKeysChange={setApiKeys}
          onCloseMobile={() => setSidebarOpen(false)}
        />
      </aside>

      <main className="flex-1 overflow-y-auto bg-white min-w-0 pt-14 md:pt-0 pb-safe">
        {currentSessionId ? (
          <SessionView
            sessionId={currentSessionId}
            apiKeys={apiKeys}
            onSessionDeleted={handleSessionDeleted}
          />
        ) : (
          <NewSession apiKeys={apiKeys} onSessionCreated={handleSessionCreated} />
        )}
      </main>
    </div>
  );
}

export default App;
