import { useState, useEffect } from 'react';
import { Download, ChevronDown, ChevronUp, Copy, Check } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { fetchReport } from '../lib/api';
import { downloadMarkdown } from '../utils/format';
import { ErrorMessage } from './ErrorMessage';

interface FinalReportProps {
  sessionId: string;
  reportPath: string | null;
}

export function FinalReport({ sessionId, reportPath }: FinalReportProps) {
  const [report, setReport] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showSource, setShowSource] = useState(false);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    const loadReport = async () => {
      if (!reportPath) {
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        const content = await fetchReport(sessionId);
        setReport(content);
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Could not load report file.';
        setError(errorMessage);
      } finally {
        setLoading(false);
      }
    };

    loadReport();
  }, [sessionId, reportPath]);

  if (loading) {
    return (
      <div className="bg-libra-light-gray rounded-lg p-6 text-center">
        <p className="text-gray-600 font-inter">Loading report...</p>
      </div>
    );
  }

  if (error && !report) {
    return <ErrorMessage title="Report Error" message={error} />;
  }

  if (!reportPath || !report) {
    return null;
  }

  const handleDownload = () => {
    downloadMarkdown(report, `research_report_${sessionId.substring(0, 8)}.md`);
  };

  const handleCopy = async () => {
    if (!report) return;
    try {
      await navigator.clipboard.writeText(report);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      const ta = document.createElement('textarea');
      ta.value = report;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand('copy');
      document.body.removeChild(ta);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="space-y-6">
      {/* Report header + Download + Copy */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="md:col-span-2 flex items-center gap-2 px-4 py-3 bg-green-50 border border-green-300 rounded-lg">
          <span className="text-xl">✅</span>
          <span className="text-sm font-inter font-600 text-green-700">Report ready for download</span>
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleCopy}
            className="flex-1 px-4 py-3 bg-libra-black text-white rounded-lg font-manrope font-600 text-sm hover:bg-libra-dark-gray transition-colors flex items-center justify-center gap-2"
          >
            {copied ? (
              <>
                <Check className="w-4 h-4" />
                Copied!
              </>
            ) : (
              <>
                <Copy className="w-4 h-4" />
                Copy MD
              </>
            )}
          </button>
          <button
            onClick={handleDownload}
            className="flex-1 px-4 py-3 bg-libra-black text-white rounded-lg font-manrope font-600 text-sm hover:bg-libra-dark-gray transition-colors flex items-center justify-center gap-2"
          >
            <Download className="w-4 h-4" />
            Download MD
          </button>
        </div>
      </div>

      {/* Preview Markdown Source */}
      <div className="border border-libra-border rounded-lg overflow-hidden">
        <button
          onClick={() => setShowSource(!showSource)}
          className="w-full px-4 py-3 bg-libra-light-gray hover:bg-gray-300 transition-colors flex items-center justify-between"
        >
          <span className="font-manrope font-600 text-sm text-libra-black">👁 Preview Markdown Source</span>
          {showSource ? (
            <ChevronUp className="w-5 h-5 text-gray-700" />
          ) : (
            <ChevronDown className="w-5 h-5 text-gray-700" />
          )}
        </button>

        {showSource && (
          <div className="px-4 py-4 bg-white border-t border-libra-border">
            <p className="text-xs text-gray-600 font-inter mb-3">Raw markdown code that will be downloaded:</p>
            <pre className="bg-libra-light-gray p-4 rounded-lg overflow-x-auto overflow-y-auto text-xs font-mono text-gray-800 leading-relaxed max-h-96">
              {report}
            </pre>
            <p className="text-xs text-gray-600 font-inter mt-3">💡 Copy this code or download the file above</p>
          </div>
        )}
      </div>

      {/* Rendered Report */}
      <div className="prose prose-sm max-w-none bg-white border border-libra-border rounded-lg p-6">
        {error ? (
          <ErrorMessage message={error} />
        ) : (
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              h1: ({ ...props }) => <h1 className="text-2xl font-manrope font-700 mb-4 mt-6 first:mt-0" {...props} />,
              h2: ({ ...props }) => <h2 className="text-xl font-manrope font-700 mb-3 mt-5" {...props} />,
              h3: ({ ...props }) => <h3 className="text-lg font-manrope font-600 mb-2 mt-4" {...props} />,
              h4: ({ ...props }) => <h4 className="text-base font-manrope font-600 mb-2 mt-3" {...props} />,
              p: ({ ...props }) => <p className="text-sm leading-relaxed mb-3 text-gray-700" {...props} />,
              ul: ({ ...props }) => <ul className="list-disc list-inside space-y-2 mb-3" {...props} />,
              ol: ({ ...props }) => <ol className="list-decimal list-inside space-y-2 mb-3" {...props} />,
              li: ({ ...props }) => <li className="text-sm text-gray-700" {...props} />,
              strong: ({ ...props }) => <strong className="font-semibold text-libra-black" {...props} />,
              em: ({ ...props }) => <em className="italic" {...props} />,
              hr: ({ ...props }) => <hr className="my-4 border-libra-border" {...props} />,
              a: ({ href, ...props }) => (
                <a
                  href={href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-libra-black underline hover:no-underline"
                  {...props}
                />
              ),
              code: ({ className, ...props }) => {
                const isBlock = className?.includes('language-');
                return isBlock ? (
                  <code className="block bg-libra-light-gray p-3 rounded text-xs font-mono overflow-x-auto mb-3 whitespace-pre-wrap" {...props} />
                ) : (
                  <code className="bg-libra-light-gray px-1.5 py-0.5 rounded text-xs font-mono" {...props} />
                );
              },
              pre: ({ ...props }) => <pre className="mb-3" {...props} />,
              blockquote: ({ ...props }) => (
                <blockquote className="border-l-4 border-libra-border pl-4 italic my-3 text-gray-700" {...props} />
              ),
              table: ({ ...props }) => (
                <div className="overflow-x-auto my-4">
                  <table className="min-w-full border border-libra-border rounded-lg" {...props} />
                </div>
              ),
              thead: ({ ...props }) => <thead className="bg-libra-light-gray" {...props} />,
              tbody: ({ ...props }) => <tbody {...props} />,
              tr: ({ ...props }) => <tr className="border-b border-libra-border" {...props} />,
              th: ({ ...props }) => <th className="px-4 py-2 text-left text-sm font-manrope font-600" {...props} />,
              td: ({ ...props }) => <td className="px-4 py-2 text-sm text-gray-700" {...props} />,
            }}
          >
            {report}
          </ReactMarkdown>
        )}
      </div>
    </div>
  );
}
