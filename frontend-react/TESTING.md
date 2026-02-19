# React Frontend Testing

See [../docs/TESTING.md](../docs/TESTING.md) for the full testing guide.

## Quick commands

```bash
npm test              # Run Vitest (watch mode)
npm test -- --run     # Run once
npm run build         # Verify build
```

## Test structure

- `src/test/types.test.ts` — Type definitions
- `src/test/api.test.ts` — API config
- `src/test/utils.test.ts` — Utilities
- `src/test/components.test.tsx` — NewSession component
- `src/test/integration.test.ts` — Session flow
