# Threat Model

Key risks:

- Agent acts outside the authorized target scope.
- A user attempts to scan public systems.
- The LLM suggests unsafe or destructive actions.
- Evidence captures secrets or tokens.
- A vulnerable lab app is accidentally exposed.
- Prompt injection from source code or web content influences actions.

Controls:

- Required `scope.yaml` for scans.
- Host, port, scheme, method, category, and request-budget validation.
- Default denylist for metadata and broad external targets.
- Tool adapters execute only after policy validation.
- Findings are not confirmed without evidence and verifier decision.
- Evidence redaction and audit logs are enabled by default.
- Public target mode is disabled by configuration.
