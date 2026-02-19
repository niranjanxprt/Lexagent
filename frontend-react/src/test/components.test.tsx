import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { NewSession } from '../components/NewSession';

// Mock the API
vi.mock('../lib/api', () => ({
  fetchSessions: vi.fn().mockResolvedValue([]),
  fetchAgentState: vi.fn().mockResolvedValue(null),
  startSession: vi.fn().mockResolvedValue({
    session_id: 'test-123',
    state: {
      session_id: 'test-123',
      goal: 'Test goal',
      tasks: [],
      context_notes: [],
      current_step: 0,
      is_active: true,
      mode: 'plan',
      final_report_path: null,
      created_at: new Date().toISOString(),
    },
  }),
  executeStep: vi.fn(),
  deleteSession: vi.fn(),
  fetchReport: vi.fn(),
}));

describe('NewSession Component', () => {
  it('should render the component', () => {
    const onSessionCreated = vi.fn();
    render(<NewSession apiKeys={{}} onSessionCreated={onSessionCreated} />);
    expect(screen.getByRole('button')).toBeInTheDocument();
  });

  it('should have textarea for goal input', () => {
    const onSessionCreated = vi.fn();
    render(<NewSession apiKeys={{}} onSessionCreated={onSessionCreated} />);
    const textarea = screen.getByRole('textbox');
    expect(textarea).toBeInTheDocument();
  });

  it('should display placeholder text', () => {
    const onSessionCreated = vi.fn();
    render(<NewSession apiKeys={{}} onSessionCreated={onSessionCreated} />);
    const textarea = screen.getByRole('textbox') as HTMLTextAreaElement;
    expect(textarea.placeholder).toContain('AI-generated evidence');
  });

  it('should update textarea value when typing', () => {
    const onSessionCreated = vi.fn();
    render(<NewSession apiKeys={{}} onSessionCreated={onSessionCreated} />);
    const textarea = screen.getByRole('textbox') as HTMLTextAreaElement;

    fireEvent.change(textarea, { target: { value: 'Research AI Act compliance' } });
    expect(textarea.value).toBe('Research AI Act compliance');
  });

  it('should have a button to generate plan', () => {
    const onSessionCreated = vi.fn();
    render(<NewSession apiKeys={{}} onSessionCreated={onSessionCreated} />);
    const button = screen.getByRole('button');
    expect(button).toBeInTheDocument();
    expect(button.textContent).toContain('Generate Research Plan');
  });

  it('should show error when submitting empty goal', async () => {
    const onSessionCreated = vi.fn();
    render(<NewSession apiKeys={{}} onSessionCreated={onSessionCreated} />);
    const button = screen.getByRole('button') as HTMLButtonElement;

    // Button should not be disabled initially (only disabled during loading)
    expect(button.disabled).toBe(false);

    // Click button with empty textarea
    fireEvent.click(button);

    // Error message should appear
    await new Promise(resolve => setTimeout(resolve, 100));
    const error = screen.queryByText('Please enter a research goal.');
    expect(error).toBeInTheDocument();
  });

  it('should disable button when loading', async () => {
    const onSessionCreated = vi.fn();
    render(<NewSession apiKeys={{}} onSessionCreated={onSessionCreated} />);
    const button = screen.getByRole('button') as HTMLButtonElement;
    const textarea = screen.getByRole('textbox') as HTMLTextAreaElement;

    fireEvent.change(textarea, { target: { value: 'Research topic' } });
    fireEvent.click(button);

    // Button should be disabled during loading
    expect(button.disabled).toBe(true);
    expect(button.textContent).toContain('Generating Research Plan...');
  });
});
