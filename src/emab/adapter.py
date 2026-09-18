from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Protocol, Sequence


@dataclass(frozen=True)
class AdapterContext:
    """Participant-visible context supplied at formal task start."""

    run_id: str
    task_id: str
    version_id: str
    task_contract: Mapping[str, Any]
    tool_contract: Mapping[str, Any]
    limits: Mapping[str, Any]


@dataclass(frozen=True)
class Observation:
    """An external observation delivered to the participant system."""

    event_index: int
    kind: str
    payload: Mapping[str, Any]
    open_obligations: Sequence[str] = field(default_factory=tuple)


@dataclass(frozen=True)
class ToolAction:
    """A participant-system request to a declared public tool operation."""

    tool: str
    operation: str
    arguments: Mapping[str, Any]
    logical_action_id: str | None = None


@dataclass(frozen=True)
class TerminalProposal:
    """A participant-system terminal proposal or explicit handoff."""

    terminal_type: str
    output: Any
    open_obligations: Sequence[str] = field(default_factory=tuple)


ParticipantDecision = ToolAction | TerminalProposal


class ParticipantAdapter(Protocol):
    """Neutral interface; implementations retain all substantive decision logic."""

    def start_task(self, context: AdapterContext) -> None:
        """Bind the frozen visible contracts and declared run context."""

    def decide(self, observation: Observation) -> ParticipantDecision:
        """Return the next tool action or terminal proposal autonomously."""

    def close_task(self) -> None:
        """Release task-scoped resources without changing the frozen record."""
