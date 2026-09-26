## Refining

- **Crash on save** `[hotfix]` · **S**
  - Fix plan: (1) take the lock first, (2) add the assert.
  - Regression test: `tests/test_save.py::test_lock_before_write`.
  - No constraint violations.
  - Estimate: XS
