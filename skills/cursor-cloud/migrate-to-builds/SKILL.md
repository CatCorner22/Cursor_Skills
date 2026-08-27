---
name: migrate-to-builds
disable-model-invocation: true
description: Test that a Cloud Agent environment will work with prebuilt environment builds and recommend any required changes. Use when the user wants to migrate to builds, test build compatibility, or follow the Builds page setup-agent flow.
environments: [cloud]
---
# Migrate an Environment to Builds

Use this skill when the user wants to test that the current Cloud Agent environment will work with environment builds, or asks to migrate to builds. Do not enable builds yourself; the user enables them on the environment page after review.

## Resources

| Workflow | Reference |
| --- | --- |
| Migrate an existing environment to builds | [Migrate an environment to builds](references/migrate-to-builds.md) |

## Choose the workflow

Read [Migrate an environment to builds](references/migrate-to-builds.md) and follow it. Call `environment-info` first when available so the reference can classify repository-managed vs DB-managed configuration (see the tool-name table in `../env-setup/SKILL.md` for short-name vs `cursor-cloud-`-prefixed forms).

## Mental Model

Read `../env-setup/SKILL.md`'s "Mental Model", "Configuration Sources and Precedence", and "Choosing install, start, or terminals" sections first — this skill builds directly on that lifecycle model (base environment vs. repository bootstrap, `.cursor/environment.json` precedence, and how to classify setup work across `install`/`start`/`terminals`) rather than repeating it here.

The one thing specific to migration: with environment builds, `install` creates the baseline snapshot and is **not** rerun when a new pod boots from that build, so anything currently living in `install` that needs to run per-boot must move to `start` or `terminals` before the environment is build-compatible. That reclassification is the actual work of this skill — use env-setup's "Diagnose misplaced work" checklist to find what needs to move.

## Safety

- Never put tokens, passwords, private keys, or secret values in `environment.json`, Dockerfiles, committed scripts, logs, or chat output. Use supported environment secrets or build-secret mechanisms.
- Do not deploy, publish, apply infrastructure, or mutate production resources as part of environment setup.
- Keep Dockerfiles and install scripts deterministic, non-interactive, and narrowly scoped.
- Do not weaken network, certificate, or package-integrity controls merely to make setup pass.
- Avoid expensive rebuilds until static checks pass. Trigger a build only when the migrate reference says to. Unrelated questions never do.
- Do not enable builds for the environment and do not ask the user to promote, activate, merge, or save a draft as the primary next step.

## Response

Lead with the outcome. Include only the sections relevant to the request:

- Effective configuration source and whether it is repository-managed or DB-managed.
- What was inspected or changed.
- Build and fresh-agent validation evidence.
- Remaining manual action: usually enabling builds on the environment page.

When mentioning an environment or build ID in chat, use a markdown hyperlink whose link text is the ID — never a bare ID:

- Environment / environment dashboard (when directing the user to enable builds or review build status): `[<environmentPublicId>](https://cursor.com/dashboard/cloud-agents/environments/e/<environmentPublicId>)`
- Build: `[<buildId>](https://cursor.com/dashboard/cloud-agents/builds/<buildId>)`

Prefer the environment `url` from environment-info when present; otherwise construct the environment link with the format above. Do not append `#builds` — build settings and the builds list live on the default environment detail page.
