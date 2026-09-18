# Formal Run Checklist

1. Freeze the benchmark version, visible contracts, tool interface, environment identifiers, eligible task set, limits, and clock sources.
2. Register the participant-system version, parent version, model identifiers, system boundary, tool privileges, configuration digest, and intervention policy.
3. Declare the run class and track.
4. Confirm that gold values, reference answers, scorer logic, and equivalent leaked signals are unavailable to the participant system and its developers for a clean track.
5. Reset the environment and bind task identifiers and seeds where applicable.
6. Execute without task-specific human input. Record infrastructure-only intervention and apply the preregistered stop policy.
7. Capture ordered external events, logical action identifiers, tool responses, state-confirmation attempts, terminal outputs, and explicit handoffs.
8. Freeze execution files and create `receipt.json` before the isolated evaluator loads hidden material.
9. Score only frozen evidence. Record evaluator version, exclusions, missing labels, denominators, and scorer-recovery events.
10. Retain the audit package and complete version history. Never replace first-pass evidence with scoped recovery or per-task best results.
