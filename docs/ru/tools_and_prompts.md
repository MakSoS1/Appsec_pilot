# Инструменты, навыки и prompt layer

В агент добавлен слой, который разделяет три вещи:

- **System prompt**: общие правила автономного AppSec validation, scope priority, no destructive behavior, evidence redaction.
- **Skill catalog**: карточки экспертизы, которые выбираются под target: source-aware whitebox, API authz diff, OpenAPI contract, browser checks, sensitive data exposure, lab DAST.
- **Tool registry**: список адаптеров с режимами включения и evidence contract.

## Tool registry

Активные по умолчанию адаптеры:

- `http_probe_adapter`;
- `custom_checks_adapter`;
- `openapi_contract_adapter`;
- `semgrep_adapter`;
- `secret_scan_adapter`;
- `ast_structural_adapter`;
- `report_generator`.

Lab-only / optional:

- `dependency_scan_adapter`;
- `browser_checks_adapter`;
- `zap_baseline_adapter`;
- `nuclei_limited_adapter`;
- `proxy_observer_adapter`.

Каждый adapter обязан возвращать структурированный `ToolResult`: status, output, evidence и error. Это упрощает verifier и отчеты.
