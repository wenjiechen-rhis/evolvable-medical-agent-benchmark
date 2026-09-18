# Execution Bundle Specification

A bundle directory contains the participant-visible execution record. File names are fixed so independent tools can validate the package.

## Required before execution freeze

- `version_manifest.json`: declared participant-system version and lineage.
- `run_manifest.json`: run class, track, environment identifiers, eligible tasks, limits, and autonomy declaration.
- `task_contracts.jsonl`: one visible goal and completion-semantics record per eligible task, or a declared public contract reference for a sequestered instance.
- `tool_contract.json`: visible operations, effects, failure behavior, and confirmation capabilities.
- `events.jsonl`: ordered external event records.
- `terminal_outputs.jsonl`: one terminal record per eligible task.

## Generated at freeze

- `receipt.json`: SHA-256 for each frozen execution file plus a canonical bundle digest.

The receipt excludes itself and all later evaluation records.

## Added after isolated evaluation

- `evaluation_records.jsonl`: evaluator-issued labels and scorer metadata linked to the SHA-256 digest of `receipt.json`.

Evaluation records do not change the execution receipt. A scorer recovery appends or replaces the evaluation-record set under a new evaluator version while retaining the old record in the result registry.

## Event ordering

`event_index` is a non-negative integer and must increase strictly within each task. Every event carries the same `run_id` as the run manifest. Mutations that retry one intended side effect share a `logical_action_id`.

## Terminal records

Each eligible task has exactly one terminal output. Supported terminal types are `complete`, `hold`, `deny`, `limit`, `error`, and `handoff`. A terminal output declares unresolved obligations, whether partial mutation was observed, and the state-confirmation status.

## Sensitive data

Public bundles should use digests or controlled references for sensitive payloads. Do not place credentials, identifiable records, hidden cases, or evaluator secrets in a participant-visible bundle.
