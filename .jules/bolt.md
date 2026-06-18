## 2025-05-14 - [Regex and Single-Pass Optimization]
**Learning:** Manual character checking in loops (e.g., `all(c in hexdigits for c in s)`) and multi-pass list processing (e.g., finding indices then slicing) are common bottlenecks in Python. Pre-compiled regex and single-pass iteration significantly improve performance.
**Action:** Use pre-compiled regex for string validation and prefer single-pass state machines for parsing flat file structures.
