PROTOCOL_VERSION = "0.1.0"

FROZEN_EXECUTION_FILES = (
    "version_manifest.json",
    "run_manifest.json",
    "task_contracts.jsonl",
    "tool_contract.json",
    "events.jsonl",
    "terminal_outputs.jsonl",
)

RUN_CLASSES = {
    "first_pass",
    "scoped_recovery",
    "full_rerun",
    "reliability_rerun",
    "assisted_continuation",
    "scorer_recovery",
}

TRACKS = {"clean", "exposed", "assisted"}
TERMINAL_TYPES = {"complete", "hold", "deny", "limit", "error", "handoff"}
OFFICIAL_LABELS = {"correct", "incorrect", "unknown", "excluded", "contract_disputed"}
CONFIRMATION_STATUSES = {"verified", "contradicted", "unavailable", "unknown", "not_applicable"}

EVENT_TYPES = {
    "observation_available",
    "model_call",
    "tool_request",
    "tool_response",
    "mutation_attempted",
    "mutation_acknowledged",
    "confirmation_attempted",
    "confirmation_observed",
    "terminal_proposed",
    "task_stopped",
    "handoff_emitted",
    "infrastructure_event",
}

ACTOR_TYPES = {
    "participant_system",
    "environment",
    "infrastructure_operator",
    "human_after_handoff",
}
