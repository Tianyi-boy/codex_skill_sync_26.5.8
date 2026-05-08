# my-codex-skills

Personal Codex skill sync repository.

## Layout

- `codex-skills/`: copied from `C:\Users\pc\.codex\skills`, excluding system/runtime skills.
- `agents-skills/`: copied from `C:\Users\pc\.agents\skills` when present.

## Sync From This Machine

Run from this repository root:

```powershell
robocopy C:\Users\pc\.codex\skills .\codex-skills /E /XD .system codex-primary-runtime /XF *.secret *.pem *.key *.pfx *.env
robocopy C:\Users\pc\.agents\skills .\agents-skills /E /XF *.secret *.pem *.key *.pfx *.env
git status
git add .
git commit -m "Sync Codex skills"
git push
```

Before committing, check `git status` and avoid adding secrets, tokens, local `.env` files, or machine-specific credentials.
