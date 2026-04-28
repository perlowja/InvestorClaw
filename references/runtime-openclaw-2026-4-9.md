# Runtime Compatibility — OpenClaw 2026.4.9+

Behaviours confirmed against OpenClaw 2026.4.9 and must be followed exactly.

## Skill installation

Primary install path uses the linked-plugin mechanism:

```bash
git clone https://gitlab.com/argonautsystems/InvestorClaw.git /path/to/InvestorClaw
python3 -m pip install /path/to/InvestorClaw
openclaw plugins install --link /path/to/InvestorClaw
openclaw gateway restart
```

The `--link` flag creates a symlink so updates (`git pull`) are reflected
immediately without reinstalling.

## Skill removal

```bash
openclaw plugins uninstall investorclaw
openclaw gateway restart
```

## Exec session isolation

Agent `exec` sessions do **not** share filesystem context between calls.
Artifacts written in one exec call (e.g. a cloned repo) are invisible to a
subsequent exec call.

Consequence: all installation workflow steps — clone / download, dependency
install, skill directory copy, and cleanup — must be performed as direct
Bash operations by the calling agent, not delegated to the agent via exec
sessions.

## Model string aliases

The config may store `xai/grok-4-1-fast-reasoning`; runtime / sessions may
show `xai/grok-4-1-fast`. Both resolve to the same model. The alias
`grok-reasoning` also resolves to it. Accept any of the three — do not flag
as a mismatch.
