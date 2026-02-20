import { useState } from 'react';
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

  const handleSessionCreated = (sessionId: string) => {
    setCurrentSessionId(sessionId);
  };

  const handleSessionDeleted = () => {
    setCurrentSessionId(null);
  };

  const handleSessionSelect = (sessionId: string | null) => {
    setCurrentSessionId(sessionId);
  };

  return (
    <div className="flex h-screen bg-white">
      <Sidebar
        currentSessionId={currentSessionId}
        onSessionSelect={handleSessionSelect}
        apiKeys={apiKeys}
        onApiKeysChange={setApiKeys}
      />

      <main className="flex-1 overflow-y-auto bg-white">
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
