import { useState } from 'react';
import { Loader2 } from 'lucide-react';
import { startSession } from '../lib/api';
import type { APIKeys } from '../types';
import { ErrorMessage } from './ErrorMessage';

interface NewSessionProps {
  apiKeys: APIKeys;
  onSessionCreated: (sessionId: string) => void;
}

export function NewSession({ apiKeys, onSessionCreated }: NewSessionProps) {
  const [goal, setGoal] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!goal.trim()) {
      setError('Please enter a research goal.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const { session_id } = await startSession(goal, apiKeys);
      setGoal('');
      onSessionCreated(session_id);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to start session. Please try again.';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto px-4 sm:px-6 py-8 sm:py-12">
      <div className="mb-8">
        <h2 className="text-2xl sm:text-3xl font-manrope font-700 text-libra-black mb-2">
          Start a New Research Session
        </h2>
        <p className="text-gray-600 font-inter">
          Enter your legal research goal and our AI agent will create a comprehensive research plan.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label htmlFor="goal" className="block text-sm font-manrope font-600 text-libra-black mb-3">
            Research Goal
          </label>
          <textarea
            id="goal"
            value={goal}
            onChange={(e) => setGoal(e.target.value)}
            placeholder="e.g., Analyze the legal implications of AI-generated evidence in UK criminal proceedings"
            className="w-full px-4 py-3 border border-libra-border rounded-lg font-inter text-sm focus:outline-none focus:ring-2 focus:ring-libra-black focus:border-transparent resize-none"
            rows={6}
            disabled={loading}
          />
          <p className="text-xs text-gray-600 mt-2">Be specific about your research question for better results.</p>
        </div>

        {error && <ErrorMessage message={error} />}

        <button
          type="submit"
          disabled={loading}
          className="w-full px-6 py-3 min-h-[48px] bg-libra-black text-white rounded-lg font-manrope font-600 text-sm hover:bg-libra-dark-gray transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 touch-manipulation"
        >
          {loading && <Loader2 className="w-4 h-4 animate-spin" />}
          {loading ? 'Generating Research Plan...' : 'Generate Research Plan'}
        </button>
      </form>
    </div>
  );
}
