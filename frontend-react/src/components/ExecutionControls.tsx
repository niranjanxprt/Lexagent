import { useState, useEffect } from 'react';
import { Loader2 } from 'lucide-react';
import { executeStep } from '../lib/api';

interface ExecutionControlsProps {
  sessionId: string;
  isActive: boolean;
  onExecutionComplete: () => void;
}

export function ExecutionControls({
  sessionId,
  isActive,
  onExecutionComplete,
}: ExecutionControlsProps) {
  const [loading, setLoading] = useState(false);
  const [autoRun, setAutoRun] = useState(false);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    if (!autoRun || !isActive) {
      return;
    }

    let isMounted = true;
    let timeoutId: NodeJS.Timeout | null = null;

    const runAutoExecution = async () => {
      try {
        if (!isMounted) return;

        setLoading(true);
        await executeStep(sessionId);

        if (!isMounted) return;

        onExecutionComplete();

        // Schedule next execution after 3 second delay
        timeoutId = setTimeout(() => {
          if (isMounted && autoRun && isActive) {
            runAutoExecution();
          }
        }, 3000);
      } catch (err) {
        if (isMounted) {
          setError('Auto-run failed. Stopping auto-execution.');
          setAutoRun(false);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    // Start the auto-run sequence
    runAutoExecution();

    return () => {
      isMounted = false;
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
    };
  }, [autoRun, isActive, sessionId, onExecutionComplete]);

  useEffect(() => {
    if (!isActive) {
      setAutoRun(false);
    }
  }, [isActive]);

  const handleExecuteNext = async () => {
    setLoading(true);
    setError(null);

    try {
      await executeStep(sessionId);
      onExecutionComplete();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to execute step.';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex gap-3">
        <button
          onClick={handleExecuteNext}
          disabled={!isActive || loading}
          className="flex-1 px-6 py-3 bg-libra-black text-white rounded-lg font-manrope font-600 text-sm hover:bg-libra-dark-gray transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          {loading && <Loader2 className="w-4 h-4 animate-spin" />}
          {loading ? 'Executing...' : 'Execute Next Step'}
        </button>
      </div>

      <div className="flex items-center gap-3 px-4 py-3 bg-libra-light-gray rounded-lg">
        <label className="flex items-center gap-3 cursor-pointer flex-1">
          <input
            type="checkbox"
            checked={autoRun}
            onChange={(e) => setAutoRun(e.target.checked)}
            disabled={!isActive}
            className="w-4 h-4 rounded border-libra-border cursor-pointer"
          />
          <span className="text-sm font-inter font-500 text-libra-black">Auto-run all remaining steps</span>
        </label>
      </div>

      {autoRun && isActive && (
        <div className="p-3 bg-blue-50 border border-blue-300 rounded-lg">
          <p className="text-sm text-blue-700 font-inter">🔄 Auto-running research tasks...</p>
        </div>
      )}

      {error && (
        <div className="p-3 bg-red-50 border border-red-300 rounded-lg">
          <p className="text-sm text-red-700 font-inter">{error}</p>
        </div>
      )}
    </div>
  );
}
