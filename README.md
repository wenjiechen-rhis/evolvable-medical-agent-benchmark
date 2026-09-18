# Evolvable Medical Agent Benchmark Protocol

This repository is a reference-neutral toolkit for evaluating autonomous medical-agent systems across first-pass execution, sealed post-run evaluation, and versioned improvement.

It does not provide an official solution, reference workflow, gold answer set, hidden test case, or scorer implementation. Participants may use any independently designed model, orchestration method, memory system, validator, simulator, or other technology. During a formal task, however, task interpretation, information gathering, tool selection, action execution, retry decisions, and the terminal proposal must be performed by the declared participating AI system without task-specific human correction.

The toolkit implements public protocol mechanics:

- visible task and tool contract formats;
- version and run manifests;
- architecture-neutral event and terminal records;
- autonomous-run and cross-file validation;
- immutable execution receipts;
- aggregation of public metrics from already-issued evaluation records;
- clean, exposed, and assisted track labels;
- first-pass, scoped-recovery, full-rerun, reliability-rerun, and scorer-recovery run classes.

The central rule is Contract Derivability: every scored obligation must be derivable from the participant-visible task and tool contracts. Hidden data may determine the case-specific answer, but hidden evaluator conventions must not create new obligations.

## What stays outside this repository

The following artifacts must remain outside the participant-visible repository:

- gold answers and expected case values;
- scorer logic and scoring-predicate implementations;
- organizer-supplied solution policies or substantive example agents;
- hidden test instances for sealed tracks;
- private obligation-to-contract maps that would expose answer-bearing predicates;
- any comparator controller implementation, design detail, trace, rule, prompt, configuration, or reconstructive mapping.

An isolated evaluator may score a frozen execution bundle and return signed evaluation records. The public toolkit only validates and aggregates those records; it cannot derive official correctness by itself.

## Quick start

Python 3.11 or later is sufficient. The package has no runtime dependencies.

```bash
python -m pip install -e .
emab validate examples/mechanical-conformance
emab freeze examples/mechanical-conformance --output examples/mechanical-conformance/receipt.json
emab verify examples/mechanical-conformance
emab metrics examples/mechanical-conformance --output public-metrics.json
```

The example is a mechanical conformance fixture. It demonstrates the file interface and a harmless mock read operation; it contains no medical task strategy.

## Formal-run lifecycle

1. Register the declared system and version.
2. Freeze the visible contracts, environment identifiers, task set, limits, and run class.
3. Execute tasks autonomously and record ordered external events.
4. Freeze the execution files and generate an immutable receipt.
5. Send the frozen bundle to an isolated evaluator.
6. Attach returned evaluation records without changing the frozen execution.
7. Publish version-specific metrics and retain all earlier runs.

Unlimited improvement is allowed between formal runs. A later version never replaces the first pass, and a scoped recovery never becomes a full-set score.

## Repository map

- `schemas/` public JSON Schema 2020-12 definitions;
- `src/emab/` validator, receipt, verification, and metric tools;
- `docs/` protocol, governance, release, and operator guidance;
- `examples/mechanical-conformance/` non-solution interface fixture;
- `tests/` executable conformance tests;
- `.github/workflows/ci.yml` public continuous integration.

## Citation

The protocol is described in:

Wenjie Chen. *Benchmarking Evolvable Medical Agents Beyond First Pass: An Architecture Neutral Protocol for Autonomous Execution Sealed Evaluation and Versioned Improvement*. SSRN Working Paper, 2026.

Use `CITATION.cff` for machine-readable citation metadata.

## License

The repository code and public specifications are licensed under the MIT License. Benchmark datasets, environment images, model outputs, participant systems, and isolated evaluator materials may have separate terms and are not included here.
