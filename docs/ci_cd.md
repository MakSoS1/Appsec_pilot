# CI/CD

The CLI supports CI-friendly exit codes:

- `0`: scan completed, no blocking findings.
- `1`: blocking findings found.
- `2`: scan failed.
- `3`: policy violation.
- `4`: invalid configuration.
- `5`: target unavailable.

Example:

```bash
appsec scan --api-url http://localhost:8080 --target . --scope appsec.scope.yaml --profile safe-active --wait --fail-on critical
```
