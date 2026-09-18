# Protocol

## Evaluation object

The evaluated object is a declared participant system acting through a declared interface in a frozen environment. The protocol records externally auditable observations, tool requests, tool responses, mutations, confirmations, terminal outputs, handoffs, usage, and integrity metadata. It does not require private chain-of-thought disclosure.

## Contract Derivability

Every obligation enforced by an evaluator must be derivable from the visible task contract and visible tool contract available before execution. A benchmark may conceal cases, patient-specific expected values, and scorer implementation. It may not conceal the rule that makes an action, omission, or answer scoreable.

Before release, an independent reviewer should inspect a private obligation-to-contract map. The participant-visible release may include a signed coverage attestation, but the map itself remains outside the repository when it could expose hidden predicates.

## Autonomy

After a formal task begins, the declared participant system determines what to inspect, which tools to call, what payload to submit, whether to retry, and when to complete or hand off. Human operators may launch the frozen batch, maintain infrastructure without task-content intervention, and stop a run for a documented platform emergency. Patient- or task-specific human correction moves the task to an assisted track or invalidates its autonomous claim.

## Versioned evolution

A participant may submit unlimited versions between formal runs. Each version is named, declared, and evaluated independently. Every version names its parent, changes, evidence used, intended failure classes, and regression scope.

Run classes are not interchangeable:

- `first_pass`: immutable first complete formal attempt;
- `scoped_recovery`: named task slice after a declared change;
- `full_rerun`: complete eligible set under a named later version;
- `reliability_rerun`: unchanged version under controlled stochastic repetition;
- `assisted_continuation`: human action after an explicit handoff;
- `scorer_recovery`: evaluator-only correction over frozen outputs.

A scoped recovery never replaces the first pass. A per-task best-of-version composite is not a realizable system and is prohibited for the primary leaderboard.

## Sealed evaluation

Execution files are frozen before evaluator access. The evaluator loads hidden material in isolation, does not call the participant model, and returns evaluation records linked to the execution receipt. A changed scorer creates a new evaluation record; it does not mutate the execution bundle.

## Primary reporting

Every reported rate includes its numerator, denominator, version, run class, and evidence status. Primary reports keep separate:

- first-pass completion;
- first-pass official correctness over tasks with valid labels;
- later full-run completion for a named version;
- later full-run official correctness for that same version.

Write-task reporting distinguishes acknowledgment, confirmation attempt, state proof, replay, partial mutation, atomicity capability, unresolved obligations, and handoff.
