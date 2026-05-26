# Sandbox Policy

A scan starts only when scope validation succeeds. The scope controls:

- allowed hosts, ports, and schemes;
- denied targets and metadata endpoints;
- allowed HTTP methods;
- request totals, rate, concurrency, and timeout;
- test accounts;
- allowed and blocked check categories;
- approval-required check classes;
- evidence storage and redaction behavior.

Docker lab mode creates isolated services for vulnerable targets. The MVP keeps destructive and persistence-oriented categories blocked regardless of planner output.
