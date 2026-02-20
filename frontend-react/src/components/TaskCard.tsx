import { useState } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';
import { Task } from '../types';

interface TaskCardProps {
  task: Task;
  taskNumber: number;
}

const statusConfig = {
  pending: { icon: '⬜', color: 'text-gray-400', label: 'Pending' },
  in_progress: { icon: '🔄', color: 'text-blue-600', label: 'In Progress' },
  done: { icon: '✅', color: 'text-black', label: 'Done' },
  failed: { icon: '❌', color: 'text-red-600', label: 'Failed' },
};

export function TaskCard({ task, taskNumber }: TaskCardProps) {
  const [isOpen, setIsOpen] = useState(task.status === 'in_progress');
  const config = statusConfig[task.status as keyof typeof statusConfig] ?? statusConfig.pending;

  return (
    <div className="border border-libra-border rounded-lg overflow-hidden bg-white hover:border-libra-dark-gray transition-colors">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-4 py-3 flex items-center justify-between hover:bg-libra-light-gray transition-colors"
      >
        <div className="flex items-center gap-3 flex-1 text-left">
          <span className="text-xl">{config.icon}</span>
          <div className="flex-1">
            <h3 className="font-manrope font-600 text-libra-black">
              Task {taskNumber}: {task.title}
            </h3>
            <p className="text-sm text-gray-600 mt-1 line-clamp-1">{task.description}</p>
          </div>
        </div>
        <div className="flex items-center gap-2 ml-2">
          <span className="text-xs px-2 py-1 bg-libra-light-gray rounded font-inter font-500">
            {config.label}
          </span>
          {isOpen ? (
            <ChevronUp className="w-5 h-5 text-gray-600" />
          ) : (
            <ChevronDown className="w-5 h-5 text-gray-600" />
          )}
        </div>
      </button>

      {isOpen && (
        <div className="border-t border-libra-border px-4 py-4 space-y-4 bg-white">
          <div>
            <p className="text-sm font-inter font-600 text-libra-dark-gray mb-2">Description</p>
            <p className="text-sm text-gray-700 leading-relaxed">{task.description}</p>
          </div>

          {task.tool_used && (
            <div>
              <p className="text-sm font-inter font-600 text-libra-dark-gray mb-2">Tool Used</p>
              <code className="text-xs bg-libra-light-gray px-2 py-1 rounded font-mono text-gray-700">
                {task.tool_used}
              </code>
            </div>
          )}

          {task.result && (
            <div>
              <p className="text-sm font-inter font-600 text-libra-dark-gray mb-2">Findings</p>
              <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">{task.result}</p>
            </div>
          )}

          {task.reflection && (
            <div>
              <p className="text-sm font-inter font-600 text-libra-dark-gray mb-2">Reflection</p>
              <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">{task.reflection}</p>
            </div>
          )}

          {task.sources && task.sources.length > 0 && (
            <div>
              <p className="text-sm font-inter font-600 text-libra-dark-gray mb-2">Sources</p>
              <ul className="space-y-2">
                {task.sources.map((source, idx) => (
                  <li key={idx}>
                    <a
                      href={source}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-libra-black underline hover:no-underline transition-all break-all"
                    >
                      {source}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
