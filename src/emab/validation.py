from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from .constants import (
    ACTOR_TYPES,
    CONFIRMATION_STATUSES,
    EVENT_TYPES,
    FROZEN_EXECUTION_FILES,
    OFFICIAL_LABELS,
    PROTOCOL_VERSION,
    RUN_CLASSES,
    TERMINAL_TYPES,
    TRACKS,
)
from .io import read_json, read_jsonl
from .receipt import receipt_file_digest, verify_receipt


@dataclass(frozen=True)
class ValidationIssue:
    severity: str
    code: str
    location: str
    message: str

    def render(self) -> str:
        return f"{self.severity.upper()} {self.code} {self.location}: {self.message}"


def _issue(issues: list[ValidationIssue], severity: str, code: str, location: str, message: str) -> None:
    issues.append(ValidationIssue(severity, code, location, message))


def _required(obj: dict[str, Any], fields: Iterable[str], location: str, issues: list[ValidationIssue]) -> None:
    for field in fields:
        if field not in obj:
            _issue(issues, "error", "missing_field", location, f"required field {field!r} is missing")


def _protocol(obj: dict[str, Any], location: str, issues: list[ValidationIssue]) -> None:
    if obj.get("protocol_version") != PROTOCOL_VERSION:
        _issue(issues, "error", "protocol_version", location, f"protocol_version must be {PROTOCOL_VERSION}")


def _load_bundle(bundle: Path, issues: list[ValidationIssue]) -> dict[str, Any]:
    loaded: dict[str, Any] = {}
    for relative in FROZEN_EXECUTION_FILES:
        path = bundle / relative
        if not path.is_file():
            _issue(issues, "error", "missing_file", relative, "required execution file is missing")
            continue
        try:
            loaded[relative] = read_jsonl(path) if relative.endswith(".jsonl") else read_json(path)
        except Exception as exc:
            _issue(issues, "error", "invalid_json", relative, str(exc))
    evaluation_path = bundle / "evaluation_records.jsonl"
    if evaluation_path.is_file():
        try:
            loaded["evaluation_records.jsonl"] = read_jsonl(evaluation_path)
        except Exception as exc:
            _issue(issues, "error", "invalid_json", "evaluation_records.jsonl", str(exc))
    return loaded


