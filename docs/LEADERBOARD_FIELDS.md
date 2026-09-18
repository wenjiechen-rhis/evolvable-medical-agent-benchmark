# Leaderboard Fields

The primary leaderboard should expose the following fields without collapsing them into one scalar:

- participant and system version;
- clean, exposed, or assisted track;
- run class and eligible-task denominator;
- first-pass completion numerator and denominator;
- first-pass official correctness numerator and known-label denominator;
- named later full-run completion numerator and denominator;
- named later full-run official correctness numerator and known-label denominator;
- write-task confirmation coverage and status distribution;
- replayed logical actions and partial-mutation count;
- terminal-status distribution and handoff count;
- model calls, input tokens, output tokens, elapsed time, and provider or infrastructure failures;
- submitted-version count and parent version;
- evaluator version, missing-label count, contract-disputed count, and evidence status.

Candidate real-world and governance scores appear only after independent adjudication and remain visibly separate from official correctness.
