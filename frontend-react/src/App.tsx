import { useState, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import { NewSession } from './components/NewSession';
import { SessionView } from './components/SessionView';
import type { APIKeys } from './lib/api';
import './App.css';

export function App() {
  const [apiKeys, setApiKeys] = useState<APIKeys>({});
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(() => {
    const saved = localStorage.getItem('lastSessionId');
    return saved;
  });

  useEffect(() => {
    if (currentSessionId) {
      localStorage.setItem('lastSessionId', currentSessionId);
    } else {
      localStorage.removeItem('lastSessionId');
    }
  }, [currentSessionId]);

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
            onRefresh={() => {
              // Force a refresh by toggling the session
              const temp = currentSessionId;
              setCurrentSessionId(null);
              setTimeout(() => setCurrentSessionId(temp), 100);
            }}
          />
        ) : (
          <NewSession apiKeys={apiKeys} onSessionCreated={handleSessionCreated} />
        )}
      </main>
    </div>
  );
}

export default App;
