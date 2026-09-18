from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from .io import read_json, read_jsonl, sum_usage


def _rate(numerator: int, denominator: int) -> dict[str, int | float | None]:
    return {
        "numerator": numerator,
        "denominator": denominator,
        "value": (numerator / denominator) if denominator else None,
    }


def compute_public_metrics(bundle: Path) -> dict[str, Any]:
    run = read_json(bundle / "run_manifest.json")
    version = read_json(bundle / "version_manifest.json")
    terminals = read_jsonl(bundle / "terminal_outputs.jsonl")
    events = read_jsonl(bundle / "events.jsonl")
    evaluation_path = bundle / "evaluation_records.jsonl"
    evaluations = read_jsonl(evaluation_path) if evaluation_path.is_file() else []

    eligible = list(run["eligible_task_ids"])
    terminal_counts = Counter(item["terminal_type"] for item in terminals)
    completion = _rate(terminal_counts.get("complete", 0), len(eligible))

    label_counts = Counter(item["official_label"] for item in evaluations)
    known_denominator = label_counts.get("correct", 0) + label_counts.get("incorrect", 0)
    official_correctness = _rate(label_counts.get("correct", 0), known_denominator)

    mutation_attempts: Counter[str] = Counter()
    mutation_tasks: set[str] = set()
    for event in events:
        if event.get("event_type") in {"mutation_attempted", "mutation_acknowledged"}:
            mutation_tasks.add(event["task_id"])
        if event.get("event_type") == "mutation_attempted" and event.get("logical_action_id"):
            mutation_attempts[event["logical_action_id"]] += 1
    replayed_actions = sum(1 for count in mutation_attempts.values() if count > 1)
    replay_attempts = sum(max(0, count - 1) for count in mutation_attempts.values())

    confirmation_counts = Counter(
        item["state_confirmation_status"] for item in terminals if item["task_id"] in mutation_tasks
    )
    partial_mutations = sum(1 for item in terminals if item.get("partial_mutation") is True)

    missing_labels = len(eligible) - len({item["task_id"] for item in evaluations})
    usage = sum_usage(events)
    output: dict[str, Any] = {
        "protocol_version": run["protocol_version"],
        "run_id": run["run_id"],
        "participant_id": version["participant_id"],
        "system_id": version["system_id"],
        "version_id": version["version_id"],
        "parent_version_id": version.get("parent_version_id"),
        "benchmark_version": run["benchmark_version"],
        "run_class": run["run_class"],
        "track": run["track"],
        "eligible_tasks": len(eligible),
        "completion": completion,
        "official_correctness": official_correctness,
        "official_label_counts": {
            "correct": label_counts.get("correct", 0),
            "incorrect": label_counts.get("incorrect", 0),
            "unknown": label_counts.get("unknown", 0),
            "excluded": label_counts.get("excluded", 0),
            "contract_disputed": label_counts.get("contract_disputed", 0),
            "not_evaluated": max(0, missing_labels),
        },
        "terminal_counts": {name: terminal_counts.get(name, 0) for name in ("complete", "hold", "deny", "limit", "error", "handoff")},
        "write_evidence": {
            "tasks_with_mutation": len(mutation_tasks),
            "confirmation_status_counts": {
                name: confirmation_counts.get(name, 0)
                for name in ("verified", "contradicted", "unavailable", "unknown", "not_applicable")
            },
            "replayed_logical_actions": replayed_actions,
            "additional_mutation_attempts": replay_attempts,
            "partial_mutation_tasks": partial_mutations,
        },
        "usage": usage,
    }

    if run["run_class"] == "first_pass":
        output["first_pass_completion"] = completion
        output["first_pass_official_correctness"] = official_correctness
    elif run["run_class"] == "full_rerun":
        output["later_full_run_completion"] = completion
        output["later_full_run_official_correctness"] = official_correctness
    return output
