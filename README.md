# Coldline Project 5: the agent

This is your Project 5 repository. It starts where Project 4 ended: the complete Coldline
platform, with the API, the worker, the token issuer, the guardrails, the redaction, the audit
trail and the secret store. You build the agent here, in this one repository, from Task 1 to
Task 16. Each Task starts from your own work in the previous one.

The starter adds four things to the Project 4 platform:

- **The agent's packages, pinned:** LangGraph, its local server and client, and the MCP
  library, locked in `uv.lock`.
- **`poe verify`:** your tests and the repository's checks, the same command CI runs.
- **`poe demo`:** empty for now. You fill it as the agent grows.
- **A CI workflow:** `.github/workflows/verify.yml` runs `poe verify` and a secret scan on every
  pull request. Keep it exactly as supplied.

## Start the system

Prerequisites are Python 3.12 and Docker with Compose v2. The supplied bootstrap supports macOS
arm64/x86-64, Windows x86-64, and Linux x86-64/aarch64, and installs pinned uv 0.11.8 under
`.tools/bin`. If your computer cannot run the stack locally, open your repository in GitHub
Codespaces.

On macOS and most Linux distributions the interpreter is `python3`; substitute it wherever these
commands say `python`.

```shell
python infra/scripts/bootstrap.py
./.tools/bin/uv sync --frozen
./.tools/bin/uv run --frozen poe preflight
./.tools/bin/uv run --frozen poe start
./.tools/bin/uv run --frozen poe ready
./.tools/bin/uv run --frozen poe ingest
```

`poe ingest` loads the procedure corpus into the running stack; `poe start` doesn't, and a search
on an empty corpus returns nothing. `poe verify` runs it for you.

PowerShell and POSIX wrappers are available under `infra/scripts/`. After uv is on `PATH`, the
shorter `uv run --frozen poe <task>` form works; in PowerShell on Windows the pinned binary is
`.tools/bin/uv.exe`.

| Service | Local URL | Purpose |
|---|---|---|
| API | `http://localhost:8000` | Submit readings, poll exception summaries, search procedures |
| Token issuer: discovery document | `http://localhost:8180/.well-known/openid-configuration` | The development issuer's OIDC discovery document: its `issuer` and `jwks_uri` |
| Token issuer: key set | `http://localhost:8180/.well-known/jwks.json` | The published key set (JWKS) that `config/auth.yaml` names |
| Jaeger | `http://localhost:16686` | Open traces; the trace ids the audit records carry are these |
| Grafana | `http://localhost:3000` | Use the focused diagnostics dashboard |
| Prometheus | `http://localhost:9090` | Query bounded metrics and inspect the deployed alert rule |
| Alertmanager | `http://localhost:9093` | Inspect firing and resolved alerts |
| LocalStack S3/SQS/Secrets Manager | `http://localhost:4566` | The emulated object-storage, queue and secret-store endpoint |

Each of these ports can be overridden by setting the matching `COLDLINE_API_HOST_PORT`,
`COLDLINE_ISSUER_HOST_PORT`, `COLDLINE_JAEGER_HOST_PORT`, `COLDLINE_GRAFANA_HOST_PORT`,
`COLDLINE_PROMETHEUS_HOST_PORT`, `COLDLINE_ALERTMANAGER_HOST_PORT`, or
`COLDLINE_LOCALSTACK_HOST_PORT` environment variable in your shell environment or a local
`.env` file (copy `.env.example`) if a default collides with something already running on your
machine. Keep the override in place for every `poe` command. If you remap the issuer port,
keep `config/auth.yaml` unchanged: it names the default port. Host-side tools resolve the API's
and the issuer's origins from `COLDLINE_API_HOST_PORT` and `COLDLINE_ISSUER_HOST_PORT` (the
environment, then `.env`, then the default), the secret tools resolve LocalStack's host port
from `COLDLINE_LOCALSTACK_HOST_PORT` the same way, and the API and the worker use the
Compose-network origins.

This repository runs as its own Compose project, `coldline-task-5-1`. If a Project 4 stack is
still running, run `poe stop` in that repository first; otherwise `poe start` here fails
because the published ports are already taken.

PostgreSQL, Redis, worker metrics, and OTLP remain inside the Compose network. Codespaces uses the
same `compose.yaml` and keeps every forwarded port private.

## Commands

| Command | What it does |
|---|---|
| `poe verify` | Starts the stack and runs the platform's checks, then your tests under `tests/student/`. CI runs the same command. |
| `poe demo` | Runs the vaccine exception end to end. Empty until you fill it. |
| `poe start` / `poe ready` | Start the stack, then wait until every service answers. |
| `poe stop` | Stop the stack and keep its data. |
| `poe reset` | Stop the stack and delete its data volumes. |
| `poe student-tests` | Run only your tests under `tests/student/`. |

Run each one as `./.tools/bin/uv run --frozen poe <command>` (`.tools/bin/uv.exe` in PowerShell
on Windows).

## Where things live

- `src/`: the platform's code. Your agent goes here too.
- `tests/student/`: your tests. `poe verify` runs every test in this folder.
- `docs/capstone/`: your evidence notes, one per Task, named `task-NN.md` with a two-digit Task
  number, for example `docs/capstone/task-01.md`.
- `compose.yaml`: the local services. Add the services your agent needs here.
- `.github/workflows/verify.yml`: the CI workflow. Keep it unchanged.
- `docs/architecture/`, `docs/security/`, `docs/governance/`, `docs/student/`: the platform's
  design records from earlier Projects, for reference.

Never commit a secret, a key or personal data. The Project's rules for what stays out of a
submission are in the lesson on how the Project is submitted and reviewed.
