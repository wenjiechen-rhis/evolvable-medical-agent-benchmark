# Participant Adapter Interface

`emab.adapter.ParticipantAdapter` is a typing protocol, not a reference agent. It standardizes only the boundary between the benchmark harness and a participant-controlled system.

At task start the harness supplies:

- stable run, task, and version identifiers;
- the visible task contract;
- the visible tool contract;
- declared task limits.

For each observation the participant adapter returns either:

- a `ToolAction` naming a declared tool operation and arguments; or
- a `TerminalProposal` naming `complete`, `hold`, `deny`, `limit`, `error`, or `handoff`.

The participant implementation owns model calls, planning, memory, validation, orchestration, simulation, retries, and other internal methods. The repository supplies no decision policy. The harness records external events and enforces only visible interface, autonomy, limit, and evidence rules.
