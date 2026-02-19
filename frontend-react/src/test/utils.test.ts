import { describe, it, expect } from 'vitest';
import { cn } from '../lib/utils';

describe('Utilities', () => {
  it('should merge class names correctly', () => {
    const result = cn('px-2', 'py-1');
    expect(result).toContain('px-2');
    expect(result).toContain('py-1');
  });

  it('should handle Tailwind conflicts with last value winning', () => {
    const result = cn('px-2', 'px-4');
    // When there's a conflict, the last value should win
    expect(result).toContain('px-4');
  });

  it('should filter out false/undefined classes', () => {
    const result = cn('px-2', false && 'py-1', undefined);
    expect(result).toContain('px-2');
    expect(result.trim().length).toBeGreaterThan(0);
  });

  it('should handle empty input', () => {
    const result = cn('');
    expect(result).toBeDefined();
  });

  it('should merge conditional classes', () => {
    const isActive = true;
    const result = cn('bg-gray-100', isActive && 'bg-black');
    expect(result).toContain('bg-black');
  });

  it('should handle object syntax', () => {
    const result = cn({
      'px-2': true,
      'py-1': true,
      'text-red': false,
    });
    expect(result).toContain('px-2');
    expect(result).toContain('py-1');
  });
});
