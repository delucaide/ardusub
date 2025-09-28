# Simplified ArduSub Motor Slew Limiter

This repository contains a distilled example demonstrating how a ramped slew
limiter can be applied to every motor output in all vehicle modes.  A runtime
parameter named `SLEW_LIMIT` controls how aggressively the outputs change.

The implementation is intentionally lightweight so it can be exercised through
unit tests without requiring the full firmware build.

## Running the tests

```bash
pytest
```
