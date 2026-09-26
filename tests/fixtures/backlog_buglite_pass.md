## Refining

- **Crash on save** `[bug]` · **S**
  - Root cause: `app/save.py:41` writes before the lock is held.
  - Fix plan: (1) take the lock first, (2) add the assert.
  - Regression test: `tests/test_save.py::test_lock_before_write`.
  - No constraint violations.
  - Estimate: XS
