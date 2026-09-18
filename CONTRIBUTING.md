# Contributing

Contributions must preserve architecture neutrality and the sealed-evaluation boundary.

Before opening a pull request:

1. Run `python -m unittest discover -s tests -v`.
2. Run `python scripts/release_boundary_check.py`.
3. Confirm that no gold value, hidden case, scorer implementation, official solution path, substantive example agent, or comparator implementation detail is present.
4. Explain whether a schema or validator change alters a scored obligation.
5. If an obligation changes, propose a new major protocol version rather than silently changing earlier results.

Examples may demonstrate serialization, hashing, a harmless mock operation, or invalid input. They must not encode a strategy for solving benchmark tasks.
