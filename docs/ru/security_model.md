# Модель безопасности

AppSec Pilot предназначен для авторизованной проверки локальных, staging и CI targets. Главный boundary — scope file.

## Что разрешено

- чтение исходного кода target repo;
- OpenAPI import и endpoint mapping;
- безопасные HTTP probes в allowlist;
- auth-diff, role-diff, schema-diff, response-diff на test accounts;
- Semgrep, secret scan, dependency inventory;
- ZAP baseline и lab DAST только в `full-lab` профиле.

## Что запрещено

- destructive actions;
- persistence, evasion, C2, malware;
- credential theft или вывод секретов целиком;
- public internet scanning вне allowlist;
- cloud metadata probing;
- действия вне request limits.

## Evidence policy

Evidence хранится redacted. Для секретов и токенов сохраняется только маска, путь, тип и confidence. Для HTTP сохраняется краткий redacted body sample, headers и status.
