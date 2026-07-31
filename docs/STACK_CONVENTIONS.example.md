# Stack-specific conventions example

> Optional companion to the canonical
> [`AGENTS.example.md`](../config/skills/review-global-agents/references/AGENTS.example.md).
> Copy, remove, and
> adapt sections to match your actual stack. Load this file only when a task touches
> one of these technologies; do not place all stack knowledge in always-loaded global
> instructions.

## Next.js project initialization

When creating a new Next.js project, use a consistent non-interactive command. This
example deliberately keeps a root-level `app/` directory:

```bash
npx create-next-app@latest <project-name> \
  --typescript --tailwind --eslint --app --yes
```

- Do not add `--src-dir` if the convention is a root-level `app/` directory.
- Let `create-next-app` use its default import alias unless the project requires one.
- Use `--yes` in automation to avoid interactive prompts.
- Verify current flags against the installed/current Next.js documentation.

## Local email testing for Node projects

- Use `nodemailer` with SMTP transport to avoid provider-specific SDK lock-in.
- Use Mailpit locally, commonly through a development Docker Compose file.
  - Web UI: `http://localhost:8025`
  - SMTP: `localhost:1025`
- Keep production code provider-neutral by changing environment variables rather than
  the sending implementation.
- Common variables: `SMTP_HOST`, `SMTP_PORT`, `SMTP_SECURE`, `SMTP_USER`,
  `SMTP_PASS`, and `SMTP_FROM`.
- For applications where local email is optional, the email utility may explicitly
  return a result such as `{ skipped: true }` when `SMTP_HOST` is unset. Log that
  decision rather than silently pretending a message was sent.

## Domain reference guides

Large domain guides are better maintained as separate, on-demand documents or skills.
Reference only files that are actually distributed with your setup, and keep their
scope explicit. For example:

```text
SAP Commerce task  → load the SAP Commerce implementation skill/reference
Spartacus task     → load the composable-storefront skill/reference
SAP BTP task       → load the BTP implementation skill/reference
```

Before publishing a domain guide:

1. Confirm that you own or may redistribute the content.
2. Remove customer names, internal URLs, credentials, IDs, and proprietary examples.
3. Replace organization-specific package names with obvious placeholders.
4. Verify examples against current vendor documentation and supported versions.
5. Prefer a focused skill or versioned guide over thousands of always-loaded lines.
6. Add the guide to security scanning and review it independently before release.
