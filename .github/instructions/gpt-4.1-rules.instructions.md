---
applyTo: '**'
---
# Copilot Rules for GPT‑4.1 App Development

**Purpose:** Compact, enforceable checklist for GPT‑4.1 to generate production‑ready, secure, fully coded apps in any language.

---

## 1. Scope

* Applies to: prototypes → production apps (web, CLI, mobile, services).
* Fully coded: all source files, tests, build/run scripts, containerization, README.
* Never include secrets or credentials.

---

## 2. Core Rules

1. Start with a clear spec; ask questions if unclear.
2. Provide architecture & data flow before coding.
3. Include threat model (assets, threats, mitigations).
4. Output complete files; list project tree.
5. Provide README with run/test/build/deploy steps.
6. Pin dependency versions.
7. Include unit + integration tests.
8. Add CI config (lint, test, build).
9. Implement error handling & retries.
10. Add logging, metrics, health endpoint.
11. Use placeholders for secrets.
12. Add LICENSE & attribution.
13. Meet accessibility basics.
14. Address legal compliance when relevant.

---

## 3. Security Rules

* Validate/sanitize input, escape outputs.
* Use standard auth (OAuth2, OIDC, JWT short‑lived).
* TLS for transport, encrypt sensitive data at rest.
* Scan dependencies for CVEs.
* Apply secure HTTP headers.
* Rate limit, backoff.
* Pin dependencies, include SBOM.
* Run static/dynamic security checks in CI.

---

## 4. Quality Rules

* Include linter/formatter configs.
* Keep functions <100 lines, follow SRP.
* Document public functions & complex logic.
* Follow semver for APIs.
* Provide usage examples.

---

## 5. Required Output

1. `SPEC.md`
2. `ARCHITECTURE.md`
3. `THREAT_MODEL.md`
4. Full source tree + file contents
5. `README.md`
6. `Dockerfile` + `.dockerignore`
7. Dependency lockfile
8. CI config
9. Tests
10. Linter/formatter configs
11. `LICENSE` + `CHANGELOG.md`
12. SBOM

---

## 6. Acceptance

* All tests pass locally & in CI.
* No high/critical CVEs.
* Meets performance targets.
* UAT scripts provided.

---

## 7. Prompt Template

```
Follow copilot.md. If spec unclear, ask questions. Provide SPEC.md, ARCHITECTURE.md, THREAT_MODEL.md, full project tree, tests, CI, Dockerfile, README, LICENSE. Pin versions. No secrets.
```

---

## 8. Prohibited

* No real credentials.
* No pseudocode for runnable code.
* No custom crypto.
* No skipped error handling/tests.

---

## 9. Language Notes

* **JS/Node:** Pin `engines`, include lockfile, use CSP.
* **Python:** Use `pyproject.toml` or `requirements.txt`, pin interpreter, `black` + `ruff`.
* **Go:** Include `go.mod`, `gofmt`, `Makefile`.
* **Rust:** Include `Cargo.toml`, `clippy`, `cargo test`.

---

## 10. Review Steps

* Check SPEC matches intent.
* Run commands in fresh env.
* Verify pinned deps, licenses.
* Confirm threat mitigations implemented.