def validate_bundle(bundle: Path, verify_frozen_receipt: bool = True) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    if not bundle.is_dir():
        return [ValidationIssue("error", "not_directory", str(bundle), "bundle path is not a directory")]
    data = _load_bundle(bundle, issues)
    if any(issue.severity == "error" and issue.code in {"missing_file", "invalid_json"} for issue in issues):
        return issues

    version = data["version_manifest.json"]
    run = data["run_manifest.json"]
    contracts = data["task_contracts.jsonl"]
    tool_contract = data["tool_contract.json"]
    events = data["events.jsonl"]
    terminals = data["terminal_outputs.jsonl"]

    for location, obj in (("version_manifest.json", version), ("run_manifest.json", run), ("tool_contract.json", tool_contract)):
        _protocol(obj, location, issues)
    for index, obj in enumerate(contracts, start=1):
        _protocol(obj, f"task_contracts.jsonl:{index}", issues)
    for index, obj in enumerate(events, start=1):
        _protocol(obj, f"events.jsonl:{index}", issues)
    for index, obj in enumerate(terminals, start=1):
        _protocol(obj, f"terminal_outputs.jsonl:{index}", issues)

    _required(version, ["participant_id", "system_id", "version_id", "parent_version_id", "models", "system_boundary", "configuration_digest", "change_declaration", "created_at"], "version_manifest.json", issues)
    _required(run, ["run_id", "version_id", "run_class", "track", "benchmark_version", "environment", "eligible_task_ids", "started_at", "autonomy_declaration", "limits"], "run_manifest.json", issues)
    _required(tool_contract, ["contract_id", "operations", "pagination", "error_semantics", "confirmation_capabilities"], "tool_contract.json", issues)

    if run.get("version_id") != version.get("version_id"):
        _issue(issues, "error", "version_mismatch", "run_manifest.json", "version_id does not match version_manifest.json")
    if run.get("run_class") not in RUN_CLASSES:
        _issue(issues, "error", "run_class", "run_manifest.json", "unsupported run_class")
    if run.get("track") not in TRACKS:
        _issue(issues, "error", "track", "run_manifest.json", "unsupported track")
    autonomy = run.get("autonomy_declaration")
    if not isinstance(autonomy, dict) or autonomy.get("task_specific_human_input_allowed") is not False:
        _issue(issues, "error", "autonomy", "run_manifest.json", "formal autonomous runs must declare task_specific_human_input_allowed=false")

    eligible_value = run.get("eligible_task_ids")
    if not isinstance(eligible_value, list) or not eligible_value or not all(isinstance(item, str) and item for item in eligible_value):
        _issue(issues, "error", "eligible_tasks", "run_manifest.json", "eligible_task_ids must be a non-empty string array")
        eligible: set[str] = set()
    else:
        eligible = set(eligible_value)
        if len(eligible) != len(eligible_value):
            _issue(issues, "error", "duplicate_task", "run_manifest.json", "eligible_task_ids must be unique")

    contract_ids: list[str] = []
    for index, contract in enumerate(contracts, start=1):
        location = f"task_contracts.jsonl:{index}"
        _required(contract, ["contract_id", "task_id", "goal", "available_information", "allowed_interaction", "terminal_form", "completion_semantics", "prohibited_actions"], location, issues)
        task_id = contract.get("task_id")
        if isinstance(task_id, str):
            contract_ids.append(task_id)
            if eligible and task_id not in eligible:
                _issue(issues, "error", "unknown_task", location, "task_id is not eligible for this run")
    if Counter(contract_ids) != Counter(eligible_value if isinstance(eligible_value, list) else []):
        _issue(issues, "error", "contract_coverage", "task_contracts.jsonl", "task contracts must cover each eligible task exactly once")

    run_id = run.get("run_id")
    last_index: dict[str, int] = defaultdict(lambda: -1)
    handoff_seen: set[str] = set()
    event_counts: Counter[str] = Counter()
    for index, event in enumerate(events, start=1):
        location = f"events.jsonl:{index}"
        _required(event, ["run_id", "task_id", "event_index", "timestamp", "actor_type", "event_type"], location, issues)
        if event.get("run_id") != run_id:
            _issue(issues, "error", "run_id", location, "run_id does not match run_manifest.json")
        task_id = event.get("task_id")
        if not isinstance(task_id, str) or task_id not in eligible:
            _issue(issues, "error", "unknown_task", location, "task_id is not eligible for this run")
            continue
        event_index = event.get("event_index")
        if not isinstance(event_index, int) or isinstance(event_index, bool) or event_index < 0:
            _issue(issues, "error", "event_index", location, "event_index must be a non-negative integer")
        elif event_index <= last_index[task_id]:
            _issue(issues, "error", "event_order", location, "event_index must increase strictly within the task")
        else:
            last_index[task_id] = event_index
        actor = event.get("actor_type")
        event_type = event.get("event_type")
        if actor not in ACTOR_TYPES:
            _issue(issues, "error", "actor_type", location, "unsupported actor_type")
        if event_type not in EVENT_TYPES:
            _issue(issues, "error", "event_type", location, "unsupported event_type")
        if event_type == "handoff_emitted":
            handoff_seen.add(task_id)
        if actor == "human_after_handoff":
            if task_id not in handoff_seen:
                _issue(issues, "error", "human_before_handoff", location, "human_after_handoff event occurred before a handoff")
            if run.get("track") != "assisted":
                _issue(issues, "error", "track_mismatch", location, "human action requires the assisted track")
        if event_type in {"mutation_attempted", "mutation_acknowledged"} and not event.get("logical_action_id"):
            _issue(issues, "error", "logical_action_id", location, "mutation events require logical_action_id")
        event_counts[task_id] += 1

    limits = run.get("limits") if isinstance(run.get("limits"), dict) else {}
    max_events = limits.get("max_events_per_task")
    if isinstance(max_events, int) and not isinstance(max_events, bool) and max_events > 0:
        for task_id, count in event_counts.items():
            if count > max_events:
                _issue(issues, "error", "event_limit", task_id, f"event count {count} exceeds declared maximum {max_events}")

    terminal_ids: list[str] = []
    for index, terminal in enumerate(terminals, start=1):
        location = f"terminal_outputs.jsonl:{index}"
        _required(terminal, ["run_id", "task_id", "terminal_type", "output", "open_obligations", "state_confirmation_status", "partial_mutation", "timestamp"], location, issues)
        if terminal.get("run_id") != run_id:
            _issue(issues, "error", "run_id", location, "run_id does not match run_manifest.json")
        task_id = terminal.get("task_id")
        if isinstance(task_id, str):
            terminal_ids.append(task_id)
            if task_id not in eligible:
                _issue(issues, "error", "unknown_task", location, "task_id is not eligible for this run")
        if terminal.get("terminal_type") not in TERMINAL_TYPES:
            _issue(issues, "error", "terminal_type", location, "unsupported terminal_type")
        if terminal.get("state_confirmation_status") not in CONFIRMATION_STATUSES:
            _issue(issues, "error", "confirmation_status", location, "unsupported state_confirmation_status")
        obligations = terminal.get("open_obligations")
        if not isinstance(obligations, list):
            _issue(issues, "error", "open_obligations", location, "open_obligations must be an array")
        elif terminal.get("terminal_type") == "complete" and obligations:
            _issue(issues, "error", "incomplete_claim", location, "complete terminal cannot retain open obligations")
    if Counter(terminal_ids) != Counter(eligible_value if isinstance(eligible_value, list) else []):
        _issue(issues, "error", "terminal_coverage", "terminal_outputs.jsonl", "terminal outputs must cover each eligible task exactly once")

    receipt_path = bundle / "receipt.json"
    if verify_frozen_receipt and receipt_path.is_file():
        for message in verify_receipt(bundle, receipt_path):
            _issue(issues, "error", "receipt", "receipt.json", message)

    evaluations = data.get("evaluation_records.jsonl", [])
    if evaluations:
        if not receipt_path.is_file():
            _issue(issues, "error", "evaluation_without_receipt", "evaluation_records.jsonl", "evaluation records require a frozen execution receipt")
        expected_receipt_digest = receipt_file_digest(bundle)
        seen_evaluation_tasks: set[str] = set()
        for index, record in enumerate(evaluations, start=1):
            location = f"evaluation_records.jsonl:{index}"
            _protocol(record, location, issues)
            _required(record, ["run_id", "task_id", "execution_receipt_sha256", "evaluator_id", "evaluator_version", "official_label", "evaluated_at"], location, issues)
            if record.get("run_id") != run_id:
                _issue(issues, "error", "run_id", location, "run_id does not match run_manifest.json")
            task_id = record.get("task_id")
            if not isinstance(task_id, str) or task_id not in eligible:
                _issue(issues, "error", "unknown_task", location, "task_id is not eligible for this run")
            elif task_id in seen_evaluation_tasks:
                _issue(issues, "error", "duplicate_evaluation", location, "task has more than one active evaluation record")
            else:
                seen_evaluation_tasks.add(task_id)
            if record.get("official_label") not in OFFICIAL_LABELS:
                _issue(issues, "error", "official_label", location, "unsupported official_label")
            if expected_receipt_digest and record.get("execution_receipt_sha256") != expected_receipt_digest:
                _issue(issues, "error", "evaluation_receipt", location, "evaluation does not reference this execution receipt")

    return issues


def errors_only(issues: Iterable[ValidationIssue]) -> list[ValidationIssue]:
    return [issue for issue in issues if issue.severity == "error"]
